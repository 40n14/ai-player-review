# Command and file reference

Follow the [playbook](PLAYBOOK.md) for each review. Use this reference to look up options, output fields, and files.

## Running commands

```text
python -I prk.py <command> [args]
```

Run commands from the toolkit's root folder. On Windows, use `prk`, or use `.\prk.cmd` if PowerShell cannot find it. Replace `P` with the path to the project settings JSON and `R` with the round's folder name or path.

- For project commands, pass `-p "P"` or `--project "P"`. You can omit it if `projects\` contains only one project settings file.
- To use machine settings, pass `--local "<local.json>"` or set `PLAYER_REVIEW_LOCAL`. For relative paths, use the base folder specified by the settings file or command. Paths in project settings are relative to that file's folder.
- Add `--json` to supported commands to read structured results. Normal output is a single JSON value on stdout. Check the error message if usage or the environment causes a failure. JSON field names are independent of the project language. Plain-text CLI messages can be in Chinese.
- Exit code `0` means success. Code `1` means the command ran but found a problem, such as a failed task or missing report. Code `2` means a usage or environment error. See the details below.

## Commands

| Command | Extra cost or allowance? | What to do or look for |
|---|---|---|
| `prk new --fields --json` | No | Read `fields`. Each has `key`, `label`, `required`, `help`, and `example`. The optional `language` field defaults to `zh`. |
| `prk new --from-json "<answers.json>" --json` | No | Create project settings from the answers. On success, read `ok` and `file`. On failure, it exits 2 without creating a file. Check `key` and `message` in `errors`. |
| `prk new` | No | Create project settings interactively with the owner. See also `projects\_template.json`. |
| `prk local` | No | Have the owner configure this machine interactively by entering key file locations only. |
| `prk install -p "P"` | No | Optional Claude Code setup. See the [setup instructions](INSTALL.md). |
| `prk check -p "P" --json` | No | Read `ok`, `problems`, and `language`. Resolve any settings problems first. |
| `prk static -p "P"` | No | Run static checks on their own. Look for `_summary.md` in `staticOutDir` by default. |
| `prk groups -p "P" --json` | No | List review groups and `defaultGroups` for the project. |
| `prk kinds --json` | No | List review methods and their IDs. |
| `prk personas --json` | No | List player personas and IDs. Add `--find "<term>"` to search. |
| `prk suggest "<genre>" --json` | No | Suggest personas for a game genre. |
| `prk presets --json` | No | List persona presets. Put the IDs you want in the project setting `presets`. |
| `prk guide -p "P" --json` | No | Check `title`, `detail`, `cmd`, `costs`, and the legacy interface's `view` in each `next` entry. Also check the project's `language`. |
| `prk plan -p "P" --groups A,B --split --json` | No | Dry run. Read the number of `tasks`, `groups`, and `estimate.text.api` or `estimate.text.sub`. |
| `prk prepare -p "P" --groups A,B --split --json` | No | Create a round, run static checks, and write task files. Read `stages`, `static`, and `language`. |
| `prk run -p "P" --groups A,B --split --parallel 4 --pay sub --yes` | Yes | Run the same round in the background after the owner approves. See the round cost report for tasks and totals. |
| `prk quick "15 + 18" -p "P" --kind wants --pay sub --yes` | Yes | Review one type of player in the background. This is one task. Use persona IDs. `--kind` defaults to `persona`. |
| `prk fake -p "P" --groups A,B --split` | No | Check queuing and merging with a fake runner. Reports and costs are sample data. |
| `prk reports -p "P" --json` | No | Read `reviewOutDir` and the round directories, reports, merged reports, cost report paths in `cost`, and maps in `reviews`. |
| `prk feedback -p "P" --json` | No | Read player feedback and entries. Pass a round folder or use `--from "<report.md>"`. Use `--full` for the whole report and `--save "<path>"` to save it elsewhere. |
| `prk cite -p "P"` | No | Verify quotes and line numbers. To check an earlier round, pass its folder path. |
| `prk page -p "P" --round "R" --json` | No | Verify sources and write `review.md` and `review.html` in the project `language`. Add `--open` to open the page. |
| `prk decide -p "P"` | No | Let the owner decide each item in the terminal. Use `--set` to record decisions already made. |
| `prk fix -p "P" --json` | Free to read the list. Background fixes cost extra. | Read the list, hand an item to the owner's AI, run a fix, undo it, or update its status. See below. |
| `prk expand -p "P" --from "<merged-report.md>" --items W1,W3 --pay sub --yes` | Yes | Write a content proposal for selected items. Ask for approval first. The game stays read-only. |
| `prk cost -p "P"` | No | Read the latest round with a cost report. You can pass another round's folder path. |
| `prk costs -p "P" --json` | No | Read costs across rounds, this month's usage, and the budget. |
| `prk pay --json` | No | Check payment methods for background reviews and the AI help guide. |
| `prk provider --json` | No | Check providers and their configuration status. |
| `prk model --json` | No | Check the current model, where it comes from, and available choices. |
| `prk guide "<question>" -p "P" --pay sub --yes --json` | Yes | Ask the AI help guide after getting approval. Keep real project material out of the question. |
| `prk ui -p "P"` | Free to open | Open the optional legacy interface. See the last section. |
| `prk ask -p "P"` | No | Show the older Claude Code chat workflow. Use the [playbook](PLAYBOOK.md) for regular reviews. |

The paid command examples use `sub`. Use the payment method the owner chose. Run `prk --help` when troubleshooting manually.

## Project language

Set `"language": "zh"` or `"language": "en"` in the project settings. The default is `zh`. `prk new --fields` lists this optional setting, and `prk check` reports invalid values. The commands `check --json`, `guide --json`, `prepare --json`, and `page --json` all return `language`. Reports, the one-page summary, the offline page, the fix list, decision records, cost records, and review conversations use the project language. The Chinese personas, review methods, agent instructions, and task templates are the source material.

For report headings, labels, and index columns, see the [bilingual report format](../../docs/report-format.md). IDs S, M, L, D, W, and F are the same in both languages. Commands and scripts that read reports, including `feedback`, `cite`, `page`, `decide`, `fix`, `score.py`, and `next_steps`, accept both formats regardless of the project language.

## Preparing tasks and generating the page

Each review group combines a review method with player personas and is defined in `reviewGroups`. Methods are registered in `kinds\kinds.json`, and the persona index is `method\画像_索引.md`. If a task calls for personas, read the base materials, presets in `presets`, and the project overlay `personaOverlay` in the order given in the task. Later layers take precedence.

### `prepare`

```text
prk prepare [-p P] [--groups A,B] [--split] [--scope TEXT] [--no-map] [--map-dir DIR] [--no-merge]
            [--who "15 + 18" [--kind KIND_ID]] [--json]
```

Options work as in `plan` or `quick`. Omit `--groups` to use the defaults. Use `--split` to split groups as set in the project, `--scope` to describe the review scope, `--no-map` to skip mapping, `--map-dir` to use an existing map directory, and `--no-merge` to skip merging. `--who` creates just one task for one type of player and skips mapping and merging.

The command creates a round under `reviewOutDir`, runs static checks, and writes task files and `_prepared.json`. It makes no AI calls and writes no cost report.

- `ok`, `round`, `dir`, and `count` give the result, round folder name, absolute path, and task count.
- `language` gives the project language for this round's deliverables.
- `stages` lists the stages in order. Each has `stage` and `tasks`. Each task has `name`, `kind`, `task`, and `writes`. The last two are absolute paths to the task file and main output. Tasks in the same stage can run in parallel. Mapping, review, and merge stages depend on the selected options.
- `static.ok` and `static.summary` give the static check result and where to find the summary. If a static check fails, the command exits 1 and still writes the task files.
- On the first review, `next` in `guide --json` points to `prk prepare`. Background-only steps have `optional: true`.
- If the latest round has `_prepared.json` and unfinished tasks, `next` in `guide --json` lists those task files. If reports are complete and the page is missing or older than the reports, it points to `prk page`.

### `page`

```text
prk page [-p P] [--round R] [--open] [--json]
```

The command verifies citations and writes `review.md` and `review.html`. The HTML is a single offline file. Double-click it, or add `--open` to use the default browser. The latest round is the default. If the project has no rounds and defines `sampleRound`, the command uses the read-only sample and writes the page to the toolkit's state directory.

- `ok`, `round`, and `dir` give the result and selected round. `html` and `md` are the paths to hand to the owner.
- `language` gives the project language used for the page and one-page summary.
- In `counts`, `S`, `M`, `L`, `D`, and `W` count Severe, Medium, Minor, Needs your decision, and Wanted but missing items. `undecided` counts items with no recorded decision.
- `missing` lists reports that `_prepared.json` or the round cost report expects but that were never written. If both files are absent, it is an empty array. `citationsBad` counts sources that did not match, or is `null` if verification failed.

## State directory

The state directory defaults to `%LOCALAPPDATA%\PlayerReviewKit`. Set `PLAYER_REVIEW_STATE` to choose a different directory. If it is unwritable, commands that need to write state use `PlayerReviewKit` in the system temporary directory. In `--json` output, `state.dir` is the actual location and `state.temporary` says whether it is temporary. Lists of personas, methods, and group suggestions still return arrays.

## Record decisions

```powershell
prk decide -p "P" --round "R" --set "S1=修; S2=放进待做: 等下个版本; W1=是设计" --json
prk decide -p "P" --round "R" --set "S1=fix; S2=later: next version; W1=by-design" --json
```

Use `--from "<report.md>"` to specify a report. Get the round from the owner's pasted decisions. These are two examples of the same input. Pick one and fill in the actual decisions. Separate items with semicolons and place any reason after a colon. When the page copies decisions, it replaces ASCII semicolons in reasons. Both sets of terms are accepted as input, and English terms are case-insensitive. Records use the project language, and both sets of terms can be read from them.

| Chinese decision | English | Chinese page button | English page button |
|---|---|---|---|
| `修` | `fix` | 要修 | Fix |
| `放进待做` | `later` | 以后再说 | Later |
| `是设计` | `by-design` | 本来就这样 | By design |
| `不是问题` | `not-an-issue` | 不是问题 | Not an issue |
| `误报` | `false-positive` | AI 看错了 | AI got it wrong |

Record only decisions from the owner. If an ID is missing from the round's report or a decision term is unknown, the command exits 2 and writes none of the batch. On success, check `ok`, `recorded` (each entry's `id`, `decision`, and `why`), `fixAdded`, and `file`. Recording the same item again updates its decision. Decisions go into `决定记录.csv` or `decisions.csv`. Choosing `fix` (修) adds the item to the fix list. Run `page` for the same round after recording.

## Payment

- `sub` uses the subscription of the account signed in on this machine. `api` uses a key and bills by usage. Check `pay`, `guidePay`, `payGuideSeparate`, and `problem` in `prk pay --json`.
- `run`, `quick`, `expand`, background `fix F3`, and `guide` with a question use extra allowance or cost money. Report the task count and any available estimate first. Use `plan` for a whole round and count the actual tasks for other actions. Add `--yes` to a non-interactive call only after the owner agrees.
- A non-interactive paid command exits 2 if no payment method has been chosen. Tell the owner what happened and ask them to choose subscription or pay-as-you-go. `--pay sub` or `--pay api` overrides the method for the current call only. Save a preference with `prk pay sub` or `prk pay api` only when the owner asks.
- The AI help guide can have its own payment setting. Use `prk pay guide sub` or `prk pay guide api`. Use `prk pay guide same` to share the review setting.
- The toolkit supports subscription billing for `anthropic` and `openai`. It uses pay-as-you-go for Gemini CLI. If the provider does not support the selected `sub` method, the command exits 2. Ask the owner to choose the provider or payment method.
- `plan` estimates from the cost ledger. Check `estimate.text.api` or `estimate.text.sub`. Say when there is no estimate because the model has no run history.

## Providers and models

`prk provider --json` lists `providers` and the current provider. For each provider, `configured` says whether the current payment method is configured. `keyReady` says whether the key path is set. `signin` and `signinReady` show whether the provider supports subscription sign-in and whether it is ready on this machine. `openai` uses Codex CLI, and `google` uses Gemini CLI. Both follow the same report and log formats.

Use `prk model --json` to read `model`, `source`, and `choices`. Save a provider or model with `prk provider <name>` or `prk model <id>` only when the owner says to. `prk model default` clears the saved model. For a one-time override, add `--provider <name>` or `--model <id>`.

If a provider needs setup, ask the owner to run `prk provider setup <name>` or use the provider settings in the legacy interface (设置 → 用哪家的 AI). The toolkit reads any key files it needs. Do not open, print, or copy them or read any `neverRead` path.

## Fix list

`<reviewOutDir>\待修清单.md` or `<reviewOutDir>\fix-list.md` uses IDs such as F1 and F2. IDs are never reused. Read the instructions for AI at the top and the entry details. Each entry in `items` from `prk fix -p "P" --json` has `id`, `title`, `severity`, `done`, `body`, `filled` (the completed fix details), `copy`, and `canUndo`. The command also returns `todo`, `copyAll`, and `file`.

- **Fix in the owner's chat.** After the owner explicitly names F3, follow the list and the game's rules and fix only F3. Mark it `[x]` and fill in the fix details. Use the project's version control to undo changes made this way. You can give the owner F3's `copy` text for another chat.
- **Send a fix to Claude Code in the background.** The provider must have `engine` set to `claude-code`. Other providers exit 2. Tell the owner it will cost money or allowance, the background agent did not see this chat, and the toolkit can restore backups of the files named in the sources. Wait for approval of that item before running `prk fix F3 -p "P" --pay sub --yes --json`. `ok` means the item was checked off. If it was not, the command exits 1. Read the log tail in `tail`.
- **Undo.** When asked, run `prk fix F3 -p "P" --undo --json`. In `_修之前\` or `_before-fix\`, `manifest.json` records the originals and the copies in `files\`. If restoration fails, name the files that were not restored. Resolve the cause and retry the same item to restore just the failed files. Reopen the item after restoring everything the toolkit can restore. Hand files in `noBackup` back to the owner.
- **Change status.** If the owner says F3 is fixed, use `prk fix F3 -p "P" --done --json`. If they want it reopened, use `prk fix F3 -p "P" --reopen --json`.

## Fields in `feedback --json`

| Field | What it means |
|---|---|
| `ok`, `dir` | Whether it found results and which round it read |
| `reports`, `merged` | Which reports it read. If a merged report exists, it reads only that report. Otherwise, group reports can contain duplicates. |
| `counts` | `S`, `M`, `L`, `D`, and `W` count Severe, Medium, Minor, Needs your decision, and Wanted but missing items |
| `conclusion` | Original “Conclusion” (结论) text |
| `feedback` | Each `player` has `says`. Each statement includes `kind`, `text`, and `refs` for feedback type, text, and referenced IDs. |
| `feedbackMarkdown` | Original “Player feedback” (玩家反馈) text. Read it if structured parsing is incomplete. |
| `lastRound` | Original “Follow-up on last round” (上一轮反馈的去向) text. Usually empty in the first round. |
| `entries` | Each item's `id`, `title`, `confidence`, and `report`. Look up the ID in the report for details and sources. |

If both feedback fields are empty, flag the missing “Player feedback” (玩家反馈) section and use `entries`. Say what still needs checking for items marked 【可能】 or [Possible].

## File locations

A round normally lives under `<reviewOutDir>\<YYYYMMDD_HHMMSS>\`. Use the project setting `reportNames` for custom report names and the table below for defaults. For `sampleRound` output paths, use the paths returned by `page --json`.

| Chinese project | English project | What it contains |
|---|---|---|
| `玩家视角审查_合并.md`, `玩家视角审查_<组>.md` | `player-review_merged.md`, `player-review_<group>.md` | Merged and group reports, with player feedback, conclusion, issues, missing options, decisions, and index |
| `….草稿.md` | `….draft.md` | Paths reviewed and candidate findings, useful for spotting gaps |
| `内容拓展提案.md` | `content-proposal.md` | Latest successful content proposal |
| `内容拓展提案_<RunId>.md` | English proposal name with `_<RunId>` | Proposal for an individual run. Custom filenames also include the run ID. |
| `决定记录.csv` | `decisions.csv` | Decisions at the root of the project output directory |
| `待修清单.md` | `fix-list.md` | Fix list at the root of the project output directory |
| `花费记录.csv` | `cost-ledger.csv` | Cost ledger across rounds at the root of the project output directory |
| `_修之前\`, `_修\` | `_before-fix\`, `_fix\` | Pre-fix backups, fix tasks, and logs at the root of the project output directory |

Programs accept both forms of each filename. If both exist, they prefer the project language's name and report the duplicate in `--json`.

| Filenames for either language | What it contains |
|---|---|
| `_prepared.json` | In-chat round task list for resuming work and checking for missing outputs |
| `review.md`, `review.html` | The one-page summary and offline page for the owner |
| `_map\` | Game map with routes, choices, states, items, endings, text, values, and dependencies |
| `_summary.md`, `_text_checks.md`, `_image_hits.md` | Static summary, text checks, and clickable areas for configured images |
| `_citations*.md` | Citation verification results |
| `task_*.md`, `log_*.txt` | Full task inputs and background logs, including `task_expand_<RunId>.md` and `log_expand_<RunId>.txt` |
| `_运行记录.txt` | Output from runs started in the legacy interface |

The round cost report records progress and cost for each background task. Its Chinese name is `_花费.md`. Use the round's `cost` from `reports --json` to find it. [Report format and filenames](../../docs/report-format.md)

Verification scripts and assistants read the report's “Index” (索引). Its English columns are ID, Severity, Confidence, File:line, and Quote. Mark any report without an index incomplete. [Report format](../../docs/report-format.md)

## Cost ledger

`花费记录.csv` or `cost-ledger.csv` records one row per background task across rounds. In `prk costs -p "P" --json`, read `month.usd` for this month's pay-as-you-go costs in dollars, `month.budget` for the monthly budget, and `month.subTokens` for subscription tokens used. `summary` groups spending by model, task category, payment method, day, and round. `rows` lists individual tasks.

Use the numbers actually recorded. Use the round cost report for the total. In-chat usage and remaining subscription allowance are outside these records. Use `prk costs -p "P" --rebuild` to rebuild the ledger from rounds. If requested, use `prk costs --budget 20` to set a budget in dollars or `prk costs --budget 0` to turn it off. The budget only provides a reminder. Tell the owner when it is close or exceeded.

## Optional legacy interface

`prk ui -p "P"` starts a local background service. If you built the launcher, you can also double-click `玩家视角审查.exe`. This interface is retained, and new page features use `prk page`. Use `reports` to find runs started from the legacy interface. Follow `_运行记录.txt` and the round cost report, then use `feedback --json` for the results.

When starting a run, writing a proposal, or starting a fix through the legacy interface, pass the page's `confirmation` back unchanged. For undo, mark done, and reopen, pass the entry's `actionBinding` as the request's `confirmation`. Starting a run or writing a proposal verifies the settings path and fingerprint, task list, provider, model, payment method, and options. A proposal also checks the merged report. Fix list actions check the round and entry. If you receive `changed`, refresh and ask the owner to confirm again.
