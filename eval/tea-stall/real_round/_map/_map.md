# 茶摊作品地图

「茶摊」是独立的虚构演示小游戏。现有文件是设计、数据、双语文本和图片，未提供运行程序或宿主。出处 `game/README.md:1–3,16–23`。

回合单位是天，按项目设置顺序为「早上：昨天的小结 → 摆摊 → 客人一个一个来 → 客人说话 → 客人点的东西和三个按钮（照价卖 / 少收一点 / 不卖）→ 客人走 → 收摊 → 夜里：看账本」。README 的一天流程对应这些步骤；一局第 7 天收摊以后出结局。出处 `project.json:22–32`、`game/README.md:5–14`、`game/data/settings.json:2`。

内容按客人分为 `granny`（阿婆）和 `zhou`（老周）两条线，叠在共用的交易、物品与结局上。出处 `project.json:158–177`、`game/README.md:25–36`。

## 表格清单

行数按数据行计算，排除表头。两张无表格的文件按事实条数计算。

| 表 | 行数 | 已读及出处 | 把握 |
|---|---:|---|---|
| [01 线](01_线.md) | 7 | `game/data/characters/granny.json:3–18`、`game/data/characters/zhou.json:3–20`、`game/README.md:25–36`、`game/text/zh.csv:13–14,19–21`、`game/text/en.csv:19–21` | 来访日、分支数据有据，日内时序有空缺 |
| [02 选择点](02_选择点.md) | 4 | `game/README.md:9–10,18–28`、`game/data/characters/zhou.json:10–20`、`game/data/settings.json:3–7`、`game/data/items.json:2–6`、`game/text/zh.csv:2–6,22,28–32` | 已知按钮可定位，撤回和启用条件没写明 |
| [03 标记和状态](03_标记和状态.md) | 7 | `game/README.md:7–14,21–22,27,34–36`、`game/data/settings.json:2`、`game/data/characters/granny.json:7–18`、`game/data/characters/zhou.json:12–20` | 声明式条件可定位，运行与存档细节没查清 |
| [04 东西](04_东西.md) | 4 | `game/data/items.json:2–6`、`game/data/settings.json:5–7`、`game/README.md:16–23,30,34`、`game/data/characters/granny.json:5,18`、`game/data/characters/zhou.json:5,19` | 物品、位置、设计中的判定有据 |
| [05 结局和必经点](05_结局和必经点.md) | 8 | `game/README.md:14,21–22,25–36`、`game/data/characters/granny.json:10–18`、`game/data/characters/zhou.json:4–20`、`game/text/zh.csv:6,13–14,22,32–33` | 设计条件有据，结局检查实现没查清 |
| [06 数值](06_数值.md) | 9 | `game/data/settings.json:2–4`、`game/data/characters/granny.json:4–6,12–18`、`game/data/characters/zhou.json:4–6,19`、`game/README.md:8–14,27`、`game/text/zh.csv:5`、`game/text/en.csv:5`、`project.json:207–211` | 配置值有据，资金校验与记账实现没写 |
| [07 文本](07_文本.md) | 10 | `game/text/zh.csv:1–33`、`game/text/en.csv:1–31`、`game/data/characters/granny.json:3–15`、`game/data/characters/zhou.json:3–20`、`project.json:179–205`、`review_out/20261119_153004/_text_checks.md:8–20,29–35` | 数据字面量和两张表有据，实际呈现没查清 |
| [08 互相牵连](08_互相牵连.md) | 3 | `game/data/characters/granny.json:12–18`、`game/data/characters/zhou.json:16,20`、`game/text/zh.csv:15,33`、`game/README.md:27,32–36` | 已配条件有据，台词优先级和阿婆获知途径未写 |
| [09 伸进宿主的地方](09_伸进宿主的地方.md) | 1 | `game/README.md:1–3` | 无宿主，留占位页 |
| [10 顺手看到的](10_顺手看到的.md) | 8 | `game/text/zh.csv:4–5,13–16,23–25,30`、`game/text/en.csv:4–5,13–16,22–25,28`、`game/data/settings.json:2,5–7`、两份角色数据和图片静态表 | 记录供复走的线索 |
| [11 设置和便利](11_设置和便利.md) | 3 | `game/text/zh.csv:2–6`、`game/text/en.csv:2–6`、`game/data/settings.json:7`、`game/README.md:7,11–12,23` | 最没把握，玩家菜单、默认值与存储未提供 |

## 不变量对应位置

| 项目设置原文 | 对应地图行 | 出处 |
|---|---|---|
| 阿婆的钱要够买她要的东西，至少在少收一点以后够。 | 06「折后价（茶摊）」「客人预算」「discount」 | `project.json:132`、`game/data/settings.json:3–4`、`game/data/characters/granny.json:5–6` |
| 第 6 天以前，玩家看得到的文字里不出现老周的来历。 | 01 老周「请求留宿」、07「option_」「zhou_」 | `project.json:133,179–191`、`game/README.md:28–29`、`game/text/zh.csv:4,22` |
| 阿婆第 7 天说的话，只能提到她可能知道的事。 | 01 阿婆「第 7 天」、08 第一、二行 | `project.json:134`、`game/data/characters/granny.json:12–15`、`game/text/zh.csv:15–16` |

## 没读到的

- 两条角色线与作品的八个文本文件已读。五张图片依据静态像素表及项目数据定位，未逐张打开查看。出处 `game/README.md:3,18,25–36`、`game/RULES.md:3–4`、`review_out/20261119_153004/_summary.md:7–15`、`review_out/20261119_153004/_image_hits.md:21–33`。
- 没有可读的运行程序或行为实现。日内先后、同时符合的台词取哪条、支付失败、按钮及设置实际可见时点、存档与清除行为无法由资料确定。出处 `game/README.md:3,5–14`、`game/data/characters/granny.json:7–18`、`game/data/characters/zhou.json:7–20`、`game/data/settings.json:1–8`。
