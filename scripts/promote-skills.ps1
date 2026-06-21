<#
.SYNOPSIS
  Promote agent-authored skills from the runtime HERMES_HOME into the tracked
  vr-overlay so recursive self-improvement becomes version-controlled.

  The agent saves new/edited skills to home/skills (runtime, gitignored). This
  copies any skill NOT bundled by Hermes and NOT already in the overlay into
  vr-overlay/skills/_promoted/<skill>, ready to review + commit.

.EXAMPLE
  .\scripts\promote-skills.ps1            # list + copy new agent skills
  .\scripts\promote-skills.ps1 -WhatIf    # preview only
#>
param([switch]$WhatIf)
$ErrorActionPreference = 'Stop'
$Root        = Split-Path -Parent $PSScriptRoot
$HomeSkills  = Join-Path $Root 'home\skills'
$Bundled     = Join-Path $Root 'hermes-agent\skills'
$OverlayDst  = Join-Path $Root 'vr-overlay\skills\_promoted'

# Names already shipped by upstream or already in our overlay = not "learned".
$known = @{}
foreach ($base in @($Bundled, (Join-Path $Root 'vr-overlay\skills'))) {
    if (Test-Path $base) {
        Get-ChildItem $base -Recurse -Filter SKILL.md | ForEach-Object {
            $known[$_.Directory.Name] = $true
        }
    }
}

$promoted = 0
Get-ChildItem $HomeSkills -Recurse -Filter SKILL.md -ErrorAction SilentlyContinue | ForEach-Object {
    $skillDir = $_.Directory
    if ($known.ContainsKey($skillDir.Name)) { return }   # bundled/seeded - skip
    $dst = Join-Path $OverlayDst $skillDir.Name
    Write-Host "PROMOTE: $($skillDir.Name)  ($($skillDir.FullName))"
    if (-not $WhatIf) {
        New-Item -ItemType Directory -Force -Path $dst | Out-Null
        Copy-Item (Join-Path $skillDir.FullName '*') $dst -Recurse -Force
    }
    $promoted++
}
if ($promoted -eq 0) { Write-Host "No new agent-authored skills to promote." }
else { Write-Host "`n$promoted skill(s) staged in vr-overlay/skills/_promoted. Review, then git add/commit." }
