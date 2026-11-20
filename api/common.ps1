# Shared by the kit's .ps1 files (dot-source it). ASCII only on purpose: Windows PowerShell 5.1 reads a .ps1
# without BOM in the ANSI code page. All Chinese text lives in UTF-8 .md / .json files.
#
# Project file (projects\<id>.json): paths may be absolute, or relative to the folder the project file is in.
# Machine settings (local.json): what belongs to this computer and never to a project or to the kit itself:
#   where Python and Claude Code are, where the API key is kept, which folders nothing may read.
#   Looked up in this order: -LocalFile, environment variable PLAYER_REVIEW_LOCAL, <kit>\local.json, none (defaults).
$script:KitUtf8 = New-Object System.Text.UTF8Encoding($false)
function Read-Utf8([string]$path) { [IO.File]::ReadAllText($path, [Text.Encoding]::UTF8) }
function Write-Utf8([string]$path, [string]$text) { [IO.File]::WriteAllText($path, $text, $script:KitUtf8) }

function Assert-TaskFilled([string]$path, [string]$text) {
  $marker = [regex]::Match($text, '\{\{[^{}]+\}\}')
  if ($marker.Success) {
    [Console]::Error.WriteLine("Unfilled task placeholder $($marker.Value) in $path")
    exit 1
  }
}

function Format-Delivery([string]$text, [string]$language, $texts) {
  # Keep the embedded Chinese instructions byte-for-byte compatible in Chinese tasks.
  $text = $text -creplace '(?m)^> \[PRK language\][^\r\n]*\r?\n\r?\n', ''
  if ($language -ceq 'en') {
    $text = $text.Replace(([string][char]0x60 + $texts.draftSuffix.zh + [char]0x60),
                          ([string][char]0x60 + $texts.draftSuffix.en + [char]0x60))
    $formatGuide = Join-Path (Split-Path $PSScriptRoot -Parent) 'docs\report-format.md'
    return "# Delivery language: English`n`n$($texts.deliveryInstruction)`n`nReport format guide: $formatGuide`n`n$text"
  }
  return $text
}

function Write-Task([string]$path, [string]$text, [string]$language, $texts) {
  $text = Format-Delivery $text $language $texts
  Assert-TaskFilled $path $text
  Write-Utf8 $path $text
}

function Get-OutputName($project, $texts, [string]$kind) {
  $pair = $texts.files.$kind
  $name = if ($project.language -ceq 'en') { $pair.en } else { $pair.zh }
  return [string](Get-Prop (Get-Prop $project 'reportNames') $kind $name)
}

function Find-ProjectOutput($project, $texts, [string]$kind) {
  $pair = $texts.files.$kind
  $other = if ($project.language -ceq 'en') { 'zh' } else { 'en' }
  foreach ($name in @((Get-OutputName $project $texts $kind), $pair.($project.language), $pair.$other)) {
    $path = Join-Path $project.reviewOutDir $name
    if (Test-Path -LiteralPath $path -PathType Leaf) { return $path }
  }
}

function Get-Prop($o, [string]$name, $default = $null) {
  if ($null -ne $o -and $o.PSObject.Properties[$name] -and $null -ne $o.$name -and "$($o.$name)" -ne '') { return $o.$name }
  return $default
}

function Get-DefaultProjectFile([string]$kit) {
  # No project file given: the kit's only one (projects\*.json, templates starting with _ left out). More than one: say which.
  $pf = @(Get-ChildItem (Join-Path $kit 'projects') -Filter *.json -ErrorAction SilentlyContinue | Where-Object { $_.Name -notlike '_*' })
  if ($pf.Count -ne 1) { throw "No -ProjectFile, and the kit has $($pf.Count) project files in projects\ ($(($pf | ForEach-Object { $_.Name }) -join ', ')): pass -ProjectFile." }
  return $pf[0].FullName
}

function Resolve-ProjPath([string]$base, $p) {
  if (-not $p) { return $p }
  $p = [Environment]::ExpandEnvironmentVariables([string]$p)
  if ([IO.Path]::IsPathRooted($p)) { return $p }
  return [IO.Path]::GetFullPath((Join-Path $base $p))
}

function Read-Project([string]$file) {
  # Every path field is absolute afterwards (static\projfile.py does the same for the Python scripts).
  $proj = (Read-Utf8 $file) | ConvertFrom-Json
  if (-not $proj.PSObject.Properties['language']) {
    $proj | Add-Member -NotePropertyName language -NotePropertyValue 'zh'
  }
  if ($proj.language -cnotin 'zh', 'en') { throw 'Project language must be zh or en.' }
  $base = Split-Path $file -Parent
  foreach ($k in 'projectRoot', 'rulesFile', 'modSource', 'modReadme', 'characterIndex', 'characterDir', 'behaviourDir', 'frameworkDir',
      'testsDir', 'testRunner', 'testLogs', 'notesDir', 'loreBible', 'characterNotes', 'changeReports', 'reviewOutDir', 'staticOutDir',
      'personaOverlay', 'apiRunner') {
    if ($proj.PSObject.Properties[$k] -and $proj.$k) { $proj.$k = Resolve-ProjPath $base $proj.$k }
  }
  foreach ($k in 'previousReviews', 'readOnlyPaths', 'neverRead') {
    if ($proj.PSObject.Properties[$k] -and $proj.$k) { $proj.$k = @($proj.$k | Where-Object { $_ } | ForEach-Object { Resolve-ProjPath $base $_ }) }
  }
  return $proj
}

function Read-Local([string]$kit, [string]$file) {
  # Returns the machine settings object, with _file = where it was read from ('' when there is none).
  if (-not $file) { $file = $env:PLAYER_REVIEW_LOCAL }
  if (-not $file) { $file = Join-Path $kit 'local.json' }
  if (Test-Path -LiteralPath $file) {
    $o = (Read-Utf8 $file) | ConvertFrom-Json
    $o | Add-Member -NotePropertyName _file -NotePropertyValue ((Resolve-Path -LiteralPath $file).Path) -Force
    if ($o.PSObject.Properties['neverRead']) {
      $base = Split-Path $o._file -Parent
      $o.neverRead = @($o.neverRead | Where-Object { $_ } | ForEach-Object { [IO.Path]::GetFullPath((Resolve-ProjPath $base $_)) })
    }
    return $o
  }
  return [pscustomobject]@{ _file = '' }
}

function Get-Python($local, $proj) {
  # Machine settings first, then the project file (older project files had it there), then whatever is on PATH.
  $p = Get-Prop $local 'python' (Get-Prop $proj 'python' '')
  if ($p) { return [Environment]::ExpandEnvironmentVariables([string]$p) }
  # prk.py sets this to the Python it runs under: without it, "python" on PATH can be a stub that runs nothing
  # (exit 9009) and the static tables are silently skipped.
  if ($env:PLAYER_REVIEW_PYTHON -and (Test-Path -LiteralPath $env:PLAYER_REVIEW_PYTHON)) { return $env:PLAYER_REVIEW_PYTHON }
  return 'python'
}

function Arg-Line([string[]]$a) {
  ($a | ForEach-Object {
    if ($_ -and $_ -notmatch '[ \t"]') { $_ }
    else { '"' + ($_ -replace '(\\*)"', '$1$1\"' -replace '(\\+)\z', '$1$1') + '"' }
  }) -join ' '
}

function Start-ReviewRunner([string[]]$a, [string]$log) {
  $settings = @{ PassThru = $true; WindowStyle = 'Hidden'; RedirectStandardOutput = "$log.out.txt"; RedirectStandardError = "$log.err.txt" }
  if (-not $env:PRK_RUNNER_RECORDS) {
    return (Start-Process powershell.exe -ArgumentList (Arg-Line $a) @settings)
  }

  # A page-started runner waits until its PID and creation time are registered. If the scheduler stops before
  # releasing it, the wrapper times out without entering the runner script.
  $record = Join-Path $env:PRK_RUNNER_RECORDS ([IO.Path]::GetFileName($log) + '.json')
  $params = @{}
  for ($i = 5; $i -lt $a.Count; $i++) {
    $flag = $a[$i].Substring(1)
    if ($flag -in 'Json', 'Subscription') { $params[$flag] = $true }
    else { $i++; $params[$flag] = $a[$i] }
  }
  $payload = @{ script = $a[4]; params = $params; record = $record } | ConvertTo-Json -Compress
  $payload64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
  $wrapper = @'
$ErrorActionPreference = 'Stop'
$job = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('PAYLOAD')) | ConvertFrom-Json
$deadline = [DateTime]::UtcNow.AddSeconds(60)
while (-not [IO.File]::Exists($job.record)) {
  if ([DateTime]::UtcNow -ge $deadline) { exit 2 }
  Start-Sleep -Milliseconds 50
}
$params = @{}
foreach ($p in $job.params.PSObject.Properties) { $params[$p.Name] = $p.Value }
$global:LASTEXITCODE = 0
& $job.script @params
exit $LASTEXITCODE
'@
  $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($wrapper.Replace('PAYLOAD', $payload64)))
  $p = Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -EncodedCommand $encoded" @settings
  try {
    $null = $p.Handle
    $identity = @{ pid = $p.Id; created = $p.StartTime.ToFileTimeUtc() } | ConvertTo-Json -Compress
    Write-Utf8 "$record.tmp" $identity
    [IO.File]::Move("$record.tmp", $record)
  } catch {
    if (-not $p.HasExited) { $p.Kill() }
    throw
  }
  return $p
}
