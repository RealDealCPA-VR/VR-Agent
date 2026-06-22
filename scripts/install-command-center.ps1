<#
.SYNOPSIS
  Install the RealDeal CPA Command Center tab into the Hermes dashboard.
  Idempotent. The dashboard source lives in the (gitignored) hermes-agent clone,
  so this script is the tracked, reproducible record of those edits. Called by
  scripts/install.ps1; re-run after updating upstream.
#>
$ErrorActionPreference = 'Stop'
$Root    = Split-Path -Parent $PSScriptRoot
$Overlay = Join-Path $Root 'vr-overlay\command-center'
$Hermes  = Join-Path $Root 'hermes-agent'
$Cli     = Join-Path $Hermes 'hermes_cli'
$Web     = Join-Path $Hermes 'web'
$NoBom = New-Object System.Text.UTF8Encoding($false)
function ReadT($p) { [System.IO.File]::ReadAllText($p) }
function WriteT($p, $t) { [System.IO.File]::WriteAllText($p, $t, $NoBom) }

if (-not (Test-Path $Hermes)) { Write-Error "Run scripts\install.ps1 first (no hermes-agent clone)."; exit 1 }

# 1) Backend: deploy the fleet data layer + routes next to the dashboard server
Copy-Item (Join-Path $Overlay 'fleet.py')        (Join-Path $Cli 'command_center_fleet.py')   -Force
Copy-Item (Join-Path $Overlay 'fleet.seed.json') (Join-Path $Cli 'fleet.seed.json')            -Force
Copy-Item (Join-Path $Overlay 'web_routes.py')   (Join-Path $Cli 'command_center_routes.py')   -Force
Write-Host "deployed: command_center_fleet.py, fleet.seed.json, command_center_routes.py -> hermes_cli"

# 2) Register the routes in web_server.py. MUST run before the SPA catch-all
#    ("/{full_path:path}") is mounted, or FastAPI resolves /api/command-center/*
#    to the catch-all. We insert immediately before `mount_spa(app)` (where the
#    codebase itself mounts plugin/auth routes for the same reason). Strip any
#    prior block first so re-runs relocate cleanly (idempotent).
$ws = Join-Path $Cli 'web_server.py'
$wsT = ReadT $ws
# strip any previously-inserted block(s) between markers, wherever they sit
# (trailing newline optional so an end-of-file block with no final newline matches)
$wsT = [System.Text.RegularExpressions.Regex]::Replace(
    $wsT, '(?s)\r?\n?# >>> RealDeal CPA Command Center.*?# <<< RealDeal CPA Command Center\r?\n?', "`n")
$block = @'
# >>> RealDeal CPA Command Center (added by scripts/install-command-center.ps1)
try:
    from hermes_cli import command_center_routes as _rdcc
    _rdcc.register(app, _require_token)
except Exception as _rdcc_err:  # never break the dashboard if the tab fails
    import logging as _rdcc_log
    _rdcc_log.getLogger(__name__).warning("command-center routes not registered: %s", _rdcc_err)
# <<< RealDeal CPA Command Center

'@
$anchor = 'mount_spa(app)'
if ($wsT -match [regex]::Escape($anchor)) {
    $idx = $wsT.IndexOf($anchor)
    $wsT = $wsT.Substring(0, $idx) + $block + $wsT.Substring($idx)
    WriteT $ws $wsT
    Write-Host "registered command-center routes in web_server.py (before mount_spa)"
} else {
    WriteT $ws ($wsT + "`n" + $block)
    Write-Host "registered command-center routes in web_server.py (appended; mount_spa anchor not found)"
}

# 3) Frontend: deploy the page component
Copy-Item (Join-Path $Overlay 'web\CommandCenterPage.tsx') (Join-Path $Web 'src\pages\CommandCenterPage.tsx') -Force
Write-Host "deployed: CommandCenterPage.tsx -> web/src/pages"

# 4) Wire the tab into App.tsx (3 idempotent inserts)
$app = Join-Path $Web 'src\App.tsx'
$t = ReadT $app
if ($t -notlike '*CommandCenterPage*') {
    $impAnchor = 'import SessionsPage from "@/pages/SessionsPage";'
    $impNew = @'
import SessionsPage from "@/pages/SessionsPage";
import CommandCenterPage from "@/pages/CommandCenterPage";
import { Network as CommandCenterIcon } from "lucide-react";
'@
    $routeAnchor = 'const BUILTIN_ROUTES_CORE: Record<string, ComponentType> = {'
    $routeNew = @'
const BUILTIN_ROUTES_CORE: Record<string, ComponentType> = {
  "/command-center": CommandCenterPage,
'@
    $navAnchor = 'const BUILTIN_NAV_REST: NavItem[] = ['
    $navNew = @'
const BUILTIN_NAV_REST: NavItem[] = [
  { path: "/command-center", label: "Command Center", icon: CommandCenterIcon },
'@
    $t = $t.Replace($impAnchor, $impNew).Replace($routeAnchor, $routeNew).Replace($navAnchor, $navNew)
    WriteT $app $t
    Write-Host "wired Command Center into App.tsx (route + nav + import)"
} else { Write-Host "ok: App.tsx already wired" }

# 5) Add the React Flow dependency + rebuild the dashboard
Push-Location $Web
try {
    if (-not (Test-Path (Join-Path $Web 'node_modules\@xyflow\react'))) {
        Write-Host "installing @xyflow/react..."
        npm install @xyflow/react --silent
    } else { Write-Host "ok: @xyflow/react already installed" }
    Write-Host "rebuilding dashboard..."
    npm run build
} finally { Pop-Location }

Write-Host "`nCommand Center installed. Restart the dashboard:" -ForegroundColor Green
Write-Host "  .\scripts\vragent.ps1 dashboard   then open the 'Command Center' tab"
