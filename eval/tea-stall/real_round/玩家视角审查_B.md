# 玩家视角审查 · B 举报和读档（2026-11-19）

范围：全部。走法：画像走查。画像：21 举报者、14 反复读档的人、18 点得飞快不读字的人。作品地图：本轮 `_map`。静态表：本轮 `_summary.md`、`_text_checks.md`、`_image_hits.md`。

走 21 × 阿婆、老周两条线，从开局到第 7 天收摊；14 在两条线上尝试各分支读档，实际保存与恢复没有实现资料；18 跳过台词，按首按钮拿东西。第 6 天按首按钮和报官冲突，分别推演报官与留宿路径。资料为设计、数据和文本，无可运行程序。

## 结论

留宿后，第 7 天的旧铜扣按不透明像素判定。玩家点到透明处后如果未能收进柜子，收摊就会清掉本局唯一一次送的铜扣。报官分支的第 7 天小结符合设计，但即使阿婆已经送花，举报仍只能走普通结局。留宿和拒绝的文字有问题，设置也可能提前说出老周来历。本组严重 1 条、中 5 条、轻 0 条、要老板定 1 条、想要但没有的 1 条。

## 玩家反馈

### 21 举报者玩到了报官后的第 7 天
- 想要的：「前两次见这个客人，按钮都只管卖不卖茶。我想试着报官，要等到他亲自开口那天。」（→ W1）
- 看不懂的：「设置里的提示说明把那个客人的来历写出来了。我还没听他说过。」（→ M1，待确认）
- 做对了的：「第六天去报官，隔天早上报了有人被带走。」（`game/data/characters/zhou.json:20` 原文 `"summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }`；`game/text/zh.csv:33` 原文 `summary_taken,昨夜有人被带走。`）
- 一句话：「想报官得等到第六天，按了隔天一早有小结。」（→ W1；`game/text/zh.csv:33` 原文 `summary_taken,昨夜有人被带走。`）

### 14 反复读档的人玩到了第 6 天三种选择及对应第 7 天（分支对照，存读档待确认）
- 看不懂的：「他问能不能过夜，拒绝的按钮却写着『不卖』。答应时还弹出『（占位）谢谢。』」（→ M3、M4）
- 看不懂的：「英文版拒绝他留宿，这里少了一句英文回话。」（→ M5）
- 觉得不公平的：「我拿到了阿婆送的花。报官这一趟最后还是普通结局。」（→ D1）
- 一句话：「第六天几个选项都试一遍，拒绝的字和留宿的回话最奇怪。」（→ M3、M4、M5）

### 18 点得飞快、不读字的人玩到了第 7 天收铜扣
- 看不懂的：「旧铜扣我点过一下，收完摊找不到了。」（→ S1）
- 做对了的：「粗茶点一下货架格子就拿起来了。」（`game/README.md:20` 原文 ``- **货架**：茶在货架的格子里。玩家点格子就拿起来（按整格判定，`data\settings.json` 的 `shelf.hit` = `cell`）。``；`game/data/items.json:4` 原文 `"coarse": { "image": "images\\items\\coarse_brick.png", "where": "shelf" },`）
- 一句话：「茶好拿。收摊前铜扣得点准，不然回头没了。」（→ S1；`game/data/settings.json:5` 原文 `"shelf": { "hit": "cell" },`）

## 问题一览

| # | 严重 | 把握 | 角色 | 玩家看到的（一句话） | 画像或格子 |
|---|---|---|---|---|---|
| S1 | 严重 | 确定 | 老周 | 点了旧铜扣图的透明处，没收进柜子，收摊就丢了 | 18 |
| M1 | 中 | 可能 | 老周 | 提示开关的说明写了第 6 天才应知道的来历 | 21 |
| M2 | 中 | 确定 | 共用 | 中英文说明上写同时可招待三位，配置是两位 | 21 |
| M3 | 中 | 确定 | 老周 | 拒绝留宿时，中文按钮写「不卖」 | 14 |
| M4 | 中 | 确定 | 老周 | 允许留宿后，回复出现占位字样 | 14 |
| M5 | 中 | 确定 | 老周 | 拒绝留宿后的回复没有英文文本 | 14 |

## 问题

### S1 点了旧铜扣却没收走，收摊后就丢了
- 严重：严重　把握：【确定】（按已写明的玩法和数据推演）　角色：老周　画像：18。
- 怎么遇到：第 6 天按列表第一项「让他躲一晚」。第 7 天旧铜扣在桌上。点一下铜扣图边缘的透明区，例如原图的左上角，未重试并收摊。
- 玩家看到：点一下没收进柜子，铜扣仍留在桌上。收摊清掉它，接着是结局，本局没有下一次领取。
- 为什么不对：旧铜扣只出现一次，32×32 图中只有 60 个像素会命中（5.9%，本轮 `_image_hits.md`）。按图的形状点很容易错过，清桌会把没收走的限时礼物带走。对照：玩家的合理期待。按像素命中和收摊清桌均有设计依据；组合起来导致这件一次性剧情物容易漏收。
- 出处：`game/data/characters/zhou.json:14` 原文 `{ "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },` → `game/data/characters/zhou.json:19` 原文 `"gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },` → `game/data/items.json:6` 原文 `"old_button": { "image": "images\\items\\old_button.png", "where": "table" }` → `game/data/settings.json:6` 原文 `"table": { "hit": "pixel", "sweepAtClose": true },`。收摊与末日见 `game/README.md:14` 原文 `一局 7 天。第 7 天收摊以后出结局。`。
- 反查：点到不透明部分可以收。找过 `old_button`、`zhou_sheltered`、`sweepAtClose`，唯一送礼是第 7 天，没有额外入口；整格规则只用于货架，`game/data/settings.json:5` 原文 `"shelf": { "hit": "cell" },`。
- 建议：优先为旧铜扣加宽点击范围，或把铜扣礼物设为收摊自动收入柜子。

### M1 提示说明可能在第 6 天前揭开老周来历
- 严重：中　把握：【可能】　角色：老周　画像：21。
- 怎么遇到：新局第 1 天尝试打开提示开关说明，随后走到第 6 天听老周开口。
- 玩家看到：如果说明可提前打开，会先读到「老周是逃兵，他的图标是灰色的」或「Old Zhou is a deserter, so his icon is grey.」（`option_hints_tip`）；第 6 天角色才说「……我是从营里跑出来的。能在你摊子后面躲一晚吗？」（`zhou_ask_1`）。
- 为什么不对：设置文字已写明来历和可识别颜色。若早于第 6 天展示，打破不变量。
- 出处：`game/text/zh.csv:4` 原文 `option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。`；`game/text/en.csv:4` 原文 `option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey.`；`game/README.md:29` 原文 `- 设定：老周的来历在第 6 天以前不能让玩家知道。`；`game/data/characters/zhou.json:10` 原文 `"day6": [ "zhou_ask_1" ]`。
- 反查：说明文字以 `option_` 登记在 `project.json` 的静态规则里；作品内没有找到调用此键的界面实现，不能确定第 1 天能否看见。剧情提问已限定在第 6 天，角色第 2、4 天卖茶时不会从此对白听出来。
- 建议：提示开关只说明图标的作用，保留第 6 天的剧情揭晓。
- 测试里怎么复现：中、英文各开一局，在第 1 至第 5 天从起始菜单和局内菜单找「显示提示」的说明，再到第 6 天对照。

### M2 说明写最多三位，茶摊配置只有两位
- 严重：中　把握：【确定】（说明与配置不符）　角色：共用　画像：21。
- 怎么遇到：开局参考茶摊说明，再按它安排招待。
- 玩家看到：两种语言都写可同时招待三位（`guide_page_1`）。设计和摊位配置只给两位。
- 为什么不对：对照我们自己说的。说明给了错误的座位预期。角色实际入座次序和第三位等待事件没有程序可核，本条只报文案与配置差值。
- 出处：`game/text/zh.csv:5` 原文 `guide_page_1,茶摊同时最多招待三位客人。客人等久了会走。`；`game/text/en.csv:5` 原文 `guide_page_1,The stall can serve up to three guests at once. Guests leave if they wait too long.`；`game/data/settings.json:2` 原文 `"stall": { "seats": 2, "days": 7 },`。
- 反查：只有一个摊位容量配置。设计也写两位，`game/README.md:8` 原文 ``2. 摆摊。茶摊有两个座位（`data\settings.json` 的 `stall.seats`）。``。
- 建议：把两种说明统一到两位。

### M3 拒绝留宿的中文按钮写成「不卖」
- 严重：中　把握：【确定】　角色：老周　画像：14。
- 怎么遇到：第 6 天把三种留宿选择分别查一遍。老周说能否在摊后躲一晚，玩家打算拒绝。
- 玩家看到：「让他躲一晚」「不卖」「去报官」；选择「不卖」实际是拒绝留宿。
- 为什么不对：问题问能否留宿，按钮表达不卖茶。交易和留宿使用了同一个键。对照：前后不一样。
- 出处：`game/text/zh.csv:22` 原文 `zhou_ask_1,……我是从营里跑出来的。能在你摊子后面躲一晚吗？` → `game/data/characters/zhou.json:15` 原文 `{ "button": "btn_refuse", "reply": "zhou_refused" },` → `game/text/zh.csv:30` 原文 `btn_refuse,不卖`。
- 反查：文件里只找到这一处拒绝留宿按钮映射，没有单独的中文覆盖。留宿拒绝后不设被带走或留宿结果，也不会发这两个结果对应的礼物或小结。
- 建议：留宿拒绝使用单独的键，中文写「不能让你留宿」或「拒绝留宿」。

### M4 同意老周留宿，回复里写「占位」
- 严重：中　把握：【确定】　角色：老周　画像：14。
- 怎么遇到：第 6 天听完留宿请求，点「让他躲一晚」。
- 玩家看到：「（占位）谢谢。」（`zhou_stay_thanks`），英文也有「(placeholder) Thanks.」。
- 为什么不对：编辑标记出现在角色回话。对照：玩家可见文案与角色口吻。
- 出处：`game/data/characters/zhou.json:14` 原文 `{ "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },`；`game/text/zh.csv:24` 原文 `zhou_stay_thanks,（占位）谢谢。`；`game/text/en.csv:23` 原文 `zhou_stay_thanks,(placeholder) Thanks.`。
- 反查：上一行的注释不会显示，但这两行的占位字样在回复的值里面。留宿分支指向该键，没有替换回复，次日仍是留宿分支的铜扣。
- 建议：移掉两种语言的编辑标记，用正式回复替换。

### M5 英文表缺拒绝留宿后的回话
- 严重：中　把握：【确定】（英文表缺键；回退表现待确认）　角色：老周　画像：14。
- 怎么遇到：用英文内容推演，第 6 天老周提出留宿，选「Refuse」。
- 玩家看到：该处请求和选项有英语，拒绝之后那句「……知道了。」没有英文内容。界面是显示键名、回退中文还是空白，文件没有说明。
- 为什么不对：第 6 天实际选项指到只有中文的回话。对照：两种语言的内容。
- 出处：`game/data/characters/zhou.json:15` 原文 `{ "button": "btn_refuse", "reply": "zhou_refused" },`；`game/text/zh.csv:25` 原文 `zhou_refused,……知道了。`；`game/text/en.csv:23` 原文 `zhou_stay_thanks,(placeholder) Thanks.`，紧接着下一段是按钮，查完整表未见 `zhou_refused`。
- 反查：全作品搜 `zhou_refused`，只见上述数据引用和中文回话。选择拒绝后符合已写明的无后话分支。
- 建议：英文表给原回复键加一句对应译文。

## 想要但没有的

### W1 举报者想提前试报官，第 2、4 天只能交易
- 谁想要：21 举报者。在哪一步：老周前两次来访，玩家想试报尚未开口承认的可疑客人。
- 他想做什么、为什么：这类玩家会试报可疑对象，也会尝试一次无理由举报，看官府怎样回应。
- 现在有的选项：「照价卖」「少收一点」「不卖」（`game/README.md:10` 原文 `4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。`）。报官只在留宿请求的选择列表中（`game/data/characters/zhou.json:13` 原文 `"day6": [`；`game/data/characters/zhou.json:16` 原文 `{ "button": "btn_report", "sets": "flag:zhou_taken" }`）。
- 没有它，他只能：先决定卖不卖茶，等到第 6 天对方公开来历后才有机会举报。这保留了剧情揭晓顺序。
- 作品里别处有没有同类的选项：对第 2、4 天未找到；第 6 天已经有。
- 把握：【确定没有】。搜过「举报」「报官」和 `btn_report`，可操作入口只在第 6 天分支。README 也只列出了普通交易。
- 可以怎么加：允许玩家提前做一次笼统报案，由官府以「没有可以辨认的情况」回应。保留第 6 天正式选择。

## 要老板定

### D1 阿婆已经送花，按规矩报官也只能普通结局
- 把握：【设计】　画像：14 的分支对照；21 的举报动机。
- 代码和设计稿一致：`game/README.md:34` 原文 `- 好结局：阿婆送了花，而且老周没有被带走。`；`game/README.md:35` 原文 `- 普通结局：别的情况。`。第 1、3 天各少收一次满足 `game/data/characters/granny.json:18` 原文 `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`。第 6 天报官仍有第 7 天被带走的小结。
- 玩家那边：照顾阿婆和是否配合官府能分别选择，报官仍直接排除好结局。早上小结告诉他事件发生，设计没有说明结局里会说为什么给普通结局。
- 选项：1.（推荐）保留两种结局，在结局回顾标出两条选择的结果，让玩家能理解普通结局。2. 加一个配合官府后的独立结局，让两条线各有回应。3. 保持，玩家通过重走另一条分支比较结果。

## 查过、没问题的

- 21：报官分支有次晨确认；虽然选项没有 `reply`，`game/data/characters/zhou.json:20` 原文 `"summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }` 和 `game/text/zh.csv:33` 原文 `summary_taken,昨夜有人被带走。` 挡住「举报完全没有后续」。
- 14：留宿才有铜扣，报官才有小结。拒绝是单独分支。两者在设计里由各自条件挡开（`game/data/characters/zhou.json:14–20`）。运行时读档会不会串线仍走不了。
- 21、18：两次主动拒卖后阿婆不来，符合警告。第一次拒卖后的原话见 `game/text/zh.csv:14`：`granny_warn,你今天不卖我……下回再这样，我就不来了。`。18 跳过这句时会错过它，不能据此说没有警告。
- 18：粗茶可点整格（`game/data/settings.json:5` 原文 `"shelf": { "hit": "cell" },`），不受小图限制。提示小图标本来不接受点击（`game/data/settings.json:7` 原文 `"hints": { "icon": "images\\ui\\hint_icon.png", "clickable": false }`）。
- 阿婆在报官分支说「……他们昨夜把人带走了。茶我不喝了。」（`game/text/zh.csv:15`），未点名；早上也有同一件事的小结（`game/text/zh.csv:33`）。未写阿婆消息来源，不能判她不可能听闻。

## 这次没走到的

- 画像 14、18 没有项目对照，按通用层推到茶摊。没有 14 所需的强退、保存与从回合开头重读的实现资料。进游戏后再查：第 6 天选择前存档 → 报官 → 第 7 天看小结 → 读旧档改选留宿 → 看铜扣及小结 → 读档两次，核奖励和通报是否重复、旧分支是否残留。阿婆可在第 3 天拒卖或少收后同样重来，观察是否继续来访。
- 18 的同帧连点、跳过会否漏选、临门确认、首项实际布局未给出。进游戏后再查：第 1 天连点交易首项，核价钱与账本；第 6 天连点首项，第 7 天核铜扣次数与画面上的可点区域。
- 阿婆预算低于原价时按「照价卖」的界面反应，以及两条末日台词条件同真时的显示优先级没有程序。对照 `game/data/characters/granny.json:5–6,12–18` 和 `game/data/settings.json:3–4`。未实测提示什么时候可开、翻译缺键时的回退，也无画面、声音和碰撞运行资料。测试步骤均先不跑。

## 索引

编号 | 严重 | 把握 | 文件:行 | 那一行的原文
S1 | 严重 | 确定 | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },
S1 | 严重 | 确定 | game/data/characters/zhou.json:19 | "gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },
S1 | 严重 | 确定 | game/data/items.json:6 | "old_button": { "image": "images\\items\\old_button.png", "where": "table" }
S1 | 严重 | 确定 | game/data/settings.json:6 | "table": { "hit": "pixel", "sweepAtClose": true },
S1 | 严重 | 确定 | game/README.md:14 | 一局 7 天。第 7 天收摊以后出结局。
M1 | 中 | 可能 | game/text/zh.csv:4 | option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。
M1 | 中 | 可能 | game/text/en.csv:4 | option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey.
M1 | 中 | 可能 | game/README.md:29 | - 设定：老周的来历在第 6 天以前不能让玩家知道。
M2 | 中 | 确定 | game/text/zh.csv:5 | guide_page_1,茶摊同时最多招待三位客人。客人等久了会走。
M2 | 中 | 确定 | game/text/en.csv:5 | guide_page_1,The stall can serve up to three guests at once. Guests leave if they wait too long.
M2 | 中 | 确定 | game/data/settings.json:2 | "stall": { "seats": 2, "days": 7 },
M3 | 中 | 确定 | game/data/characters/zhou.json:15 | { "button": "btn_refuse", "reply": "zhou_refused" },
M3 | 中 | 确定 | game/text/zh.csv:22 | zhou_ask_1,……我是从营里跑出来的。能在你摊子后面躲一晚吗？
M3 | 中 | 确定 | game/text/zh.csv:30 | btn_refuse,不卖
M4 | 中 | 确定 | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },
M4 | 中 | 确定 | game/text/zh.csv:24 | zhou_stay_thanks,（占位）谢谢。
M4 | 中 | 确定 | game/text/en.csv:23 | zhou_stay_thanks,(placeholder) Thanks.
M5 | 中 | 确定 | game/data/characters/zhou.json:15 | { "button": "btn_refuse", "reply": "zhou_refused" },
M5 | 中 | 确定 | game/text/zh.csv:25 | zhou_refused,……知道了。
M5 | 中 | 确定 | game/text/en.csv:23 | zhou_stay_thanks,(placeholder) Thanks.
W1 | 想要 | 确定没有 | game/README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。
W1 | 想要 | 确定没有 | game/data/characters/zhou.json:13 | "day6": [
W1 | 想要 | 确定没有 | game/data/characters/zhou.json:16 | { "button": "btn_report", "sets": "flag:zhou_taken" }
D1 | 要定 | 设计 | game/README.md:34 | - 好结局：阿婆送了花，而且老周没有被带走。
D1 | 要定 | 设计 | game/README.md:35 | - 普通结局：别的情况。
D1 | 要定 | 设计 | game/data/characters/zhou.json:20 | "summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }
