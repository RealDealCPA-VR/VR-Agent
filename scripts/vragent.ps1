<#
.SYNOPSIS
  VRAGENT launcher. Runs the repo-local Hermes agent with an in-repo HERMES_HOME
  so all state (config, persona, skills, sessions, memory) stays inside this project.

.EXAMPLE
  .\scripts\vragent.ps1                 # interactive CLI
  .\scripts\vragent.ps1 --tui           # terminal UI
  .\scripts\vragent.ps1 doctor          # health check
  .\scripts\vragent.ps1 dashboard       # web dashboard on http://127.0.0.1:9119
  .\scripts\vragent.ps1 model           # switch provider/model
  .\scripts\vragent.ps1 gateway run     # start messaging gateway (Slack, etc.)
#>
$ErrorActionPreference = 'Stop'

# Repo root = parent of this scripts/ directory
$Root = Split-Path -Parent $PSScriptRoot
$env:HERMES_HOME = Join-Path $Root 'home'

# Use the repo-local uv venv created by scripts/install.ps1
$hermes = Join-Path $Root 'hermes-agent\.venv\Scripts\hermes.exe'
if (-not (Test-Path $hermes)) {
    Write-Error "Hermes is not installed yet. Run: .\scripts\install.ps1"
    exit 1
}

& $hermes @args
exit $LASTEXITCODE
