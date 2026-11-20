# Player-perspective bug review run headless: paid by an API key, or with -Subscription by the reviewer program's own login.
# One headless Claude Code task per review group (or per group x split), then merge tasks. Every task goes through the
# runner (the kit's api\run_api_task.ps1 unless the project file names another) with -Json; the runner loads the key
# itself and never prints it; this script never touches the key.
# This file stays ASCII on purpose: Windows PowerShell 5.1 reads a .ps1 without BOM in the ANSI code page.
# All Chinese text comes from UTF-8 files: the agent prompt, merge.md, the templates and texts.json in this folder,
# kinds\kinds.json and the walk files next to it, the project file.
# Nothing about one game is fixed here: paths, groups, splits and names come from the project file; what belongs to
# this computer (Python, Claude Code, the key, folders nobody may read) comes from the machine settings (local.json).
#
#   -Scope              free text: characters, files, a change report, or ALL (default)
#   -Groups             review group ids from the project file (default: its defaultGroups), or free text like '3 + 8'
#                       (free text = a persona walk with those personas)
#   -Kind               the review kind for a free-text group (default persona); groups of the project file bring their own
#   -SplitByCharacters  one task per group x characterSplits entry of the project file; merge in two levels when there
#                       is more than one group: each group's splits first (reportNames.groupMerged), then the groups
#   -Parallel           run tasks at the same time (Start-Process, one log each), at most -MaxParallel (default 7)
#                       at once; the rest wait in a queue. Without -Parallel the tasks run one after another.
#   -OutDir             default <project reviewOutDir>\<yyyyMMdd_HHmmss> (a new folder each run; _2, _3 ... if taken)
#   -Model              passed to the runner only when given (otherwise the machine settings' defaultModel)
#   -NoMerge            skip the merge tasks (merge on the subscription instead)
#   -DryRun             write the task files and print the commands; no API call, no static tables, no cost table
#   -PrepareOnly        run static tables and write all task files and _prepared.json; do not launch a runner
#   -MaxTurns           passed to the runner (default 200)
#   -NoMap              skip the map task (kinds\map.md: one task reads the work first and writes tables of its lines,
#                       choices, flags, things, endings, numbers and texts into <OutDir>\_map; every reviewer reads them)
#   -MapDir             use a map made earlier (a folder with _map.md) instead of making a new one
#   -Expand             after the merge: one more task turns the report's "wanted but missing" entries into content
#                       proposals with drafts (kinds\expand.md, api\expand_api.ps1). Never changes the work. Off by
#                       default: usually the owner picks entries first, then expand_api.ps1 -Items runs on those.
#   -RunId              optional identifier for the -Expand task and log files.
#   -LocalFile          machine settings (default: environment variable PLAYER_REVIEW_LOCAL, then <kit>\local.json)
#   -Subscription       pay with the login of the reviewer program on this computer (Claude Code's; Codex's ChatGPT
#                       login) instead of a key: passed as it is to every task's runner and to
#                       expand_api.ps1. Only for providers with "signin": true in api\providers.json (the runner checks).
# Each task's result is read from the JSON line the CLI prints last (run_result.ps1): is_error and subtype decide
# success; total_cost_usd, num_turns and duration_ms go into the cost table (reportNames.cost), rewritten after
# every task. A report counts only when it was written after its task started, so an old report in a reused folder
# is never merged as this run's. Stopping this script stops the queue; tasks already running finish on their own.
param(
  [string]$Scope = 'ALL',
  [string[]]$Groups,
  [switch]$SplitByCharacters,
  [string]$OutDir,
  [string]$Model,
  [string]$Provider,
  [switch]$Parallel,
  [int]$MaxParallel = 7,
  [switch]$NoMerge,
  [switch]$DryRun,
  [switch]$PrepareOnly,
  [string]$ProjectFile,
  [string]$Runner,
  [int]$MaxTurns = 200,
  [string]$LocalFile,
  [switch]$NoMap,
  [string]$MapDir,
  [switch]$Expand,
  [string]$Kind = 'persona',
  [switch]$Subscription,
  [string]$RunId
)
$ErrorActionPreference = 'Stop'
if ($DryRun -and $PrepareOnly) { throw 'Use either -DryRun or -PrepareOnly.' }
$planning = $DryRun -or $PrepareOnly
$hasRunId = $PSBoundParameters.ContainsKey('RunId')
if ($hasRunId -and $RunId -cnotmatch '\A[A-Za-z0-9_-]{1,40}\z') { throw 'Invalid -RunId: use 1 to 40 ASCII letters, digits, underscores or hyphens.' }
$kit = Split-Path $PSScriptRoot -Parent
. (Join-Path $PSScriptRoot 'common.ps1')     # Read-Utf8, Write-Utf8, Get-Prop, Read-Project, Read-Local, Get-Python
if (-not $ProjectFile) { $ProjectFile = Get-DefaultProjectFile $kit }
$ProjectFile = (Resolve-Path $ProjectFile).Path
. (Join-Path $PSScriptRoot 'run_result.ps1')   # Read-RunResult, Test-RunOk, Write-CostFile, Get-CostRow, Fill-Text

$proj = Read-Project $ProjectFile
$local = Read-Local $kit $LocalFile
$python = Get-Python $local $proj
$T = (Read-Utf8 (Join-Path $PSScriptRoot 'texts.json')) | ConvertFrom-Json
$C = if ($proj.language -ceq 'en') { $T.costEn } else { $T.cost }
$owner = [string](Get-Prop $proj 'ownerName' $T.ownerDefault)
$unit = [string](Get-Prop $proj 'splitUnitName' $T.unitDefault)
if (-not $Runner) { $Runner = [string](Get-Prop $proj 'apiRunner' (Join-Path $PSScriptRoot 'run_api_task.ps1')) }
# Review kinds: kinds\kinds.json registers them, one walk file each. A group picks one with "kind" (older files: "walk").
$kindsDir = Join-Path $kit 'kinds'
$kinds = @{}
foreach ($kd in ((Read-Utf8 (Join-Path $kindsDir 'kinds.json')) | ConvertFrom-Json).kinds) { $kinds[[string]$kd.id] = $kd }
if ($MaxParallel -lt 1) { $MaxParallel = 1 }
$cap = if ($Parallel) { $MaxParallel } else { 1 }
if (-not $OutDir) {
  $base = Join-Path $proj.reviewOutDir (Get-Date -Format 'yyyyMMdd_HHmmss')
  $OutDir = $base
  $k = 2
  while (Test-Path $OutDir) { $OutDir = "${base}_$k"; $k++ }
}
if (-not $planning -and -not (Test-Path $Runner)) { throw "Runner not found: $Runner" }
New-Item -ItemType Directory -Force $OutDir | Out-Null
$OutDir = (Resolve-Path $OutDir).Path
$runStart = Get-Date

# Report and cost file names (Chinese, so they come from the project file / texts.json).
$rn = Get-Prop $proj 'reportNames' ([pscustomobject]@{})
$nameGroup = Get-OutputName $proj $T 'group'
$nameMerged = Get-OutputName $proj $T 'merged'
$nameSplit = [string](Get-Prop $rn 'split' $nameGroup.Replace('{0}', '{0}_{1}'))
$nameGroupMerged = Get-OutputName $proj $T 'groupMerged'
$costPath = Join-Path $OutDir (Get-OutputName $proj $T 'cost')

# Review groups (reviewGroups; older project files: personaGroups): ids from the project file ("A,B" as one argument also works), anything else is free text.
$known = @{}
$groupDefs = Get-Prop $proj 'reviewGroups' (Get-Prop $proj 'personaGroups' @())
foreach ($g in $groupDefs) { $known[[string]$g.id] = $g }
if (-not $Groups -or $Groups.Count -eq 0) { $Groups = @($proj.defaultGroups) }
$list = @()
foreach ($g in $Groups) {
  $parts = @($g -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
  if (($parts | Where-Object { -not $known.ContainsKey($_) }).Count -eq 0) { $list += $parts } else { $list += $g }
}
$groupsToRun = @()
$n = 0
foreach ($g in $list) {
  $n++
  if ($known.ContainsKey($g)) {
    $def = $known[$g]
    $kindId = [string](Get-Prop $def 'kind' (Get-Prop $def 'walk' 'persona'))
    $groupsToRun += [pscustomobject]@{ Id = $def.id; Title = "$($def.id) $($def.name)"; Personas = (@($def.personas) -join '; '); Kind = $kindId }
  } else {
    $groupsToRun += [pscustomobject]@{ Id = "G$n"; Title = "G$n"; Personas = $g; Kind = $Kind }
  }
}
# Every group's kind must be registered, have its walk file, and find what it needs in the project file.
if ($PrepareOnly -and -not $groupsToRun.Count) { throw 'No review groups: use -Groups or set defaultGroups.' }
$kindBody = @{}
foreach ($g in $groupsToRun) {
  if (-not $kinds.ContainsKey($g.Kind)) { throw "Group $($g.Id): review kind '$($g.Kind)' is not in kinds\kinds.json (known: $(($kinds.Keys | Sort-Object) -join ', '))." }
  $kd = $kinds[$g.Kind]
  if ([string](Get-Prop $kd 'role' 'review') -ne 'review') { throw "Group $($g.Id): '$($g.Kind)' is a preparing step, not a review kind; it runs by itself before the reviewers (see -NoMap, -MapDir)." }
  foreach ($need in @(Get-Prop $kd 'needs' @())) {
    if (-not (Get-Prop $proj ([string]$need))) { throw "Group $($g.Id): review kind '$($g.Kind)' needs '$need' in the project file." }
  }
  if (-not $kindBody.ContainsKey($g.Kind)) {
    $kf = Join-Path $kindsDir ([string]$kd.file)
    if (-not (Test-Path -LiteralPath $kf)) { throw "Review kind '$($g.Kind)': walk file not found: $kf" }
    $kindBody[$g.Kind] = Read-Utf8 $kf
  }
}

# Splits (characterSplits: characters, levels, chapters ... whatever the project's unit is): ids go into task and log file names (Start-Process breaks on non-ASCII paths), names into report names.
$splits = @($null)
if ($SplitByCharacters) {
  $splits = @($proj.characterSplits | Where-Object { $_ })
  if ($splits.Count -eq 0) { throw "-SplitByCharacters: the project file has no characterSplits." }
  $covered = @{}
  foreach ($s in $splits) {
    if ($s.id -notmatch '^[A-Za-z0-9_-]+$') { throw "characterSplits id '$($s.id)': use only ASCII letters, digits, _ and - (it goes into task and log file names)." }
    foreach ($ch in @($s.characters) + @($s.minor)) { if ($ch) { $covered[[string]$ch] = $true } }   # not $c: names ignore case, $C is the cost texts
  }
  # Optional check: one data file per unit in characterDir (splitCheckFilter, default *.json) = the full list of units.
  $cdir = Get-Prop $proj 'characterDir' ''
  if ($cdir -and (Test-Path $cdir)) {
    foreach ($f in Get-ChildItem $cdir -Filter ([string](Get-Prop $proj 'splitCheckFilter' '*.json'))) {
      if (-not $covered.ContainsKey($f.BaseName)) { Write-Warning "'$($f.BaseName)' (in characterDir) is in no characterSplits entry: no task walks it on purpose." }
    }
  }
}

# Shared text: the reviewer prompt without its YAML header, with the kit and project paths filled in.
function Fill([string]$text) { $text.Replace('{{KIT}}', $kit).Replace('{{PROJECT_FILE}}', $ProjectFile).Replace('{{OWNER}}', $owner) }
$agentBody = Fill ((Read-Utf8 (Join-Path $kit 'agent\player-bug-reviewer.md')) -replace '(?s)^---\r?\n.*?\r?\n---\r?\n', '')
$mergeBody = Fill (Read-Utf8 (Join-Path $kit 'skill\player-review\merge.md'))
function Read-TaskTemplate([string]$name) {
  Fill ((Read-Utf8 (Join-Path $PSScriptRoot $name)).Replace($T.headlessTitle, '').Replace($T.headlessIntro, $T.taskIntro))
}
$taskTpl = Read-TaskTemplate 'task_template.md'
$mergeTpl = Read-TaskTemplate 'merge_template.md'
# The map (kinds\map.md, role prepare): made first by its own task, or taken from -MapDir, or left out with -NoMap.
$mapFolder = ''; $makeMap = $false
if ($MapDir) {
  if (-not (Test-Path -LiteralPath (Join-Path $MapDir '_map.md'))) { throw "-MapDir: no _map.md in $MapDir" }
  $mapFolder = (Resolve-Path -LiteralPath $MapDir).Path
} elseif (-not $NoMap -and $kinds.ContainsKey('map')) {
  $mapFolder = Join-Path $OutDir '_map'; $makeMap = $true
}
$mapLine = if ($mapFolder) { Fill-Text $T.mapLine @{ DIR = $mapFolder } } else { $T.mapNone }
# The owner's decisions on the last round's feedback (written by the skill's step 7): the next round starts from them.
$decFile = Find-ProjectOutput $proj $T 'decisions'
$decLine = if ($decFile) { Fill-Text $T.decisionsLine @{ PATH = $decFile } } else { $T.decisionsNone }
if ($proj.language -ceq 'en' -or ($decFile -and (Split-Path $decFile -Leaf) -eq $T.files.decisions.en)) {
  $fixList = Find-ProjectOutput $proj $T 'fixList'
  if ($decFile) { $decLine += ' Read either language of decision words as defined in docs/report-format.md.' }
  if ($fixList) { $decLine += " Fix list: $fixList" }
}
foreach ($k in @($kindBody.Keys)) { $kindBody[$k] = Fill $kindBody[$k] }
$readOnly = (@(Get-Prop $proj 'readOnlyPaths' @()) -join ', ')
if (-not $readOnly) { $readOnly = $T.nothingListed }
# reviewFocus (project file): what this review should look at first; one line on top of every task (none: line removed).
$focus = [string](Get-Prop $proj 'reviewFocus' '')
function Focus-Line([string]$tpl) { if ($focus) { Fill-Text $tpl @{ FOCUS = $focus } } else { '' } }
function Drop-EmptyFocus([string]$tpl) { if ($focus) { $tpl } else { $tpl -replace '(?m)^\{\{FOCUS\}\}
?
', '' } }
$neverReadList = @(Get-Prop $proj 'neverRead' @()) + @(Get-Prop $local 'neverRead' @()) | Where-Object { $_ } | Select-Object -Unique
$neverRead = (@($neverReadList) -join ', ')
if (-not $neverRead) { $neverRead = $T.nothingListed }

# Static tables (local, read-only, a few seconds): run_all.py writes the tables the project's staticTables names
# and _summary.md into the out folder; the reviewers and the merge read them.
$summary = Join-Path $OutDir '_summary.md'
$staticArgs = @('--project', $ProjectFile)
$staticCmd = "& '$python' -I '$kit\static\run_all.py' --project '$ProjectFile'"
if ($local._file) {
  $staticArgs += @('--local', $local._file)
  $staticCmd += " --local '$($local._file)'"
}
$staticCmd += " '$OutDir'"
$staticOk = $false
if ($DryRun) {
  Write-Host 'Static tables (dry run, not run):'
  Write-Host "  $staticCmd"
} else {
  try {
    & $python -I "$kit\static\run_all.py" @staticArgs $OutDir
    $staticOk = ($LASTEXITCODE -eq 0) -and (Test-Path -LiteralPath $summary -PathType Leaf)
    if (-not $staticOk) { Write-Warning "Static tables: run_all.py exited with $LASTEXITCODE or did not write the summary; the reviewers will run them themselves." }
  } catch { Write-Warning "Static tables failed ($_); the reviewers will run them themselves." }
}

# The ledger: one row per task, kept across rounds (cost_ledger.py reads the logs; the same round can be recorded any number of times).
function Update-Ledger {
  $la = @('--project', $ProjectFile)
  if ($local._file) { $la += @('--local', $local._file) }   # the price table is in the machine settings
  try {
    & $python -I "$kit\api\cost_ledger.py" @la $OutDir | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "cost_ledger.py exited with code $LASTEXITCODE" }
    return $true
  } catch {
    Write-Warning "Cost ledger not updated: $_"
    return $false
  }
}

function Runner-Args([string]$task, [string]$log) {
  # Never -AllowModEdits: reviews are read-only. -Json: the CLI's last line is the result JSON (cost, turns, errors).
  # The project folder and the read-only / never-read paths come from the project file (nothing is fixed in the runner).
  $a = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Runner, '-TaskFile', $task, '-LogFile', $log, '-WorkDir', $proj.projectRoot)
  $ro = (@(Get-Prop $proj 'readOnlyPaths' @()) -join ';'); if ($ro) { $a += @('-ReadOnly', $ro) }   # empty: leave the switch out
  $nr = (@(Get-Prop $proj 'neverRead' @()) -join ';'); if ($nr) { $a += @('-NeverRead', $nr) }
  if ($local._file) { $a += @('-LocalFile', $local._file) }   # the runner adds the machine settings' neverRead itself
  $a += @('-MaxTurns', "$MaxTurns", '-Json')
  if ($Model) { $a += @('-Model', $Model) }
  if ($Provider) { $a += @('-Provider', $Provider) }
  if ($Subscription) { $a += '-Subscription' }   # the login of this computer pays, no key is read
  return $a
}
function Fill-Template([string]$tpl, $map) {
  # $map is [ordered]: BODY goes last, so text inside the body is never treated as a placeholder.
  foreach ($k in $map.Keys) { $tpl = $tpl.Replace('{{' + $k + '}}', [string]$map[$k]) }
  return $tpl
}
function New-Task([string]$name, [string]$title, [string]$kind, [string]$report) {
  if ($proj.language -ceq 'en') { $title = $name }
  $job = [pscustomobject]@{ Name = $name; Title = $title; Kind = $kind; Report = $report;
    Task = (Join-Path $OutDir "task_$name.md"); Log = (Join-Path $OutDir "log_$name.txt"); Args = $null;
    Deps = @(); Level = ''; State = 'pending'; Proc = $null; Exit = $null; Start = $null; End = $null;
    PreviousReport = $null; Fresh = $false; RunOk = $false; Ok = $false; Result = $null }
  $job.Args = Runner-Args $job.Task $job.Log
  if (-not $planning -and (Test-Path -LiteralPath $report)) {
    Write-Warning "$report is from an earlier run: it is not merged unless this run rewrites it."
  }
  return $job
}

# Review tasks: one per group, or one per group x split. Their task files are written now.
function Others-Line($me) {
  $o = @($groupsToRun | Where-Object { $_.Id -ne $me.Id } | ForEach-Object { "$($_.Title) [$([string]$kinds[$_.Kind].name)]" })
  if ($o.Count) { $o -join $T.othersSep } else { $T.nothingListed }
}
$jobs = @()
$byGroup = @{}
foreach ($g in $groupsToRun) {
  $byGroup[$g.Id] = @()
  foreach ($s in $splits) {
    if ($s) {
      $name = "$($g.Id)_$($s.id)"
      $title = Fill-Text $T.titleSplit @{ GROUP = $g.Title; SPLIT = $s.name }
      $splitLabel = if ($proj.language -ceq 'en' -and -not ($rn.split -or $rn.group)) { $s.id } else { $s.name }
      $report = Join-Path $OutDir ($nameSplit -f $g.Id, $splitLabel)
      $minor = @($s.minor | Where-Object { $_ })
      # how a split's scope reads depends on the review kind (kinds.json: splitScope)
      $scopeTpl = [string](Get-Prop $kinds[$g.Kind] 'splitScope' $T.splitScopeFallback)
      $scopeText = Fill-Text $scopeTpl @{ UNIT = $unit; ITEMS = (@($s.characters) -join $T.listSep);
        MINOR = $(if ($minor.Count) { Fill-Text $T.splitMinor @{ MINOR = ($minor -join $T.listSep) } } else { '' }); NOTE = $s.note }
      if ($Scope -and $Scope -ne 'ALL') { $scopeText += Fill-Text $T.scopeWhole @{ SCOPE = $Scope } }
    } else {
      $name = $g.Id
      $title = $g.Title
      $report = Join-Path $OutDir ($nameGroup -f $g.Id)
      $scopeText = $Scope + $T.scopeAllNote
    }
    $j = New-Task $name $title 'review' $report
    $kindLine = Fill-Text $T.kindLine @{ NAME = [string]$kinds[$g.Kind].name; ID = $g.Kind }
    $text = Fill-Template (Drop-EmptyFocus $taskTpl) ([ordered]@{ GROUP = $title; FOCUS = (Focus-Line $T.focusLine); PROJECT_FILE = $ProjectFile; KIND = $kindLine; SCOPE = $scopeText; PERSONAS = $(if ($g.Personas) { $g.Personas } else { $T.nothingListed });
      PYTHON = $python; STATIC = "$OutDir (start with $summary)"; MAP = $mapLine; DECISIONS = $decLine; OTHERS = (Others-Line $g); REPORT = $report; READONLY = $readOnly; NEVERREAD = $neverRead; BODY = $agentBody; KIND_BODY = $kindBody[$g.Kind] })
    Write-Task $j.Task $text $proj.language $T
    $jobs += $j
    $byGroup[$g.Id] += $j
  }
}
$reviewCount = $jobs.Count

# Merge tasks. Their task files are written when their inputs are done (only reports written in this run go in).
$mergedReport = Join-Path $OutDir $nameMerged
$final = $null
if (-not $NoMerge) {
  if ($SplitByCharacters -and $groupsToRun.Count -gt 1) {
    $groupMerges = @()
    foreach ($g in $groupsToRun) {
      $m = New-Task "merge_$($g.Id)" (Fill-Text $T.titleGroupMerge @{ GROUP = $g.Title }) 'merge' (Join-Path $OutDir ($nameGroupMerged -f $g.Id))
      $m.Deps = @($byGroup[$g.Id])
      $m.Level = (Fill-Text $T.mergeLevelGroup @{ GROUP = $g.Title }) + $T.mergeLevelNext
      $groupMerges += $m
    }
    $final = New-Task 'merge' $T.titleFinalMerge 'merge' $mergedReport
    $final.Deps = $groupMerges
    $final.Level = $T.mergeLevelFinal
    $jobs += $groupMerges
  } else {
    $final = New-Task 'merge' $T.titleFinalMerge 'merge' $mergedReport
    $final.Deps = @($jobs)
    if ($SplitByCharacters) { $final.Level = Fill-Text $T.mergeLevelGroup @{ GROUP = $groupsToRun[0].Title } }
  }
  $jobs += $final
}

# The map task goes first; every review waits for it (a failed map does not stop them: the tasks say what to do then).
$mapJob = $null
if ($makeMap) {
  New-Item -ItemType Directory -Force $mapFolder | Out-Null
  $mapJob = New-Task 'map' ([string]$kinds['map'].name) 'map' (Join-Path $mapFolder '_map.md')
  $mapText = Fill-Template (Read-TaskTemplate 'map_template.md') ([ordered]@{ PROJECT_FILE = $ProjectFile; SCOPE = $Scope;
    STATIC = "$OutDir (start with $summary)"; REPORT = $mapJob.Report; READONLY = $readOnly; NEVERREAD = $neverRead;
    BODY = (Fill (Read-Utf8 (Join-Path $kindsDir ([string]$kinds['map'].file)))) })
  Write-Task $mapJob.Task $mapText $proj.language $T
  foreach ($j in @($jobs | Where-Object { $_.Kind -eq 'review' })) { $j.Deps = @($mapJob) }
  $jobs = @($mapJob) + $jobs
}

function Prepare-Merge($j) {
  # Inputs: each dependency's report written in this run. A group merge that wrote nothing is replaced by that
  # group's own split reports. No input at all: the merge is skipped.
  $have = @(); $notes = @()
  foreach ($d in $j.Deps) {
    if ($planning -or $d.Fresh) {
      $have += $d.Report
      if (-not $planning -and -not $d.Ok) { $notes += "$($d.Title): $($T.missingShaky) ($((Get-CostRow $d $C)[1]); log $($d.Log))" }
    } elseif ($d.Kind -eq 'merge' -and @($d.Deps | Where-Object { $_.Fresh }).Count) {
      $have += @($d.Deps | Where-Object { $_.Fresh } | ForEach-Object { $_.Report })
      $notes += "$($d.Title): $($T.missingGroupMerge) ($((Get-CostRow $d $C)[1]); log $($d.Log))"
    } else {
      $notes += "$($d.Title): $($T.missingNoReport) ($((Get-CostRow $d $C)[1]); log $($d.Log))"
    }
  }
  if ($have.Count -eq 0) { $j.State = 'skipped'; Write-Warning "$($j.Name): no report to merge, skipped."; return }
  # Citation check (static\check_citations.py, a few seconds): does every file:line in the reports' index hold that text?
  $citeOut = Join-Path $OutDir "_citations_$($j.Name).md"
  # A chat round (-PrepareOnly) has no reports yet: the AI runs "prk cite" on the round folder right before the merge
  # stage, which writes _citations.md there (the playbook says so). Point the merge task at that file.
  if ($PrepareOnly) { $citeOut = Join-Path $OutDir '_citations.md' }
  $cites = Fill-Text $T.citesIfPresent @{ PATH = $citeOut }
  if (-not $planning) {
    $citeArgs = @('--project', $ProjectFile, '--out', $citeOut)
    foreach ($path in @(Get-Prop $local 'neverRead' @())) { if ($path) { $citeArgs += @('--never', $path) } }
    try {
      $result = @(& $python -I "$kit\static\check_citations.py" @citeArgs @have)
      if ($LASTEXITCODE -ne 0) { throw "check_citations.py exited with code $LASTEXITCODE" }
      if ($result -cnotcontains 'citations-written' -or -not (Test-Path -LiteralPath $citeOut -PathType Leaf)) {
        throw 'check_citations.py did not write the table for this check.'
      }
    } catch { $cites = $T.citesNone; Write-Warning "$($j.Name): citation check failed ($_)." }
  }
  $tpl = $mergeTpl
  if (-not $j.Level) { $tpl = $tpl -replace '(?m)^\{\{LEVEL\}\}\r?\n', '' }
  $tpl = Drop-EmptyFocus $tpl
  $text = Fill-Template $tpl ([ordered]@{ FOCUS = (Focus-Line $T.focusLineMerge); PROJECT_FILE = $ProjectFile; SCOPE = $Scope; LEVEL = $j.Level; INPUTS = ($have -join ' ; ');
    MISSING = $(if ($notes.Count) { $notes -join ' ; ' } else { $T.missingIfAny }); MAP = $mapLine; DECISIONS = $decLine; CITES = $cites; OUTPUT = $j.Report; READONLY = $readOnly; NEVERREAD = $neverRead; BODY = $mergeBody })
  Write-Task $j.Task $text $proj.language $T
}

function Write-Prepared {
  # The jobs are already in dependency order, so each stage is one after its latest prerequisite.
  $stageOf = @{}
  $stages = [ordered]@{}
  foreach ($j in $jobs) {
    $stage = 1
    foreach ($d in $j.Deps) { $stage = [Math]::Max($stage, 1 + $stageOf[$d.Name]) }
    $stageOf[$j.Name] = $stage
    $key = [string]$stage
    if (-not $stages.Contains($key)) { $stages[$key] = [ordered]@{ stage = $stage; tasks = @() } }
    $stages[$key].tasks += [ordered]@{ name = $j.Name; kind = $j.Kind; task = $j.Task; writes = $j.Report }
  }
  $prepared = [ordered]@{ ok = $staticOk; language = $proj.language; round = (Split-Path $OutDir -Leaf); dir = $OutDir;
    stages = @($stages.Values); static = [ordered]@{ ok = $staticOk; summary = $summary }; count = $jobs.Count }
  Write-Utf8 (Join-Path $OutDir '_prepared.json') (ConvertTo-Json -InputObject $prepared -Depth 8)
}

function Launch-Task($j) {
  if (Test-Path -LiteralPath $j.Report -PathType Leaf) {
    $report = Get-Item -LiteralPath $j.Report
    $j.PreviousReport = @{ LastWrite = $report.LastWriteTimeUtc; Length = $report.Length }
  }
  $j.Start = Get-Date
  try {
    $p = Start-ReviewRunner $j.Args $j.Log
    $null = $p.Handle   # keep the handle so ExitCode is readable after the process ends
    $j.Proc = $p
    $j.State = 'running'
    Write-Host "$(Get-Date -Format T) start $($j.Name) (log $($j.Log))"
  } catch {
    Write-Warning "$($j.Name): could not start ($_)."
    $j.End = Get-Date; $j.Exit = -1; $j.Result = Read-RunResult $j.Log; $j.Ok = $false; $j.State = 'done'
  }
}
function Finish-Task($j) {
  $j.End = Get-Date
  $j.Exit = $j.Proc.ExitCode
  $j.Result = Read-RunResult $j.Log
  $j.RunOk = ($j.Exit -eq 0) -and (Test-RunOk $j.Result)
  if (Test-Path -LiteralPath $j.Report -PathType Leaf) {
    $report = Get-Item -LiteralPath $j.Report
    $j.Fresh = ($report.Length -gt 0) -and ($report.LastWriteTime -ge $j.Start.AddSeconds(-2)) -and
      (-not $j.PreviousReport -or $report.LastWriteTimeUtc -ne $j.PreviousReport.LastWrite -or $report.Length -ne $j.PreviousReport.Length)
  }
  if ($j.RunOk -and -not $j.Fresh) {
    Add-Content -LiteralPath $j.Log -Encoding UTF8 -Value 'report status: missing or unchanged'
  }
  $j.Ok = $j.RunOk -and $j.Fresh           # a task counts as ok only when it also wrote its report in this run
  $j.State = 'done'
  $r = $j.Result
  $what = if ($j.Ok) { 'ok' } elseif ($j.RunOk) { 'FAILED (CLI ok but no report written)' } elseif ($r.Found) { "FAILED ($($r.Subtype))" } else { "FAILED (no result JSON, exit $($j.Exit))" }
  $money = if ($r.Found) { ", $(Format-Usd $r.Cost) USD, $($r.Turns) turns" } else { '' }
  Write-Host "$(Get-Date -Format T) done  $($j.Name): $what$money, report $(if ($j.Fresh) { 'written' } else { 'NOT written' })"
  if (-not $j.Ok) { Write-Warning "$($j.Name): read the log $($j.Log)" }
}

if ($PrepareOnly) {
  foreach ($j in $jobs) { if ($j.Kind -eq 'merge') { Prepare-Merge $j } }
  Write-Prepared
  if (-not $staticOk) { exit 1 }
  exit 0
}

$mergeCount = @($jobs | Where-Object { $_.Kind -eq 'merge' }).Count
Write-Host ("Groups: " + (($groupsToRun | ForEach-Object { "$($_.Title) [$($_.Kind)]" }) -join ' | '))
if ($focus) { Write-Host 'Focus : reviewFocus of the project file is on top of every task.' }
Write-Host ("Tasks : " + $(if ($mapJob) { '1 map, ' } elseif ($mapFolder) { '(map from -MapDir) ' } else { '(no map) ' }) + "$reviewCount review" + $(if ($SplitByCharacters) { " ($($groupsToRun.Count) groups x $($splits.Count) splits)" } else { '' }) +
  ", $mergeCount merge; at most $cap at a time")
Write-Host ("Pay   : " + $(if ($Subscription) { 'subscription login of this computer (-Subscription), no key' } else { 'API key / provider account' }))
if ($DryRun) {
  foreach ($j in $jobs) { if ($j.Kind -eq 'merge') { Prepare-Merge $j } }
  Write-Host 'Tasks (dry run, not run):'
  foreach ($j in $jobs) { Write-Host ("  [$($j.Name)] powershell.exe " + (Arg-Line $j.Args)) }
} else {
  $costInfo = @{ Dir = $OutDir; Start = $runStart; Model = $Model; Cap = $cap }
  $null = Write-CostFile $costPath $jobs $costInfo $C
  while ($true) {
    $changed = $false
    foreach ($j in @($jobs | Where-Object { $_.State -eq 'running' })) {
      if ($j.Proc.HasExited) { Finish-Task $j; $changed = $true }
    }
    $running = @($jobs | Where-Object { $_.State -eq 'running' }).Count
    foreach ($j in @($jobs | Where-Object { $_.State -eq 'pending' })) {
      if ($running -ge $cap) { break }
      if (@($j.Deps | Where-Object { $_.State -ne 'done' -and $_.State -ne 'skipped' }).Count) { continue }
      if ($j.Kind -eq 'merge') { Prepare-Merge $j; if ($j.State -eq 'skipped') { $changed = $true; continue } }
      Launch-Task $j
      $changed = $true
      if ($j.State -eq 'running') { $running++ }
    }
    if ($changed) { $null = Write-CostFile $costPath $jobs $costInfo $C; $null = Update-Ledger }
    if (-not @($jobs | Where-Object { $_.State -eq 'pending' -or $_.State -eq 'running' }).Count) { break }
    Start-Sleep -Seconds 5
  }
  $tot = Write-CostFile $costPath $jobs $costInfo $C
  $ledgerOk = Update-Ledger
  Write-Host "$(Get-Date -Format T) all tasks finished"
}

Write-Host ''
Write-Host "Out folder : $OutDir (task_<name>.md, log_<name>.txt)"
foreach ($j in $jobs) {
  if ($DryRun) { $state = 'dry run' }
  elseif ($j.State -eq 'skipped') { $state = 'skipped' }
  else {
    $state = if ($j.Ok) { 'ok' } elseif ($j.RunOk) { 'FAILED (no report)' } elseif ($j.Result.Found) { "FAILED ($($j.Result.Subtype))" } else { "FAILED (exit $($j.Exit))" }
    $state = $state + $(if ($j.Fresh) { ', written' } else { ', NOT written' })
  }
  Write-Host ("{0,-26} {1,-24} {2}" -f $j.Name, $state, $j.Report)
}
Write-Host "Static     : $OutDir\_summary.md (and the tables the project's staticTables runs)"
if ($DryRun) {
  Write-Host 'Dry run: nothing was sent to the API, no cost table written.'
} else {
  Write-Host ("Cost       : {0} USD, {1} turns; ok {2}, failed {3}, skipped {4} -> {5}" -f (Format-Usd $tot.Cost), $tot.Turns, $tot.Ok, $tot.Bad, $tot.Skip, $costPath)
  if ($ledgerOk) { Write-Host 'Ledger     : the project cost ledger was updated (prk costs).' }
  else { Write-Host 'Ledger     : pending'; Write-Warning $T.ledgerPending }
  if ($final -and -not $final.Fresh) { Write-Warning "The merge did not write $mergedReport in this run: merge on the subscription (merge.md)." }
  $expandFailed = $false
  if ($Expand -and $final -and $final.Ok) {
    $ea = @{ From = $mergedReport; ProjectFile = $ProjectFile; Runner = $Runner; MaxTurns = $MaxTurns }
    if ($local._file) { $ea.LocalFile = $local._file }
    if ($Model) { $ea.Model = $Model }
    if ($Provider) { $ea.Provider = $Provider }
    if ($Subscription) { $ea.Subscription = $true }
    if ($mapFolder) { $ea.MapDir = $mapFolder }
    if ($hasRunId) { $ea.RunId = $RunId }
    try {
      & (Join-Path $PSScriptRoot 'expand_api.ps1') @ea
      $expandFailed = $LASTEXITCODE -ne 0
    } catch {
      $expandFailed = $true
      Write-Warning "Expansion could not run: $_"
    }
    if ($expandFailed) { Write-Warning "$($T.expandFailed) (log_expand_<RunId>.txt)." }
  } elseif ($Expand) {
    $expandFailed = $true
    Write-Warning '-Expand: no successful merged report from this run, so no expansion.'
  }
  # Say which tasks failed or were skipped, and let the exit code tell callers (0 = every task ok).
  $badJobs = @($jobs | Where-Object { -not $_.Ok })
  if ($badJobs.Count) {
    Write-Host ("NOT OK ({0} of {1}): " -f $badJobs.Count, $jobs.Count) -NoNewline
    Write-Host (($badJobs | ForEach-Object { if ($_.State -eq 'skipped') { "$($_.Name) (skipped)" } else { $_.Name } }) -join ', ')
    Write-Host 'Failed review reports that were still written are merged with a note; tasks without a report are left out of the merge. Read the logs named above.'
    exit 1
  }
  if ($expandFailed) { exit 1 }
}
exit 0
