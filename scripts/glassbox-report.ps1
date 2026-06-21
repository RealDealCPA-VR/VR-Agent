<#
.SYNOPSIS
  Render a self-contained glassbox provenance HTML report for a client/period.

.DESCRIPTION
  Thin wrapper around scripts/glassbox_report.py. Reads the vr-provenance dossier,
  the hash-chained ledger, and the content-addressed evidence bundles, then writes
  home/provenance/reports/<Client>-<Period>.html. Every ledger event is shown in
  chain order with its hash + prev_hash, each evidence bundle with its source +
  sha256, and an AI-prepared-vs-human-authorized column.

.EXAMPLE
  ./glassbox-report.ps1 -Client acme -Period 2026-Q2
#>
param(
    [Parameter(Mandatory = $true)] [string] $Client,
    [Parameter(Mandatory = $true)] [string] $Period
)
$ErrorActionPreference = 'Stop'

$Root   = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root 'hermes-agent\.venv\Scripts\python.exe'
$Script = Join-Path $PSScriptRoot 'glassbox_report.py'

if (-not (Test-Path $Python)) { throw "venv python not found: $Python" }
if (-not (Test-Path $Script)) { throw "renderer not found: $Script" }

& $Python $Script --client $Client --period $Period
exit $LASTEXITCODE
