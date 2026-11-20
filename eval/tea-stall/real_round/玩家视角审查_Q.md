# 玩家视角审查 · Q 想要的选项（2026-11-19）

范围：ALL，阿婆、老周和共用流程。走法：想要的选项。画像：1 好心人、2 精明生意人、21 举报者、28 对着干的人。作品地图：`_map/_map.md` 及第 02、11 表。静态表：`_summary.md`、`_text_checks.md`、`_image_hits.md`。

## 结论

在纸面流程核了点茶、留宿请求、收礼和设置等选择。三条缺口分别出现在阿婆买茶、老周报官与给茶让价，涉及三类玩家。阿婆对少收和拒卖已有不同回应，老周三种答复也各有去向。本组严重 0、中 0、轻 0、要老板定 0，想要但没有的 3 条。

## 玩家反馈

### 1 好心人玩到了给阿婆少收、第 6 天让老周留宿

- 想要的：「我想直接请客喝一壶。现在最多只能点『少收一点』。」（→ W3）
- 做对了的：「一直少收，最后一天阿婆特意送我她晒的花。」（`game/data/characters/granny.json:18` 原文 `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`，`game/text/zh.csv:16` 原文 `granny_last_warm,这是我自己晒的花，你拿去泡。`）
- 一句话：「少收过几回，阿婆真来送花。我还想偶尔请客喝一壶。」（→ W3；`game/data/characters/granny.json:18` 原文 `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`）

### 2 精明生意人玩到了照价卖粗茶和两次不卖茉莉

- 想要的：「老周能点最便宜的粗茶，阿婆买不起茉莉时，我也想问她要不要换粗茶。」（→ W1）
- 做对了的：「头一次没卖给阿婆，她明说下回还这样就不来了。」（`game/data/characters/granny.json:11` 原文 `"afterRefused": [ "granny_warn" ],`，`game/text/zh.csv:14` 原文 `granny_warn,你今天不卖我……下回再这样，我就不来了。`）
- 一句话：「我想照价卖另一款，菜单只让我照价卖原单、少收或不卖。」（→ W1）

### 21 举报者玩到了第 6 天报官、次日看小结

- 想要的：「我按了『去报官』，第二天只写『昨夜有人被带走』。我想知道我那件报案有没有受理，带走的是不是他。」（→ W2）
- 做对了的：「隔天的小结提到了有人被带走。」（`game/data/characters/zhou.json:20` 原文 `"summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }`，`game/text/zh.csv:33` 原文 `summary_taken,昨夜有人被带走。`）
- 一句话：「有报官的后话，我想要一条能和我那次选择对上的回执。」（→ W2）

### 28 对着干的人玩到了全拒与全答应两个分支

- 做对了的：「我回绝了留宿，他回答『……知道了。』。另一次答应他，第二天桌上有他留下的铜扣。」（`game/data/characters/zhou.json:15` 原文 `{ "button": "btn_refuse", "reply": "zhou_refused" },`，`game/text/zh.csv:25` 原文 `zhou_refused,……知道了。`，`game/data/characters/zhou.json:19` 原文 `"gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },`，`game/data/items.json:6` 原文 `"old_button": { "image": "images\\items\\old_button.png", "where": "table" }`）
- 一句话：「全拒与答应他会走到不同的结果。」（`game/data/characters/zhou.json:15` 原文 `{ "button": "btn_refuse", "reply": "zhou_refused" },`，`game/data/characters/zhou.json:19` 原文 `"gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },`）

### 好几类玩家都会说的

没有三类画像都提出的同一缺口。

### 只有一类玩家会说、但很重的

本组没有严重问题。

## 问题一览

本组只提交下列选项和回应缺口。

## 想要但没有的

| 缺口 | 几个画像想要 | 没有它会怎样 |
|---|---|---|
| W1 阿婆买不起茉莉时改问要不要粗茶 | 1 类，精明生意人 | 坚持照价的玩家只能拒绝原单；连拒两次后阿婆不来 |
| W2 报官后有能对上这次选择的回执 | 1 类，举报者 | 配置中当场无专属回复，次晨只有匿名小结 |
| W3 给客人白送一壶茶 | 1 类，好心人 | 只能收全价、收折后价或不交茶 |

### W1 阿婆点茉莉钱不够时，生意人缺少提议换粗茶的选项

- 谁想要：2 精明生意人。
- 在哪一步：第 1 天阿婆第一次点茶，第 3 天再次点茶。
- 他想做什么、为什么：按标价卖一款她付得起的茶。阿婆点茉莉，预算 10 文，茉莉价 12 文，粗茶价 4 文。`game/data/characters/granny.json:5` 原文 `"wants": "jasmine",`，`game/data/characters/granny.json:6` 原文 `"budget": 10,`，`game/data/settings.json:3` 原文 `"prices": { "jasmine": 12, "coarse": 4 },`。
- 现在有的选项：「照价卖」「少收一点」「不卖」。`game/README.md:10` 原文 `4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。`；`game/text/zh.csv:28` 原文 `btn_sell,照价卖`；`game/text/zh.csv:29` 原文 `btn_discount,少收一点`；`game/text/zh.csv:30` 原文 `btn_refuse,不卖`。
- 没有它，他只能：照价派按「不卖」。愿让价时，茉莉的固定折后价 9 文在预算内，但仍是茉莉订单。连着两次按「不卖」会让阿婆离开。`game/data/settings.json:4` 原文 `"discount": 3,`，`game/data/characters/granny.json:17` 原文 `"leaveForever": { "refusedInARow": 2 },`。
- 作品里别处有没有同类的选项：粗茶有另一个来客正常点，已配货架位置。阿婆订单没有询问换茶的入口。`game/data/items.json:4` 原文 `"coarse": { "image": "images\\items\\coarse_brick.png", "where": "shelf" },`。
- 把握：【确定没有】针对现有设计中的选择。全作品文本搜了「换茶」「改点」「换一壶」「替代」、`swap`、`replace`、`substitut`、`btn_`、`choices`。选项与点单资料只列原订单的三种决定。
- 可以怎么加：加入「问她要不要粗茶」和一句同意或谢绝的回话，得到同意后才按粗茶标价成交。

### W2 举报后，举报者想看到能对上这次选择的回执

- 谁想要：21 举报者。
- 在哪一步：第 6 天听老周请求，按「去报官」，第 7 天早上查看小结。
- 他想做什么、为什么：确认举报是否受理，之后再核对老周的去向。
- 现在有的选项：「让他躲一晚」「不卖」「去报官」。`game/text/zh.csv:31` 原文 `btn_shelter,让他躲一晚`、`game/text/zh.csv:30` 原文 `btn_refuse,不卖`、`game/text/zh.csv:32` 原文 `btn_report,去报官`。留宿、拒绝分支各配回复，报官分支只配结局条件。`game/data/characters/zhou.json:14` 原文 `{ "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },`、`game/data/characters/zhou.json:15` 原文 `{ "button": "btn_refuse", "reply": "zhou_refused" },`、`game/data/characters/zhou.json:16` 原文 `{ "button": "btn_report", "sets": "flag:zhou_taken" }`。
- 没有它，他只能：等到第 7 天早上，看到「昨夜有人被带走。」小结没有说是否从玩家这次报告开始核查，也没有说带走的是谁。`game/data/characters/zhou.json:20` 原文 `"summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }`、`game/text/zh.csv:33` 原文 `summary_taken,昨夜有人被带走。`。
- 作品里别处有没有同类的选项：文档把次日小结列为报官回应，没找到可查询的受理记录。
- 把握：【确定没有】现有资料没有专属受理回执。全作品文本搜了「报官」「受理」「回执」「确认」、`report`、`receipt`、`confirm`。没有运行界面可查按键本身的通用反馈。
- 可以怎么加：按下后给一句「已向官府报案」。也可以让次日小结提到昨日报告或摊后投宿者。

### W3 好心人想请客喝茶，折后仍要向客人收钱

- 谁想要：1 好心人。
- 在哪一步：阿婆点茉莉或老周点粗茶。
- 他想做什么、为什么：好心人目前每次少收，有时会想把茶白送给客人，做比固定少收更彻底的让利。
- 现在有的选项：「照价卖」「少收一点」「不卖」。`game/README.md:10` 原文 `4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。`；`game/text/zh.csv:28` 原文 `btn_sell,照价卖`；`game/text/zh.csv:29` 原文 `btn_discount,少收一点`；`game/text/zh.csv:30` 原文 `btn_refuse,不卖`。
- 没有它，他只能：卖茶时按全价或固定折扣。茉莉少 3 文后仍收 9 文，粗茶少 3 文后仍收 1 文。`game/data/settings.json:3` 原文 `"prices": { "jasmine": 12, "coarse": 4 },`、`game/data/settings.json:4` 原文 `"discount": 3,`。
- 作品里别处有没有同类的选项：有客人送花和铜扣的动作，方向是客人给茶摊。未列摊主送茶。
- 把握：【确定没有】全作品文本搜了「白送」「赠茶」「免费」、`free`、`gift`、`btn_`。礼物字段只对应客人送物，菜单没有零价档。
- 可以怎么加：加入「这壶请你」及对应回话，再决定这笔是否计入角色记住的让利。

## 要老板定

本组无此类条目。

## 查过、没问题的

- 第 6 天可以拒绝留宿。有 `game/data/characters/zhou.json:15` 原文 `{ "button": "btn_refuse", "reply": "zhou_refused" },`；中文回话是 `game/text/zh.csv:25` 原文 `zhou_refused,……知道了。`。中文按钮复用「不卖」的文字另交画像走查看。
- 报官确有次日回应，见 `game/data/characters/zhou.json:20` 原文 `"summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }` 和 `game/text/zh.csv:33` 原文 `summary_taken,昨夜有人被带走。`。W2 限于可核对的回执。
- 阿婆少收有感谢，达到门槛可送花；不卖有警告与离场。`game/data/characters/granny.json:10` 原文 `"afterDiscount": [ "granny_thanks" ],`、`game/data/characters/granny.json:11` 原文 `"afterRefused": [ "granny_warn" ],`、`game/data/characters/granny.json:17` 原文 `"leaveForever": { "refusedInARow": 2 },`、`game/data/characters/granny.json:18` 原文 `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`。
- 对着干的玩家可不收礼。收摊会清走未收的物品，见 `game/data/settings.json:6` 原文 `"table": { "hit": "pixel", "sweepAtClose": true },`。提示图标无点击功能，货架按整格点取，见 `game/data/settings.json:7` 原文 `"hints": { "icon": "images\\ui\\hint_icon.png", "clickable": false }`、`game/data/settings.json:5` 原文 `"shelf": { "hit": "cell" },`。
- 第 2、4 天总想先报官，没有可供指认的剧情事实；第 6 天才配置留宿请求和报官按钮。`game/data/characters/zhou.json:4` 原文 `"visits": { "days": [ 2, 4, 6 ] },`、`game/data/characters/zhou.json:10` 原文 `"day6": [ "zhou_ask_1" ]`、`game/data/characters/zhou.json:16` 原文 `{ "button": "btn_report", "sets": "flag:zhou_taken" }`。

## 这次没走到的

- 没有运行程序。支付失败、选错茶、主动等待、提前收摊、留宿选项暂不选择的界面，及存档读档之后的变化都没有可核的行为代码。若有可玩版本，依次测试全价卖茉莉失败、故意点粗茶、让客人等待并跨到下一天、存读后查看来客记录和未收桌上物。
- 显示提示和中英文本在数据中有位置，实际菜单、切换时机、默认值与保存方式没有资料。检查可玩版本的设置页与回到标题页再进游戏后的状态。
- 茉莉、粗茶、旧铜扣、花与提示图只查了落点、判定和统计。实际触控大小、界面动效、显示与声音需要可玩版本。

## 索引

编号 | 严重 | 把握 | 文件:行 | 那一行的原文
--- | --- | --- | --- | ---
W1 | 想要 | 确定没有 | game/README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。
W1 | 想要 | 确定没有 | game/text/zh.csv:28 | btn_sell,照价卖
W1 | 想要 | 确定没有 | game/text/zh.csv:29 | btn_discount,少收一点
W1 | 想要 | 确定没有 | game/text/zh.csv:30 | btn_refuse,不卖
W1 | 想要 | 确定没有 | game/data/characters/granny.json:5 | "wants": "jasmine",
W1 | 想要 | 确定没有 | game/data/characters/granny.json:6 | "budget": 10,
W1 | 想要 | 确定没有 | game/data/settings.json:3 | "prices": { "jasmine": 12, "coarse": 4 },
W1 | 想要 | 确定没有 | game/data/settings.json:4 | "discount": 3,
W1 | 想要 | 确定没有 | game/data/characters/granny.json:17 | "leaveForever": { "refusedInARow": 2 },
W1 | 想要 | 确定没有 | game/data/items.json:4 | "coarse": { "image": "images\\items\\coarse_brick.png", "where": "shelf" },
W2 | 想要 | 确定没有 | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },
W2 | 想要 | 确定没有 | game/data/characters/zhou.json:15 | { "button": "btn_refuse", "reply": "zhou_refused" },
W2 | 想要 | 确定没有 | game/data/characters/zhou.json:16 | { "button": "btn_report", "sets": "flag:zhou_taken" }
W2 | 想要 | 确定没有 | game/text/zh.csv:31 | btn_shelter,让他躲一晚
W2 | 想要 | 确定没有 | game/text/zh.csv:30 | btn_refuse,不卖
W2 | 想要 | 确定没有 | game/text/zh.csv:32 | btn_report,去报官
W2 | 想要 | 确定没有 | game/data/characters/zhou.json:20 | "summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }
W2 | 想要 | 确定没有 | game/text/zh.csv:33 | summary_taken,昨夜有人被带走。
W3 | 想要 | 确定没有 | game/README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。
W3 | 想要 | 确定没有 | game/text/zh.csv:28 | btn_sell,照价卖
W3 | 想要 | 确定没有 | game/text/zh.csv:29 | btn_discount,少收一点
W3 | 想要 | 确定没有 | game/text/zh.csv:30 | btn_refuse,不卖
W3 | 想要 | 确定没有 | game/data/settings.json:3 | "prices": { "jasmine": 12, "coarse": 4 },
W3 | 想要 | 确定没有 | game/data/settings.json:4 | "discount": 3,
