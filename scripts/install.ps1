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

Step "0/8 Preflight: verify prerequisites on PATH"
# Fail fast with an actionable message instead of a cryptic mid-run error.
foreach ($tool in @('git', 'uv', 'node', 'npm')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "$tool not found on PATH - install it first (see SETUP-NEW-MACHINE.md section 1)."
    }
}
# pnpm is optional - only the KarbonCopy sibling needs it.
if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    Write-Warning "pnpm not found on PATH - KarbonCopy live MCP will be unavailable until pnpm is installed."
}
# Node 20.x is required for the QuickBooks live COM binding (winax). Hermes itself
# runs on newer Node, so this is a warning, not a hard stop.
try {
    $nv = (node --version) -replace '^v', ''
    $major = [int]($nv.Split('.')[0])
    if ($major -ge 22) {
        Write-Warning "Node $nv detected - the QuickBooks live COM binding (winax) only builds on Node 20.x. Hermes still runs, but the QB live MCP will fail to build."
    }
} catch {
    Write-Warning "Could not determine Node version - ensure Node 20.x for the QuickBooks live COM binding."
}

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

# Declare the overlay's own MCP runtime dep (mcp) independently of the upstream extras.
$mcpReqs = Join-Path $Root 'vr-overlay/mcp/requirements.txt'
if (Test-Path $mcpReqs) { uv pip install --directory $Hermes -r $mcpReqs }

Step "4b/8 Build Node sibling MCPs: QuickBooks (npm) + KarbonCopy (pnpm)"
# Same warn-and-skip-if-absent pattern as the Python siblings above. Idempotent:
# skip the build when the artifact already exists (unless -force is desired).
$qb = "$Projects/Quickbooks MCP Desktop"
if (Test-Path $qb) {
    if (-not (Test-Path "$qb/dist/index.js")) {
        Push-Location $qb
        try {
            if (Test-Path "$qb/package-lock.json") { npm ci } else { npm install }
            npm run build
        } finally { Pop-Location }
    } else { Write-Host "QuickBooks MCP already built (dist/index.js present)" }
} else { Write-Warning "Quickbooks MCP Desktop not found at $qb - quickbooks MCP will be unavailable until it's present." }

$kc = "$Projects/KarbonCopy"
if (Test-Path $kc) {
    if (-not (Test-Path "$kc/node_modules")) {
        if (Get-Command pnpm -ErrorAction SilentlyContinue) {
            Push-Location $kc
            try { pnpm install } finally { Pop-Location }
        } else { Write-Warning "pnpm not found on PATH - cannot install KarbonCopy; the karboncopy MCP will be unavailable. Install pnpm (npm install -g pnpm) and re-run." }
    } else { Write-Host "KarbonCopy already installed (node_modules present)" }
} else { Write-Warning "KarbonCopy not found at $kc - karboncopy MCP will be unavailable until it's present." }

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

$envFile = Join-Path $Root 'home\.env'
$envState = if (Test-Path $envFile) { "(already created - fill in your key)" } else { "(will be created on first sync from env.example)" }

Write-Host "`nDone. Get started in 3 steps:" -ForegroundColor Green
Write-Host "  1. Add an LLM key to your .env $envState"
Write-Host "       Path: $envFile"
Write-Host "       Open: notepad `"$envFile`""
Write-Host "       Set OPENROUTER_API_KEY or ANTHROPIC_API_KEY."
Write-Host "       Get an OpenRouter key at https://openrouter.ai/keys"
Write-Host "  2. Verify:  .\scripts\vragent.ps1 doctor"
Write-Host "  3. Start:   .\scripts\vragent.ps1"
