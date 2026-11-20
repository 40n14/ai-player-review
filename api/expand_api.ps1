# Content expansion, paid by an API key (or with -Subscription by the login on this computer): one headless task that reads a merged review report and writes
# a proposal file (what to add to the work, with drafts in the work's own formats). It never changes the work.
# The walk is kinds\expand.md; the task file is built from expand_template.md. Same runner, machine settings and
# project file as player_review_api.ps1. ASCII only on purpose (Windows PowerShell 5.1).
#
#   -From       the merged review report to work from (required)
#   -Items      which entries to do, e.g. "W1,W3,D2" (default: every W entry, and the D entries whose first option adds content)
#   -OutFile    the latest proposal (default: next to the report, name from reportNames.expand or texts.json)
#   -MapDir     the map folder (default: <report folder>\_map when it has a _map.md)
#   -RunId      optional identifier for the task, log and proposal files
#   -ProjectFile, -LocalFile, -Runner, -Model, -Provider, -MaxTurns, -DryRun, -Subscription   as in player_review_api.ps1
param(
  [Parameter(Mandatory)][string]$From,
  [string]$Items,
  [string]$OutFile,
  [string]$MapDir,
  [string]$ProjectFile,
  [string]$LocalFile,
  [string]$Runner,
  [string]$Model,
  [string]$Provider,
  [int]$MaxTurns = 200,
  [switch]$DryRun,
  [switch]$Subscription,
  [string]$RunId
)
$ErrorActionPreference = 'Stop'
trap {
  Write-Warning "$_"
  Write-Host 'Result : FAILED; expansion did not complete.'
  exit 1
}
if ($PSBoundParameters.ContainsKey('RunId')) {
  if ($RunId -cnotmatch '\A[A-Za-z0-9_-]{1,40}\z') { throw 'Invalid -RunId: use 1 to 40 ASCII letters, digits, underscores or hyphens.' }
} else {
  $RunId = "$(Get-Date -Format 'yyyyMMdd_HHmmssfff')_$([guid]::NewGuid().ToString('N').Substring(0, 4))"
}
$kit = Split-Path $PSScriptRoot -Parent
. (Join-Path $PSScriptRoot 'common.ps1')
. (Join-Path $PSScriptRoot 'run_result.ps1')
if (-not $ProjectFile) { $ProjectFile = Get-DefaultProjectFile $kit }
$ProjectFile = (Resolve-Path $ProjectFile).Path
if (-not (Test-Path -LiteralPath $From)) { throw "Merged report not found: $From" }
$From = (Resolve-Path -LiteralPath $From).Path
$dir = Split-Path $From -Parent

$proj = Read-Project $ProjectFile
$local = Read-Local $kit $LocalFile
$T = (Read-Utf8 (Join-Path $PSScriptRoot 'texts.json')) | ConvertFrom-Json
$owner = [string](Get-Prop $proj 'ownerName' $T.ownerDefault)
if (-not $Runner) { $Runner = [string](Get-Prop $proj 'apiRunner' (Join-Path $PSScriptRoot 'run_api_task.ps1')) }
if (-not $DryRun -and -not (Test-Path $Runner)) { throw "Runner not found: $Runner" }
if (-not $OutFile) { $OutFile = Join-Path $dir ([string](Get-OutputName $proj $T 'expand')) }
$OutFile = [IO.Path]::GetFullPath($OutFile)
$stem = [IO.Path]::GetFileNameWithoutExtension($OutFile)
$proposal = Join-Path (Split-Path $OutFile -Parent) ($stem + "_$RunId" + [IO.Path]::GetExtension($OutFile))
if (-not $MapDir) { $guess = Join-Path $dir '_map'; if (Test-Path -LiteralPath (Join-Path $guess '_map.md')) { $MapDir = $guess } }
$mapLine = if ($MapDir) { Fill-Text $T.mapLine @{ DIR = (Resolve-Path -LiteralPath $MapDir).Path } } else { $T.mapNone }
$itemsLine = if ($Items) { $Items } else { $T.expandAllItems }
$readOnly = (@(Get-Prop $proj 'readOnlyPaths' @()) -join ', '); if (-not $readOnly) { $readOnly = $T.nothingListed }
$neverReadList = @(Get-Prop $proj 'neverRead' @()) + @(Get-Prop $local 'neverRead' @()) | Where-Object { $_ } | Select-Object -Unique
$neverRead = (@($neverReadList) -join ', '); if (-not $neverRead) { $neverRead = $T.nothingListed }

function Fill([string]$text) { $text.Replace('{{KIT}}', $kit).Replace('{{PROJECT_FILE}}', $ProjectFile).Replace('{{OWNER}}', $owner) }
$body = Fill (Read-Utf8 (Join-Path $kit 'kinds\expand.md'))
$tpl = Read-Utf8 (Join-Path $PSScriptRoot 'expand_template.md')
$map = [ordered]@{ PROJECT_FILE = $ProjectFile; FROM = $From; ITEMS = $itemsLine; MAP = $mapLine; REPORT = $proposal;
  READONLY = $readOnly; NEVERREAD = $neverRead; BODY = $body }   # BODY last: text inside it is never treated as a placeholder
foreach ($k in $map.Keys) { $tpl = $tpl.Replace('{{' + $k + '}}', [string]$map[$k]) }
$task = Join-Path $dir "task_expand_$RunId.md"
$log = Join-Path $dir "log_expand_$RunId.txt"
if ((Test-Path -LiteralPath $log) -or (Test-Path -LiteralPath $proposal)) { throw "Expansion RunId already used: $RunId" }
$tpl = Format-Delivery $tpl $proj.language $T
Assert-TaskFilled $task $tpl
$stream = [IO.File]::Open($task, [IO.FileMode]::CreateNew)
try {
  $bytes = $script:KitUtf8.GetBytes($tpl)
  $stream.Write($bytes, 0, $bytes.Length)
} finally { $stream.Dispose() }

$a = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Runner, '-TaskFile', $task, '-LogFile', $log, '-WorkDir', $proj.projectRoot)
$ro = (@(Get-Prop $proj 'readOnlyPaths' @()) -join ';'); if ($ro) { $a += @('-ReadOnly', $ro) }
$nr = (@(Get-Prop $proj 'neverRead' @()) -join ';'); if ($nr) { $a += @('-NeverRead', $nr) }
if ($local._file) { $a += @('-LocalFile', $local._file) }
$a += @('-MaxTurns', "$MaxTurns", '-Json')
if ($Model) { $a += @('-Model', $Model) }
if ($Provider) { $a += @('-Provider', $Provider) }
if ($Subscription) { $a += '-Subscription' }   # the login of this computer pays, no key is read
Write-Host "Expand : from $From"
Write-Host ("Pay    : " + $(if ($Subscription) { 'subscription login of this computer (-Subscription), no key' } else { 'API key / provider account' }))
Write-Host "Items  : $(if ($Items) { $Items } else { '(all W entries, and D entries that add content)' })"
Write-Host "Task   : $task"
Write-Host "Out    : $proposal"
if ($DryRun) {
  Write-Host "Dry run, not run: powershell.exe $(Arg-Line $a)"
  exit 0
}
try {
  $process = Start-ReviewRunner $a $log
  $null = $process.Handle
  $process.WaitForExit()
  $runnerExit = $process.ExitCode
} catch {
  $runnerExit = 1
  Write-Warning "Expansion runner could not be started: $_"
}
$res = Read-RunResult $log
$fresh = (Test-Path -LiteralPath $proposal -PathType Leaf) -and (Get-Item -LiteralPath $proposal).Length -gt 0
$runnerOk = ($runnerExit -eq 0) -and (Test-RunOk $res)
$ok = $runnerOk -and $fresh
if ($runnerOk -and -not $fresh) {
  Add-Content -LiteralPath $log -Encoding UTF8 -Value 'report status: missing or unchanged'
}
$la = @('--project', $ProjectFile); if ($local._file) { $la += @('--local', $local._file) }
try {
  & (Get-Python $local $proj) -I (Join-Path $PSScriptRoot 'cost_ledger.py') @la $dir | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "cost_ledger.py exited with code $LASTEXITCODE" }
} catch { Write-Host 'Ledger     : pending'; Write-Warning "Cost ledger not updated: $_" }
if ($ok) {
  $tmp = "$proposal.latest.tmp"
  try {
    [IO.File]::Copy($proposal, $tmp)
    try { [IO.File]::Move($tmp, $OutFile) }
    catch [IO.IOException] { [IO.File]::Replace($tmp, $OutFile, [NullString]::Value, $true) }
  } catch {
    $ok = $false
    Write-Warning "Could not publish latest proposal: $_"
  } finally {
    if ([IO.File]::Exists($tmp)) { [IO.File]::Delete($tmp) }
  }
}
$money = if ($res.Found) { "$(Format-Usd $res.Cost) USD, $($res.Turns) turns" } else { 'no result JSON' }
Write-Host ("Result : {0}; {1}; proposal {2}; log {3}" -f $(if ($ok) { 'ok' } else { 'FAILED' }), $money, $(if ($fresh) { 'written' } else { 'NOT written' }), $log)
if (-not $ok) { Write-Warning $T.expandFailed; exit 1 }
exit 0
