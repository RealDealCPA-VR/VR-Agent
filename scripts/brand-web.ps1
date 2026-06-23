<#
.SYNOPSIS
  Re-brand the Hermes web dashboard to RealDeal CPA (name, tab title, favicon)
  and rebuild it. Idempotent - safe to re-run after a `git pull` of upstream.

  The dashboard source lives in the (gitignored) hermes-agent clone, so this
  script is the tracked, reproducible record of those edits. Called by
  scripts/install.ps1; run it manually after updating upstream.
#>
$ErrorActionPreference = 'Stop'
$Root  = Split-Path -Parent $PSScriptRoot
$Web   = Join-Path $Root 'hermes-agent\web'
$Brand = Join-Path $Root 'vr-overlay\brand'

# Read/write UTF-8 explicitly. PS 5.1 Get-Content -Raw reads ANSI (mangles non-ASCII)
# and Set-Content -Encoding UTF8 writes a BOM (which can corrupt web source files).
$NoBom = New-Object System.Text.UTF8Encoding($false)
function Patch($path, $pattern, $replacement, $label) {
    if (-not (Test-Path $path)) { Write-Host "skip ($label): $path missing"; return }
    $raw = [System.IO.File]::ReadAllText($path)
    if ($raw -match $pattern) {
        [System.IO.File]::WriteAllText($path, ($raw -replace $pattern, $replacement), $NoBom)
        Write-Host "branded: $label"
    } else {
        Write-Host "ok ($label): already branded or pattern absent"
    }
}

# 1) Browser tab title
Patch (Join-Path $Web 'index.html') '<title>[^<]*</title>' '<title>RealDeal CPA</title>' 'index.html title'
# 2) Favicon -> our SVG mark
Patch (Join-Path $Web 'index.html') 'href="/favicon\.(ico|svg)"' 'href="/favicon.svg"' 'index.html favicon'
Copy-Item (Join-Path $Brand 'favicon.svg') (Join-Path $Web 'public\favicon.svg') -Force
Write-Host "copied: favicon.svg -> web/public"

# 3) All user-facing brand strings across ALL languages (header brand, achievements
#    panel title, share-tweet text). Order: "Achievements" before bare "Agent".
Get-ChildItem (Join-Path $Web 'src\i18n') -Filter '*.ts' -ErrorAction SilentlyContinue | ForEach-Object {
    Patch $_.FullName 'Hermes Achievements' 'RealDeal CPA Achievements' "i18n $($_.Name) achievements"
    Patch $_.FullName 'Hermes Agent' 'RealDeal CPA' "i18n $($_.Name) brand/tweet"
}
# 4) Sidebar wordmark (hardcoded JSX)
Patch (Join-Path $Web 'src\App.tsx') 'Hermes(\s*<br />\s*)Agent' 'RealDeal${1}CPA' 'App.tsx wordmark'
# 4b) FastAPI app title (shown in the dashboard's /docs + OpenAPI schema)
Patch (Join-Path $Root 'hermes-agent\hermes_cli\web_server.py') 'FastAPI\(title="Hermes Agent"' 'FastAPI(title="RealDeal CPA"' 'web_server FastAPI title'
# 4c) Telegram onboarding default bot name
Patch (Join-Path $Web 'src\pages\ChannelsPage.tsx') 'bot_name: "Hermes Agent"' 'bot_name: "RealDeal CPA"' 'ChannelsPage bot_name'

# 5) Rebuild the SPA that `hermes dashboard` serves (web -> hermes_cli/web_dist)
Write-Host "`nRebuilding dashboard (npm run build)..." -ForegroundColor Cyan
Push-Location $Web
try { npm run build } finally { Pop-Location }
Write-Host "`nDone. Restart the dashboard to see the rebrand." -ForegroundColor Green
