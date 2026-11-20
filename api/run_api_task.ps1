# Runs one task file in a separate, headless Claude Code that is paid by an API key instead of a subscription.
# Nothing about a project or a computer is fixed in this script:
#   the project folder and its read-only / never-read paths come from the caller (player_review_api.ps1 reads them
#   from the project file); where Claude Code is and where the key is kept come from the machine settings (local.json).
# The key is read straight into this process's environment: never printed, never written to a log or a file.
#
#   -TaskFile   the task (UTF-8 Markdown) the headless run reads and follows
#   -LogFile    where the run's output goes; with -Json its last line is the CLI's result JSON
#   -WorkDir    the project folder the task works in (project file: projectRoot)
#   -ReadOnly   paths the task must not change, ';'-separated (project file: readOnlyPaths)
#   -NeverRead  paths the task must never read, list or search, ';'-separated (project file: neverRead).
#               The machine settings' neverRead and the folder of the key file are always added.
#   -LocalFile  machine settings (default: environment variable PLAYER_REVIEW_LOCAL, then <kit>\local.json)
#   -Model      passed to the CLI; not given = machine settings' defaultModel; neither = the CLI's own default
#   -AllowEdits lets the task change the -ReadOnly paths as the task file says (reviews never pass it)
#   -Json       the CLI prints one JSON result at the end (total_cost_usd, usage, num_turns, duration)
#   -Stream     every event as a JSON line (for diagnosing: which key source is used, API errors)
#   -Subscription  use the reviewer program's own login on this computer instead of an API key (prk pay sub):
#               Claude Code's login or Codex's ChatGPT login. Only for providers
#               with "signin": true in api\providers.json. No key is read, the session's variables and config folder are
#               left alone, and any API key variable already in the environment is removed for this run so it cannot be
#               billed by accident.
#   -Tools      the tools this run may use, ';'-separated (default: machine settings' allowedTools). The guide passes
#               Read;Grep;Glob: it only reads.
#   -Answer     the task file holds a question: print only the answer (the guide uses this)
# A string with ';' and not a string array: powershell.exe -File passes every argument as one plain string.
#
# Machine settings used here (all optional except a key source):
#   claudeExe       path of the Claude Code executable, or a folder to search for the newest claude.exe; empty = "claude" on PATH
#   apiKeyFile      a text file that holds the API key (only this script reads it), or
#   apiKeyEnv       the name of an environment variable that already holds the key
#   apiConfigDir    a config folder used only for these runs (default %LOCALAPPDATA%\PlayerReviewKit\claude-config)
#   isolateFromSession  true (default): drop the calling session's CLAUDE_* / ANTHROPIC_* variables first.
#                   Why: started from inside a desktop or IDE session, the child inherits that session's account
#                   variables and can be billed to that session's plan or credit instead of the API key's. With the
#                   variables dropped and its own config folder, the run can only use the key given here.
#   dropEnvPattern  regex of the variables to drop (default '^(CLAUDE_|CLAUDECODE$|ANTHROPIC_)')
#   defaultModel, allowedTools, neverRead
#   providers       per provider: where its key is and its settings (see -Provider)
#
#   -Provider   which model provider pays and answers (api\providers.json lists the known ones; the machine settings'
#               providers.<name> says where that provider's key is). Not given: machine settings' defaultProvider, else
#               "anthropic" with the top-level apiKeyFile / apiKeyEnv / defaultModel (how older settings were written).
#               kinds: anthropic (ANTHROPIC_API_KEY), compatible (ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN, the model id
#               also goes into ANTHROPIC_MODEL and the alias variables so every request of the run stays on that provider),
#               bedrock / vertex / foundry (Claude Code's own switches). The session isolation below applies to all of them.
param([Parameter(Mandatory)][string]$TaskFile, [Parameter(Mandatory)][string]$LogFile, [Parameter(Mandatory)][string]$WorkDir,
  [string]$ReadOnly = '', [string]$NeverRead = '', [string]$LocalFile = '', [string]$Model = '', [int]$MaxTurns = 200,
  [Alias('AllowModEdits')][switch]$AllowEdits, [switch]$Json, [switch]$Stream,
  [switch]$Subscription, [string]$Tools = '', [switch]$Answer, [string]$Provider = '')
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')
$kit = Split-Path $PSScriptRoot -Parent
$local = Read-Local $kit $LocalFile

$fmt = if ($Json) { @('--output-format', 'json') } else { @() }
if ($Stream) { $fmt = @('--output-format', 'stream-json', '--verbose') }
if (-not (Test-Path -LiteralPath $WorkDir)) { throw "WorkDir not found: $WorkDir" }
$WorkDir = (Resolve-Path -LiteralPath $WorkDir).Path
function Split-Paths([string]$s) { @($s -split ';' | ForEach-Object { $_.Trim().TrimEnd('\') } | Where-Object { $_ }) }

# Claude Code: a file, a folder to search (the version folder changes whenever the app updates), or PATH.
# (Read only when Claude Code is the reviewer; the other programs are found by engine_run.py.)
$exe = [Environment]::ExpandEnvironmentVariables([string](Get-Prop $local 'claudeExe' ''))
function Find-Claude {
  $exe = $script:exe

if ($exe -and (Test-Path -LiteralPath $exe -PathType Container)) {
  # Exact names only: -Include in Windows PowerShell 5.1 also let through ".verified" and ".payload" (small files next to
  # claude.exe in the app's version folders, written a second later), and the newest of those is not a program.
  # Order: claude.exe, then claude.cmd, then claude; the newest file of the first name found.
  $names = @('claude.exe', 'claude.cmd', 'claude')
  $all = @(Get-ChildItem -LiteralPath $exe -Recurse -Depth 4 -File -Filter 'claude*' -ErrorAction SilentlyContinue |
    Where-Object { $names -contains $_.Name.ToLowerInvariant() })
  $found = $null
  foreach ($n in $names) {
    $found = $all | Where-Object { $_.Name -ieq $n } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($found) { break }
  }
  if (-not $found) { throw "No Claude Code executable (claude.exe, claude.cmd or claude) under claudeExe folder: $exe" }
  $exe = $found.FullName
} elseif ($exe) {
  if (-not (Test-Path -LiteralPath $exe)) { throw "claudeExe not found: $exe" }
} else {
  $cmd = Get-Command claude -ErrorAction SilentlyContinue
  if (-not $cmd) { throw 'Claude Code not found: set claudeExe in the machine settings (local.json), or put "claude" on PATH.' }
  $exe = $cmd.Source
}
  return $exe
}

# The provider: the kit's catalog (api\providers.json) under the machine settings' own entry for it (key location, region ...).
if (-not $Provider) { $Provider = [string](Get-Prop $local 'defaultProvider' 'anthropic') }
$catalog = $null
$catFile = Join-Path $PSScriptRoot 'providers.json'
$providerData = if (Test-Path -LiteralPath $catFile) { (Read-Utf8 $catFile) | ConvertFrom-Json }
$catalog = Get-Prop $providerData 'providers' $null
$cat = Get-Prop $catalog $Provider $null
$mine = Get-Prop (Get-Prop $local 'providers' $null) $Provider $null
if (-not $cat -and -not $mine) { throw "Unknown provider: $Provider (api\providers.json, or providers.$Provider in the machine settings)" }
function Prov([string]$name, $default = '') { $v = Get-Prop $mine $name $null; if ($null -eq $v) { $v = Get-Prop $cat $name $default }; return $v }
$kind = [string](Prov 'kind' 'compatible')
$engine = [string](Prov 'engine' 'claude-code')   # which program is the reviewer: claude-code, codex (GPT), gemini
if ($Provider -eq 'anthropic' -and -not $mine) {
  # older machine settings: the anthropic key and model are written at the top level
  $mine = [pscustomobject]@{ apiKeyFile = (Get-Prop $local 'apiKeyFile' ''); apiKeyEnv = (Get-Prop $local 'apiKeyEnv' ''); model = (Get-Prop $local 'defaultModel' '') }
}
$blocked = Get-Prop (Get-Prop $providerData 'subscriptionUnsupported') $engine
if ($Subscription -and $blocked) {
  $texts = (Read-Utf8 (Join-Path $PSScriptRoot 'texts.json')) | ConvertFrom-Json
  throw (Get-Prop $texts $blocked)
}
if ($Subscription -and -not (Prov 'signin' $false)) {
  # a login of its own exists only for the providers marked signin (api\providers.json); every other one is paid by key
  throw "Provider $Provider has no sign-in of its own (api\providers.json: signin): it can only be paid by key. Leave out -Subscription, or use a provider with signin (anthropic, openai)."
}

# The key: from a file only this script reads, or from an environment variable (read before the variables are dropped).
$keyFile = [Environment]::ExpandEnvironmentVariables([string](Get-Prop $mine 'apiKeyFile' ''))
$keyEnv = [string](Get-Prop $mine 'apiKeyEnv' '')
$key = ''
if (-not $Subscription) {
  if ($keyFile) {
    if (-not (Test-Path -LiteralPath $keyFile)) { throw "apiKeyFile of provider $Provider not found: $keyFile" }
    $key = ([IO.File]::ReadAllText($keyFile)).Trim()
  } elseif ($keyEnv) {
    $key = [string][Environment]::GetEnvironmentVariable($keyEnv)
  }
  # the cloud platforms can sign in another way (an AWS profile, gcloud, az login); every other provider needs a key
  if (-not $key -and $kind -notin 'bedrock', 'vertex', 'foundry', 'google-vertex') {
    throw "No API key for provider ${Provider}: set providers.$Provider.apiKeyFile (a text file with the key) or apiKeyEnv (an environment variable name) in the machine settings (local.json)."
  }
  if ($kind -eq 'compatible' -and -not (Prov 'baseUrl' '')) { throw "Provider $Provider has no baseUrl (machine settings: providers.$Provider.baseUrl)." }
}

if ($engine -eq 'claude-code') { $exe = Find-Claude }
$roPaths = Split-Paths $ReadOnly
$stateDir = $env:PLAYER_REVIEW_STATE
if (-not $stateDir) {
  $stateBase = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { [IO.Path]::GetTempPath() }
  $stateDir = Join-Path $stateBase 'PlayerReviewKit'
}
$defaultConfigDir = Join-Path $stateDir 'claude-config'

$nrPaths = @(Split-Paths $NeverRead) + @(@(Get-Prop $local 'neverRead' @()) | ForEach-Object { ([string]$_).TrimEnd('\') } | Where-Object { $_ })
if ($keyFile) { $nrPaths += (Split-Path $keyFile -Parent) }
$nrPaths = @($nrPaths | Select-Object -Unique)

if ($Subscription) {
  # The login of this computer pays: keep its config folder and session, but make sure no API key can be picked up
  # (Claude Code's, and the ones Codex and Gemini CLI would use instead of their login).
  foreach ($n in 'ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'CODEX_API_KEY', 'OPENAI_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY') {
    Remove-Item "Env:$n" -ErrorAction SilentlyContinue
  }
} else {
  if ((Get-Prop $local 'isolateFromSession' $true) -ne $false) {
    $drop = [string](Get-Prop $local 'dropEnvPattern' '^(CLAUDE_|CLAUDECODE$|ANTHROPIC_)')
    Get-ChildItem Env: | Where-Object { $_.Name -match $drop } | ForEach-Object { Remove-Item "Env:$($_.Name)" -ErrorAction SilentlyContinue }
  }
  $cfg = [Environment]::ExpandEnvironmentVariables([string](Get-Prop $local 'apiConfigDir' $defaultConfigDir))
  $env:CLAUDE_CONFIG_DIR = $cfg
  New-Item -ItemType Directory -Force $cfg | Out-Null
}
if (-not $Model) { $Model = [string](Prov 'model' '') }
if (-not $Model -and $Provider -eq 'anthropic') { $Model = [string](Get-Prop $local 'defaultModel' '') }
$modelArgs = if ($Model) { @('--model', $Model) } else { @() }
$toolList = @(Get-Prop $local 'allowedTools' @('Read', 'Grep', 'Glob', 'Write', 'Edit', 'Bash', 'WebFetch', 'WebSearch'))
$toolArgs = @('--permission-mode', 'acceptEdits', '--allowedTools') + $toolList
$limitTools = $PSBoundParameters.ContainsKey('Tools')
if ($limitTools) {
  $toolList = @($Tools -split '[;,]' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
  if (-not $toolList.Count) { throw '-Tools requires at least one built-in tool.' }
  $toolArgs = @('--strict-mcp-config', '--tools') + $toolList
}

$roText = if ($roPaths.Count) {
  if ($AllowEdits) { "You may modify $($roPaths -join ', ') as the task file says. " } else { "Don't modify $($roPaths -join ', '). " }
} else { '' }
$nrText = if ($nrPaths.Count) { "Never read, list or search anything under $($nrPaths -join ', '). " } else { '' }
$prompt = "Read the task file $TaskFile (UTF-8) and do exactly what it says, working in $WorkDir. " + $nrText + $roText +
  "When finished, print a short summary in the delivery language requested in the task file: what you wrote where, the top points, and anything uncertain."
if ($Answer) {
  # No absolute path in this prompt: paths can hold the account name. The never-read folders are enforced by the deny rules below.
  $full = (Resolve-Path -LiteralPath $TaskFile).Path
  $rel = if ($full.StartsWith($WorkDir, [StringComparison]::OrdinalIgnoreCase)) { '.' + $full.Substring($WorkDir.Length) } else { $full }
  $prompt = "Read the task file $rel (UTF-8). It holds a question and how to answer it. Read only files inside the current folder. " +
    "Don't change any file and don't run anything. Print only the answer, in the delivery language requested in the task file."
}
# Read(...) deny rules cover every file-reading tool (Read, Grep, Glob); Bash rules match the folder's own name.
$deny = @()
if ($limitTools) { $deny += 'mcp__*' }
foreach ($p in $nrPaths) {
  $deny += "Read($($p.Replace('\', '/'))/**)"
  $deny += "Bash(*$(Split-Path $p -Leaf)*)"
}
$denyArgs = if ($deny.Count) { @('--disallowedTools') + $deny } else { @() }

$setVars = @()
function Set-RunEnv([string]$name, [string]$value) { if ($value) { Set-Item "Env:$name" $value; $script:setVars += $name } }
if (-not $Subscription) {
  switch ($kind) {
    'anthropic' { Set-RunEnv 'ANTHROPIC_API_KEY' $key }
    'compatible' {
      Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue   # in -p mode a set ANTHROPIC_API_KEY is always used
      Set-RunEnv 'ANTHROPIC_BASE_URL' ([string](Prov 'baseUrl' ''))
      Set-RunEnv 'ANTHROPIC_AUTH_TOKEN' $key
      # every request of the run (the main loop, the small helper calls, subagents) goes to this provider's models
      $small = [string](Prov 'smallModel' '')
      if (-not $small) { $small = $Model }
      foreach ($n in 'ANTHROPIC_MODEL', 'ANTHROPIC_DEFAULT_OPUS_MODEL', 'ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_FABLE_MODEL', 'CLAUDE_CODE_SUBAGENT_MODEL') { Set-RunEnv $n $Model }
      Set-RunEnv 'ANTHROPIC_DEFAULT_HAIKU_MODEL' $small
      Set-RunEnv 'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC' '1'
    }
    'bedrock' {
      Set-RunEnv 'CLAUDE_CODE_USE_BEDROCK' '1'
      Set-RunEnv 'AWS_REGION' ([string](Prov 'region' ''))
      Set-RunEnv 'AWS_PROFILE' ([string](Prov 'awsProfile' ''))
      Set-RunEnv 'AWS_BEARER_TOKEN_BEDROCK' $key
    }
    'vertex' {
      Set-RunEnv 'CLAUDE_CODE_USE_VERTEX' '1'
      Set-RunEnv 'CLOUD_ML_REGION' ([string](Prov 'region' ''))
      Set-RunEnv 'ANTHROPIC_VERTEX_PROJECT_ID' ([string](Prov 'projectId' ''))
      Set-RunEnv 'GOOGLE_APPLICATION_CREDENTIALS' ([Environment]::ExpandEnvironmentVariables([string](Prov 'credentialsFile' '')))
    }
    'foundry' {
      Set-RunEnv 'CLAUDE_CODE_USE_FOUNDRY' '1'
      Set-RunEnv 'ANTHROPIC_FOUNDRY_RESOURCE' ([string](Prov 'resource' ''))
      Set-RunEnv 'ANTHROPIC_FOUNDRY_BASE_URL' ([string](Prov 'baseUrl' ''))
      Set-RunEnv 'ANTHROPIC_FOUNDRY_API_KEY' $key
    }
    'openai' {
      Set-RunEnv 'CODEX_API_KEY' $key                           # codex exec takes a key per run from this variable
      $ch = Join-Path ([Environment]::ExpandEnvironmentVariables([string](Get-Prop $local 'apiConfigDir' $defaultConfigDir))) 'codex-home'
      New-Item -ItemType Directory -Force $ch | Out-Null
      Set-RunEnv 'CODEX_HOME' $ch                               # a clean home: no stored ChatGPT login, no user config
      foreach ($n in 'OPENAI_API_KEY') { Remove-Item "Env:$n" -ErrorAction SilentlyContinue }
    }
    'google' {
      Set-RunEnv 'GEMINI_API_KEY' $key
      foreach ($n in 'GOOGLE_API_KEY', 'GOOGLE_CLOUD_PROJECT', 'GOOGLE_APPLICATION_CREDENTIALS') { Remove-Item "Env:$n" -ErrorAction SilentlyContinue }
    }
    'google-vertex' {
      Set-RunEnv 'GOOGLE_CLOUD_PROJECT' ([string](Prov 'projectId' ''))
      Set-RunEnv 'GOOGLE_CLOUD_LOCATION' ([string](Prov 'region' ''))
      Set-RunEnv 'GOOGLE_APPLICATION_CREDENTIALS' ([Environment]::ExpandEnvironmentVariables([string](Prov 'credentialsFile' '')))
      foreach ($n in 'GEMINI_API_KEY', 'GOOGLE_API_KEY') { Remove-Item "Env:$n" -ErrorAction SilentlyContinue }
    }
    default { throw "Provider $Provider has an unknown kind: $kind" }
  }
  # extra variables the provider's own page recommends (api\providers.json env, then the machine settings' env)
  foreach ($src in @((Get-Prop $cat 'env' $null), (Get-Prop $mine 'env' $null))) {
    if ($src) { foreach ($p in $src.PSObject.Properties) { Set-RunEnv $p.Name ([string]$p.Value) } }
  }
}
$key = $null
Set-Location -LiteralPath $WorkDir
"started $(Get-Date -Format s), model $(if ($Model) { $Model } else { '(cli default)' }), workdir $WorkDir, paid by $(if ($Subscription) { 'subscription login' } elseif ($kind -eq 'anthropic') { 'api key' } else { 'provider account' }), provider $(if ($Subscription) { 'subscription' } else { $Provider })" | Out-File $LogFile -Encoding utf8
if ($engine -ne 'claude-code') {
  # Another program is the reviewer. It cannot be told "never read these folders" the way Claude Code is (deny rules):
  # only by the prompt. So it runs only when the machine settings say that is acceptable for this provider.
  if ($nrPaths.Count -and -not (Prov 'promptOnlyNeverRead' $false)) {
    throw ("Provider $Provider runs $engine, which can only be ASKED not to read: " + ($nrPaths -join ', ') +
      ". If that is acceptable, set providers.$Provider.promptOnlyNeverRead = true in the machine settings (prk provider setup $Provider asks).")
  }
  $paid = if ($Subscription) { 'subscription login' } else { 'api key' }
  $ea = @('-I', (Join-Path $PSScriptRoot 'engine_run.py'), '--engine', $engine, '--task', $TaskFile, '--log', $LogFile, '--workdir', $WorkDir,
    '--max-turns', "$MaxTurns", '--paid', $paid, '--provider', $(if ($Subscription) { 'subscription' } else { $Provider }),
    '--never-read', ($nrPaths -join ';'), '--read-only', ($roPaths -join ';'))
  if ($Model) { $ea += @('--model', $Model) }
  if ($Answer) { $ea += '--answer' }
  $ex = [Environment]::ExpandEnvironmentVariables([string](Get-Prop $local ($engine + 'Exe') ''))
  if ($ex) { $ea += @('--exe', $ex) }
  $code = 0
  try {
    & (Get-Python $local $null) @ea
    $code = $LASTEXITCODE
  } finally {
    foreach ($n in $setVars) { Remove-Item "Env:$n" -ErrorAction SilentlyContinue }
  }
  if ($Json -or $Answer) { exit $code }
  exit $code
}
$ErrorActionPreference = 'Continue'   # PowerShell 5.1 turns the CLI's stderr lines into errors otherwise
# The CLI writes UTF-8. PowerShell 5.1 decodes a program's output with the console's code page (936 on a Chinese
# Windows), which garbled every non-ASCII character in the log and broke the result JSON at the end (the answer
# and the cost could not be read). Decode as UTF-8 for this call; without a console the setter can fail: then as before.
$oldOut = $null
try { $oldOut = [Console]::OutputEncoding; [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false } catch { }
try {
  & $exe -p $prompt @modelArgs --max-turns $MaxTurns @fmt @toolArgs @denyArgs 2>&1 | ForEach-Object { "$_" } |
    Out-File $LogFile -Append -Encoding utf8
  $code = $LASTEXITCODE
  "finished $(Get-Date -Format s), exit $code" | Out-File $LogFile -Append -Encoding utf8
} finally {
  if ($oldOut) { try { [Console]::OutputEncoding = $oldOut } catch { } }
  foreach ($n in $setVars) { Remove-Item "Env:$n" -ErrorAction SilentlyContinue }
}
exit $code
