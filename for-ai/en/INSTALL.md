# First-time setup

Run these commands from the toolkit's root folder. On Windows, use `prk`, or use `.\prk.cmd` if PowerShell cannot find it. You can also replace `prk` with `python -I prk.py`. Replace the placeholders in angle brackets with real values and quote paths.

## 1. Check the environment

Run `python --version`. You need Python 3.8 or later. If you use the Windows Python launcher, run `py -3 --version`. If Python is unavailable, ask the owner to install it. Static checks and report pages require Python. If the owner specifically requests a manual check, follow the [playbook's troubleshooting steps](PLAYBOOK.md#troubleshooting).

PowerShell comes with Windows. In PowerShell, check `$PSVersionTable.PSVersion`. You can also look for `powershell` or `pwsh` first. If neither is available, tell the owner that `prepare` and `run` require PowerShell and that the toolkit has only been tested on Windows. Commands such as `check` and `static` still work with Python.

The state directory defaults to `%LOCALAPPDATA%\PlayerReviewKit`. You can set `PLAYER_REVIEW_STATE` to use a different location. If that location is unwritable, the toolkit stores temporary state in `PlayerReviewKit` inside the system temporary directory. Read-only commands still work. The `state` object in `--json` output gives the actual location and says whether it is temporary.

## 2. Create the project settings

```powershell
prk new --fields --json
```

Read `fields`. Use each field's `label` and `help` to ask the owner all the necessary questions at once. Use `required` to identify mandatory fields and `example` to explain what to enter. Ask for the game folder, where to save reports, and which materials the assistant may read, as specified by the fields. If the project already has a settings file, go straight to checking it.

During setup, ask whether the owner wants the review in Chinese or English. Set `language` to `zh` or `en`. The field is optional and defaults to `zh`. Use `en` if the owner chooses English or has been speaking English throughout and has not chosen another language. Use the project language for review deliverables and conversations.

If the owner asks you to decide or is unavailable, fill in what you can tell from the project, such as where the game is and where to put reports. Ask about required fields you cannot infer. After setup, tell the owner what you entered for each field so they can correct it.

Use the returned `key` names and value types to save the answers locally as a UTF-8 JSON object, then run the following commands.

```powershell
prk new --from-json "<answers.json>" --json
prk check -p "<project.json>" --json
```

Check `ok` and `file` from `new`. If it fails, read the `key` and `message` fields in `errors` and correct the answers before retrying. Replace `<project.json>` with `file`, then check `ok`, `problems`, and `language` from `check`. Resolve any problems before continuing. Add `--local "<local.json>"` if you need machine settings. Confirm only where key files are stored. Tell the owner whether the settings passed.

## 3. Install the skill in your assistant

Copy `skill\player-review\SKILL.md` from the toolkit to `player-review/SKILL.md` under the appropriate directory below. In the copy, replace `{{KIT}}` with the toolkit's full path, `{{PROJECT_FILE}}` with the full path to the project settings, and `{{OWNER}}` with the name or title to use for the owner in reports. Keep the two metadata lines and both `---` delimiters. A project-level install lets each copy point to its own project. Keep filled-in copies with real paths in the owner's environment.

If the sandbox blocks writes to the skill directory, give the owner the filled-in skill text and destination so they can install it or approve the write. In one Codex CLI test, writing to the project's `.agents\skills\` in a sandbox restricted to project writes caused later commands to fail during sandbox initialization. You can skip the skill and read the [review playbook](PLAYBOOK.md) each time.

| Tool | Skill location (append `player-review/SKILL.md`) | Header | Reads `AGENTS.md` automatically? | Can delegate? | Official documentation checked |
|---|---|---|---|---|---|
| Claude Code | Project `.claude/skills/`, personal `~/.claude/skills/` | YAML with `name` and `description` | Supported from v2.1.277. By default it reads it automatically only when it finds no applicable `CLAUDE.md` or `CLAUDE.local.md`. Configuration can affect this. You can also import it from `CLAUDE.md`. | Yes, with built-in or custom agents | 2026-11-19 (C16) |
| Codex CLI | Project `.agents/skills/`, personal `~/.agents/skills/` | YAML with `name` and `description` | Yes, in order from the project root to the current directory | Yes, when requested or directed by applicable instructions | 2026-11-19 (C17). In restricted sandboxes, skip installation and read the playbook. |
| Cursor | Project `.cursor/skills/` or `.agents/skills/`, personal `~/.cursor/skills/` or `~/.agents/skills/` | YAML with `name` and `description` | The editor supports project roots and subdirectories. CLI documentation confirms project roots. CLI subdirectories are unverified. | Yes, when the current Agent supports delegation | 2026-11-19 (C18) |
| Gemini CLI | Project `.gemini/skills/` or `.agents/skills/`, personal `~/.gemini/skills/` or `~/.agents/skills/` | YAML with `name` and `description` | It reads `GEMINI.md` by default. Add `AGENTS.md` through `context.fileName`. | Yes, with local and custom subagents | 2026-11-19 (C19) |
| GitHub Copilot CLI | Project `.github/skills/`, `.claude/skills/`, or `.agents/skills/`, personal `~/.copilot/skills/` or `~/.agents/skills/` | YAML with `name` and `description` | The main CLI session reads it. Whether subagents inherit it depends on the agent type and settings. | Yes, with general-purpose or custom agents | 2026-11-19 (C20) |

`~` is the user's home directory. The GitHub Copilot row covers the CLI. For other interfaces, check their official instructions. [References](../../docs/references.md)

Use the skill in a session that can read the toolkit folder and run commands. If your tool is missing from the table, use its skill or project-rule format and keep the instructions that point to the playbook. If it has no skill or rule support, read the [review playbook](PLAYBOOK.md) whenever the owner asks for a review.

Claude Code has an optional shortcut. `prk install` calls `install.ps1` to put the skill and three agent definitions in the project's `.claude` folder and fill in the three placeholders. It replaces previously installed files of the same names. Open a new session afterward.

```powershell
prk install -p "<project.json>"
```

## 4. Try the example

Use a copy of `examples\tea-stall` with no review rounds yet. Generate the page first, then prepare the tasks. `prepare` creates a new round, and `page` defaults to the latest round.

```powershell
prk page -p examples\tea-stall\project.json --json
prk prepare -p examples\tea-stall\project.json --json
```

Both commands are free and make no AI calls. For the first, check `ok` and `html`, then open the file and look for the handwritten sample feedback. For the second, check `ok`, `static.ok`, and `stages`, and confirm that the files in `task` exist. If the example already has rounds, the page shows the latest one by default. To see the sample, use a fresh copy and keep the existing rounds.

Once both checks pass, tell the owner, “Setup is complete. Next time, say ‘Review this game from the players' point of view,’ or name an area to review. I'll give you the report page.”
