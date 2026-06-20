<#
.SYNOPSIS
  Render the tracked vr-overlay (config, persona, branding, memory, MCP launchers)
  into the repo-local HERMES_HOME. Paths are resolved at render time so the project
  is portable across machines/usernames.

  - config.yaml.tmpl       -> home/config.yaml         (__VRAGENT_ROOT__ replaced)
  - mcp/launchers/*.cmd.tmpl-> home/launchers/*.cmd     (__PROJECTS_ROOT__ replaced)
  Skills are read live from vr-overlay via config skills.external_dirs.
#>
$ErrorActionPreference = 'Stop'
$Root     = Split-Path -Parent $PSScriptRoot
$Overlay  = Join-Path $Root 'vr-overlay'
$Home_    = Join-Path $Root 'home'
$RootFwd  = $Root.Replace('\','/')                       # config uses forward slashes
$Projects = Split-Path -Parent $Root                     # siblings (QuickBooks MCP, KarbonCopy, ...)

# Read/write as UTF-8 explicitly. PS 5.1 Get-Content -Raw defaults to ANSI and
# would mangle non-ASCII (em dashes, ·, →); .NET ReadAllText auto-detects UTF-8.
$NoBom = New-Object System.Text.UTF8Encoding($false)
function ReadText($path)  { [System.IO.File]::ReadAllText($path) }
function WriteText($path, $text) { [System.IO.File]::WriteAllText($path, $text, $NoBom) }

New-Item -ItemType Directory -Force -Path $Home_ | Out-Null

# 1) Render config.yaml from template
$cfg = (ReadText (Join-Path $Overlay 'config\config.yaml.tmpl')).Replace('__VRAGENT_ROOT__', $RootFwd)
WriteText (Join-Path $Home_ 'config.yaml') $cfg
Write-Host "rendered: config.yaml (root=$RootFwd)"

# 2) Persona
Copy-Item (Join-Path $Overlay 'SOUL.md') (Join-Path $Home_ 'SOUL.md') -Force
Write-Host "synced: SOUL.md"

# 3) Render MCP launchers for external projects -> home/launchers/*.cmd
$launchSrc = Join-Path $Overlay 'mcp\launchers'
$launchDst = Join-Path $Home_ 'launchers'
New-Item -ItemType Directory -Force -Path $launchDst | Out-Null
Get-ChildItem $launchSrc -Filter '*.cmd.tmpl' -ErrorAction SilentlyContinue | ForEach-Object {
    $out = Join-Path $launchDst ($_.BaseName)            # strips .tmpl -> name.cmd
    $txt = (ReadText $_.FullName).Replace('__PROJECTS_ROOT__', $Projects)
    WriteText $out $txt
    Write-Host "rendered launcher: $($_.BaseName)  (projects=$Projects)"
}

# 4) Branding: CLI skins + dashboard themes (always refresh from overlay)
foreach ($d in @('skins','dashboard-themes')) {
    $src = Join-Path $Overlay $d
    if (Test-Path $src) {
        $dst = Join-Path $Home_ $d
        New-Item -ItemType Directory -Force -Path $dst | Out-Null
        Copy-Item (Join-Path $src '*.yaml') $dst -Force
        Write-Host "synced: $d/*.yaml"
    }
}

# 5) Memory seeds: copy USER.md / MEMORY.md ONLY if absent (never clobber the
#    agent's own curated memory once it starts learning).
$mem = Join-Path $Home_ 'memories'
New-Item -ItemType Directory -Force -Path $mem | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $mem 'clients') | Out-Null   # per-client profiles
foreach ($f in @('USER.md','MEMORY.md')) {
    $dst = Join-Path $mem $f
    if (-not (Test-Path $dst)) {
        Copy-Item (Join-Path $Overlay "memory\$f") $dst -Force
        Write-Host "seeded: memories\$f"
    } else { Write-Host "kept existing memories\$f" }
}

# 6) Seed .env from template on first run (never overwrite a filled one)
$envPath = Join-Path $Home_ '.env'
if (-not (Test-Path $envPath)) {
    Copy-Item (Join-Path $Overlay 'config\env.example') $envPath -Force
    Write-Host "seeded: home\.env  (fill in your API keys)"
} else { Write-Host "kept existing home\.env" }
