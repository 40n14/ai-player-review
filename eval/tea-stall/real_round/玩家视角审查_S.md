# 玩家视角审查 · S 软锁 / 卡死（2026-11-19）

范围：全部。走法：软锁 / 卡死。画像 4 马虎的人给出误点、漏收和错过的操作线索。地图：本轮 `_map`。静态表：本轮 `_summary.md`、`_image_hits.md`、`_text_checks.md`。

## 结论

旧铜扣和花包都按图片形状点击，透明处点不到。铜扣只有 5.9% 的原图像素不透明。玩家点空后直接收摊，会失去没收入柜的礼物，之后本局结束。现有设计里交易、对话及结局均有正常出口。严重 1、中 1、轻 0、要老板定 1、想要但没有的 0。

## 玩家反馈

### 4 马虎的人玩到了第 7 天收摊

- 觉得不公平的：「我在桌上那枚铜扣旁边点了一下，收摊后铜扣就没了，柜里也没有。」（→ S1）
- 看不懂的：「要是开局就能看到那条提示，它已经把那位客人的来历说了。」（→ M1，待确认）
- 做对了的：「我第一次没卖茶给阿婆，她告诉我再这样她就不来了。」（`game/text/zh.csv:14` 原文 `granny_warn,你今天不卖我……下回再这样，我就不来了。`）
- 一句话：「桌上那枚铜扣我没收成，收摊就没了。」（→ S1）

## 必经点

| 必经点 | 需要什么 | 能弄没吗 | 弄没以后 |
|---|---|---|---|
| 阿婆买茉莉 | 她来访。标价 12，少收后 9，她有 10 | 可按「不卖」。连着两次后她不再来 | 有首次警告，仍有普通结局。见 D1（`game/data/settings.json:3–4`、`game/data/characters/granny.json:4–6,17`、`game/README.md:10,27,35`） |
| 阿婆送花 | 第 7 天、少收至少两次 | 可在最早两次来访少收，避开最后一天触发顺序。先赶走她会失去此路线 | 花包点空还能再点，留桌到收摊会丢。见 S1（`game/data/characters/granny.json:4,17–18`、`game/README.md:21–22,27`） |
| 老周说来历并求留宿 | 第 6 天来访 | 有三种回答。错过、取消或超时的处理未给 | 正常三条分支都有定义，只有第 6 天配置请求（`game/data/characters/zhou.json:4,10,12–20`、`game/README.md:28–30`） |
| 旧铜扣收入柜子 | 第 6 天留宿。第 7 天点中桌上的铜扣 | 点空后未补点，收摊时丢 | 只发这一天，本局结束。见 S1（`game/data/characters/zhou.json:14,19`、`game/data/items.json:6`、`game/README.md:14,21–22`） |
| 第 7 天早间小结 | 第 6 天报官 | 留宿和拒绝不设报官标记 | 没有抓人的小结是分支差异（`game/data/characters/zhou.json:14–16,20`、`game/text/zh.csv:33`） |
| 好结局或普通结局 | 第 7 天收摊。好结局要求阿婆送花且老周没被带走 | 报官或没送花会失去好结局 | 文档给了普通结局。实际是否要收花未知（`game/README.md:14,34–35`） |
| 三条不变量 | 折后买得起，身份第 6 天才说，阿婆只说可能知道的事 | 预算条件成立。设置说明若提前可见，可能破坏身份揭露 | 设置见 M1。阿婆只说有人被带走，早间小结也写同一事（`project.json:132–134`、`game/text/zh.csv:4,15,22,33`） |

## 问题一览

| # | 严重 | 把握 | 角色 | 玩家看到的 | 画像或格子 |
|---|---|---|---|---|---|
| S1 | 严重 | 确定 | 老周、阿婆 | 点到透明处收不起礼物，最后一天收摊后被清走 | 4、05、11 |
| M1 | 中 | 可能 | 老周 | 「显示提示」说明可能在第 6 天前说出来历 | 4、16 |

## 问题

### S1 第 7 天点空后直接收摊，铜扣或花包就没了

- 严重：严重。把握：【确定】（现有设计和数据中的条件路线）。角色：老周、阿婆。画像：4 马虎的人。
- 怎么遇到：
  1. 铜扣路线：第 6 天听完老周请求，按「让他躲一晚」。第 7 天桌上出现旧铜扣。花包路线：第 1、3 天各按一次「少收一点」，阿婆第 7 天送花。这两个条件可在同一局满足。
  2. 在礼物图片范围内点到透明处，没有再点中就收摊。
  3. 礼物没进柜子，收摊时被扫掉。本局进入结局，礼物没有再发的一天。
- 玩家看到：按「让他躲一晚」（`game/text/zh.csv:31` 键 `btn_shelter`）或两次按「少收一点」（`game/text/zh.csv:29` 键 `btn_discount`）。最后一天点到图的透明处时礼物留在原处，之后收摊便不在桌上或柜里。
- 为什么不对：玩家点击了礼物所占的位置，奖励没有收取，结束当天就失去本局取得这份礼物的机会。对照：合理期待。设计写了按图点击和清桌，资料未见漏收提醒。
- 出处：
  - `game/data/characters/zhou.json:14` 原文 `{ "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },`，第 19 行原文 `"gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },`。
  - `game/data/characters/granny.json:4` 原文 `"visits": { "firstDay": 1, "everyDays": 2 },`，第 18 行原文 `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`。折后价 9，预算 10，见必经点。
  - `game/data/items.json:5` 原文 `"dried_flowers": { "image": "images\\items\\dried_flowers.png", "where": "table" },`，第 6 行原文 `"old_button": { "image": "images\\items\\old_button.png", "where": "table" }`。
  - `game/data/settings.json:6` 原文 `"table": { "hit": "pixel", "sweepAtClose": true },`。`game/README.md:21` 原文为「- **桌上**：客人送的东西留在桌上。玩家点它，收进柜子。点在图的透明处不算点中（按图的形状判定，`table.hit` = `pixel`）。」第 22 行原文为「- 收摊时，桌上还没收的东西会被扫掉（`table.sweepAtClose`）。」第 14 行原文 `一局 7 天。第 7 天收摊以后出结局。`。
  - 本轮 `_image_hits.md:17` 的铜扣行记录原图 32×32、不透明 60 像素，占 5.9%。第 29 行的花包同样 32×32、不透明 624 像素，占 60.9%。这是原图比例。
- 反查：搜过 `old_button`、`dried_flowers`、`zhou_sheltered`、`sweepAtClose`、补发、存档和读档。礼物各有一个发放条件。点中非透明处能补救，收摊会结束机会。现有资料没有另外的收取方式、漏收提醒或补发入口。存读档行为未提供。
- 必经点和损失：第 7 天把桌面礼物收入柜子。这里能确定的后果是礼物丢失。`game/README.md:34` 写的是「阿婆送了花」，没有把铜扣或是否已经把花收进柜子列为好结局条件。
- 建议：给桌面礼物较宽的点击区域，例如和货架一样按整格判定。也可在收摊前提示还有礼物未收。

### M1 设置里的「显示提示」说明可能提前说出老周的来历

- 严重：中。把握：【可能】。角色：老周。画像：4 马虎的人。
- 怎么遇到：第 1–5 天打开设置，查看「显示提示」的说明。
- 玩家看到：若此时可见，会看到「打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。」（`game/text/zh.csv:4` 键 `option_hints_tip`）。英文同键也写明身份。
- 为什么不对：第 6 天自述前就会知道来历。对照：`project.json:133` 的不变量和 `game/README.md:29` 的设定。
- 出处：`game/text/zh.csv:4` 原文 `option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。`；`game/text/en.csv:4` 原文 `option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey.`；`game/README.md:29` 原文 `- 设定：老周的来历在第 6 天以前不能让玩家知道。`。
- 反查：搜过 `option_hints_tip`、`deserter`、`逃兵`、`zhou_ask_1`。第 6 天自述有日期条件（`game/data/characters/zhou.json:10` 原文 `"day6": [ "zhou_ask_1" ]`），设置说明的显示条件未提供。
- 建议：两种语言的设置说明都只写图标用途。
- 测试里怎么复现：新开一局 → 第 1 天查看中英「显示提示」说明 → 第 6 天听老周自述。要确认设置说明能否在开局看到。

## 想要但没有的

本组没有单独条目。

## 要老板定

### D1 连续两次没卖茶后，阿婆不再回来

- 把握：【设计】。角色：阿婆。画像：4 马虎的人。
- 怎么遇到：第 1 天、第 3 天都按「不卖」。第 1 天有「你今天不卖我……下回再这样，我就不来了。」的警告。
- 数据和设计一致：`game/data/characters/granny.json:17` 原文 `"leaveForever": { "refusedInARow": 2 },`。`game/text/zh.csv:14` 原文 `granny_warn,你今天不卖我……下回再这样，我就不来了。`。`game/README.md:27` 写「连着两次被"不卖"，她就不再来（第一次被拒绝时她会说一句警告）。」
- 玩家后果：第 5、7 天都见不到阿婆，拿不到她的花包。其他客人和普通结局仍有定义。
- 反查：搜 `refusedInARow`、`leaveForever`、`granny_warn`，只见退出条件、警告和正常来访。没有恢复来访的分支。
- 选项：
  1. （推荐）保留退出和首次警告，第二次操作前再提示。误按时能知道后果。
  2. 保留现状。读了警告的玩家可有意放弃这条线。漏过警告的人可能要等到下次才发现阿婆不来。
  3. 隔一次来访再让阿婆回来。玩家还有补救机会，但能达到送花条件的来访次数会变少。

## 查过、没问题的

- 茉莉预算不挡所有出口。`game/data/settings.json:3` 原文 `"prices": { "jasmine": 12, "coarse": 4 },`，第 4 行原文 `"discount": 3,`。`game/data/characters/granny.json:6` 原文 `"budget": 10,`。折后 9，满足折后能买的不变量。`game/README.md:10` 原文 `4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。`
- 粗茶图透明多，但仍可按格拿取。`game/data/items.json:4` 原文 `"coarse": { "image": "images\\items\\coarse_brick.png", "where": "shelf" },`。`game/data/settings.json:5` 原文 `"shelf": { "hit": "cell" },`。提示图标也是明确不可点（同文件第 7 行原文 `"hints": { "icon": "images\\ui\\hint_icon.png", "clickable": false }`）。
- 老周两个标记有写入。`game/data/characters/zhou.json:14` 原文 `{ "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },`，第 16 行原文 `{ "button": "btn_report", "sets": "flag:zhou_taken" }`。第 19、20 行分别用于礼物和小结。第 15 行原文 `{ "button": "btn_refuse", "reply": "zhou_refused" },`，拒绝留宿也是正常出口。
- 阿婆只说有人被带走。`game/text/zh.csv:15` 原文 `granny_last_cold,……他们昨夜把人带走了。茶我不喝了。`。`game/text/zh.csv:33` 原文 `summary_taken,昨夜有人被带走。`。早间小结也有同一事件。台词没有透露她知道老周的来历，她从哪里听说未交代。

## 这次没走到的

- `game/README.md:3` 写明没有运行程序。退出和打断请求、客人超时及让位、存读档、库存变化、柜满和清扫实现均待确认。待有程序时：第 6 天未回答请求时关闭窗口再回来。第 7 天礼物在桌、在柜、已扫三种状态各跨一次存读档。
- 第 7 天才达成第二次少收时，送花检查可能在交易之前，也可能在之后。两次少收且报官时，冷句和暖句两项条件可同时满足。`game/data/characters/granny.json:13–14,18` 未写优先级。待有程序时：第 5 天前仅少收一次，选报官，第 7 天再少收，记录台词、花包和结局。另走一局第 3 天已满足门槛作对照。
- 结局按送花还是收花判定、礼物的屏幕点击大小和设置说明可见时点待实测。箱中有花与花仍在桌上的结束结果需要比较。以上步骤先不跑。

## 索引

编号 | 严重 | 把握 | 文件:行 | 那一行的原文
S1 | 严重 | 确定 | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },
S1 | 严重 | 确定 | game/data/characters/zhou.json:19 | "gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },
S1 | 严重 | 确定 | game/data/characters/granny.json:4 | "visits": { "firstDay": 1, "everyDays": 2 },
S1 | 严重 | 确定 | game/data/characters/granny.json:6 | "budget": 10,
S1 | 严重 | 确定 | game/data/characters/granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }
S1 | 严重 | 确定 | game/data/items.json:5 | "dried_flowers": { "image": "images\\items\\dried_flowers.png", "where": "table" },
S1 | 严重 | 确定 | game/data/items.json:6 | "old_button": { "image": "images\\items\\old_button.png", "where": "table" }
S1 | 严重 | 确定 | game/data/settings.json:3 | "prices": { "jasmine": 12, "coarse": 4 },
S1 | 严重 | 确定 | game/data/settings.json:4 | "discount": 3,
S1 | 严重 | 确定 | game/data/settings.json:6 | "table": { "hit": "pixel", "sweepAtClose": true },
S1 | 严重 | 确定 | game/README.md:14 | 一局 7 天。第 7 天收摊以后出结局。
S1 | 严重 | 确定 | game/README.md:21 | - **桌上**：客人送的东西留在桌上。玩家点它，收进柜子。点在图的透明处不算点中（按图的形状判定，`table.hit` = `pixel`）。
S1 | 严重 | 确定 | game/README.md:22 | - 收摊时，桌上还没收的东西会被扫掉（`table.sweepAtClose`）。
S1 | 严重 | 确定 | game/README.md:34 | - 好结局：阿婆送了花，而且老周没有被带走。
S1 | 严重 | 确定 | game/text/zh.csv:29 | btn_discount,少收一点
S1 | 严重 | 确定 | game/text/zh.csv:31 | btn_shelter,让他躲一晚
M1 | 中 | 可能 | game/text/zh.csv:4 | option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。
M1 | 中 | 可能 | game/text/en.csv:4 | option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey.
M1 | 中 | 可能 | game/README.md:29 | - 设定：老周的来历在第 6 天以前不能让玩家知道。
M1 | 中 | 可能 | game/data/characters/zhou.json:10 | "day6": [ "zhou_ask_1" ]
D1 | 要老板定 | 设计 | game/data/characters/granny.json:4 | "visits": { "firstDay": 1, "everyDays": 2 },
D1 | 要老板定 | 设计 | game/data/characters/granny.json:17 | "leaveForever": { "refusedInARow": 2 },
D1 | 要老板定 | 设计 | game/text/zh.csv:14 | granny_warn,你今天不卖我……下回再这样，我就不来了。
D1 | 要老板定 | 设计 | game/text/zh.csv:30 | btn_refuse,不卖
D1 | 要老板定 | 设计 | game/README.md:27 | - **阿婆**（`granny`）：每两天来一次，要一壶茉莉。钱不多。连着两次被"不卖"，她就不再来（第一次被拒绝时她会说一句警告）。少收过她两次以上，第 7 天她会送一包自己晒的花。
D1 | 要老板定 | 设计 | game/README.md:35 | - 普通结局：别的情况。
