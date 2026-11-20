# Fake runner for testing player_review_api.ps1 without any API call (no cost, no key). ASCII only.
# Same parameters as the real run_api_task.ps1: -TaskFile -LogFile -WorkDir [-ReadOnly] [-NeverRead] [-Model] [-MaxTurns] [-Json]
# Writes a short fake report to the path after the "write to" line of the task file, sleeps 1-4 s, logs
# "started", one CLI-style result JSON line and "finished ..., exit N".
# Failure switches (environment variables, inherited by the child processes):
#   FAKE_MODES = "<taskname>=<mode>,<taskname>=<mode>"  (taskname = task_<name>.md without prefix/suffix, e.g. A_part1, merge_A, merge)
#     modes: noreport  no report file written (JSON failure)
#            error     JSON is_error true, subtype error_during_execution (report written)
#            maxturns  JSON is_error true, subtype error_max_turns (report written, "unfinished")
#            nojson    no JSON line in the log (report written)
#            exit1     no JSON, exit code 1, no report
#            crash     like exit1 but no "finished" line either
#   FAKE_CONCURRENCY_LOG = path: every start/end appended as "<ticks> start|end <name>" (to count tasks at once)
#   FAKE_SLEEP = "min,max" seconds (default 1,4)
# Fix tasks (built from api\fix_template.md by prk fix; the log name starts with log_fix_): no report. It pretends to
# fix the item: appends one line to the first file the item cites, ticks the item in the fix list and fills in its
# fields (the words are in texts.json, fakeFix). It changes a file only when the file is under the folder named in
#   FAKE_FIX_ROOT = a test copy of a project (without it, only the fix list is touched)
#   FAKE_FIX_MODE = nofix: change nothing and tick nothing (an AI that did not finish)
param([string]$TaskFile, [string]$LogFile, [string]$WorkDir, [string]$ReadOnly, [string]$NeverRead, [string]$LocalFile,
  [string]$Model = 'fake-model', [int]$MaxTurns = 200, [switch]$Json, [Alias('AllowModEdits')][switch]$AllowEdits,
  [switch]$Subscription, [string]$Tools = '', [switch]$Answer, [string]$Provider = '')
# -Answer (the guide): no report is written; the result text says it is fake. -Subscription and -Tools are only logged.
# -WorkDir, -ReadOnly, -NeverRead, -LocalFile: same as the real runner; the fake one only checks WorkDir exists and logs them.
if ($WorkDir -and -not (Test-Path -LiteralPath $WorkDir)) { Write-Error "WorkDir not found: $WorkDir"; exit 4 }
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$name = [IO.Path]::GetFileNameWithoutExtension($TaskFile) -replace '^task_', ''
$mode = 'ok'
$modes = @{}
foreach ($p in ($env:FAKE_MODES -split ',')) { $kv = $p.Trim() -split '=', 2; if ($kv.Count -eq 2) { $modes[$kv[0]] = $kv[1] } }
if ($modes.ContainsKey($name)) { $mode = $modes[$name] }
elseif ($name -like 'expand_*' -and $modes.ContainsKey('expand')) { $mode = $modes['expand'] }
function CLog($what) {
  if ($env:FAKE_CONCURRENCY_LOG) {
    for ($i = 0; $i -lt 20; $i++) {
      try { [IO.File]::AppendAllText($env:FAKE_CONCURRENCY_LOG, "$([DateTime]::Now.Ticks) $what $name`r`n"); break } catch { Start-Sleep -Milliseconds 50 }
    }
  }
}
$task = [IO.File]::ReadAllText($TaskFile, [Text.Encoding]::UTF8)
$english = $task.StartsWith('# Delivery language: English')
$report = $null
foreach ($l in ($task -split "`r?`n")) {
  $m = [regex]::Match($l, '(?i)^-[ \t]+[^\uFF1A:\r\n]*\u5199\u5230[\uFF1A:][ \t]*[\x60"\x27]?([^\r\n]+\.md)[\x60"\x27]?[ \t]*(?:[\uFF08(][^\r\n]*)?$')
  if ($m.Success) { $report = $m.Groups[1].Value; break }
}
$started = Get-Date
[IO.File]::WriteAllText($LogFile, "started $($started.ToString('s')), model $Model, workdir $WorkDir, readonly $ReadOnly, neverread $NeverRead, provider $(if ($Subscription) { 'subscription' } elseif ($Provider) { $Provider } else { '(default)' })`n", $utf8)
CLog 'start'
$lo = 1; $hi = 4
if ($env:FAKE_SLEEP) { $a = $env:FAKE_SLEEP -split ','; $lo = [double]$a[0]; $hi = [double]$a[1] }
$rnd = New-Object Random
$sleep = $lo + $rnd.NextDouble() * ($hi - $lo)
Start-Sleep -Milliseconds ([int]($sleep * 1000))
$F = ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'texts.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json).fakeFix
if (-not $Answer -and (([IO.Path]::GetFileName($LogFile) -like 'log_fix_*') -or ($F -and $task.Contains([string]$F.taskMark)))) {
  $list = $null; $item = $null; $cite = $null
  foreach ($l in ($task -split "`r?`n")) {
    if (-not $list) { $m = [regex]::Match($l, [string]$F.listLine); if ($m.Success) { $list = $m.Groups[1].Value; continue } }
    if (-not $item) { $m = [regex]::Match($l, [string]$F.itemLine); if ($m.Success) { $item = $m.Groups[1].Value; continue } }
    if ($item -and -not $cite) { $m = [regex]::Match($l, '`([^`\r\n]+?):(\d+)(?:-\d+)?`'); if ($m.Success) { $cite = $m.Groups[1].Value } }
  }
  $changed = ''
  if ($env:FAKE_FIX_MODE -ne 'nofix' -and $cite -and $env:FAKE_FIX_ROOT) {
    $full = [IO.Path]::GetFullPath($(if ([IO.Path]::IsPathRooted($cite)) { $cite } else { Join-Path $WorkDir $cite }))
    $root = [IO.Path]::GetFullPath($env:FAKE_FIX_ROOT).TrimEnd('\') + '\'
    if ($full.StartsWith($root, [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $full -PathType Leaf)) {
      [IO.File]::AppendAllText($full, "`nFAKE-FIX $item`n", $utf8)
      $changed = $cite
    }
  }
  if ($env:FAKE_FIX_MODE -ne 'nofix' -and $list -and $item -and (Test-Path -LiteralPath $list)) {
    $fill = if ($changed) { ([string]$F.fill).Replace('{{FILE}}', $changed) } else { [string]$F.fillNoFile }
    $txt = [IO.File]::ReadAllText($list, [Text.Encoding]::UTF8)
    $pat = '(?ms)^(###\s*\[[ xX]?\]\s*' + $item + '\b[^\n]*\n.*?^#{4,6}\s*' + ('(?:' + [regex]::Escape([string]$F.doneHeading) + '|Fill in after fixing)') + '[^\n]*\n)(.*?)(?=^#{1,3}\s|\z)'
    $txt = [regex]::Replace($txt, $pat, [Text.RegularExpressions.MatchEvaluator] { param($mm) $heading = $mm.Groups[1].Value
      $details = if ($english -or $heading.Contains('Fill in after fixing')) {
        "- Changed: $(if ($changed) { $changed } else { 'None' }) (fake runner)`n- Verified: None`n- Needs an in-game check: None`n- Uncertainties: None`n- Other observations: None"
      } else { $fill }
      $heading + $details + "`n`n" })
    $txt = [regex]::Replace($txt, '(?m)^###\s*\[ ?\]\s*(' + $item + ')\b', '### [x] $1')
    [IO.File]::WriteAllText($list, $txt, $utf8)
  }
  $ms = [int]($sleep * 1000)
  $j = '{"duration_ms":' + $ms + ',"total_cost_usd":0.0456,"usage":{"input_tokens":1200,"output_tokens":300},"is_error":false,"num_turns":7,"subtype":"success","result":"fake fix (no AI was called): ' + $item + '","type":"result"}'
  [IO.File]::AppendAllText($LogFile, $j + "`n", $utf8)
  [IO.File]::AppendAllText($LogFile, "finished $((Get-Date).ToString('s')), exit 0`n", $utf8)
  CLog 'end'
  exit 0
}
if ($Answer) {
  $ms = [int]($sleep * 1000)
  $paid = if ($Subscription) { 'subscription' } else { 'api' }
  $j = '{"duration_ms":' + $ms + ',"total_cost_usd":0.0123,"is_error":false,"num_turns":3,"subtype":"success","result":"**fake answer** (no AI was called; mode ' + $paid + ', tools ' + $Tools + ')\n\n1. step one\n2. step two\n\n```\nprk plan\n```","type":"result"}'
  [IO.File]::AppendAllText($LogFile, $j + "`n", $utf8)
  [IO.File]::AppendAllText($LogFile, "finished $((Get-Date).ToString('s')), exit 0`n", $utf8)
  CLog 'end'
  exit 0
}
if (-not $report) { [IO.File]::AppendAllText($LogFile, "fake runner: no report path found in task`n", $utf8); CLog 'end'; exit 3 }
if ($mode -notin 'noreport', 'exit1', 'crash') {
  $txt = "# fake report $name`n`nmode: $mode`ntask file: $TaskFile`n"
  if ($english -and $name -eq 'map') {
    $txt = "# Project map`n`nFake map for testing the review pipeline.`n"
  } elseif ($english -and $name -like 'expand_*') {
    $txt = "# Content proposal`n`n## Proposals from gaps`n`nFake proposal for testing the review pipeline.`n"
  } elseif ($english) {
    $feedback = if ($name -like 'merge*') { 'Player feedback summary' } else { 'Player feedback' }
    $evidence = [IO.Path]::GetFileName($TaskFile) + ':1'
    $txt = @"
# Player review - $name

## Conclusion

This is a fake review for testing. Four sample entries exercise the offline review workflow.

## $feedback

### Example player
- Stuck: I could not continue. (S1)
- Confused: I did not understand the result. (M2)
- Wants: I wanted another option. (W1)

## Issues at a glance

| ID | Severity |
|---|---|
| S1 | Severe |
| M1 | Medium |
| M2 | Medium |

## Issues

### S1 A sample blocking issue
- Severity: Severe
- Confidence: [Confirmed]
- How you get there: Follow the example steps.
- What the player sees: Progress stops.
- Source: ``$evidence`` - # Delivery language: English
- Verification: Sample verification.

### M1 A sample feedback issue
- Confidence: [Possible]
- Suggestion: Explain the outcome.

### M2 A sample clarity issue
- Confidence: [Confirmed]
- How to reproduce: Repeat the example action.

## Wanted but missing

### W1 An example alternate option
- Who wants it: Example player.
- Confidence: [Definitely missing]

## Index

| ID | Severity | Confidence | File:line | Quote |
|---|---|---|---|---|
| S1 | Severe | [Confirmed] | $evidence | # Delivery language: English |
| M1 | Medium | [Possible] | $evidence | # Delivery language: English |
| M2 | Medium | [Confirmed] | $evidence | # Delivery language: English |
| W1 | | [Definitely missing] | $evidence | # Delivery language: English |
"@
    $txt += "`n"
  }
  [IO.File]::WriteAllText($report, $txt, $utf8)
}
$cost = [Math]::Round(0.5 + $rnd.NextDouble(), 4)
$turns = $rnd.Next(20, 120)
$isErr = 'false'; $sub = 'success'; $exit = 0
switch ($mode) {
  'noreport' { $isErr = 'true'; $sub = 'error_missing_report'; $exit = 1 }
  'error' { $isErr = 'true'; $sub = 'error_during_execution' }
  'maxturns' { $isErr = 'true'; $sub = 'error_max_turns'; $turns = $MaxTurns }
}
if ($mode -in 'nojson', 'exit1', 'crash') {
  [IO.File]::AppendAllText($LogFile, "Error: something went wrong (fake)`n", $utf8)
  if ($mode -ne 'nojson') { $exit = 1 }
} else {
  $ms = [int]($sleep * 1000)
  $j = '{"duration_api_ms":' + $ms + ',"stop_reason":"end_turn","total_cost_usd":' + $cost.ToString([Globalization.CultureInfo]::InvariantCulture) + ',"usage":{"input_tokens":50},"is_error":' + $isErr + ',"num_turns":' + $turns + ',"subtype":"' + $sub + '","result":"fake result \"quoted\" text, with {braces}","type":"result","duration_ms":' + $ms + '}'
  [IO.File]::AppendAllText($LogFile, $j + "`n", $utf8)
}
if ($mode -ne 'crash') { [IO.File]::AppendAllText($LogFile, "finished $((Get-Date).ToString('s')), exit $exit`n", $utf8) }
CLog 'end'
exit $exit
