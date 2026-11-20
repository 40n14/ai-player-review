# Copies (not links) the kit's agents (reviewer, checker) and the player-review skill into a project's .claude folder,
# so Claude Code finds them there. Re-run after changing the master copies in this kit: it overwrites them.
# {{KIT}}, {{PROJECT_FILE}} and {{OWNER}} in the copied text files become this kit's folder, the project file and
# the project's ownerName (who decides; texts.json has the default).
# ASCII only on purpose (Windows PowerShell 5.1 reads a .ps1 without BOM in the ANSI code page).
#   powershell -NoProfile -ExecutionPolicy Bypass -File <kit>\install.ps1 [-ProjectFile <json>] [-ProjectRoot <folder>]
param([string]$ProjectFile, [string]$ProjectRoot)
$ErrorActionPreference = 'Stop'
$kit = $PSScriptRoot
. (Join-Path $kit 'api\common.ps1')
if (-not $ProjectFile) { $ProjectFile = Get-DefaultProjectFile $kit }
$ProjectFile = (Resolve-Path $ProjectFile).Path
$proj = Read-Project $ProjectFile
$T = (Read-Utf8 (Join-Path $kit 'api\texts.json')) | ConvertFrom-Json
$owner = [string](Get-Prop $proj 'ownerName' $T.ownerDefault)
if (-not $ProjectRoot) { $ProjectRoot = $proj.projectRoot }
if (-not $ProjectRoot -or -not (Test-Path $ProjectRoot)) { throw "Project folder not found: $ProjectRoot" }
$ProjectRoot = (Resolve-Path $ProjectRoot).Path

function Copy-Filled([string]$from, [string]$to) {
  New-Item -ItemType Directory -Force (Split-Path $to -Parent) | Out-Null
  if ($from -match '\.(md|json|txt)$') {
    $t = (Read-Utf8 $from).Replace('{{KIT}}', $kit).Replace('{{PROJECT_FILE}}', $ProjectFile).Replace('{{OWNER}}', $owner)
    Write-Utf8 $to $t   # no BOM: the YAML header must start the file
  } else {
    Copy-Item -LiteralPath $from -Destination $to -Force
  }
  Write-Host "  $to"
}

Write-Host "Installing into $ProjectRoot\.claude (project file $ProjectFile)"
# Every agent of the kit (the reviewer, the checker ...). Other agents the project has are left alone.
Get-ChildItem (Join-Path $kit 'agent') -Filter *.md | ForEach-Object {
  Copy-Filled $_.FullName (Join-Path $ProjectRoot (Join-Path '.claude\agents' $_.Name))
}

# The skill folder is mirrored: files no longer in the kit are removed from the installed copy.
$src = Join-Path $kit 'skill\player-review'
$dst = Join-Path $ProjectRoot '.claude\skills\player-review'
$wanted = @{}
Get-ChildItem $src -Recurse -File | ForEach-Object {
  $rel = $_.FullName.Substring($src.Length).TrimStart('\')
  $wanted[$rel.ToLowerInvariant()] = $true
  Copy-Filled $_.FullName (Join-Path $dst $rel)
}
if (Test-Path $dst) {
  Get-ChildItem $dst -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($dst.Length).TrimStart('\')
    if (-not $wanted.ContainsKey($rel.ToLowerInvariant())) { Remove-Item -LiteralPath $_.FullName -Force; Write-Host "  removed old $($_.FullName)" }
  }
}
Write-Host 'Done. A new Claude Code session picks up the agent and the skill. The walk files (kinds\), personas (method\) and static scripts are read from the kit itself.'
