<#
.SYNOPSIS
  Sign and version a snapshot of the learned "employee" state so it survives a
  model swap and proves "I did not change last year".

  Zips the tracked learned state:
    - vr-overlay/skills/_promoted   (if it exists; promoted/learned skills)
    - home/memories                 (curated memory + per-client profiles)
  into home/snapshots/<yyyy-MM-dd-HHmmss>/state.zip, and writes a manifest.json
  in that dir listing every included file with its SHA-256.

.PARAMETER List
  List existing snapshots (newest first) with file counts.

.PARAMETER Diff
  Two snapshot ids (dir names or paths). Compares their manifests and reports
  files changed / added / removed by SHA-256 hash.

.EXAMPLE
  .\snapshot-state.ps1
  .\snapshot-state.ps1 -List
  .\snapshot-state.ps1 -Diff 2026-06-21-093000 2026-06-21-110000
#>
[CmdletBinding(DefaultParameterSetName = 'Create')]
param(
    [Parameter(ParameterSetName = 'List')]
    [switch]$List,

    # -Diff <a> <b> : the switch enables Diff mode; the two snapshot ids follow
    # as positional args (collected via ValueFromRemainingArguments for PS 5.1).
    [Parameter(ParameterSetName = 'Diff')]
    [switch]$Diff,

    [Parameter(ParameterSetName = 'Diff', Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Ids
)

$ErrorActionPreference = 'Stop'

$Root      = Split-Path -Parent $PSScriptRoot
$Overlay   = Join-Path $Root 'vr-overlay'
$Home_     = Join-Path $Root 'home'
$SnapRoot  = Join-Path $Home_ 'snapshots'

$NoBom = New-Object System.Text.UTF8Encoding($false)
function WriteText($path, $text) { [System.IO.File]::WriteAllText($path, $text, $NoBom) }

# Resolve a snapshot manifest path from an id, a dir name, or a direct path.
function Resolve-Manifest($id) {
    if (Test-Path $id -PathType Leaf) { return (Resolve-Path $id).Path }
    $candidates = @(
        $id,
        (Join-Path $id 'manifest.json'),
        (Join-Path $SnapRoot $id),
        (Join-Path (Join-Path $SnapRoot $id) 'manifest.json')
    )
    foreach ($c in $candidates) {
        if (Test-Path $c -PathType Leaf) { return (Resolve-Path $c).Path }
    }
    throw "Snapshot manifest not found for '$id' (looked under $SnapRoot)."
}

# Read a manifest.json and return a hashtable of relpath -> sha256.
function Read-ManifestHashes($manifestPath) {
    $json = [System.IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
    $map = @{}
    foreach ($f in $json.files) { $map[$f.path] = $f.sha256 }
    return $map
}

# ---- -List -----------------------------------------------------------------
if ($List) {
    if (-not (Test-Path $SnapRoot)) {
        Write-Host "No snapshots yet ($SnapRoot does not exist)."
        return
    }
    $dirs = Get-ChildItem -Path $SnapRoot -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending
    if (-not $dirs) { Write-Host "No snapshots in $SnapRoot."; return }
    Write-Host "Snapshots in $SnapRoot :"
    foreach ($d in $dirs) {
        $mf = Join-Path $d.FullName 'manifest.json'
        $count = '?'
        $zip = '(no zip)'
        if (Test-Path $mf) {
            $m = [System.IO.File]::ReadAllText($mf) | ConvertFrom-Json
            $count = @($m.files).Count
        }
        if (Test-Path (Join-Path $d.FullName 'state.zip')) { $zip = 'state.zip' }
        Write-Host ("  {0}  files={1}  {2}" -f $d.Name, $count, $zip)
    }
    return
}

# ---- -Diff <a> <b> ---------------------------------------------------------
if ($PSCmdlet.ParameterSetName -eq 'Diff') {
    if (-not $Ids -or $Ids.Count -ne 2) {
        throw "Usage: -Diff <a> <b>  (exactly two snapshot ids)."
    }
    $ma = Resolve-Manifest $Ids[0]
    $mb = Resolve-Manifest $Ids[1]
    $a = Read-ManifestHashes $ma
    $b = Read-ManifestHashes $mb

    $added   = @($b.Keys | Where-Object { -not $a.ContainsKey($_) } | Sort-Object)
    $removed = @($a.Keys | Where-Object { -not $b.ContainsKey($_) } | Sort-Object)
    $changed = @($a.Keys | Where-Object { $b.ContainsKey($_) -and ($a[$_] -ne $b[$_]) } | Sort-Object)

    Write-Host ("Diff  A={0}" -f $Ids[0])
    Write-Host ("      B={0}" -f $Ids[1])
    Write-Host ""
    if (-not $added -and -not $removed -and -not $changed) {
        Write-Host "IDENTICAL: no files changed, added, or removed (state unchanged)."
        return
    }
    if ($changed) { Write-Host "CHANGED:"; $changed | ForEach-Object { Write-Host "  ~ $_" } }
    if ($added)   { Write-Host "ADDED:";   $added   | ForEach-Object { Write-Host "  + $_" } }
    if ($removed) { Write-Host "REMOVED:"; $removed | ForEach-Object { Write-Host "  - $_" } }
    Write-Host ""
    Write-Host ("Summary: {0} changed, {1} added, {2} removed." -f $changed.Count, $added.Count, $removed.Count)
    return
}

# ---- Create a snapshot (default) -------------------------------------------
$sources = @()
$promoted = Join-Path $Overlay 'skills\_promoted'
if (Test-Path $promoted) { $sources += [pscustomobject]@{ Path = $promoted; Label = '_promoted' } }
$memories = Join-Path $Home_ 'memories'
if (Test-Path $memories) { $sources += [pscustomobject]@{ Path = $memories; Label = 'memories' } }

if (-not $sources) {
    throw "Nothing to snapshot: neither $promoted nor $memories exists."
}

$stamp   = Get-Date -Format 'yyyy-MM-dd-HHmmss'
$snapDir = Join-Path $SnapRoot $stamp
New-Item -ItemType Directory -Force -Path $snapDir | Out-Null

# Collect every file with a stable forward-slash relative path: <label>/<rel>.
$entries = New-Object System.Collections.ArrayList
$zipInputs = New-Object System.Collections.ArrayList
foreach ($s in $sources) {
    $base = (Resolve-Path $s.Path).Path
    $files = Get-ChildItem -Path $base -Recurse -File -ErrorAction SilentlyContinue
    foreach ($f in $files) {
        $rel = $f.FullName.Substring($base.Length).TrimStart('\', '/').Replace('\', '/')
        $relPath = "$($s.Label)/$rel"
        $hash = (Get-FileHash -Path $f.FullName -Algorithm SHA256).Hash.ToLower()
        [void]$entries.Add([pscustomobject]@{
            path   = $relPath
            sha256 = $hash
            bytes  = $f.Length
        })
        [void]$zipInputs.Add($f.FullName)
    }
}

$zipPath = Join-Path $snapDir 'state.zip'
if ($zipInputs.Count -gt 0) {
    Compress-Archive -Path ($zipInputs.ToArray()) -DestinationPath $zipPath -Force
} else {
    # No files at all: still produce an (empty) archive marker so callers can rely on it.
    Compress-Archive -Path $snapDir -DestinationPath $zipPath -Force -ErrorAction SilentlyContinue
}

# Sign the manifest: a top-level SHA-256 over the sorted per-file hashes so the
# whole snapshot has one verifiable signature.
$sorted = $entries | Sort-Object path
$sigText = ($sorted | ForEach-Object { "$($_.path):$($_.sha256)" }) -join "`n"
$sha = [System.Security.Cryptography.SHA256]::Create()
$sigBytes = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($sigText))
$signature = ([System.BitConverter]::ToString($sigBytes)).Replace('-', '').ToLower()

$manifest = [ordered]@{
    schema       = 'realdeal.snapshot-state/1'
    snapshot     = $stamp
    created_utc  = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    sources      = @($sources | ForEach-Object { $_.Label })
    file_count   = $entries.Count
    signature    = $signature
    files        = @($sorted)
}
$manifestPath = Join-Path $snapDir 'manifest.json'
WriteText $manifestPath ($manifest | ConvertTo-Json -Depth 6)

Write-Host "Snapshot created: $snapDir"
Write-Host ("  files:     {0}" -f $entries.Count)
Write-Host ("  zip:       {0}" -f $zipPath)
Write-Host ("  manifest:  {0}" -f $manifestPath)
Write-Host ("  signature: {0}" -f $signature)
