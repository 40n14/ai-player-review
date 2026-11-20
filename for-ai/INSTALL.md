# 第一次安装

在工具包根目录执行下面的命令。Windows 上可用 `prk`，PowerShell 找不到它时用 `.\prk.cmd`，也可把 `prk` 换成 `python -I prk.py`。示例里的尖括号内容换成实际值，路径加引号。

## 1. 看环境

先跑 `python --version`。需要 Python 3.8 或更新版本。Windows 上如果用 `py`，就查 `py -3 --version`。没有可用的 Python，就告诉负责人先装 Python。静态表和页面此时做不了。负责人明确要求手工查看时，按[审查步骤](PLAYBOOK.md#出了事)处理。

Windows 自带 PowerShell。在 PowerShell 里看 `$PSVersionTable.PSVersion`，也可以先查找 `powershell` 或 `pwsh`。找不到时，告诉负责人 `prepare` 和 `run` 用不了，以及工具包目前只在 Windows 上验证过。有 Python 仍可用 `check`、`static` 等命令。

状态目录默认是 `%LOCALAPPDATA%\PlayerReviewKit`，也可用 `PLAYER_REVIEW_STATE` 指定。写不了时，需要暂存的东西放到系统临时目录下的 `PlayerReviewKit`。能只读的命令照常用。`--json` 对象的 `state` 会给出实际目录和是否用了临时位置。

## 2. 建项目设置

```powershell
prk new --fields --json
```

看 `fields`。用每项的 `label` 和 `help`，一次把需要负责人回答的问题问完。`required` 标出必填项，`example` 只用来解释要填什么。请负责人说明作品目录、报告写到哪、哪些资料可以读等字段实际问到的事。已有项目设置就直接检查。

建项目设置时，问负责人审查用中文还是英文。`language` 填 `zh` 或 `en`，可以不填，缺省是 `zh`。负责人明确选英文，或一直用英文交流又没另外指定，就填 `en`。交付和审查对话用项目语言。

如果负责人说「你自己定」或不在场，按看得到的情况填写，比如作品在哪、报告放在哪。必填项里确实看不出来的再问。建好后逐项告诉负责人实际填了什么，请他发现不对时再改。

按 `key` 把回答写成一个 UTF-8 JSON 对象，存到本机的回答文件。照返回的字段和类型填写。然后运行：

```powershell
prk new --from-json "<answers.json>" --json
prk check -p "<project.json>" --json
```

先看 `new` 的 `ok` 和 `file`。失败时看 `errors` 的 `key` 和 `message`，补好再建。把 `<project.json>` 换成 `file`，再看 `check` 的 `ok`、`problems` 和 `language`，有问题先处理。需要机器设置时加 `--local "<local.json>"`，只确认密钥文件的位置。告诉负责人项目设置是否通过检查。

## 3. 把技能装进当前工具

复制工具包里的 `skill\player-review\SKILL.md` 到下表的 `player-review/SKILL.md`。在副本里把 `{{KIT}}` 换成工具包的完整路径，`{{PROJECT_FILE}}` 换成项目设置的完整路径，`{{OWNER}}` 换成报告里对负责人的称呼。保留开头两行元数据和两道 `---`。建议装在项目下，让每份副本指向自己的项目。带真实路径的副本留在负责人使用的环境里。

沙箱不让往技能目录写时，把已经填好记号的指路牌内容和目标位置交给负责人，请他自己放或批准。Codex CLI 有过一次实测，在只许写项目目录的沙箱里写入项目的 `.agents\skills\` 后，后续命令都报沙箱初始化错误。技能可以跳过，每次审查时直接读[审查步骤](PLAYBOOK.md)。

| 工具 | 技能放哪（路径后接 `player-review/SKILL.md`） | 文件开头 | 自动读 `AGENTS.md` 吗 | 能派子代理吗 | 官方资料核对日期 |
|---|---|---|---|---|---|
| Claude Code | 项目 `.claude/skills/`，个人 `~/.claude/skills/` | YAML，保留 `name`、`description` | 从 v2.1.277 起支持。默认找不到适用的 `CLAUDE.md` 或 `CLAUDE.local.md` 时才自动读，受配置影响。也可从 `CLAUDE.md` 导入 | 能，用自带或自定义代理 | 2026-11-19（C16） |
| Codex CLI | 项目 `.agents/skills/`，个人 `~/.agents/skills/` | YAML，`name`、`description` | 会，按项目根目录到当前目录的指令顺序读 | 能，由请求或适用指令触发 | 2026-11-19（C17）。受限沙箱里跳过安装，直接读审查步骤 |
| Cursor | 项目 `.cursor/skills/` 或 `.agents/skills/`，个人 `~/.cursor/skills/` 或 `~/.agents/skills/` | YAML，保留 `name`、`description` | 会，编辑器支持项目根目录和子目录。CLI 的根目录有官方说明，子目录没核实 | 能，当前 Agent 有委派能力时可用 | 2026-11-19（C18） |
| Gemini CLI | 项目 `.gemini/skills/` 或 `.agents/skills/`，个人 `~/.gemini/skills/` 或 `~/.agents/skills/` | YAML，`name`、`description` | 默认读 `GEMINI.md`。可通过 `context.fileName` 加上 `AGENTS.md` | 能，支持本地和自定义子代理 | 2026-11-19（C19） |
| GitHub Copilot CLI | 项目 `.github/skills/`、`.claude/skills/` 或 `.agents/skills/`，个人 `~/.copilot/skills/` 或 `~/.agents/skills/` | YAML，`name`、`description` | CLI 主会话会读。子代理能否继承取决于代理类型和设置 | 能，可委派给通用或自定义子代理 | 2026-11-19（C20） |

表里的 `~` 是用户目录。GitHub Copilot 这一行按 CLI 核对。其他界面以各自的官方说明为准，另见 [参考文献](../docs/references.md)。

装好后，在能读工具包路径、能执行命令的会话里使用。工具没列在表里，就按该工具的技能或项目规则格式放，保留指向玩法说明的正文。工具没有技能或规则入口时，每次收到「审查」就直接读 [审查步骤](PLAYBOOK.md)。

Claude Code 还有可选快捷装法。`prk install` 会调用 `install.ps1`，把指路牌和三份代理定义装进项目的 `.claude`，自动填好三个记号。它会覆盖之前装过的同名文件。装好后开一个新会话。

```powershell
prk install -p "<project.json>"
```

## 4. 用例子试一下

拿一份还没有审查轮次的 `examples\tea-stall` 验证。先生成页面，再准备任务。`prepare` 会新建一轮，而 `page` 默认挑最近一轮。

```powershell
prk page -p examples\tea-stall\project.json --json
prk prepare -p examples\tea-stall\project.json --json
```

这两条命令不花钱，也不调 AI。第一条看 `ok` 和 `html`，打开该文件确认能看到手写示范反馈。第二条看 `ok`、`static.ok` 和 `stages`，确认 `task` 指向的任务文件存在。已有审查轮次时，默认生成该轮页面。要专看示范就用一份未跑过的例子，保留已有轮次。

两项都通过后，告诉负责人「装好了。下次说『从玩家视角审查一下』，或说清只看哪一处，我就会把报告页面交给你。」
