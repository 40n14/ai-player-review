# 每次审查怎么走

先读 [AGENTS.md](../AGENTS.md)。下面的 `P` 是这次的项目设置路径，`R` 是这次的轮次。把它们换成实际值。命令在工具包根目录运行，Windows PowerShell 可用 `.\prk.cmd`，也可把 `prk` 换成 `python -I prk.py`。机器设置、付法和参数细节见 [命令参考](REFERENCE.md)。

交付和审查对话用项目设置的 `language`，没填就是中文。画像、走法、代理说明和任务模板用中文读。审查员、合并员和核对员按项目语言写，报告的标题和标记照[报告格式](../docs/report-format.md)。编号 S、M、L、D、W、F 两种语言都一样。文件名以[文件表](REFERENCE.md#文件在哪)为准。

## 1. 看现在到哪了

```powershell
prk guide -p "P" --json
prk reports -p "P" --json
prk check -p "P" --json
```

读 `guide` 的 `next`，再用 `reports` 的 `reviews` 确认轮次。该项目 `reviewOutDir` 下有 `决定记录.csv` 或 `decisions.csv` 就按复查处理。`check` 返回项目的 `language`。`problems` 有内容就先告诉负责人并处理。报告齐了而页面缺失或过时，直接去第 5 步。

告诉负责人现在是第一轮、继续做哪一轮，还是只差页面。已有 `_prepared.json` 而任务没做完时，按原清单接着做，已写完的跳过。负责人已从旧页面启动后台任务时，用 `reports` 找该轮，读 `_运行记录.txt` 和该轮 `cost` 指向的花费表，同一轮只启动一次。

## 2. 定范围和审查组

```powershell
prk groups -p "P" --json
```

默认用 `defaultGroups`。负责人点名组或范围时照他的说法，写进 `--groups` 和 `--scope`。只改了几处，就选覆盖改动、牵连部分和上一轮待核条目的组，通常可以少派。拿不准就问一句。这次的范围用命令参数传入即可。

组里的 `kind` 是走法，`personas` 是画像编号。只派一类玩家可用 `prk prepare -p "P" --who "15 + 18" --kind wants --json`。这一跑法只有一个任务，省去地图和合并，`--kind` 省略时用 `persona`。

## 3. 选跑法，报任务数

**默认在当前对话里做。** 用负责人这场会话自己的额度，`prepare` 本身不调 AI。用同一组范围、拆分和地图选项运行演习，数 `tasks` 有几项，把任务数和组别告诉负责人。任务很多（例如超过六个）时，先问要不要少派几组。`--who` 的任务数直接报 1。

```powershell
prk plan -p "P" --groups A,B --scope "<scope>" --split --json
```

演习如果只因后台付法或服务商设置而失败，仍可用第 4 步的 `prepare` 拿 `count`。先报数再开始做任务。

**负责人想让任务在后台跑，或任务很多时，可以用后台跑法。** 用同样的范围和选项跑 `plan`，报 `tasks` 的个数、`groups` 和 `estimate.text` 中所选付法的估价。估不了就照实说。等负责人同意任务和付法，再放到后台执行。下面以负责人选 `sub` 为例。

```powershell
prk run -p "P" --groups A,B --scope "<scope>" --split --parallel 4 --pay sub --yes
```

等后台跑完，到第 5 步。按该轮花费表报合计。后台跑一类玩家用 `quick`，先按一个任务报范围和可用的估价，再等负责人同意。

## 4. 在对话里做任务

```powershell
prk prepare -p "P" --groups A,B --scope "<scope>" --split --json
```

按第 2 步选好的范围改命令。用默认组时省略 `--groups`，不用拆分就省略 `--split`。看 `round`、`count`、`static.ok` 和 `stages`。静态表有一张没成，就读 `static.summary`，告诉负责人哪张没成，以及这影响哪些任务。

照 `stages` 的顺序走。每个任务先读 `task` 文件全文，照里面的步骤、范围和交付要求做。主要结果写到 `writes`，草稿等附带文件照任务指定的位置写。任务期间只读作品，别编译、开游戏或跑测试。每完成一个任务，确认输出文件实际存在。

- 当前工具能派子代理时，把同一阶段的任务一起派，等该阶段完成再进入下一阶段。给每个子代理一句话：「请读『<task 的完整路径>』全文照做，只读作品，只写任务指定的文件（主输出『<writes 的完整路径>』），五行以内回复结果和漏做的事。」
- Claude Code 装过 `player-bug-reviewer` 等代理类型时可用相应类型。没有这些类型就用通用子代理。
- 当前工具不能派时，自己一份一份做。先把这一份写进文件，再重读下一份的任务文件。只沿用下一份任务指定的输入。合并要核对时，按任务给的主张回原文件复走，并说明这一轮没有独立核对员。证据不足的留【可能】。
- **进合并那一阶段以前**（`kind` 是 `merge` 的任务），先跑一次 `prk cite -p "P" "<round folder>"`，传入这一轮的文件夹。不花钱，几秒钟。它把前面每份报告的出处核一遍，写出合并任务要读的 `_citations.md`。没跑成就告诉负责人，合并任务会改成直接回原文件核。
- 子代理没回来或没落盘，照实记为未完成。按任务说明处理缺少的前置材料。依赖该输出且无法继续的任务先停下，告诉负责人缺什么。

## 5. 生成页面

```powershell
prk page -p "P" --round "R" --json
```

看 `ok`、`html`、`md`、`counts`、`missing` 和 `citationsBad`。`missing` 有内容就列出缺的报告。`citationsBad` 大于 0 就报条数，提醒负责人先别采信这些条目。引文核验没成时也说清楚。加 `--open` 可用默认浏览器帮负责人打开页面。生成失败时说明报错和已有文件。

## 6. 把结果交给负责人

对话里五行以内。先说好几类玩家都会说的，再说只有一类玩家提到但影响很重的。只说已有报告支持的内容，标了【可能】或 [Possible] 的说明还有哪步待确认。有缺项或核验问题时放在这段一起报。用 `counts` 报数字，给出 `html` 的路径，提醒负责人可在页面上选决定并点「复制给 AI」（Copy for AI）。

## 7. 记负责人说过的决定

中文页面复制回来的话如下。

```text
请把这些决定记进决定记录（轮次 20261119_153000）：
S1 = 修
S2 = 放进待做（原因：等下个版本）
W1 = 是设计
```

英文页面复制回来的话如下。

```text
Please record these decisions (round 20261119_153000):
S1 = fix
S2 = later (reason: next version)
W1 = by-design
```

把对应轮次和决定交给 `prk decide --set`。这两条 `decide` 命令是两种输入示例，按负责人贴回的内容执行一条，然后刷新页面。

```powershell
prk decide -p "P" --round 20261119_153000 --set "S1=修; S2=放进待做: 等下个版本; W1=是设计" --json
prk decide -p "P" --round 20261119_153000 --set "S1=fix; S2=later: next version; W1=by-design" --json
prk page -p "P" --round 20261119_153000 --json
```

检查 `recorded` 和 `fixAdded` 再刷新，交回同一轮的新页面。负责人直接在对话里说也一样。只记他说过的决定。编号或轮次不清楚就先核实。需要问时，有选项提问功能就分组用，没有就列编号和可选决定请他回复。两种决定词都能输入，记录用项目语言。见[决定词表](REFERENCE.md#记决定)。

## 8. 只修点名的那一条

负责人明确说「修 F3」后，先跑 `prk fix -p "P" --json` 找到 `file`（`待修清单.md` 或 `fix-list.md`），读页首给 AI 的说明和 F3。照作品自己的规矩只修 F3。验证后打 `[x]`，填写修复记录，把改动和验证结果告诉负责人。想把这一条交给自己的另一个会话时，给负责人这一条的 `copy`。后台直接修的付法和撤回办法见 [待修清单](REFERENCE.md#待修清单)。

## 9. 改完再审一轮

改完以后从第 1 步再来。新任务会自动带上决定记录，先核上一轮说要修的条目。复查范围再加这次改动和受牵连的部分。看报告里的「上一轮反馈的去向」（Follow-up on last round），告诉负责人哪些解决了、哪些还在。

## 10. 可选：写内容提案

负责人挑了「想要但没有的」条目后，先报这次一个任务和付法，等他同意。下面以负责人选 `sub` 为例，把 `--from` 填成那一轮的合并报告。提案只写建议和草稿，作品保持只读。

```powershell
prk expand -p "P" --from "<merged-report.md>" --items W1,W3 --pay sub --yes
```

读这次的提案和该任务花费，把提案路径及花费交给负责人。

## 出了事

- **退出码 2。** 看命令报错或 JSON 的 `error`、`errors`，照它核对参数、路径和环境。后台命令遇到付法问题，交给负责人选。
- **`prepare` 跑不了或任务文件读不到。** 核对报错、轮次、`task` 路径和权限。先告诉负责人卡在哪里、需要他做什么。只有负责人说「那你先手工看看」，才读作品并反馈。交回时明确这只是手工查看，缺任务文件、静态表和出处核对，未完成正式审查。
- **报告缺节。** 缺「玩家反馈」（Player feedback）或「索引」（Index）都要说明，`feedback` 和 `page` 能读多少就交多少。
- **后台任务失败。** 看该轮花费表和对应 `log_*.txt` 末尾。有 `Credit balance` 一类报错时停止，告诉负责人去看账单。
- **没有 Python 或 PowerShell。** 没 Python 时静态表和页面做不了。没 PowerShell 时 `prepare` 和 `run` 用不了。按 [安装说明](INSTALL.md#1-看环境) 说清能继续做到哪一步。
