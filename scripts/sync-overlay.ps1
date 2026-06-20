<#
.SYNOPSIS
  Sync the tracked vr-overlay (config, persona) into the repo-local HERMES_HOME.
  Skills are read live from vr-overlay via config `skills.external_dirs`, so they
  are NOT copied here. Run after editing config.yaml or SOUL.md.
#>
$ErrorActionPreference = 'Stop'
$Root    = Split-Path -Parent $PSScriptRoot
$Overlay = Join-Path $Root 'vr-overlay'
$Home_   = Join-Path $Root 'home'

New-Item -ItemType Directory -Force -Path $Home_ | Out-Null

# config.yaml + SOUL.md are required at the HERMES_HOME root
Copy-Item (Join-Path $Overlay 'config\config.yaml') (Join-Path $Home_ 'config.yaml') -Force
Copy-Item (Join-Path $Overlay 'SOUL.md')            (Join-Path $Home_ 'SOUL.md')     -Force
Write-Host "synced: config.yaml, SOUL.md -> $Home_"

# Seed .env from template on first run (never overwrite a filled one)
$envPath = Join-Path $Home_ '.env'
if (-not (Test-Path $envPath)) {
    Copy-Item (Join-Path $Overlay 'config\env.example') $envPath -Force
    Write-Host "seeded: home\.env  (fill in your API keys)"
} else {
    Write-Host "kept existing home\.env"
}
