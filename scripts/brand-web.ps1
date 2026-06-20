<#
.SYNOPSIS
  Re-brand the Hermes web dashboard to RealDeal CPA (name, tab title, favicon)
  and rebuild it. Idempotent — safe to re-run after a `git pull` of upstream.

  The dashboard source lives in the (gitignored) hermes-agent clone, so this
  script is the tracked, reproducible record of those edits. Called by
  scripts/install.ps1; run it manually after updating upstream.
#>
$ErrorActionPreference = 'Stop'
$Root  = Split-Path -Parent $PSScriptRoot
$Web   = Join-Path $Root 'hermes-agent\web'
$Brand = Join-Path $Root 'vr-overlay\brand'

function Patch($path, $pattern, $replacement, $label) {
    if (-not (Test-Path $path)) { Write-Host "skip ($label): $path missing"; return }
    $raw = Get-Content $path -Raw
    if ($raw -match $pattern) {
        ($raw -replace $pattern, $replacement) | Set-Content $path -Encoding UTF8 -NoNewline
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

# 3) Header brand name (i18n default = English)
Patch (Join-Path $Web 'src\i18n\en.ts') 'brand:\s*"Hermes Agent"' 'brand: "RealDeal CPA"' 'en.ts brand'
# 4) Sidebar wordmark (hardcoded JSX)
Patch (Join-Path $Web 'src\App.tsx') 'Hermes(\s*<br />\s*)Agent' 'RealDeal${1}CPA' 'App.tsx wordmark'

# 5) Rebuild the SPA that `hermes dashboard` serves (web -> hermes_cli/web_dist)
Write-Host "`nRebuilding dashboard (npm run build)..." -ForegroundColor Cyan
Push-Location $Web
try { npm run build } finally { Pop-Location }
Write-Host "`nDone. Restart the dashboard to see the rebrand." -ForegroundColor Green
