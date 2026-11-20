# 命令和文件参考

每次审查按 [审查步骤](PLAYBOOK.md) 走。这里查参数、结果和文件位置。

## 怎么调命令

```text
python -I prk.py <command> [args]
```

在工具包根目录运行。Windows 上可以用 `prk`，在 PowerShell 中找不到时用 `.\prk.cmd`。下文 `P` 代表项目设置 JSON 的路径，`R` 代表轮次文件夹名或路径。把这两个占位符换成实际值。

- 涉及项目的命令明确带 `-p "P"`（也可写 `--project "P"`）。`projects\` 只有一份项目设置时可以省略。
- 有机器设置就带 `--local "<local.json>"`，或设 `PLAYER_REVIEW_LOCAL`。路径相对哪一层以设置文件及命令说明为准。项目设置里的相对路径以该文件所在目录为准。
- 读结果时，对支持的命令加 `--json`。正常返回时，标准输出只有一段 JSON。遇到用法或环境错误也看报错。JSON 字段名不随项目语言变，普通命令提示可以是中文。
- 退出码 `0` 表示做成了，`1` 表示做了但有问题（如任务失败或没找到报告），`2` 表示用法或环境不对。新命令的细节见下文。

## 命令一览

| 命令 | 另花钱或用额度 | 看什么、做什么 |
|---|---|---|
| `prk new --fields --json` | 不 | 看 `fields`，每项有 `key`、`label`、`required`、`help`、`example`。其中 `language` 可选，默认 `zh` |
| `prk new --from-json "<answers.json>" --json` | 不 | 照回答建项目设置。成功看 `ok`、`file`。失败退出 2，看 `errors` 的 `key`、`message`，文件未创建 |
| `prk new` | 不 | 交互式建项目设置，要负责人回答。也可参考 `projects\_template.json` |
| `prk local` | 不 | 交互式设置这台机器，只填 key 文件位置，由负责人操作 |
| `prk install -p "P"` | 不 | Claude Code 的可选安装办法，见 [安装说明](INSTALL.md) |
| `prk check -p "P" --json` | 不 | 看 `ok`、`problems` 和 `language`，设置有问题就先处理 |
| `prk static -p "P"` | 不 | 单跑静态表。默认看 `staticOutDir` 下的 `_summary.md` |
| `prk groups -p "P" --json` | 不 | 看项目的审查组和 `defaultGroups` |
| `prk kinds --json` | 不 | 看走法及走法 ID |
| `prk personas --json` | 不 | 看玩家画像和编号，可加 `--find "<term>"` |
| `prk suggest "<genre>" --json` | 不 | 看这种游戏适合哪些画像 |
| `prk presets --json` | 不 | 看有哪些画像预设。要用的 ID 填进项目设置的 `presets` |
| `prk guide -p "P" --json` | 不 | 看 `next` 每项的 `title`、`detail`、`cmd`、`costs`、旧页面入口 `view`，以及项目的 `language` |
| `prk plan -p "P" --groups A,B --split --json` | 不 | 演习。看 `tasks` 的个数、`groups`、`estimate.text.api` 或 `estimate.text.sub` |
| `prk prepare -p "P" --groups A,B --split --json` | 不 | 新建轮次、静态表和任务文件。看 `stages`、`static` 和 `language` |
| `prk run -p "P" --groups A,B --split --parallel 4 --pay sub --yes` | 会 | 后台做同一轮审查。等负责人同意再执行。用本轮花费表看任务和合计 |
| `prk quick "15 + 18" -p "P" --kind wants --pay sub --yes` | 会 | 后台只问一类玩家。一个任务，画像用编号，`--kind` 默认 `persona` |
| `prk fake -p "P" --groups A,B --split` | 不 | 用假 runner 验证排队和合并。报告和花费是演示数据 |
| `prk reports -p "P" --json` | 不 | 看 `reviewOutDir` 和 `reviews` 里的轮次目录、报告、合并、花费表路径 `cost` 和地图 |
| `prk feedback -p "P" --json` | 不 | 看玩家反馈和条目。可指定轮次文件夹参数或 `--from "<report.md>"`。`--full` 看整份，`--save "<path>"` 另存 |
| `prk cite -p "P"` | 不 | 核对原文和行号。要查旧轮次，另传轮次文件夹路径 |
| `prk page -p "P" --round "R" --json` | 不 | 核出处并按 `language` 写 `review.md` 和 `review.html`。加 `--open` 打开页面 |
| `prk decide -p "P"` | 不 | 负责人在终端逐条作决定。也可用 `--set` 记他已给出的决定 |
| `prk fix -p "P" --json` | 查清单不花，后台修会 | 查清单、交给自己的 AI、直接修、撤回和改状态，见下文 |
| `prk expand -p "P" --from "<merged-report.md>" --items W1,W3 --pay sub --yes` | 会 | 写指定条目的内容提案。先问负责人同不同意。作品保持只读 |
| `prk cost -p "P"` | 不 | 看最近有花费表的一轮。可另传轮次文件夹路径 |
| `prk costs -p "P" --json` | 不 | 看跨轮次花费、本月用量和预算 |
| `prk pay --json` | 不 | 看后台检查及问 AI 向导各怎么付 |
| `prk provider --json` | 不 | 看服务商及配置状态 |
| `prk model --json` | 不 | 看当前模型、来源和可选型号 |
| `prk guide "<question>" -p "P" --pay sub --yes --json` | 会 | 问 AI 向导，先征得同意。问题里别带真实项目资料 |
| `prk ui -p "P"` | 打开不花 | 打开可选的旧页面，见末节 |
| `prk ask -p "P"` | 不 | 显示旧的 Claude Code 对话用法。平时用 [审查步骤](PLAYBOOK.md) |

花费命令里的 `sub` 是示例，实际要按负责人选的付法。手工排查时可先用 `prk --help`。

## 项目语言

在项目设置里写 `"language": "zh"` 或 `"language": "en"`，不写则用 `zh`。`prk new --fields` 会列这个可选项，`prk check` 会报不认识的值。`check --json`、`guide --json`、`prepare --json` 和 `page --json` 都返回 `language`。报告、一页纸、离线页面、修复清单、决定记录、花费表和审查对话用项目语言。画像、走法、代理说明和任务模板以中文为准。

报告标题、标记和索引列见[中英报告格式](../docs/report-format.md)。编号 S、M、L、D、W、F 两种语言都一样。读报告的命令和脚本（如 `feedback`、`cite`、`page`、`decide`、`fix`、`score.py`、`next_steps`）都认两种格式，和项目语言无关。

## 准备任务、出页面

每个审查组是一种走法加几类玩家画像，配置在 `reviewGroups`。走法登记在 `kinds\kinds.json`，画像索引在 `method\画像_索引.md`。任务需要读画像时，照任务指定的通用层、`presets` 预设、`personaOverlay` 项目对照层逐层读，后面的优先。

### `prepare`

```text
prk prepare [-p P] [--groups A,B] [--split] [--scope TEXT] [--no-map] [--map-dir DIR] [--no-merge]
            [--who "15 + 18" [--kind KIND_ID]] [--json]
```

参数和 `plan` 或 `quick` 的含义一样。省略 `--groups` 用默认组，`--split` 按项目设置拆组，`--scope` 写范围，`--no-map` 跳过地图，`--map-dir` 使用指定目录的地图，`--no-merge` 跳过合并。`--who` 只派一类玩家，只有一个任务，省去地图和合并。

它在 `reviewOutDir` 下新建一轮，跑静态表，写任务文件和 `_prepared.json`。不调 AI，也不写花费表。

- `ok`、`round`、`dir`、`count` 是结果、轮次文件夹名、目录绝对路径和任务总数。
- `language` 是本轮交付用的项目语言。
- `stages` 按顺序列阶段，每段有 `stage` 和 `tasks`。每个任务有 `name`、`kind`、`task`、`writes`。`task` 和 `writes` 是任务文件与主输出的绝对路径。同阶段可并行。地图、审查、合并依所选选项排进相应阶段。
- `static.ok` 和 `static.summary` 告诉你静态表成没成、摘要在哪。静态表有一张没成时退出 1，任务文件仍会写出。
- 第一次审查时，`guide --json` 的 `next` 会先给出 `prk prepare`。只在后台跑时需要的步骤标为 `optional: true`。
- 最近一轮有 `_prepared.json` 且任务未完成时，`guide --json` 的 `next` 会列待做的任务文件。报告齐了而页面缺失或比报告旧时，下一步会指向 `prk page`。

### `page`

```text
prk page [-p P] [--round R] [--open] [--json]
```

先核引文，再写 `review.md` 和 `review.html`。HTML 是单个离线文件，可双击，也可加 `--open` 用默认浏览器打开。默认取最近一轮。项目没有轮次但配置了 `sampleRound` 时，用只读示范轮生成，输出在工具包的状态目录。

- `ok`、`round`、`dir` 表示生成结果及选中的轮次。`html` 和 `md` 是交给负责人的文件路径。
- `language` 是页面和一页纸的项目语言。
- `counts` 的 `S`、`M`、`L`、`D`、`W` 依次是严重、中、轻、要负责人定、想要但没有的。`undecided` 是还没记决定的条数。
- `missing` 列出按 `_prepared.json` 或本轮花费表应该有却没写出的报告。两份都没有时返回空数组。`citationsBad` 是出处对不上的条数，没核成时为 `null`。

## 状态目录

状态目录默认是 `%LOCALAPPDATA%\PlayerReviewKit`，可用 `PLAYER_REVIEW_STATE` 指定。指定位置写不了时，需要写状态的命令改用系统临时目录下的 `PlayerReviewKit`。`--json` 对象中的 `state.dir` 是实际目录，`state.temporary` 表示是否用了临时位置。画像、走法和组选建议的列表输出保持数组格式。

## 记决定

```powershell
prk decide -p "P" --round "R" --set "S1=修; S2=放进待做: 等下个版本; W1=是设计" --json
prk decide -p "P" --round "R" --set "S1=fix; S2=later: next version; W1=by-design" --json
```

`--from "<report.md>"` 可以指定报告。轮次编号来自负责人粘贴的决定。两行是两种输入示例，选一行照实际决定填。分号隔开各条，冒号后可加一句理由。页面复制决定时会替换理由里的半角分号。输入两种词都认，英文大小写不分。写记录用项目语言，读记录两种词都认。

| 中文决定词 | English | 中文页面按钮 | English page button |
|---|---|---|---|
| `修` | `fix` | 要修 | Fix |
| `放进待做` | `later` | 以后再说 | Later |
| `是设计` | `by-design` | 本来就这样 | By design |
| `不是问题` | `not-an-issue` | 不是问题 | Not an issue |
| `误报` | `false-positive` | AI 看错了 | AI got it wrong |

只记负责人给出的决定。编号不在该轮报告或决定词不认识时，退出 2，整批都不写。成功看 `ok`、`recorded`（每条 `id`、`decision`、`why`）、`fixAdded` 和 `file`。同一条再记一次就是改决定。决定写进 `决定记录.csv` 或 `decisions.csv`。选「修」（`fix`）会进入待修清单。记录后对同一轮再跑 `page`。

## 怎么付

- `sub` 用这台电脑上已登录账号的会员额度。`api` 用 key 按实际用量付费。`prk pay --json` 看 `pay`、`guidePay`、`payGuideSeparate`、`problem`。
- `run`、`quick`、`expand`、后台 `fix F3` 和带问题的 `guide` 会另用额度或钱。先报任务数和可用估价。整轮用 `plan` 先报，单项操作照实际任务数报。负责人同意后，非交互调用才带 `--yes`。
- 没选过付法时，非交互付费调用退出 2。把报错告诉负责人，请他选会员额度或按次付费。`--pay sub` 或 `--pay api` 只覆盖这次。负责人说以后都这么付，才用 `prk pay sub` 或 `prk pay api` 记住。
- 问 AI 向导可单独记付法，用 `prk pay guide sub` 或 `prk pay guide api`。跟检查一样就用 `prk pay guide same`。
- 工具包的会员付法支持 `anthropic` 和 `openai`。Gemini CLI 在本工具包中走按次付费。选了 `sub` 而服务商不支持时，命令退出 2，由负责人选服务商或付法。
- `plan` 的估价来自花费总账。看 `estimate.text.api` 或 `estimate.text.sub`。模型没跑过时照实说估不了。

## 服务商和模型

`prk provider --json` 列 `providers` 和当前服务商。每家的 `configured` 表示按当前付法配好没有，`keyReady` 表示 key 路径已设好，`signin` 和 `signinReady` 表示支持会员登录及本机是否就绪。`openai` 用 Codex CLI，`google` 用 Gemini CLI，输出沿用同一套报告和日志格式。

`prk model --json` 看 `model`、`source` 和 `choices`。负责人指定以后才用 `prk provider <name>` 或 `prk model <id>` 记住。`prk model default` 清除记住的型号。只改这次加 `--provider <name>` 或 `--model <id>`。

服务商没设好，可请负责人运行 `prk provider setup <name>`，或在旧页面「设置 → 用哪家的 AI」填写。密钥文件由工具包自己读。不要打开、打印或复制它，也不要读任何 `neverRead` 路径。

## 待修清单

`<reviewOutDir>\待修清单.md` 或 `<reviewOutDir>\fix-list.md` 里的编号是 F1、F2 等，编号不重复用。页首给 AI 的说明和每条详情一起读。`prk fix -p "P" --json` 的 `items` 每条有 `id`、`title`、`severity`、`done`、`body`、`filled`（修复记录各项）、`copy`、`canUndo`。还返回 `todo`、`copyAll`、`file`。

- **在负责人自己的会话里修。** 他明确说修 F3 后，按清单和作品自己的规矩只修 F3。修完打 `[x]`，填写修复记录。这条路的撤回靠项目自己的版本管理。可把 F3 的 `copy` 交给负责人在自己的另一个会话使用。
- **派后台 Claude Code 修。** 仅 `engine` 为 `claude-code` 的服务商支持，别家退出 2。先告诉负责人这会用额度或花钱、后台代理没看到这场对话、工具会备份出处里的文件并可撤回这些备份。负责人逐条同意后才跑 `prk fix F3 -p "P" --pay sub --yes --json`。`ok` 代表清单打了勾。没打勾退出 1，看 `tail` 的日志末尾。
- **撤回。** 负责人要求时用 `prk fix F3 -p "P" --undo --json`。`_修之前\` 或 `_before-fix\` 的 `manifest.json` 记原件和 `files\` 里的副本。恢复失败就报哪些没恢复，排除原因后重跑同一条，只恢复上次失败的文件。能恢复的都恢复后才放回待修。`noBackup` 里的文件交给负责人处理。
- **改状态。** 负责人说 F3 修好了用 `prk fix F3 -p "P" --done --json`，要求放回待修用 `prk fix F3 -p "P" --reopen --json`。

## `feedback --json` 的字段

| 字段 | 怎么看 |
|---|---|
| `ok`、`dir` | 有没有读到结果、是哪一轮 |
| `reports`、`merged` | 实际读的报告。合并报告存在时只读它，否则各组报告可能有重复 |
| `counts` | `S`、`M`、`L`、`D`、`W`，对应严重、中、轻、要定、想要但没有的 |
| `conclusion` | 「结论」原文 |
| `feedback` | 每类 `player` 的 `says`。每句有 `kind`、`text`、`refs`，即反馈类型、内容、所指条目编号 |
| `feedbackMarkdown` | 「玩家反馈」原文，结构化字段解析不全时读它 |
| `lastRound` | 「上一轮反馈的去向」原文，第一轮通常为空 |
| `entries` | 条目的 `id`、`title`、`confidence`、`report`。照编号到原报告查细节和出处 |

两种玩家反馈字段都空时，说明报告缺「玩家反馈」（Player feedback）这一节，按 `entries` 说。对标【可能】或 [Possible] 的条目说明还要确认什么。

## 文件在哪

一般一轮在 `<reviewOutDir>\<YYYYMMDD_HHMMSS>\` 下。报告名按项目设置的 `reportNames`，没有自定时用下表。`sampleRound` 的输出位置以 `page --json` 返回的路径为准。

| 中文项目 | English project | 怎么用 |
|---|---|---|
| `玩家视角审查_合并.md`、`玩家视角审查_<组>.md` | `player-review_merged.md`、`player-review_<group>.md` | 合并报告、各组报告。看玩家反馈、结论、问题、想要但没有的、要定的和索引 |
| `….草稿.md` | `….draft.md` | 审查员走了哪几趟、有哪些候选，可查漏在哪 |
| `内容拓展提案.md` | `content-proposal.md` | 最近一次成功生成的提案 |
| `内容拓展提案_<RunId>.md` | 英文提案名加 `_<RunId>` | 每次拓展的提案，自定名称也会加运行编号 |
| `决定记录.csv` | `decisions.csv` | 项目输出根目录里的决定记录 |
| `待修清单.md` | `fix-list.md` | 项目输出根目录里的待修清单 |
| `花费记录.csv` | `cost-ledger.csv` | 项目输出根目录里的跨轮次花费总账 |
| `_修之前\`、`_修\` | `_before-fix\`、`_fix\` | 项目输出根目录里的修前备份、修复任务和日志 |

程序查找时两种文件名都认。两种都找到时优先用项目语言的名字，并在 `--json` 里提醒。

| 两种项目都用的文件名 | 怎么用 |
|---|---|
| `_prepared.json` | 对话轮次的任务清单，供恢复任务与核对缺失输出 |
| `review.md`、`review.html` | 给负责人的一页纸和离线页面 |
| `_map\` | 作品地图，含路线、选择点、状态、东西、结局、文本、数值和牵连 |
| `_summary.md`、`_text_checks.md`、`_image_hits.md` | 静态表、文字检查、登记了图片时的点击面积 |
| `_citations*.md` | 引文核验结果 |
| `task_*.md`、`log_*.txt` | 每个任务收到的完整材料和后台日志，包括 `task_expand_<RunId>.md` 和 `log_expand_<RunId>.txt` |
| `_运行记录.txt` | 旧页面启动后的运行输出 |

本轮花费表记后台每个任务的进度和花费。中文名是 `_花费.md`，其他写法见[报告格式](../docs/report-format.md)。用 `reports --json` 里该轮的 `cost` 找它。

报告末尾的「索引」（Index）供核验脚本和 AI 用。列为编号、严重、把握、`文件:行` 和原文，英文列见[报告格式](../docs/report-format.md)。缺索引就把这份报告标为不完整。

## 花费总账

`花费记录.csv` 或 `cost-ledger.csv` 每个后台任务一行，跨轮次自动记录。`prk costs -p "P" --json` 看 `month.usd`（本月按次付费美元）、`month.budget`（设置的月预算）、`month.subTokens`（会员用掉的 token）。`summary` 按模型、类别、付法、天和轮次汇总，`rows` 是逐任务记录。

以账里有的数字为准。每轮用该轮的花费表报合计。对话内审查的用量和会员剩余额度不从这两处估算。`prk costs -p "P" --rebuild` 可从轮次重建总账。负责人要求变更预算时用 `prk costs --budget 20`（美元）或 `prk costs --budget 0`（取消）。预算只提醒，快到或超了先告诉负责人。

## 可选的旧页面

`prk ui -p "P"` 会启动本机后台服务。已经编过启动器的也可双击 `玩家视角审查.exe`。这个页面保留，后续功能走 `prk page`。旧页面上启动的轮次用 `reports` 找，用 `_运行记录.txt` 和本轮花费表跟进，结束后用 `feedback --json` 看结果。

用旧页面接口开跑、写建议或直接修时，把页面给的 `confirmation` 原样带回。撤回、标完成、放回待修时，用那条的 `actionBinding` 作为请求的 `confirmation`。检查和写建议会核对项目设置路径和指纹、任务名单、服务商、型号、付法和选项。写建议也核合并报告，待修清单动作也核轮次和条目。收到 `changed` 就刷新，再请负责人确认。
