"""
RealDeal CPA Command Center — backend routes.

Deployed (by scripts/install-command-center.ps1) next to the dashboard server
as hermes_cli/command_center_routes.py, alongside hermes_cli/command_center_fleet.py.
web_server.py calls register(app, _require_token) once after the FastAPI app is built.

Thin layer over the fleet data module: serve fleet state + options, add/patch/remove
agents, reset. All endpoints require the dashboard session token (the frontend's
fetchJSON injects it automatically).
"""
# NOTE: do NOT add `from __future__ import annotations` here. FastAPI resolves the
# `request: Request` parameter annotation via the module globals; as a stringized
# annotation it would be treated as a query field ("Field required") and 422 every
# call. Keep Request/HTTPException imported at module scope so the names resolve.
from fastapi import Request, HTTPException


def register(app, require_token=None):
    if require_token is None:
        def require_token(_request):  # localhost fallback: no-op
            return None

    # fleet module is deployed beside this file as command_center_fleet
    try:
        from hermes_cli import command_center_fleet as fleet
    except Exception:  # running from the overlay dir (dev)
        import importlib.util
        import pathlib
        p = pathlib.Path(__file__).with_name("fleet.py")
        spec = importlib.util.spec_from_file_location("command_center_fleet", p)
        fleet = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fleet)

    @app.get("/api/command-center/state")
    async def cc_state(request: Request):
        require_token(request)
        return fleet.load()

    @app.get("/api/command-center/options")
    async def cc_options(request: Request):
        require_token(request)
        return fleet.options()

    @app.post("/api/command-center/agents")
    async def cc_add(request: Request):
        require_token(request)
        b = await request.json()
        name = (b.get("name") or "").strip()
        if not name:
            raise HTTPException(status_code=400, detail="name is required")
        agent = fleet.add_agent(name, b.get("role", ""), b.get("model", ""),
                                b.get("skills") or [], b.get("tools") or [])
        return {"ok": True, "agent": agent}

    @app.patch("/api/command-center/agents/{agent_id}")
    async def cc_patch(agent_id: str, request: Request):
        require_token(request)
        b = await request.json()
        agent = fleet.update_agent(agent_id, **b)
        if agent is None:
            raise HTTPException(status_code=404, detail="agent not found")
        return {"ok": True, "agent": agent}

    @app.delete("/api/command-center/agents/{agent_id}")
    async def cc_delete(agent_id: str, request: Request):
        require_token(request)
        return {"ok": fleet.remove_agent(agent_id)}

    @app.post("/api/command-center/reset")
    async def cc_reset(request: Request):
        require_token(request)
        return fleet.reset()

    # The dashboard registers a SPA catch-all ("/{full_path:path}") that matches
    # every path. FastAPI resolves routes in registration order, so unless our
    # API routes precede the catch-all they get swallowed (404/405). Move them to
    # the front of the router so this works no matter when register() is called.
    routes = app.router.routes
    ours = [r for r in routes if getattr(r, "path", "").startswith("/api/command-center")]
    for r in ours:
        routes.remove(r)
    for r in reversed(ours):
        routes.insert(0, r)
