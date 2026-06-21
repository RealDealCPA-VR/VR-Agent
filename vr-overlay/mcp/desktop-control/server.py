"""
VRAGENT desktop-control MCP server.

Gives the agent Windows GUI control (Hermes' built-in `computer_use` is macOS-only).
Fast primitives go straight through pyautogui for a tight screenshot->act->verify
loop; multi-step automation is delegated to the audited ai_rpa_system WorkflowExecutor
(which runs a security scan and refuses CRITICAL-risk workflows by default).

Registered in config.yaml under mcp_servers.desktop. Runs over stdio.

Safety:
  - pyautogui FAILSAFE stays ON: slam the mouse into any screen corner to abort.
  - The paired `desktop-control` skill instructs the agent to screenshot first,
    confirm before destructive UI actions, and verify after acting.
"""
from __future__ import annotations

import io
import json
from typing import Optional

from mcp.server.fastmcp import FastMCP, Image

mcp = FastMCP("desktop-control")

# --- lazy singletons -------------------------------------------------------
_pg = None
_engine = None


def _pyautogui():
    global _pg
    if _pg is None:
        import pyautogui
        pyautogui.FAILSAFE = True   # mouse-to-corner kill switch
        pyautogui.PAUSE = 0.1
        _pg = pyautogui
    return _pg


def _automation_engine():
    global _engine
    if _engine is None:
        from ai_rpa_system.automation_engine import AutomationEngine
        _engine = AutomationEngine()
    return _engine


def _png_bytes(img, max_width: int = 1366) -> bytes:
    # Downscale wide screenshots to keep vision-token cost sane.
    if img.width > max_width:
        h = int(img.height * max_width / img.width)
        img = img.resize((max_width, h))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# --- observe ---------------------------------------------------------------
@mcp.tool()
def screen_info() -> str:
    """Return the primary screen size as 'WIDTHxHEIGHT' (pixels)."""
    w, h = _pyautogui().size()
    return f"{w}x{h}"


@mcp.tool()
def screenshot(region: Optional[list[int]] = None) -> Image:
    """Capture the screen and return it as a PNG image so you can see the desktop.

    region: optional [x, y, width, height] to capture just part of the screen.
    Take a screenshot BEFORE acting (to find targets) and AFTER (to verify).
    """
    pg = _pyautogui()
    if region is not None:
        if len(region) != 4:
            raise ValueError("region must be exactly [x, y, width, height]")
        shot = pg.screenshot(region=tuple(int(v) for v in region))
    else:
        shot = pg.screenshot()
    return Image(data=_png_bytes(shot), format="png")


# --- mouse -----------------------------------------------------------------
@mcp.tool()
def move_mouse(x: int, y: int) -> str:
    """Move the mouse to absolute screen coordinates (x, y)."""
    _pyautogui().moveTo(x, y, duration=0.2)
    return f"moved to ({x}, {y})"


@mcp.tool()
def click(x: int, y: int, button: str = "left", clicks: int = 1) -> str:
    """Click at (x, y). button: 'left'|'right'|'middle'. clicks: 1 or 2."""
    _automation_engine().click(x, y, button=button, clicks=clicks)
    return f"{button} click x{clicks} at ({x}, {y})"


@mcp.tool()
def double_click(x: int, y: int) -> str:
    """Double-click at (x, y)."""
    _automation_engine().click(x, y, button="left", clicks=2)
    return f"double click at ({x}, {y})"


@mcp.tool()
def right_click(x: int, y: int) -> str:
    """Right-click at (x, y) (context menu)."""
    _automation_engine().click(x, y, button="right", clicks=1)
    return f"right click at ({x}, {y})"


@mcp.tool()
def drag(x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> str:
    """Drag from (x1, y1) to (x2, y2)."""
    pg = _pyautogui()
    pg.moveTo(x1, y1, duration=0.2)
    pg.dragTo(x2, y2, duration=duration, button="left")
    return f"dragged ({x1},{y1}) -> ({x2},{y2})"


@mcp.tool()
def scroll(amount: int, x: Optional[int] = None, y: Optional[int] = None) -> str:
    """Scroll vertically. Positive = up, negative = down. Optionally at (x, y)."""
    _automation_engine().scroll(amount, x=x, y=y)
    return f"scrolled {amount}"


@mcp.tool()
def locate_image(image_path: str, confidence: float = 0.8) -> str:
    """Find an on-screen template image; return its center 'x,y' or 'not found'.

    image_path: path to a PNG/JPG of the UI element to locate.
    """
    try:
        loc = _pyautogui().locateCenterOnScreen(image_path, confidence=confidence)
    except Exception as e:  # pyscreeze raises if not found in some versions
        return f"not found ({e.__class__.__name__})"
    if loc is None:
        return "not found"
    return f"{int(loc.x)},{int(loc.y)}"


# --- keyboard --------------------------------------------------------------
@mcp.tool()
def type_text(text: str) -> str:
    """Type text at the current focus (as if typed on the keyboard)."""
    _automation_engine().type_text(text)
    return f"typed {len(text)} chars"


@mcp.tool()
def press_key(key: str) -> str:
    """Press a single key, e.g. 'enter', 'tab', 'esc', 'f5', 'down'."""
    _automation_engine().press_key(key)
    return f"pressed {key}"


@mcp.tool()
def hotkey(keys: list[str]) -> str:
    """Press a key combination, e.g. ['ctrl','c'] or ['win','r'] or ['alt','tab']."""
    _automation_engine().hotkey(*keys)
    return f"hotkey {'+'.join(keys)}"


# --- apps ------------------------------------------------------------------
@mcp.tool()
def open_application(name: str) -> str:
    """Open/launch a Windows application by name or path (uses the Run dialog).

    Examples: 'notepad', 'excel', 'chrome', 'C:/path/to/app.exe'.
    """
    pg = _pyautogui()
    pg.hotkey("win", "r")
    pg.sleep(0.6)
    _automation_engine().type_text(name)
    pg.press("enter")
    return f"launched '{name}'"


# --- audited multi-step ----------------------------------------------------
@mcp.tool()
def run_workflow(steps_json: str, allow_unsafe: bool = False) -> str:
    """Run a multi-step desktop workflow through the audited RPA engine.

    steps_json: a JSON array of ai_rpa_system ActionStep objects, e.g.
      [{"action":"open_application","description":"open notepad","target":"notepad"},
       {"action":"type","description":"type hello","text":"hello"}]
    A security scan runs first and blocks CRITICAL-risk workflows unless
    allow_unsafe=true. Returns an LLM-friendly summary of each step's result.
    """
    from ai_rpa_system.models import Workflow, ActionStep

    try:
        raw = json.loads(steps_json)
    except json.JSONDecodeError as e:
        return f"error: steps_json is not valid JSON ({e})"
    if not isinstance(raw, list):
        return "error: steps_json must be a JSON array of ActionStep objects"
    try:
        steps = [ActionStep(**s) for s in raw]
    except Exception as e:
        return f"error: invalid step ({e.__class__.__name__}: {e})"

    from ai_rpa_system.executor import WorkflowExecutor
    wf = Workflow(name="vragent_adhoc", description="ad-hoc desktop workflow", steps=steps)
    ex = WorkflowExecutor()
    result = ex.execute_workflow(wf, validate=True, safe=True, allow_unsafe=allow_unsafe)
    return ex.get_llm_friendly_result(result)


if __name__ == "__main__":
    mcp.run()
