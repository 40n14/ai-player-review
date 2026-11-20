# Reads what one headless Claude Code run cost and whether it worked, from its log, and writes the cost table.
# The runner (run_api_task.ps1 -Json) logs "started <time>, model <m>", then the CLI output, whose last line is one
# JSON object of type "result" (total_cost_usd, num_turns, duration_ms, is_error, subtype, result, usage ...),
# then "finished <time>, exit <n>". The JSON line stays in the log as it is; this file only reads it.
# ASCII only on purpose (Windows PowerShell 5.1); the Chinese labels come from texts.json.
#   . .\run_result.ps1                      defines the functions (player_review_api.ps1 does this)
#   .\run_result.ps1 -CheckLog <log.txt>    prints what it reads from one log (exit 1 when no result JSON)
param([string]$CheckLog)

function Get-JsonField([string]$s, [string]$name) {
  # Top-level field by regex (fallback when ConvertFrom-Json fails). (?<!\\) skips the same name inside an escaped string.
  $m = [regex]::Match($s, '(?<!\\)"' + [regex]::Escape($name) + '"\s*:\s*("(?:[^"\\]|\\.)*"|[^,}\]\s]+)')
  if ($m.Success) { return $m.Groups[1].Value.Trim('"') }
  return $null
}

function Read-RunResult([string]$path) {
  $r = [pscustomobject]@{ Found = $false; Cost = $null; Turns = $null; DurationMs = $null; IsError = $null; Subtype = $null;
    Model = $null; CliExit = $null; Problem = $null }
  if (-not $path -or -not (Test-Path -LiteralPath $path)) { $r.Problem = 'no log'; return $r }
  $lines = [IO.File]::ReadAllLines($path, [Text.Encoding]::UTF8)
  foreach ($l in $lines) {
    if ($l -match '^started \S+, model (\S+)') { $r.Model = $Matches[1] }
    if ($l -match '^finished \S+, exit (-?\d+)') { $r.CliExit = [int]$Matches[1] }
  }
  $line = $null
  for ($i = $lines.Count - 1; $i -ge 0; $i--) {
    if ($lines[$i] -match '^\s*\{' -and $lines[$i] -match '"type"\s*:\s*"result"') { $line = $lines[$i]; break }
  }
  if (-not $line) {
    $all = $lines -join "`n"
    if ($all -match '"total_cost_usd"') { $line = $all } else { $r.Problem = 'no result JSON'; return $r }
  }
  $o = $null
  try { $o = $line | ConvertFrom-Json } catch { $o = $null }
  if ($o -and ($null -ne $o.total_cost_usd -or $o.type -eq 'result')) {
    # other reviewer programs (engine_run.py) write the same line with total_cost_usd null: they do not report money
    $r.Cost = if ($null -ne $o.total_cost_usd) { [double]$o.total_cost_usd } else { $null }
    if ($null -ne $o.num_turns) { $r.Turns = [int]$o.num_turns }
    if ($null -ne $o.duration_ms) { $r.DurationMs = [double]$o.duration_ms }
    if ($null -ne $o.is_error) { $r.IsError = [bool]$o.is_error }
    $r.Subtype = [string]$o.subtype
  } else {
    $v = Get-JsonField $line 'total_cost_usd'
    if ($null -eq $v) { $r.Problem = 'result JSON without total_cost_usd'; return $r }
    $r.Cost = if ($v -eq 'null') { $null } else { [double]::Parse($v, [Globalization.CultureInfo]::InvariantCulture) }
    $v = Get-JsonField $line 'num_turns'; if ($v -match '^\d+$') { $r.Turns = [int]$v }
    $v = Get-JsonField $line 'duration_ms'; if ($v -match '^[\d.]+$') { $r.DurationMs = [double]::Parse($v, [Globalization.CultureInfo]::InvariantCulture) }
    $v = Get-JsonField $line 'is_error'; if ($v -in 'true', 'false') { $r.IsError = ($v -eq 'true') }
    $r.Subtype = Get-JsonField $line 'subtype'
  }
  $r.Found = $true
  return $r
}

function Test-RunOk($res) {
  # With the JSON: is_error false and subtype success. Without it: the run counts as failed.
  if ($res.Found) { return ($res.IsError -eq $false) -and ($res.Subtype -eq 'success') }
  return $false
}

function Fill-Text([string]$t, $map) {
  foreach ($k in $map.Keys) { $t = $t.Replace('{{' + $k + '}}', [string]$map[$k]) }
  return $t
}

function Format-Duration([double]$seconds, $C) {
  $s = [int][Math]::Floor($seconds)
  if ($s -lt 60) { return Fill-Text $C.sec @{ S = $s } }
  if ($s -lt 3600) { return Fill-Text $C.min @{ M = [int][Math]::Floor($s / 60); S = $s % 60 } }
  return Fill-Text $C.hour @{ H = [int][Math]::Floor($s / 3600); M = [int][Math]::Floor(($s % 3600) / 60) }
}

function Format-Usd($v) { if ($null -eq $v) { return '-' } [string]::Format([Globalization.CultureInfo]::InvariantCulture, '{0:0.00}', [double]$v) }

function Get-JobSeconds($j) {
  # Seconds for one task: the CLI's duration_ms when there is one, otherwise the clock.
  if ($j.Result -and $null -ne $j.Result.DurationMs) { return $j.Result.DurationMs / 1000 }
  if ($j.Start -and $j.End) { return ($j.End - $j.Start).TotalSeconds }
  if ($j.Start -and $j.State -eq 'running') { return ((Get-Date) - $j.Start).TotalSeconds }
  return $null
}

function Get-CostRow($j, $C) {
  # Cells of one table row. $j: Title, State (pending|running|done|skipped), Result, Ok (CLI ok and report written), RunOk, Fresh, Exit, Log.
  $res = $j.Result
  switch ($j.State) {
    'pending' { $status = $C.pending }
    'running' { $status = $C.running }
    'skipped' { $status = $C.skipped }
    default {
      if ($res -and $res.Found) {
        $runOk = if ($j.PSObject.Properties['RunOk']) { $j.RunOk } else { $j.Ok }
        $status = if ($j.Ok) { $C.ok } elseif ($runOk) { $C.okNoReport } else { "$($C.error) ($($res.Subtype))" }
      } else {
        $code = if ($res -and $null -ne $res.CliExit) { $res.CliExit } else { $j.Exit }   # the CLI's own exit code when logged
        $status = "$($C.noJson) ($($C.exit) $code)"
      }
    }
  }
  $report = if ($j.State -eq 'done') { if ($j.Fresh) { $C.written } else { $C.notWritten } } else { '-' }
  $sec = Get-JobSeconds $j
  $time = if ($null -ne $sec) { Format-Duration $sec $C } else { '-' }
  $cost = if ($res -and $res.Found) { Format-Usd $res.Cost } else { '-' }
  $turns = if ($res -and $null -ne $res.Turns) { "$($res.Turns)" } else { '-' }
  $log = if ($j.Log) { Split-Path $j.Log -Leaf } else { '-' }
  return @($j.Title, $status, $report, $cost, $turns, $time, $log)
}

function Write-CostFile([string]$path, $jobs, $info, $C) {
  # $info: Dir, Start (datetime), Model (or empty: taken from the logs), Cap. Rewritten after every task.
  $jobs = @($jobs)
  $model = $info.Model
  if (-not $model) {
    $model = (@($jobs | Where-Object { $_.Result -and $_.Result.Model } | ForEach-Object { $_.Result.Model } | Select-Object -Unique) -join ', ')
    if (-not $model) { $model = '-' }
  }
  $now = Get-Date
  $out = New-Object System.Collections.Generic.List[string]
  $out.Add($C.title); $out.Add('')
  $out.Add((Fill-Text $C.head @{ DIR = $info.Dir; START = $info.Start.ToString('yyyy-MM-dd HH:mm:ss'); NOW = $now.ToString('yyyy-MM-dd HH:mm:ss'); MODEL = $model; CAP = $info.Cap }))
  $out.Add(''); $out.Add($C.columns)
  $sumCost = 0.0; $sumTurns = 0; $sumSec = 0.0; $ok = 0; $bad = 0; $open = 0; $skip = 0
  foreach ($j in $jobs) {
    $cells = Get-CostRow $j $C
    $out.Add('| ' + (($cells | ForEach-Object { ([string]$_).Replace('|', '/') }) -join ' | ') + ' |')
    if ($j.Result -and $j.Result.Found) { $sumCost += $j.Result.Cost; if ($null -ne $j.Result.Turns) { $sumTurns += $j.Result.Turns } }
    $sec = Get-JobSeconds $j; if ($null -ne $sec) { $sumSec += $sec }
    switch ($j.State) { 'done' { if ($j.Ok) { $ok++ } else { $bad++ } } 'skipped' { $skip++ } default { $open++ } }
  }
  $note = Fill-Text $C.totalNote @{ N = $jobs.Count; OK = $ok; BAD = $bad; OPEN = $open; SKIP = $skip }
  $wall = Fill-Text $C.wall @{ WALL = (Format-Duration ($now - $info.Start).TotalSeconds $C); SUM = (Format-Duration $sumSec $C) }
  $out.Add("| $($C.total) | $note | | **$(Format-Usd $sumCost)** | $sumTurns | $wall | |")
  [IO.File]::WriteAllText($path, (($out -join "`n") + "`n"), (New-Object System.Text.UTF8Encoding($false)))
  return [pscustomobject]@{ Cost = $sumCost; Turns = $sumTurns; Ok = $ok; Bad = $bad; Open = $open; Skip = $skip }
}

if ($CheckLog) {
  $res = Read-RunResult $CheckLog
  $res | Format-List
  if ($res.Found) {
    $sec = if ($null -ne $res.DurationMs) { [int][Math]::Floor($res.DurationMs / 1000) } else { '-' }
    Write-Host ("cost {0} USD, {1} turns, {2} s, ok {3}" -f (Format-Usd $res.Cost), $res.Turns, $sec, (Test-RunOk $res))
    exit 0
  }
  Write-Host "No result JSON in $CheckLog ($($res.Problem))."
  exit 1
}
