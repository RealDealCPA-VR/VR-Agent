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

# Branding: CLI skins + dashboard themes (always refresh from overlay)
foreach ($pair in @(@('skins','skins'), @('dashboard-themes','dashboard-themes'))) {
    $src = Join-Path $Overlay $pair[0]
    if (Test-Path $src) {
        $dst = Join-Path $Home_ $pair[1]
        New-Item -ItemType Directory -Force -Path $dst | Out-Null
        Copy-Item (Join-Path $src '*.yaml') $dst -Force
        Write-Host "synced: $($pair[0])/*.yaml -> $dst"
    }
}

# Memory seeds: copy USER.md / MEMORY.md ONLY if absent (never clobber the
# agent's own curated memory once it starts learning).
$mem = Join-Path $Home_ 'memories'
New-Item -ItemType Directory -Force -Path $mem | Out-Null
foreach ($f in @('USER.md','MEMORY.md')) {
    $dst = Join-Path $mem $f
    if (-not (Test-Path $dst)) {
        Copy-Item (Join-Path $Overlay "memory\$f") $dst -Force
        Write-Host "seeded: memories\$f"
    } else { Write-Host "kept existing memories\$f" }
}

# Seed .env from template on first run (never overwrite a filled one)
$envPath = Join-Path $Home_ '.env'
if (-not (Test-Path $envPath)) {
    Copy-Item (Join-Path $Overlay 'config\env.example') $envPath -Force
    Write-Host "seeded: home\.env  (fill in your API keys)"
} else {
    Write-Host "kept existing home\.env"
}
