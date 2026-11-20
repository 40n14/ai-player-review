# Run a review

Read the [English section of AGENTS.md](../../AGENTS.md#english) first. Replace `P` with the project settings path and `R` with the round. Run commands from the toolkit's root folder. In Windows PowerShell, you can use `.\prk.cmd` or replace `prk` with `python -I prk.py`. For machine settings, payment methods, and options, see the [command reference](REFERENCE.md).

Use the project setting `language` for deliverables and review conversations. The default is Chinese. Read the Chinese personas, review methods, agent instructions, and task templates. Reviewers, mergers, and checkers write in the project language. Use the headings and labels in the [report format](../../docs/report-format.md). The IDs S, M, L, D, W, and F are the same in both languages. See the [file table](REFERENCE.md#file-locations) for filenames.

## 1. Check where things stand

```powershell
prk guide -p "P" --json
prk reports -p "P" --json
prk check -p "P" --json
```

Read `next` from `guide` and confirm the round with `reviews` from `reports`. If `reviewOutDir` contains `决定记录.csv` or `decisions.csv`, handle this as a follow-up. `check` returns the project's `language`. Tell the owner about any entries in `problems` and address them before proceeding. If the reports are ready and the page is missing or outdated, go to step 5.

Tell the owner whether this is the first round, which round you are resuming, or whether only the page is left. If `_prepared.json` exists and tasks are unfinished, use that task list and skip completed tasks. If the owner already started background jobs from the legacy interface, find the round with `reports`. Follow `_运行记录.txt` and the round cost report at `cost`. Start each round only once.

## 2. Choose the scope and review groups

```powershell
prk groups -p "P" --json
```

Start with `defaultGroups`. If the owner names groups or a scope, use those with `--groups` and `--scope`. For a small change, choose groups that cover the changes, related areas, and items to verify from the last round. A smaller set is usually enough. Ask if the scope is unclear. Pass the scope for this round as a command option.

In each group, `kind` is the review method and `personas` lists persona IDs. To hear from one type of player, use `prk prepare -p "P" --who "15 + 18" --kind wants --json`. This creates one task and skips mapping and merging. Without `--kind`, it uses `persona`.

## 3. Choose how to run and report the task count

**Work in the current chat by default.** This uses the owner's current session allowance. `prepare` itself makes no AI calls. Dry-run the same scope, splitting, and map options. Count the entries in `tasks` and tell the owner the total and which groups will run. If there are many tasks, for example more than six, ask if they want fewer groups. With `--who`, report one task.

```powershell
prk plan -p "P" --groups A,B --scope "<scope>" --split --json
```

If the dry run fails only because of background payment or provider settings, use `prepare` in step 4 and read `count`. Report the count before starting the tasks.

**Use background jobs if the owner wants them or there are many tasks.** Run `plan` with the same scope and options. Report the number of `tasks`, the `groups`, and the estimate in `estimate.text` for the chosen payment method. Say if no estimate is available. Wait for the owner to approve the tasks and payment method before starting. This example uses `sub`.

```powershell
prk run -p "P" --groups A,B --scope "<scope>" --split --parallel 4 --pay sub --yes
```

Wait for the jobs to finish, then go to step 5. Use the round cost report for the total. To run one type of player in the background, use `quick`. Report the scope, one task, and any available estimate, then wait for approval.

## 4. Do the tasks in chat

```powershell
prk prepare -p "P" --groups A,B --scope "<scope>" --split --json
```

Use the scope from step 2. Omit `--groups` to use the defaults and omit `--split` if you are keeping the groups together. Check `round`, `count`, `static.ok`, and `stages`. If a static check failed, read `static.summary` and tell the owner which check failed and which tasks it affects.

Follow `stages` in order. For each task, read the entire `task` file and follow its steps, scope, and output requirements. Write the main result to `writes` and put drafts and other files where the task specifies. Work read-only on the game. Keep it closed and skip builds and tests. After each task, confirm that its output exists.

- If your tool can delegate, send all tasks in the current stage together. Wait for them before moving on. Give each subagent this instruction. “Read the entire file at the full `task` path and follow it. Treat the game as read-only. Write only the files listed in the task, including the main output at the full `writes` path. Report the result and any unfinished work in five lines or fewer.”
- In Claude Code, use the appropriate agent type if types such as `player-bug-reviewer` are installed. Otherwise, use general-purpose subagents.
- If your tool cannot delegate, do the tasks one at a time. Write the current output before reading the next task file in full. Carry forward only the inputs named by the next task. When merging requires a cross-check, use the claims in the task to check the original files and say that this round had no independent checker. Keep [Possible] on items with insufficient evidence.
- **Before merging** (tasks with `kind` set to `merge`), run `prk cite -p "P" "<round folder>"`. It is free and takes a few seconds. It checks the sources in each earlier report and writes `_citations.md` for the merge task. If it fails, tell the owner. The merge task will check the original files directly.
- Mark a subagent's task unfinished if it has yet to return or write its output. Follow the task instructions for missing inputs. Pause a dependent task if it cannot proceed and tell the owner what is missing.

## 5. Generate the page

```powershell
prk page -p "P" --round "R" --json
```

Check `ok`, `html`, `md`, `counts`, `missing`, and `citationsBad`. List any reports in `missing`. If `citationsBad` is greater than zero, report the count and tell the owner to hold off on using those items. Say if the citation check failed. Add `--open` to open the page in the default browser. If generation fails, report the error and which files exist.

## 6. Deliver the results

Use five lines or fewer in chat. Lead with what several types of players would say. Then mention anything only one type raised that has a serious impact. Stick to what the reports support and say what still needs checking for items marked 【可能】 or [Possible]. Include any missing outputs or verification issues. Use `counts` for numbers, give the `html` path, and remind the owner to choose decisions on the page and click **Copy for AI** (复制给 AI).

## 7. Record the owner's decisions

The Chinese page copies this format.

```text
请把这些决定记进决定记录（轮次 20261119_153000）：
S1 = 修
S2 = 放进待做（原因：等下个版本）
W1 = 是设计
```

The English page copies this format.

```text
Please record these decisions (round 20261119_153000):
S1 = fix
S2 = later (reason: next version)
W1 = by-design
```

Pass the round and decisions to `prk decide --set`. The two `decide` lines show alternative inputs. Use one based on what the owner pasted, then refresh the page.

```powershell
prk decide -p "P" --round 20261119_153000 --set "S1=修; S2=放进待做: 等下个版本; W1=是设计" --json
prk decide -p "P" --round 20261119_153000 --set "S1=fix; S2=later: next version; W1=by-design" --json
prk page -p "P" --round 20261119_153000 --json
```

Check `recorded` and `fixAdded` before refreshing, then give the owner the updated page for the same round. Follow the same steps for decisions given directly in chat. Record only what the owner decided. Confirm unclear IDs or rounds first. If you need to ask, group the choices with a multiple-choice tool if available. Otherwise, list the IDs and options for the owner to reply. Both sets of decision words are accepted. Records use the project language. [Decision terms](REFERENCE.md#record-decisions)

## 8. Fix only the named item

When the owner explicitly says “fix F3,” run `prk fix -p "P" --json` to find `file` (`待修清单.md` or `fix-list.md`). Read the instructions for AI at the top and the F3 entry. Follow the game's rules and fix only F3. After verifying, mark it `[x]`, fill in the fix details, and tell the owner what changed and how you checked it. Give the owner the entry's `copy` text if they want to hand it to another chat. For payment and undoing background fixes, see the [fix list](REFERENCE.md#fix-list).

## 9. Review again after changes

Go back to step 1. New tasks include the decision record so reviewers can check the items marked for fixing last round first. Include this round's changes and related areas in scope. Use the report's “Follow-up on last round” (上一轮反馈的去向) to tell the owner what is resolved and what remains.

## 10. Optional content proposal

Once the owner picks “Wanted but missing” items, report that this takes one task and explain how it will be paid for. Wait for approval. This example uses `sub`. Pass the merged report from that round to `--from`. The proposal contains suggestions and drafts and leaves the game untouched.

```powershell
prk expand -p "P" --from "<merged-report.md>" --items W1,W3 --pay sub --yes
```

Read the proposal and its task cost. Give the owner the proposal path and cost.

## Troubleshooting

- **Exit code 2.** Read the command error or the JSON `error` or `errors`. Check the options, paths, and environment. If a background command has a payment issue, ask the owner to choose how to pay.
- **`prepare` fails or a task file is unreadable.** Check the error, round, `task` path, and permissions. Tell the owner what is blocking the review and what they need to do. Check the game manually only if they ask you to. When reporting back, label it a manual check and explain that the task files, static checks, and citation verification are missing and the formal review is unfinished.
- **Report sections are missing.** Say if “Player feedback” (玩家反馈) or “Index” (索引) is missing. Deliver the output available from `feedback` and `page`.
- **A background job fails.** Read the round cost report and the end of the matching `log_*.txt`. If the error mentions something like `Credit balance`, stop and ask the owner to check billing.
- **Python or PowerShell is missing.** Static checks and report pages require Python. `prepare` and `run` require PowerShell. Use the [setup instructions](INSTALL.md#1-check-the-environment) to explain what can still run.
