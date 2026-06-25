<#
.SYNOPSIS
  Re-brand the Hermes web dashboard to RealDeal CPA (name, tab title, favicon)
  and rebuild it. Idempotent - safe to re-run after a `git pull` of upstream.

  The dashboard source lives in the (gitignored) hermes-agent clone, so this
  script is the tracked, reproducible record of those edits. Called by
  scripts/install.ps1; run it manually after updating upstream.
#>
param([switch]$Force)
$ErrorActionPreference = 'Stop'
$Root  = Split-Path -Parent $PSScriptRoot
$Web   = Join-Path $Root 'hermes-agent\web'
$Brand = Join-Path $Root 'vr-overlay\brand'

# Read/write UTF-8 explicitly. PS 5.1 Get-Content -Raw reads ANSI (mangles non-ASCII)
# and Set-Content -Encoding UTF8 writes a BOM (which can corrupt web source files).
$NoBom = New-Object System.Text.UTF8Encoding($false)
function Patch($path, $pattern, $replacement, $label) {
    if (-not (Test-Path $path)) { Write-Host "skip ($label): $path missing"; return $false }
    $raw = [System.IO.File]::ReadAllText($path)
    if ($raw -match $pattern) {
        [System.IO.File]::WriteAllText($path, ($raw -replace $pattern, $replacement), $NoBom)
        Write-Host "branded: $label"
        return $true
    } else {
        Write-Host "ok ($label): already branded or pattern absent"
        return $false
    }
}

# Track whether any brand string actually changed, to skip a no-op rebuild.
$Changed = $false

# 1) Browser tab title
$Changed = (Patch (Join-Path $Web 'index.html') '<title>[^<]*</title>' '<title>RealDeal CPA</title>' 'index.html title') -or $Changed
# 2) Favicon -> our SVG mark
$Changed = (Patch (Join-Path $Web 'index.html') 'href="/favicon\.(ico|svg)"' 'href="/favicon.svg"' 'index.html favicon') -or $Changed
Copy-Item (Join-Path $Brand 'favicon.svg') (Join-Path $Web 'public\favicon.svg') -Force
Write-Host "copied: favicon.svg -> web/public"

# 3) All user-facing brand strings across ALL languages (header brand, achievements
#    panel title, share-tweet text). Order: "Achievements" before bare "Agent".
Get-ChildItem (Join-Path $Web 'src\i18n') -Filter '*.ts' -ErrorAction SilentlyContinue | ForEach-Object {
    $Changed = (Patch $_.FullName 'Hermes Achievements' 'RealDeal CPA Achievements' "i18n $($_.Name) achievements") -or $Changed
    $Changed = (Patch $_.FullName 'Hermes Agent' 'RealDeal CPA' "i18n $($_.Name) brand/tweet") -or $Changed
}
# 4) Sidebar wordmark (hardcoded JSX)
$Changed = (Patch (Join-Path $Web 'src\App.tsx') 'Hermes(\s*<br />\s*)Agent' 'RealDeal${1}CPA' 'App.tsx wordmark') -or $Changed
# 4b) FastAPI app title (shown in the dashboard's /docs + OpenAPI schema)
$Changed = (Patch (Join-Path $Root 'hermes-agent\hermes_cli\web_server.py') 'FastAPI\(title="Hermes Agent"' 'FastAPI(title="RealDeal CPA"' 'web_server FastAPI title') -or $Changed
# 4c) Telegram onboarding default bot name
$Changed = (Patch (Join-Path $Web 'src\pages\ChannelsPage.tsx') 'bot_name: "Hermes Agent"' 'bot_name: "RealDeal CPA"' 'ChannelsPage bot_name') -or $Changed

# 5) Rebuild the SPA that `hermes dashboard` serves (web -> hermes_cli/web_dist).
#    Skip the (expensive) Vite build when nothing changed and the dist already exists.
$WebDist = Join-Path $Root 'hermes-agent\hermes_cli\web_dist'
if ($Force -or $Changed -or -not (Test-Path $WebDist)) {
    Write-Host "`nRebuilding dashboard (npm run build)..." -ForegroundColor Cyan
    Push-Location $Web
    try { npm run build } finally { Pop-Location }
    Write-Host "`nDone. Restart the dashboard to see the rebrand." -ForegroundColor Green
} else {
    Write-Host "`nok: dashboard already branded and built; skipping npm build (use -Force to rebuild)." -ForegroundColor Green
}
