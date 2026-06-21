<#
.SYNOPSIS
  Optimize RealDeal CPA for the chosen LLM. Offer-only by default.

.EXAMPLE
  .\scripts\optimize-skills.ps1                 # show what tuning the current model would get
  .\scripts\optimize-skills.ps1 -Model haiku    # offer for a specific model before switching
  .\scripts\optimize-skills.ps1 -Apply          # apply tuning for the current model + re-sync
  .\scripts\optimize-skills.ps1 -Apply -Model claude-opus-4.5
  .\scripts\optimize-skills.ps1 -Revert         # remove model-style override + re-sync
#>
param([string]$Model, [switch]$Apply, [switch]$Revert)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$py = Join-Path $Root 'hermes-agent\.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { Write-Error "Run scripts\install.ps1 first (no venv)."; exit 1 }

$pyArgs = @((Join-Path $PSScriptRoot 'optimize_skills.py'))
if ($Model)  { $pyArgs += @('--model', $Model) }
if ($Apply)  { $pyArgs += '--apply' }
if ($Revert) { $pyArgs += '--revert' }

& $py @pyArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($Apply -or $Revert) {
    Write-Host "`nRe-rendering overlay..." -ForegroundColor Cyan
    & (Join-Path $PSScriptRoot 'sync-overlay.ps1')
}
