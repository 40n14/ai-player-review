# 玩家视角审查 · M 经济和数值漏洞（2026-11-19）

范围：全部，两位客人和共用交易、物品、结算。走法：经济和数值漏洞。画像：2 精明生意人（中立中立），用于判断会查看哪些数。作品地图：`_map`。静态表：`_text_checks.md`、`_image_hits.md`。数值表：`game\data\settings.json`、两份 `game\data\characters` 客人表、`game\data\items.json`。

## 结论

未查实能刷钱、重复领取、错走结局或损失物品的经济漏洞。阿婆预算 10 文，茉莉原价 12 文，折后 9 文，满足项目写明的不变量。原价选项在她钱不够时如何提示，仍要等交易界面验证。指南多写了一个座位，英文感谢台词省了少收金额。严重 0 条，中 1 条（可能），轻 2 条，要老板定 0 条，想要但没有的 1 条（可能）。项目没有另填 `reviewFocus`，本次重点核了预算、折扣、礼物和收摊结算。

## 玩家反馈

### 2 精明生意人（中立中立）玩到了阿婆点单、少收回话和夜里账本

- 看不懂的：「阿婆点茉莉，菜单里有『照价卖』。要是这单卖不成，我想知道是差多少钱。」（→ M1）
- 查价时看到的：「指南说同时能接三位客人。英文那句感谢只说上回有少收，没说少收多少。」（→ L1、L2）
- 想要的：「我夜里想按单对账，看看给哪一桌少收了多少。」（→ W1）
- 做对了的：「我给阿婆少收过，她后来专门说她记得。」（`game\text\zh.csv:13` 原文 `granny_thanks,上回你少收了我{0}文，我记着呢。`）
- 一句话：「少收之后有回话，我收摊还想查这笔到底收了多少。」（→ W1；`game\text\zh.csv:13` 原文 `granny_thanks,上回你少收了我{0}文，我记着呢。`）

## 进项表

钱按标价和折扣计算，只表示单笔成交金额。库存成本和实付记账规则未提供，不能当作净利润。

| 进项 | 数值 | 条件和重复次数 | 冷却或时点 | 出处 |
|---|---:|---|---|---|
| 茉莉茶收入 | 原价 12；折后 `12 − 3 = 9` | 阿婆点茉莉，预算 10。原价差 2，折后余 1。第 1、3、5、7 天有配置来访，同一次能否重复交易及预算是否重置未写 | 来访相隔两天，连续拒卖两次提前结束。第 7 天交易和送礼先后未知 | `game\data\settings.json:3–4`、`game\data\characters\granny.json:4–6,17–18` |
| 粗茶收入 | 原价 4；折后 `4 − 3 = 1` | 老周点粗茶，预算 4。原价刚好，折后余 3。第 2、4 天常规来访，第 6 天另有留宿选项，是否另做交易未知 | 按列出的来访日，同次成交冷却未写 | `game\data\settings.json:3–4`、`game\data\characters\zhou.json:4–6,10–17` |
| 阿婆的花 | 1 包礼物，未列货币价格 | 少收至少 2 次且走到第 7 天，点桌上的礼物收进柜子 | 第 7 天，是否有已领取标记未知 | `game\README.md:21–22,27`、`game\data\characters\granny.json:18`、`game\data\items.json:5` |
| 老周的旧铜扣 | 1 枚礼物，未列货币价格 | 第 6 天答应留宿，第 7 天点桌上的礼物收进柜子 | 第 7 天，是否有已领取标记未知 | `game\README.md:21–22,30`、`game\data\characters\zhou.json:14,19`、`game\data\items.json:6` |
| 阿婆记得少收 | 每次实际少收计一次，2 次解锁礼物条件 | 阿婆来访，选「少收一点」。感谢台词单独配置。未找到数值好感、经验、熟练度、声望或抽取次数 | 可跨来访累积。入账和持久化时点未知 | `game\text\zh.csv:6,29`、`game\README.md:27`、`game\data\characters\granny.json:10,14,18` |

## 出项表

| 出项 | 数值或结果 | 条件和重复次数 | 冷却或时点 | 出处 |
|---|---|---|---|---|
| 每单折扣 | 少收 3 文 | 选择「少收一点」。以两种标价计算，少收后的金额均为正数 | 成交时的取值实现未提供 | `game\data\settings.json:3–4`、`game\README.md:9–10` |
| 订单给出的茶 | 一位客人点一样东西，库存增减和成本未列 | 从货架点取。同次能否反复交付未写 | 货架按格取茶 | `game\README.md:9–10,20`、`game\data\items.json:3–4` |
| 拒卖 | 该次没有售茶收入。连续拒卖阿婆 2 次，失去后续订单和到访送礼机会 | 阿婆可能先警告。老周的第 6 天拒绝是留宿分支 | 阿婆按连续次数，老周的留宿选择配置在第 6 天 | `game\README.md:27,30`、`game\data\characters\granny.json:11,17`、`game\data\characters\zhou.json:13–19` |
| 报官 | 没配置钱货奖罚，失去好结局条件和本分支的旧铜扣 | 第 6 天选择「去报官」 | 第 7 天早上小结，第 7 天收摊出结局 | `game\data\characters\zhou.json:14–20`、`game\README.md:14,30,34–35` |
| 收摊扫桌 | 每一件还在桌上的礼物被扫掉 | 没点取礼物就收摊，可分别影响两件礼物 | 第 7 天礼物当日收摊，收入柜子后另无清理规则 | `game\README.md:21–22`、`game\data\settings.json:6` |

## 问题一览

| # | 严重 | 把握 | 角色 | 玩家看到的（一句话） | 画像或格子 |
|---|---|---|---|---|---|
| M1 | 中 | 可能 | 阿婆 | 阿婆付不起原价，「照价卖」是否说明差额未知 | 第 1 天，按原价交易 |
| L1 | 轻 | 确定 | 通用 | 中英文指南写三个座位，配置和设计写两个 | 摆摊，查座位容量 |
| L2 | 轻 | 确定 | 阿婆 | 英文感谢少收时省了金额 | 少收后看阿婆回话 |

## 问题

### M1 阿婆付不起原价，「照价卖」可能不给玩家说清差额

- 严重：中　把握：【可能】　角色：阿婆　画像：2 精明生意人。
- 怎么遇到：第 1 天阿婆要茉莉。拿茶，选「照价卖」。听她怎么回应，再核对夜里的账本。账本所列的收入应能和实际交易结果对应。
- 玩家看到：阿婆说「老样子，一壶茉莉。」（`game\text\zh.csv:10` 键 `granny_first_1`）。通用菜单写「照价卖」「少收一点」「不卖」（`game\text\zh.csv:28–30`）。资料没有写阿婆付不起时界面会显示哪一句。
- 为什么不对：买家预算 10 文，照价要 12 文，少收后 9 文。按原价遇到失败时，玩家需要知道差两文以及还能怎样成交。对照：玩家的合理期待。
- 出处：`game\data\characters\granny.json:4–6` 原文依次为 `  "visits": { "firstDay": 1, "everyDays": 2 },`、`  "wants": "jasmine",`、`  "budget": 10,`。`game\data\settings.json:3–4` 原文依次为 `  "prices": { "jasmine": 12, "coarse": 4 },`、`  "discount": 3,`。`game\README.md:10` 原文 `4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。`。`game\README.md:12` 原文 `6. 夜里看账本：今天赚了多少、谁来过。`
- 反查：在 `game` 的 JSON、CSV、Markdown 查过 `budget`、`btn_sell`、`不够`、`欠`、`赊`、`refund`。有预算、通用按钮和确实买得起的折后价。支付失败提示、原价按钮是否会禁用、尝试原价后能否即时改选，资料没有说明。
- 建议：在点单旁显示原价、折后价和客人预算。若结算会失败，直接提示「还差 2 文」，保留少收选项。
- 测试里怎么复现：新局第 1 天 → 点取茉莉 → 看阿婆预算和两档价是否可见 → 选「照价卖」→ 查失败提示、能否当场改选、夜里是否有入账 → 过一天再查有没有误记为拒卖。在另一局直接选「少收一点」，对照账本应记的 9 文。验证版若支持存档，再读档看收入是否和实际成交一致。

### L1 指南写能招待三位客人，摊位定义只有两个座位

- 严重：轻　把握：【确定】　角色：通用　画像：2 精明生意人。
- 怎么遇到：摆摊前查游戏说明的第一条，按上面的容量安排接待。
- 玩家看到：中文「茶摊同时最多招待三位客人。客人等久了会走。」；英文「The stall can serve up to three guests at once. Guests leave if they wait too long.」（`game\text\zh.csv:5`、`game\text\en.csv:5`，键 `guide_page_1`）。
- 为什么不对：两种语言都把可接待数多写了一位。对照：说明和实际设定。现有两位客人按奇偶日到访，没有配置第三位普通客人，未发现因此少卖一单的路线。
- 出处：`game\data\settings.json:2` 原文 `  "stall": { "seats": 2, "days": 7 },`。`game\README.md:8` 原文 ``2. 摆摊。茶摊有两个座位（`data\settings.json` 的 `stall.seats`）。``
- 反查：在 `game` 的 JSON、CSV、Markdown 查过 `stall.seats`、`位客人`、`serve up to`。两份指南都说三位，规则和配置都指向两个座位，没有找到加座规则。`game\data\characters\granny.json:4` 原文 `  "visits": { "firstDay": 1, "everyDays": 2 },`。`game\data\characters\zhou.json:4` 原文 `  "visits": { "days": [ 2, 4, 6 ] },`。
- 建议：两种语言都改成两位，或让指南取配置的座位数。

### L2 阿婆的英文感谢省掉上一单少收的金额

- 严重：轻　把握：【确定】　角色：阿婆　画像：2 精明生意人。
- 怎么遇到：在阿婆的订单选「少收一点」，随后看到她针对少收的感谢。对照同一行中英文台词。
- 玩家看到：中文模板「上回你少收了我{0}文，我记着呢。」英文「You charged me less last time. I remember.」（`game\text\zh.csv:13`、`game\text\en.csv:13`，键 `granny_thanks`）。中文模板有金额位，英文省掉了它。中文运行时能否填成 `3` 未核实。
- 为什么不对：作为上一笔交易的回话，英文固定文本只确认发生过少收，没交代少收多少。对照：双语文本对同一笔交易提供的信息不一致。
- 出处：`game\data\characters\granny.json:10` 原文 `    "afterDiscount": [ "granny_thanks" ],`。`game\data\settings.json:4` 原文 `  "discount": 3,`。两份表的整行原文见索引。
- 反查：在 `game` 的 JSON、CSV、Markdown 查过 `granny_thanks`、`discount`、`charged me less`。只有这一个感谢键，没找到英文的另一行金额回话。账本是否会另给这笔明细未写。
- 建议：英文保留与中文同义的金额位，并核对两种文本都能取到实际少收金额。

## 想要但没有的

### W1 算账的玩家想在夜里按订单核对收入和折扣

- 谁想要：2 精明生意人。在哪一步：少收成交后，夜里打开账本。
- 他想做什么、为什么：核对阿婆这单实际是不是收了 9 文，也对照客人是否到访。现有常规来访日通常只有一位客人，玩家知道标价就能用当日总收入反推。逐单记录可以直接核对实际采用的价格和成交结果。
- 现在有的内容：夜里看全日赚了多少、谁来过（`game\README.md:12` 原文 `6. 夜里看账本：今天赚了多少、谁来过。`）。交易菜单有「照价卖」「少收一点」「不卖」（`game\text\zh.csv:28–30`，原文见索引）。
- 如果账本没有明细，玩家就只能靠当日汇总和自己的记忆对账。阿婆的感谢只覆盖该角色的折扣路线（`game\data\characters\granny.json:10` 原文 `    "afterDiscount": [ "granny_thanks" ],`）。
- 把握：【可能没有】。查过作品文本和数据中的 `账本`、`折扣`、`交易`、`ledger`、`discount`，只找到汇总说明和交易记录条件。没运行界面，看不到账本是否另设明细，同类入口也没查到。
- 可以怎么加：在夜间账本为每单显示客人、茶、标价、减价和实收，未成交也留一句原因。其他缺选项由 Q 组走查。

## 要老板定

无。

## 查过、没问题的

- 阿婆并非连折后也买不起。`12 − 3 = 9 ≤ 10`，符合 `project.json:132` 原文 `    "阿婆的钱要够买她要的东西，至少在少收一点以后够。",`。老周的粗茶原价恰好是预算，折后也大于零。`game\data\settings.json:3–4` 原文 `  "prices": { "jasmine": 12, "coarse": 4 },`、`  "discount": 3,`。`game\data\characters\zhou.json:6` 原文 `  "budget": 4,`。当前配置没有 0、负数、小数或重复叠加折扣的标价入口。
- 售茶、柜中礼物均无第二个售卖方向可组成完整闭环。`game\README.md:20–21` 原文分别是 ``- **货架**：茶在货架的格子里。玩家点格子就拿起来（按整格判定，`data\settings.json` 的 `shelf.hit` = `cell`）。``、``- **桌上**：客人送的东西留在桌上。玩家点它，收进柜子。点在图的透明处不算点中（按图的形状判定，`table.hit` = `pixel`）。`` 全作品文本中没找到 `回购`、`转卖`、`resell` 对应入口，两件礼物没有标价。不能把礼物当回款，也不能把成交金额当净赚。
- 连着两次来访都拒卖后，设计会停掉阿婆之后的订单。`game\data\characters\granny.json:17` 原文 `  "leaveForever": { "refusedInARow": 2 },`，`game\text\zh.csv:14` 原文 `granny_warn,你今天不卖我……下回再这样，我就不来了。`。读档后是否还执行这条未知。
- 报官没有可抵掉结局后果的钱货奖励。`game\data\characters\zhou.json:16` 原文 `      { "button": "btn_report", "sets": "flag:zhou_taken" }`，`game\README.md:34` 原文 `- 好结局：阿婆送了花，而且老周没有被带走。`。第 6 天留宿分支才有旧铜扣条件，拒绝分支只配回话。

## 这次没走到的

- 只有数据、文本和设计，没有交易、存档和结算程序（`game\README.md:3` 原文 `这是给审查工具包做演示用的假游戏。没有可以运行的程序，只有设计、数据和文本。`）。没法确定余额是否逐单扣减、是否跨来访重置、库存会不会减到负数、连续点击是否重记及记录如何保存。待验证：一笔售茶时连续点击 → 查货和钱各变几次 → 收摊看账本 → 支持读档时载入成交前后两种档。
- 两件礼物都配置在第 7 天，未找到已领取、存档或随机参数。待验证：第 1、3 天给阿婆少收，第 6 天让老周留宿 → 第 7 天把礼物依次收入柜子 → 重进场景、读档后查看桌上、柜内件数 → 对照留在桌上直接收摊的结局。也需比较第 5、7 天凑够两次时礼物是在最后一笔交易前还是之后判断。没有随机机制的现成事实可重摇。
- 第 6 天是否还做粗茶生意、第 7 天阿婆说「茶我不喝了」时是否还有交易入口，资料没定（`game\data\characters\zhou.json:10–17`、`game\data\characters\granny.json:5,13–14`、`game\text\zh.csv:15` 原文 `granny_last_cold,……他们昨夜把人带走了。茶我不喝了。`）。待验证：第 6 天选择报官，分别在先前少收 0 次和 2 次的局过到第 7 天 → 查阿婆实际台词、交易按钮、赠花和当日收入。
- 没找到跳日、交租、还债或金钱罚款入口。第 7 天收摊出结局有文档规定（`game\README.md:14` 原文 `一局 7 天。第 7 天收摊以后出结局。`），无法验证退出、关门或读档是否跳过结算。待有可运行版本时，比较正常收摊和中断后进入下一天的早间小结、礼物及结局。
- 地图本次所用条目回原始资料核对后可作线索，地图也没有补上余额、存货、持久化和日内时序。座位显示、按钮状态、账本明细均留待运行验证。静态图片表显示铜扣面积小，相关拾取问题属 S 组走法。本组未测点击手感。
- 两条关于剧透和阿婆获知老周去向的不变量涉及台词和举报路线，本组只核对应路线的交易和钱货后果。

## 索引

编号 | 严重 | 把握 | 文件:行 | 那一行的原文
M1 | 中 | 可能 | game\data\characters\granny.json:4 |   "visits": { "firstDay": 1, "everyDays": 2 },
M1 | 中 | 可能 | game\data\characters\granny.json:5 |   "wants": "jasmine",
M1 | 中 | 可能 | game\data\characters\granny.json:6 |   "budget": 10,
M1 | 中 | 可能 | game\data\settings.json:3 |   "prices": { "jasmine": 12, "coarse": 4 },
M1 | 中 | 可能 | game\data\settings.json:4 |   "discount": 3,
M1 | 中 | 可能 | game\README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。
M1 | 中 | 可能 | game\README.md:12 | 6. 夜里看账本：今天赚了多少、谁来过。
M1 | 中 | 可能 | game\text\zh.csv:10 | granny_first_1,老样子，一壶茉莉。
M1 | 中 | 可能 | game\text\zh.csv:28 | btn_sell,照价卖
M1 | 中 | 可能 | game\text\zh.csv:29 | btn_discount,少收一点
M1 | 中 | 可能 | game\text\zh.csv:30 | btn_refuse,不卖
L1 | 轻 | 确定 | game\text\zh.csv:5 | guide_page_1,茶摊同时最多招待三位客人。客人等久了会走。
L1 | 轻 | 确定 | game\text\en.csv:5 | guide_page_1,The stall can serve up to three guests at once. Guests leave if they wait too long.
L1 | 轻 | 确定 | game\data\settings.json:2 |   "stall": { "seats": 2, "days": 7 },
L1 | 轻 | 确定 | game\README.md:8 | 2. 摆摊。茶摊有两个座位（`data\settings.json` 的 `stall.seats`）。
L1 | 轻 | 确定 | game\data\characters\granny.json:4 |   "visits": { "firstDay": 1, "everyDays": 2 },
L1 | 轻 | 确定 | game\data\characters\zhou.json:4 |   "visits": { "days": [ 2, 4, 6 ] },
L2 | 轻 | 确定 | game\data\characters\granny.json:10 |     "afterDiscount": [ "granny_thanks" ],
L2 | 轻 | 确定 | game\data\settings.json:4 |   "discount": 3,
L2 | 轻 | 确定 | game\text\zh.csv:13 | granny_thanks,上回你少收了我{0}文，我记着呢。
L2 | 轻 | 确定 | game\text\en.csv:13 | granny_thanks,You charged me less last time. I remember.
W1 | 想要 | 可能没有 | game\README.md:12 | 6. 夜里看账本：今天赚了多少、谁来过。
W1 | 想要 | 可能没有 | game\text\zh.csv:28 | btn_sell,照价卖
W1 | 想要 | 可能没有 | game\text\zh.csv:29 | btn_discount,少收一点
W1 | 想要 | 可能没有 | game\text\zh.csv:30 | btn_refuse,不卖
