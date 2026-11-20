# 报告格式 / Report format

英文项目的交付使用右列的固定标题、字段和标记，中文项目使用左列。程序读报告时两种格式都认。引用作品时保留原文、文件名和行号。只给审查员读的走法和模板仍可用中文。

For English projects, use the headings, fields, and markers in the English column. Readers accept both formats. Keep source quotations, file names, and line numbers as written.

## 报告 / Reports

编号沿用 S（严重）、M（中）、L（轻）、D（要负责人定）、W（想要但没有的）、F（待修清单）。同一报告内分别编号，例如 `S1`、`M2`、`W1`。

Keep the same IDs in both languages. Use `### M1 Title` for a finding and `### [ ] F1 Title` for an open fix. Change `[ ]` to `[x]` when the fix is complete.

| 中文 | English |
|---|---|
| `# 玩家视角审查` | `# Player review` |
| `## 结论` | `## Conclusion` |
| `## 玩家反馈` | `## Player feedback` |
| `## 玩家反馈汇总`（合并） | `## Player feedback summary` (merged) |
| `## 问题一览` | `## Issues at a glance` |
| `## 问题` | `## Issues` |
| `## 想要但没有的` | `## Wanted but missing` |
| `## 要<负责人>定` | `## Needs your decision` |
| `## 查过、没问题的` | `## Checked and fine` |
| `## 这次没走到的` | `## Not covered this time` |
| `## 上一轮反馈的去向` | `## Follow-up on last round` |
| `## 误报和不报的` | `## Dismissed and not reported` |
| `## 要进游戏确认的` | `## Needs an in-game check` |
| `## 已报，还在` | `## Previously reported and still present` |
| `## 索引` | `## Index` |
| 严重 / 中 / 轻 | Severe / Medium / Minor |
| 【确定】 / 【可能】 / 【设计】 | [Confirmed] / [Possible] / [Design] |
| 【确定没有】 / 【可能没有】 | [Definitely missing] / [Possibly missing] |
| 【推断】 / 【回归】 | [Inferred] / [Regression] |
| 索引表头 `编号 \| 严重 \| 把握 \| 文件:行 \| 原文` | Index header `ID \| Severity \| Confidence \| File:line \| Quote` |
| 怎么遇到 / 玩家看到 / 为什么不对 / 出处 / 反查 / 建议 / 测试里怎么复现 | How you get there / What the player sees / Why it is wrong / Source / Cross-check / Suggestion / How to reproduce |
| 谁想要 / 现在有的选项 / 没有它时 / 把握 / 可以怎么加 | Who wants it / Options today / Without it / Confidence / How to add it |
| 卡住的 / 看不懂的 / 觉得不公平的 / 想要的 / 做对了的 / 一句话 | Stuck / Confused / Feels unfair / Wants / Done right / In one line |
| 范围 / 走法 / 画像 / 作品地图 / 静态表 | Scope / Review method / Persona / Project map / Static checks |
| 角色 / 哪几组报的 / 核对 | Character / Reported by / Verification |
| 在哪一步 / 他想做什么、为什么 / 作品里别处有没有同类的选项 | Where it happens / What they want to do and why / Similar options elsewhere |
| 玩家类型（画像） / 他会说什么 / 对应的条目 / 哪几组走过他 | Player type (persona) / What they would say / Related IDs / Groups that played this persona |
| 好几类玩家都会说的 / 只有一类玩家会说、但很重的 | Shared across personas / Serious for one persona |
| 上一轮的编号 / 上一轮的决定 / 这一轮 / 出处 | Previous ID / Previous decision / This round / Source |
| 解决了 / 还在（回归） / 还在（还没修） / 还在（待做） / 不在这次范围里 | Resolved / Still present (regression) / Still present (fix pending) / Still present (deferred) / Outside this round’s scope |
| 核对员结论：成立 / 不成立 / 定不了 / 出处不实 | Verification verdict: Holds / Does not hold / Inconclusive / Source does not match |
| 核对员回话栏：编号 / 结论 / 走过的路 / 找过的挡板 / 关键的一处 / 更正 / 进游戏要看的 | Verification reply fields: ID / Verdict / Steps checked / Blocking conditions checked / Key source / Corrections / Needs an in-game check |
| 覆盖表 / 候选 / 记下的事实 | Coverage / Candidates / Notes on facts |

英文逐条字段用半角冒号，例如 `- Confidence: [Confirmed]`。单独的玩家反馈按 `### Persona name` 和 `- Stuck: … (S1)` 写，合并时也可以用上表中的玩家类型表头。索引每行一处出处，放在报告最后。

## 走法专有部分 / Review methods

| 中文 | English |
|---|---|
| 画像走查：画像 × 线的覆盖表 | Persona review: Persona and route coverage |
| 想要的选项：缺口一览 | Missing options: Gaps at a glance |
| 软锁 / 卡死：必经点表 | Softlocks: Required progression points |
| 经济和数值漏洞：经济走查、进项表、出项表 | Economy and balance: Economy review, Sources, Sinks |
| 认知走查：新手任务走查、最伤新手的三条 | Cognitive walkthrough: New player tasks, Top three new-player barriers |
| 巡游包：巡游记录 | Testing tours: Tour results |
| 事实账本：事实账本 | Continuity review: Fact ledger |
| 交互走法：交互表、截图清单 | Interaction review: Interaction matrix, Screenshot checklist |
| 补丁面和卸载：补丁面表、卸载残留表 | Patch and uninstall review: Patch surface, Uninstall leftovers |
| 无障碍清单：清单核查表 | Accessibility: Accessibility checklist results |
| 内容清单：内容核查表、文化和表现 | Content review: Content checklist results, Culture and representation |
| 作品地图：总览、线、选择点、标记和状态 | Project map: Overview, Routes, Choice points, Flags and state |
| 作品地图：东西、结局和必经点、数值、文本 | Project map: Items, Endings and required progression points, Values, Text |
| 作品地图：互相牵连、伸进宿主的地方、设置和便利、顺手看到的 | Project map: Cross-route effects, Host integration, Settings and accessibility, Other observations |
| 内容拓展提案 / 第一部分：从缺口来的提案 | Content proposal / Proposals from gaps |
| 第二部分：哪类玩家在这里没事可做 / 第三部分：排个序 | Underserved players / Suggested order |
| 给谁 / 加在哪 / 加什么 / 怎么接上现有的 / 草稿【草稿】 | Who it is for / Where it goes / What to add / How it fits / Draft [Draft] |
| 自查 / 要动的文件 / 大小 / 最省的替代 | Self-check / Files to change / Size / Smallest alternative |

## 待修清单和决定 / Fix list and decisions

| 中文 | English |
|---|---|
| `# 待修清单` | `# Fix list` |
| `## 给 AI 的说明` / `## 背景笔记` / `## 要修的` | `## Instructions for AI` / `## Background notes` / `## Items to fix` |
| 用过的最大编号 / 来自 / 有多要紧 / 负责人说 | Highest assigned ID / From / Severity / Owner reason |
| `#### 修完填这里` | `#### Fill in after fixing` |
| 改了 / 自己核过 / 要进游戏看的 / 没把握的 / 顺手看到的 | Changed / Verified / Needs an in-game check / Uncertainties / Other observations |
| 修（要修） | fix (Fix) |
| 放进待做（以后再说） | later (Later) |
| 是设计（本来就这样） | by-design (By design) |
| 不是问题（不是问题） | not-an-issue (Not an issue) |
| 误报（AI 看错了） | false-positive (AI got it wrong) |

`prk decide --set` accepts either spelling. For example, `S1=fix; M2=later: next version`. The page copies the English decisions in this form:

```text
Please record these decisions (round 20261119_153000):
S1 = fix
M2 = later (reason: next version)
W1 = by-design
```

## 文件名 / File names

| 中文 | English |
|---|---|
| `决定记录.csv` | `decisions.csv` |
| `待修清单.md` | `fix-list.md` |
| `花费记录.csv` | `cost-ledger.csv` |
| `_花费.md` | `_cost.md` |
| `玩家视角审查_<组>.md` | `player-review_<group>.md` |
| `玩家视角审查_<组>_<份名>.md` | `player-review_<group>_<split-id>.md` |
| `玩家视角审查_<组>_合并.md` | `player-review_<group>_merged.md` |
| `玩家视角审查_合并.md` | `player-review_merged.md` |
| `….草稿.md` | `….draft.md` |
| `内容拓展提案.md` | `content-proposal.md` |
| `_修之前/`、`_修/` | `_before-fix/`, `_fix/` |

用 `reportNames` 写明的报告名优先。找旧文件时也会认另一种写法。两种都存在时优先用项目语言，相关命令的 JSON 返回 `warnings`。地图目录 `_map/`、地图表的固定文件名、页面 `review.html`、一页纸 `review.md`、任务 `task_*.md` 和日志 `log_*.txt` 沿用既有写法。地图表正文按项目语言写。
