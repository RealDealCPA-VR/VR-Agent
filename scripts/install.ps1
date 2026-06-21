<#
.SYNOPSIS
  One-shot reproducible setup for VRAGENT (overlay on Hermes).
  Safe to re-run: skips steps already done.

  Prereqs on PATH: git, uv, node 20.x, npm. (pnpm optional, for KarbonCopy live.)
  Note: Node 20.x is recommended - the QuickBooks live COM binding (winax) won't
  build on Node 22+, and Hermes runs fine on 20 despite a higher engines hint.
#>
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Hermes = Join-Path $Root 'hermes-agent'
$Venv = Join-Path $Hermes '.venv'
$Projects = (Split-Path -Parent $Root).Replace('\','/')   # sibling projects (RPA, VR-Ledger, ...)
$Pin = '2ab09a6c50836d8cc407e4957c828161d0bbd81b'   # see HERMES_PIN.txt

function Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }

Step "1/8 Clone upstream Hermes (pinned)"
if (-not (Test-Path (Join-Path $Hermes '.git'))) {
    git clone https://github.com/NousResearch/hermes-agent.git $Hermes
    if ($LASTEXITCODE -ne 0) { throw "git clone failed (exit $LASTEXITCODE)" }
    git -C $Hermes checkout $Pin
    if ($LASTEXITCODE -ne 0) { Write-Warning "Could not check out pinned commit $Pin - staying on default branch (upstream may have drifted)." }
} else { Write-Host "hermes-agent already present" }

Step "2/8 Create Python 3.11 venv"
if (-not (Test-Path $Venv)) { uv venv --python 3.11 --directory $Hermes } else { Write-Host "venv exists" }

Step "3/8 Install Hermes (extras + capability packs)"
uv pip install --directory $Hermes -e ".[cli,web,mcp,messaging,slack,cron,anthropic,vision,fal,exa,firecrawl,google,youtube,edge-tts]"

Step "4/8 Install local engines: desktop-control (RPA) + VR-Ledger"
# Sibling projects, resolved relative to this project's parent folder.
# Warn-and-skip (don't abort) if a sibling is absent - its MCP just won't load.
if (Test-Path "$Projects/RPA") { uv pip install --directory $Hermes -e "$Projects/RPA[gui]" }
else { Write-Warning "RPA project not found at $Projects/RPA - desktop-control MCP will be unavailable until it's present." }
if (Test-Path "$Projects/VR-Ledger") { uv pip install --directory $Hermes -e "$Projects/VR-Ledger" }
else { Write-Warning "VR-Ledger project not found at $Projects/VR-Ledger - vr-ledger MCP will be unavailable until it's present." }

Step "5/8 Seed built-in + finance/research skills into HERMES_HOME"
$homeSkills = Join-Path $Root 'home\skills'
New-Item -ItemType Directory -Force -Path $homeSkills | Out-Null
Copy-Item (Join-Path $Hermes 'skills\*') $homeSkills -Recurse -Force
# High-value optional skills for an accounting/consulting power user
$opt = Join-Path $Hermes 'optional-skills'
foreach ($s in @('finance\3-statement-model','finance\dcf-model','finance\comps-analysis','finance\lbo-model','finance\merger-model','finance\excel-author','finance\pptx-author','finance\stocks','research\duckduckgo-search','research\domain-intel')) {
    $src = Join-Path $opt $s
    if (Test-Path $src) {
        $dst = Join-Path $homeSkills (Split-Path $s -Parent)
        New-Item -ItemType Directory -Force -Path $dst | Out-Null
        Copy-Item $src $dst -Recurse -Force
    }
}

Step "6/8 Install agent-browser (web browsing) + Chromium"
Push-Location $Hermes
try {
    npm install
    $ab = Join-Path $Hermes 'node_modules\.bin\agent-browser.cmd'
    if (Test-Path $ab) { & $ab install }
    else { Write-Warning "agent-browser not found after npm install - browser automation unavailable until 'npm install' succeeds." }
} finally { Pop-Location }

Step "7/8 Sync overlay (config + persona) into HERMES_HOME"
& (Join-Path $PSScriptRoot 'sync-overlay.ps1')

Step "8/8 Re-brand the web dashboard to RealDeal CPA (+ rebuild)"
& (Join-Path $PSScriptRoot 'brand-web.ps1')

Write-Host "`nDone. Next:" -ForegroundColor Green
Write-Host "  1. Put an LLM key in home\.env  (OPENROUTER_API_KEY or ANTHROPIC_API_KEY)"
Write-Host "  2. .\scripts\vragent.ps1 doctor"
Write-Host "  3. .\scripts\vragent.ps1            # start the agent"
