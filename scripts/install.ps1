<#
.SYNOPSIS
  One-shot reproducible setup for VRAGENT (overlay on Hermes).
  Safe to re-run: skips steps already done.

  Prereqs on PATH: git, uv, node 20.x, npm. (pnpm optional, for KarbonCopy live.)
#>
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Hermes = Join-Path $Root 'hermes-agent'
$Venv = Join-Path $Hermes '.venv'
$Pin = '2ab09a6c50836d8cc407e4957c828161d0bbd81b'   # see HERMES_PIN.txt

function Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }

Step "1/7 Clone upstream Hermes (pinned)"
if (-not (Test-Path (Join-Path $Hermes '.git'))) {
    git clone https://github.com/NousResearch/hermes-agent.git $Hermes
    git -C $Hermes checkout $Pin 2>$null
} else { Write-Host "hermes-agent already present" }

Step "2/7 Create Python 3.11 venv"
if (-not (Test-Path $Venv)) { uv venv --python 3.11 --directory $Hermes } else { Write-Host "venv exists" }

Step "3/7 Install Hermes (curated extras)"
uv pip install --directory $Hermes -e ".[cli,web,mcp,messaging,slack,cron,anthropic,vision]"

Step "4/7 Install RPA engine for desktop control (ai-rpa-system[gui])"
uv pip install --directory $Hermes -e "C:/Users/VR/Projects/RPA[gui]"

Step "5/7 Seed Hermes' built-in skills into HERMES_HOME"
$homeSkills = Join-Path $Root 'home\skills'
New-Item -ItemType Directory -Force -Path $homeSkills | Out-Null
Copy-Item (Join-Path $Hermes 'skills\*') $homeSkills -Recurse -Force

Step "6/7 Install agent-browser (web browsing) + Chromium"
Push-Location $Hermes
npm install
& (Join-Path $Hermes 'node_modules\.bin\agent-browser.cmd') install
Pop-Location

Step "7/7 Sync overlay (config + persona) into HERMES_HOME"
& (Join-Path $PSScriptRoot 'sync-overlay.ps1')

Write-Host "`nDone. Next:" -ForegroundColor Green
Write-Host "  1. Put an LLM key in home\.env  (OPENROUTER_API_KEY or ANTHROPIC_API_KEY)"
Write-Host "  2. .\scripts\vragent.ps1 doctor"
Write-Host "  3. .\scripts\vragent.ps1            # start the agent"
