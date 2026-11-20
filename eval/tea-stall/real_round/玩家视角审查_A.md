# 玩家视角审查 · A 好心人和算账的（2026-11-19）

范围：ALL。走法：画像走查。画像：1 好心人、2 精明生意人、17 一句一句细读的人。
路线：好心人少收两位客人、第 6 天答应留宿；生意人只照价成交、第 6 天拒绝留宿。两种选择各走完阿婆和老周一线到第 7 天，叠加 17 全程细读中文，又单列报官后的文字反查。英表是文本补查。
作品地图见同轮 `_map/_map.md`，静态表见 `_summary.md`。本轮是设计、配置、文本的静态走查。

## 结论

旧铜扣只在答应留宿后的第 7 天取得。点击透明处会漏收，收摊会扫掉未收的铜扣。没有证据表明这会改变结局。
两位客人的文字有数处可见问题，包括阿婆初次来就说「老样子」，老周留宿回复还带占位标记。中文拒绝留宿按钮沿用「不卖」。
前期能否看到设置剧透、第一次少收的感谢时点、冷暖两条末日对白如何取舍，需运行版确认。共严重 1、中 9、轻 0、要老板定 1、想要但没有的 2。

## 玩家反馈

### 1 好心人（中立善）玩到了第 7 天收摊

- 看不懂的：「我答应让他躲，结果他的谢谢前面有个『占位』。」（→ M5）
- 卡住的：「桌上看到了铜扣，点到图边没收进去。收摊之后它就没了。」（→ S1）
- 想要的：「阿婆钱不多，我想把茉莉直接给她。」（→ W1）
- 做对了的：「我给阿婆少收了几回，第 7 天她给我自己晒的花。」（`game\data\characters\granny.json:18` 原文 `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`；`game\text\zh.csv:16` 原文 `granny_last_warm,这是我自己晒的花，你拿去泡。`）
- 一句话：「我一路帮到最后，阿婆送了花，但桌上的铜扣漏收就没了。」（→ S1；`game\data\characters\granny.json:18` 原文 `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`）

### 2 精明生意人（中立中立）玩到了第 7 天收摊

- 想要的：「茉莉这单卖不成，能不能问她要不要换便宜的粗茶？」（→ W2）
- 看不懂的：「他问的是能不能住一晚，为什么拒绝写成『不卖』？」（→ M6）
- 做对了的：「我第一次不卖，阿婆就讲明了再拒她就不来。」（`game\data\characters\granny.json:11` 原文 `"afterRefused": [ "granny_warn" ],`；`game\text\zh.csv:14` 原文 `granny_warn,你今天不卖我……下回再这样，我就不来了。`）
- 一句话：「我坚持照价，要么卖茉莉，要么只能不卖。」（→ W2）

### 17 一句一句细读的人玩到了两线末日，并对照报官分支

- 看不懂的：「阿婆先说『老样子』，下一句就问我是不是新摊。我们刚见面啊。」（→ M1）
- 看不懂的：「第一次少收如果当场念成『上回』，我会以为漏了一次见面。」（→ M2，待确认）
- 看不懂的：「设置要是开局就能看，这里直接告诉我老周是谁了。」（→ M3，待确认）
- 看不懂的：「说明写同时三位，摆摊只有两个座位。」（→ M4）
- 做对了的：「老周点了几回便宜茶，到了第 6 天才第一次开口问能不能躲一晚。」（`game\data\characters\zhou.json:4` 原文 `"visits": { "days": [ 2, 4, 6 ] },`；`game\data\characters\zhou.json:10` 原文 `"day6": [ "zhou_ask_1" ]`；`game\text\zh.csv:22` 原文 `zhou_ask_1,……我是从营里跑出来的。能在你摊子后面躲一晚吗？`）
- 一句话：「剧情里本来慢慢才讲他的来历，设置里那句话可能提前讲完了。」（→ M3，待确认）

## 问题一览

| # | 严重 | 把握 | 角色 | 玩家看到的 | 画像或格子 |
|---|---|---|---|---|
| S1 | 严重 | 确定 | 老周 | 点到旧铜扣的透明处收不进柜，收摊就失去这枚礼物 | 1 好心人 |
| M1 | 中 | 确定 | 阿婆 | 首次见阿婆，先听到「老样子」又听到「新开的吧」 | 17 一句一句细读的人 |
| M2 | 中 | 可能 | 阿婆 | 第一次少收时，阿婆的感谢可能提前说成「上回」 | 17 一句一句细读的人 |
| M3 | 中 | 可能 | 老周 | 设置提示可能在第 6 天前交代老周身份 | 17 一句一句细读的人 |
| M4 | 中 | 确定 | 共同说明 | 说明写三个客位，摆摊设计和数据都只有两个 | 17 一句一句细读的人 |
| M5 | 中 | 确定 | 老周 | 答应老周留宿，感谢台词带着占位字样 | 1 好心人 |
| M6 | 中 | 确定 | 老周 | 答复留宿请求时，中文拒绝按钮写「不卖」 | 2 精明生意人 |
| M7 | 中 | 确定 | 老周 | 拒绝留宿的回复缺英译 | 2 的路线，英文表补查 |
| M8 | 中 | 确定 | 阿婆 | 第 7 天阿婆送花台词在英文表里仍是中文 | 1 的路线，英文表补查 |
| M9 | 中 | 可能 | 阿婆 | 报官且至少两次少收后，阿婆末日冷暖两句都可能符合 | 17 一句一句细读的人（另走报官分支） |

## 问题

### S1 点到旧铜扣的透明处收不进柜，收摊就失去这枚礼物

- 严重：严重　把握：【确定】　角色：老周　画像：1 好心人
- 怎么遇到
  1. 第 6 天听完老周的请求，选「让他躲一晚」。
  2. 第 7 天看到桌上的旧铜扣。点在图框里透明的地方，例如原图内相对坐标 (0,0)，没有再点中铜扣的非透明像素，随后收摊。
- 玩家看到：铜扣没有收到柜里。按现有设计，关摊后桌上那枚铜扣被扫走，本局当晚结局。
- 为什么不对：按图形点击和收摊扫桌本来就是设计。旧铜扣的实际可点区域只有 60／1024 像素，仍占一张 32×32 图。第 7 天礼物只有这一个取得时点，点落透明区后，期待已收到的玩家会失去这份礼物。结局条件写的是阿婆是否送花、老周是否被带走。
- 出处：`game\data\characters\zhou.json:19` 原文 `"gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },`；`game\data\items.json:6` 原文 `"old_button": { "image": "images\\items\\old_button.png", "where": "table" }`；`game\data\settings.json:6` 原文 `"table": { "hit": "pixel", "sweepAtClose": true },`；`game\README.md:14` 原文 `一局 7 天。第 7 天收摊以后出结局。`；`game\README.md:21` 原文 `` - **桌上**：客人送的东西留在桌上。玩家点它，收进柜子。点在图的透明处不算点中（按图的形状判定，`table.hit` = `pixel`）。 ``；`game\README.md:22` 原文 `` - 收摊时，桌上还没收的东西会被扫掉（`table.sweepAtClose`）。 ``；`game\README.md:30` 原文 `- 答应：第 7 天他留下一枚旧铜扣。拒绝：他走了，没有后话。报官：第 7 天早上的小结写"昨夜有人被带走"。`；`game\README.md:34` 原文 `- 好结局：阿婆送了花，而且老周没有被带走。`；`review_out\20261119_153004\_image_hits.md:17` 原文 `` | `game\images\items\old_button.png` | 32×32 | 2×2 | 5.9%（60 个像素） | 12×12，从 (10,10) 起 | ``。
- 反查：全作品搜 `old_button`、`sweepAtClose`、`柜子`、`取回`。README 与数据相符；没找到其它领取、自动收入柜子或日后补领入口。看不到实际缩放或提示。
- 建议：给旧铜扣提供更宽的有效命中区，并确认桌上其它物品的命中规则；也可让未收的唯一结局礼物有一次明确的收取机会。

### M1 首次见阿婆，先听到「老样子」又听到「新开的吧」

- 严重：中　把握：【确定】　角色：阿婆　画像：17 一句一句细读的人
- 怎么遇到
  1. 第 1 天首次开摊。
  2. 读完阿婆初访两句。
- 玩家看到：「老样子，一壶茉莉。」接「这摊子是新开的吧？」两句是 `granny_first_1`、`granny_first_2`。
- 为什么不对：初访就用熟客点单说法，紧跟一句新摊。后续另有「又来打扰了」，说明数据区分了初次与再来。
- 出处：`game\data\characters\granny.json:4` 原文 `"visits": { "firstDay": 1, "everyDays": 2 },`；`game\data\characters\granny.json:8` 原文 `"first": [ "granny_first_1", "granny_first_2" ],`；`game\data\characters\granny.json:9` 原文 `"again": [ "granny_again_1" ],`；`game\text\zh.csv:10` 原文 `granny_first_1,老样子，一壶茉莉。`；`game\text\zh.csv:11` 原文 `granny_first_2,这摊子是新开的吧？`；`game\text\zh.csv:12` 原文 `granny_again_1,又来打扰了。今天还是茉莉。`；`game\text\en.csv:10` 原文 `granny_first_1,The usual. A pot of jasmine.`；`game\text\en.csv:11` 原文 `granny_first_2,This stall is new, isn't it?`。
- 反查：查了 `firstDay`、`granny_first_1`、`granny_again_1`。初访两句都直接列出，无先前交易条件。英文也有同样先后。
- 建议：初访改为直接点茶，熟客说法留到再访。

### M2 第一次少收时，阿婆的感谢可能提前说成「上回」

- 严重：中　把握：【可能】　角色：阿婆　画像：17 一句一句细读的人
- 怎么遇到
  1. 第 1 天初见阿婆，选「少收一点」。
  2. 读折扣反馈，再在第 3 天回访时对照。
- 玩家看到：折扣反馈键 `granny_thanks` 的中文文案是「上回你少收了我{0}文，我记着呢。」实际出现在哪一天、是否替换 `{0}` 均待确认。
- 为什么不对：首次成交若立刻读出「上回」，它指向一笔未发生的交易。若把原模板显示给玩家，金额也不明。
- 出处：`game\data\characters\granny.json:4` 原文 `"visits": { "firstDay": 1, "everyDays": 2 },`；`game\data\characters\granny.json:10` 原文 `"afterDiscount": [ "granny_thanks" ],`；`game\text\zh.csv:13` 原文 `granny_thanks,上回你少收了我{0}文，我记着呢。`；`game\text\en.csv:13` 原文 `granny_thanks,You charged me less last time. I remember.`；`game\data\settings.json:4` 原文 `"discount": 3,`；`game\text\zh.csv:29` 原文 `btn_discount,少收一点`。
- 反查：搜 `afterDiscount`、`granny_thanks`、`format`。只找到人物的折扣反馈键与两份文字，未找到延期机制或插值实现。若在第 3 天才说且插值正常，中文这句可成立。
- 建议：要当场说就用「这回」；要追忆则绑定已成功成交的一次上一访。两种说法都核对折扣金额插值。
- 测试里怎么复现：第 1 天第一次少收 → 看当场台词 → 第 3 天读再访台词 → 比对出现时机和金额格式。

### M3 设置提示可能在第 6 天前交代老周身份

- 严重：中　把握：【可能】　角色：老周　画像：17 一句一句细读的人
- 怎么遇到
  1. 第 6 天前查看「显示提示」旁的说明。
  2. 继续玩到第 6 天读客人的自述。
- 玩家看到：`option_hints_tip` 中文直接写「老周是逃兵，他的图标是灰色的。」英文同样写了 `deserter`。能打开该说明的最早一天待确认。
- 为什么不对：老周的来历设计为第 6 天自己说。提前读到设置说明会揭示身份，哪怕此前角色名字只显示「客人」。
- 出处：`game\text\zh.csv:2` 原文 `# ==== 设置和说明 ====`；`game\text\zh.csv:3` 原文 `option_hints,显示提示`；`game\text\zh.csv:4` 原文 `option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。`；`game\text\en.csv:4` 原文 `option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey.`；`game\text\zh.csv:19` 原文 `zhou_name,客人`；`game\text\zh.csv:22` 原文 `zhou_ask_1,……我是从营里跑出来的。能在你摊子后面躲一晚吗？`；`game\data\characters\zhou.json:10` 原文 `"day6": [ "zhou_ask_1" ]`；`game\README.md:29` 原文 `- 设定：老周的来历在第 6 天以前不能让玩家知道。`；`project.json:133` 原文 `"第 6 天以前，玩家看得到的文字里不出现老周的来历。",`。
- 反查：搜 `option_hints_tip`、`hints`、`deserter`、`逃兵`。提示说明有两份文本，未见 UI 门槛实现；第 6 天自述的日限制只在角色数据中。
- 建议：设置说明只说明图标作用；第 6 天以后再用角色文本交代身份。
- 测试里怎么复现：开新局 → 第 1 天、首次见老周后分别找设置说明 → 检查第 6 天前提示文字和可见图标。

### M4 说明写三个客位，摆摊设计和数据都只有两个

- 严重：中　把握：【确定】　角色：共同说明　画像：17 一句一句细读的人
- 怎么遇到
  1. 查看茶摊说明第一条。
  2. 对照每天开摊时的客位。
- 玩家看到：`guide_page_1` 中英都写了可同时招待三位；摊位配置和摆摊说明只给两个。
- 为什么不对：同一容量给出两个答案。按三位安排行动会错误预期还有一个空位。资料无法确定排队和等待流失是否实际发生。
- 出处：`game\text\zh.csv:5` 原文 `guide_page_1,茶摊同时最多招待三位客人。客人等久了会走。`；`game\text\en.csv:5` 原文 `guide_page_1,The stall can serve up to three guests at once. Guests leave if they wait too long.`；`game\data\settings.json:2` 原文 `"stall": { "seats": 2, "days": 7 },`；`game\README.md:8` 原文 `` 2. 摆摊。茶摊有两个座位（`data\settings.json` 的 `stall.seats`）。 ``。
- 反查：对比 `guide_page_1`、`stall.seats`、README 的摆摊步骤。未找到分天扩容或第三位例外，UI 显示未验。
- 建议：两张表统一成两个客位，或直接读取摊位容量后输出文字。

### M5 答应老周留宿，感谢台词带着占位字样

- 严重：中　把握：【确定】　角色：老周　画像：1 好心人
- 怎么遇到
  1. 第 6 天听他说要躲一晚。
  2. 选「让他躲一晚」，读答应分支的回复。
- 玩家看到：`zhou_stay_thanks` 是「（占位）谢谢。」。英文也是 `(placeholder) Thanks.`。
- 为什么不对：分支明确引用这条回复。玩家答应后会读到写给作者的编辑标记，两张表同样保留。
- 出处：`game\data\characters\zhou.json:10` 原文 `"day6": [ "zhou_ask_1" ]`；`game\data\characters\zhou.json:14` 原文 `{ "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },`；`game\text\zh.csv:24` 原文 `zhou_stay_thanks,（占位）谢谢。`；`game\text\en.csv:23` 原文 `zhou_stay_thanks,(placeholder) Thanks.`；`game\text\zh.csv:31` 原文 `btn_shelter,让他躲一晚`。
- 反查：搜 `zhou_stay_thanks`。它是留宿回复的键，不只是 CSV 注释。资料没有可切换的正式版本。
- 建议：去掉占位标记并核对两种语言。

### M6 答复留宿请求时，中文拒绝按钮写「不卖」

- 严重：中　把握：【确定】　角色：老周　画像：2 精明生意人
- 怎么遇到
  1. 第 6 天照价卖粗茶，读老周请求。
  2. 比较「让他躲一晚」、「去报官」和剩下的按钮。
- 玩家看到：拒绝放在 `choices.day6`，使用 `btn_refuse`，中文是「不卖」。英文 `Refuse` 没有专指交易。
- 为什么不对：玩家需要答复借宿，按钮却写在拒绝出售。这个按钮跟日常交易同名，实际走的是拒绝借宿分支。
- 出处：`game\data\characters\zhou.json:15` 原文 `{ "button": "btn_refuse", "reply": "zhou_refused" },`；`game\text\zh.csv:22` 原文 `zhou_ask_1,……我是从营里跑出来的。能在你摊子后面躲一晚吗？`；`game\text\zh.csv:30` 原文 `btn_refuse,不卖`；`game\text\zh.csv:31` 原文 `btn_shelter,让他躲一晚`；`game\text\zh.csv:32` 原文 `btn_report,去报官`；`game\text\en.csv:28` 原文 `btn_refuse,Refuse`；`game\README.md:10` 原文 `4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。`。
- 反查：搜 `btn_refuse`、`zhou_refused`。第 6 天拒绝没有单独的专用键或另一处中文文案。
- 建议：给借宿拒绝独立文字，例如「不能在这儿留宿」，交易仍显示「不卖」。

### M7 拒绝留宿的回复缺英译

- 严重：中　把握：【确定】　角色：老周　画像：2 的路线，英文表补查
- 怎么遇到
  1. 用英文文本走第 6 天。
  2. 选 `Refuse`。
- 玩家看到：分支指定 `zhou_refused`，只有中文「……知道了。」有对应值。英文没有这一键。
- 为什么不对：英文表不能为这一步提供英文回复，实际回退成中文、露键名或省去回复未知。
- 出处：`game\data\characters\zhou.json:15` 原文 `{ "button": "btn_refuse", "reply": "zhou_refused" },`；`game\text\zh.csv:25` 原文 `zhou_refused,……知道了。`；`game\text\en.csv:22` 原文 `zhou_ask_1,...I ran from the camp. Can I hide behind your stall for a night?`；`game\text\en.csv:23` 原文 `zhou_stay_thanks,(placeholder) Thanks.`；`game\text\en.csv:28` 原文 `btn_refuse,Refuse`。
- 反查：完整读取 `game\text\en.csv`，并搜 `zhou_refused`。只有角色数据的调用和中文表的原句，未找到通用回退实现。
- 建议：为该键补英文，并确认缺键时的回退行为。

### M8 第 7 天阿婆送花台词在英文表里仍是中文

- 严重：中　把握：【确定】　角色：阿婆　画像：1 的路线，英文表补查
- 怎么遇到
  1. 用英文文本，在老周没有被带走的分支给阿婆少收至少两次。
  2. 第 7 天读阿婆送花台词。
- 玩家看到：英文表的 `granny_last_warm` 仍写「这是我自己晒的花，你拿去泡。」。
- 为什么不对：英文版其余阿婆对白是英文，送花分支的文本却跳回中文；读不懂中文的人缺少收礼的语境。
- 出处：`game\data\characters\granny.json:13` 原文 `{ "when": "flag:zhou_taken", "line": "granny_last_cold" },`；`game\data\characters\granny.json:14` 原文 `{ "when": "discounts>=2", "line": "granny_last_warm" }`；`game\data\characters\granny.json:18` 原文 `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`；`game\text\zh.csv:16` 原文 `granny_last_warm,这是我自己晒的花，你拿去泡。`；`game\text\en.csv:15` 原文 `granny_last_cold,...They took someone away last night. I won't have tea.`；`game\text\en.csv:16` 原文 `granny_last_warm,这是我自己晒的花，你拿去泡。`；`game\README.md:36` 原文 `- 阿婆第 7 天说的话要看老周怎样了：他被带走，她说一句冷话；否则说家常。`。
- 反查：搜 `granny_last_warm`、`discounts`。角色末日列表直接引用此键；未找到另一条已翻译的同义回复。
- 建议：翻译英语值，同时保留中文原句。

### M9 报官且至少两次少收后，阿婆末日冷暖两句都可能符合

- 严重：中　把握：【可能】　角色：阿婆　画像：17 一句一句细读的人（另走报官分支）
- 怎么遇到
  1. 对阿婆至少两次少收。
  2. 第 6 天去报官。第 7 天读早间小结，再读阿婆的末日话和收礼。
- 玩家看到：`granny_last_cold` 是「……他们昨夜把人带走了。茶我不喝了。」；`granny_last_warm` 是「这是我自己晒的花，你拿去泡。」实际是否只显示前一句待确认。
- 为什么不对：两条条件能同局成立，但 README 说老周被带走就说冷话，否则说家常。若逐条处理匹配，可能在同一次来访听到设计上互斥的冷暖台词。
- 出处：`game\data\characters\granny.json:13` 原文 `{ "when": "flag:zhou_taken", "line": "granny_last_cold" },`；`game\data\characters\granny.json:14` 原文 `{ "when": "discounts>=2", "line": "granny_last_warm" }`；`game\data\characters\granny.json:18` 原文 `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`；`game\data\characters\zhou.json:16` 原文 `{ "button": "btn_report", "sets": "flag:zhou_taken" }`；`game\data\characters\zhou.json:20` 原文 `"summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }`；`game\text\zh.csv:15` 原文 `granny_last_cold,……他们昨夜把人带走了。茶我不喝了。`；`game\text\zh.csv:16` 原文 `granny_last_warm,这是我自己晒的花，你拿去泡。`；`game\text\zh.csv:33` 原文 `summary_taken,昨夜有人被带走。`；`game\README.md:36` 原文 `- 阿婆第 7 天说的话要看老周怎样了：他被带走，她说一句冷话；否则说家常。`。
- 反查：查 `lastDay`、`discounts`、`flag:zhou_taken`。冷分支排在列表第一项，但没有发现按首项停住的实现。送花是另外的字段。
- 建议：明确被带走时的台词与否则分支互斥；同时说明报官后已满足的送花是否照发。
- 测试里怎么复现：第 1、3 天少收 → 第 6 天报官 → 第 7 天核对早上小结、阿婆话的条数顺序和花有没有送。

## 想要但没有的

### W1 好心人在阿婆点茉莉时想直接送茶

- 谁想要：1 好心人。第 1 天阿婆点茉莉，玩家打算帮她。
- 他想做什么、为什么：让阿婆无须付钱，照画像的无偿给与做法。
- 现在有的选项：「照价卖」「少收一点」「不卖」。`game\README.md:10` 原文 `4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。`；`game\text\zh.csv:28` 原文 `btn_sell,照价卖`；`game\text\zh.csv:29` 原文 `btn_discount,少收一点`；`game\text\zh.csv:30` 原文 `btn_refuse,不卖`。
- 没有它，他只能：按固定档少收，标价 12 减 3 等于 9，阿婆预算 10 够付，但不能把本单降到零。`game\data\settings.json:3` 原文 `"prices": { "jasmine": 12, "coarse": 4 },`；`game\data\settings.json:4` 原文 `"discount": 3,`；`game\data\characters\granny.json:6` 原文 `"budget": 10,`。
- 把握：【确定没有】已列设计中的共用交易按钮，并搜作品文本和数据里的白送、送茶、免费、zero、free、give、gift。发现的是客人给玩家的礼物，与送茶入口无关。`game\data\characters\granny.json:18` 原文 `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`。
- 可以怎么加：在交易选项增加「送她一壶」，并注明是否也算帮过一次。

### W2 生意人想请阿婆换一种便宜的茶照价成交

- 谁想要：2 精明生意人。阿婆点茉莉的交易。
- 他想做什么、为什么：阿婆有 10，茉莉标价 12，粗茶标价 4。生意人照自己的玩法不让利，则可尝试先问她是否愿意换粗茶，再照价卖。`game\data\characters\granny.json:5` 原文 `"wants": "jasmine",`；`game\data\characters\granny.json:6` 原文 `"budget": 10,`；`game\data\settings.json:3` 原文 `"prices": { "jasmine": 12, "coarse": 4 },`。
- 现在有的选项：「照价卖」「少收一点」「不卖」。`game\README.md:10` 原文 `4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。`。
- 没有它，他只能：按这位生意人的玩法拒卖，先听到警告，连拒两次后阿婆不来。`game\text\zh.csv:14` 原文 `granny_warn,你今天不卖我……下回再这样，我就不来了。`；`game\data\characters\granny.json:17` 原文 `"leaveForever": { "refusedInARow": 2 },`。
- 把握：【确定没有】列齐交易选项，搜了换茶、改点、替换、swap、substitute、coarse、choices、wants。粗茶可从货架取，是老周的点单；没有问阿婆是否愿意换茶的入口。`game\data\items.json:4` 原文 `"coarse": { "image": "images\\items\\coarse_brick.png", "where": "shelf" },`；`game\data\characters\zhou.json:5` 原文 `"wants": "coarse",`。
- 可以怎么加：给资金不够的茉莉订单加「问她要不要换粗茶」，由角色答应或拒绝，再走对应的正常交易。

## 要老板定

### D1 只照价经营时，阿婆第二次被拒后永久不再回来

- 把握：【设计】。`game\data\characters\granny.json:4` 原文 `"visits": { "firstDay": 1, "everyDays": 2 },`；`game\data\characters\granny.json:6` 原文 `"budget": 10,`；`game\data\characters\granny.json:17` 原文 `"leaveForever": { "refusedInARow": 2 },`；`game\data\settings.json:3` 原文 `"prices": { "jasmine": 12, "coarse": 4 },`；`game\README.md:27` 原文 `` - **阿婆**（`granny`）：每两天来一次，要一壶茉莉。钱不多。连着两次被"不卖"，她就不再来（第一次被拒绝时她会说一句警告）。少收过她两次以上，第 7 天她会送一包自己晒的花。 ``。
- 玩家那边：阿婆点的茶 12，预算 10。按本组生意人的玩法拒卖，第 1 天收到警告；第 3 天再拒就从之后的来访消失。`game\text\zh.csv:14` 原文 `granny_warn,你今天不卖我……下回再这样，我就不来了。`。第 7 天也没机会走送花和好结局。`game\data\characters\granny.json:18` 原文 `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`；`game\README.md:34` 原文 `- 好结局：阿婆送了花，而且老周没有被带走。`。
- 选项：1.（推荐）保留第二次后的离开，点「不卖」以前把剩余机会说得更明确，玩家能在最终离开前看清后果。2. 区分钱不够没谈成和主动拒卖，玩家坚持照价时还能遇见她。3. 保留当前警告与门槛，玩家承担已预告的后果。

## 查过、没问题的

- 好心人：折后茉莉为 9，低于阿婆预算 10；折后粗茶为 1，低于老周预算 4。没有发现两种茶首笔少收仍买不起的配置。`game\data\settings.json:3` 原文 `"prices": { "jasmine": 12, "coarse": 4 },`；`game\data\settings.json:4` 原文 `"discount": 3,`；`game\data\characters\granny.json:6` 原文 `"budget": 10,`；`game\data\characters\zhou.json:6` 原文 `"budget": 4,`。
- 好心人：粗茶图非透明只占 9.6%，但取茶由货架格子判定。提示图标 7.8%，本身无可点击操作。两张图的透明面积不会造成所怀疑的点击失败。`review_out\20261119_153004\_image_hits.md:19` 原文 `` | `game\images\items\coarse_brick.png` | 32×32 | 2×2 | 9.6%（98 个像素） | 14×7，从 (9,13) 起 | ``；`review_out\20261119_153004\_image_hits.md:18` 原文 `` | `game\images\ui\hint_icon.png` | 16×16 | 1×1 | 7.8%（20 个像素） | 2×12，从 (7,2) 起 | ``；`game\data\items.json:4` 原文 `"coarse": { "image": "images\\items\\coarse_brick.png", "where": "shelf" },`；`game\data\settings.json:5` 原文 `"shelf": { "hit": "cell" },`；`game\data\settings.json:7` 原文 `"hints": { "icon": "images\\ui\\hint_icon.png", "clickable": false }`。
- 生意人：阿婆第 5 天不再来与两次连续拒绝吻合，首拒已有警告。拒绝留宿后没铜扣也与设计吻合。`game\data\characters\granny.json:17` 原文 `"leaveForever": { "refusedInARow": 2 },`；`game\text\zh.csv:14` 原文 `granny_warn,你今天不卖我……下回再这样，我就不来了。`；`game\data\characters\zhou.json:19` 原文 `"gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },`；`game\README.md:30` 原文 `- 答应：第 7 天他留下一枚旧铜扣。拒绝：他走了，没有后话。报官：第 7 天早上的小结写"昨夜有人被带走"。`。
- 细读：阿婆冷话只说有人被带走，第 7 天早上小结也提到这件事，不能单凭触发字段推断她不可能得知，更不能说她知道玩家报官。`game\data\characters\granny.json:13` 原文 `{ "when": "flag:zhou_taken", "line": "granny_last_cold" },`；`game\text\zh.csv:15` 原文 `granny_last_cold,……他们昨夜把人带走了。茶我不喝了。`；`game\text\zh.csv:33` 原文 `summary_taken,昨夜有人被带走。`；`game\README.md:30` 原文 `- 答应：第 7 天他留下一枚旧铜扣。拒绝：他走了，没有后话。报官：第 7 天早上的小结写"昨夜有人被带走"。`。
- 细读：CSV 的「占位」段头是注释。拒绝之后的中文回复本身不含占位。`game\text\zh.csv:1` 原文 `# 茶摊：中文文本。每行 键,文字（只按第一个逗号切）。# 开头是注释。`；`game\text\zh.csv:23` 原文 `# 占位：等作者写`；`game\text\zh.csv:25` 原文 `zhou_refused,……知道了。`。

## 这次没走到的

- 17 没有项目对照。按通用层用中文逐句看，叠上 1 或 2 的选择；补做一份报官结尾的静态文本对照。
- 项目没有运行程序。未验证设置和说明的首次出现时点、默认语言、等待、存读档、对话回看、多条件台词取舍、实际点击缩放或支付失败时怎样显示。上面的运行验证步骤没有执行。
- 第 7 天之后按设计已经结局，无更多回合供复走。`game\README.md:14` 原文 `一局 7 天。第 7 天收摊以后出结局。`。
- 独立的读档／跳字、软锁、经济反复操作和想要选项全集交由其它组。此组从两条角色线的普通到达路径查证。

## 索引

编号 | 严重 | 把握 | 文件:行 | 那一行的原文
S1 | 严重 | 确定 | game\data\characters\zhou.json:19 | "gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },
S1 | 严重 | 确定 | game\data\items.json:6 | "old_button": { "image": "images\\items\\old_button.png", "where": "table" }
S1 | 严重 | 确定 | game\data\settings.json:6 | "table": { "hit": "pixel", "sweepAtClose": true },
S1 | 严重 | 确定 | game\README.md:14 | 一局 7 天。第 7 天收摊以后出结局。
S1 | 严重 | 确定 | game\README.md:21 | - **桌上**：客人送的东西留在桌上。玩家点它，收进柜子。点在图的透明处不算点中（按图的形状判定，`table.hit` = `pixel`）。
S1 | 严重 | 确定 | game\README.md:22 | - 收摊时，桌上还没收的东西会被扫掉（`table.sweepAtClose`）。
S1 | 严重 | 确定 | game\README.md:30 | - 答应：第 7 天他留下一枚旧铜扣。拒绝：他走了，没有后话。报官：第 7 天早上的小结写"昨夜有人被带走"。
S1 | 严重 | 确定 | game\README.md:34 | - 好结局：阿婆送了花，而且老周没有被带走。
S1 | 严重 | 确定 | review_out\20261119_153004\_image_hits.md:17 | \| `game\images\items\old_button.png` \| 32×32 \| 2×2 \| 5.9%（60 个像素） \| 12×12，从 (10,10) 起 \|
M1 | 中 | 确定 | game\data\characters\granny.json:4 | "visits": { "firstDay": 1, "everyDays": 2 },
M1 | 中 | 确定 | game\data\characters\granny.json:8 | "first": [ "granny_first_1", "granny_first_2" ],
M1 | 中 | 确定 | game\data\characters\granny.json:9 | "again": [ "granny_again_1" ],
M1 | 中 | 确定 | game\text\zh.csv:10 | granny_first_1,老样子，一壶茉莉。
M1 | 中 | 确定 | game\text\zh.csv:11 | granny_first_2,这摊子是新开的吧？
M1 | 中 | 确定 | game\text\zh.csv:12 | granny_again_1,又来打扰了。今天还是茉莉。
M1 | 中 | 确定 | game\text\en.csv:10 | granny_first_1,The usual. A pot of jasmine.
M1 | 中 | 确定 | game\text\en.csv:11 | granny_first_2,This stall is new, isn't it?
M2 | 中 | 可能 | game\data\characters\granny.json:4 | "visits": { "firstDay": 1, "everyDays": 2 },
M2 | 中 | 可能 | game\data\characters\granny.json:10 | "afterDiscount": [ "granny_thanks" ],
M2 | 中 | 可能 | game\text\zh.csv:13 | granny_thanks,上回你少收了我{0}文，我记着呢。
M2 | 中 | 可能 | game\text\en.csv:13 | granny_thanks,You charged me less last time. I remember.
M2 | 中 | 可能 | game\data\settings.json:4 | "discount": 3,
M2 | 中 | 可能 | game\text\zh.csv:29 | btn_discount,少收一点
M3 | 中 | 可能 | game\text\zh.csv:2 | # ==== 设置和说明 ====
M3 | 中 | 可能 | game\text\zh.csv:3 | option_hints,显示提示
M3 | 中 | 可能 | game\text\zh.csv:4 | option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。
M3 | 中 | 可能 | game\text\en.csv:4 | option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey.
M3 | 中 | 可能 | game\text\zh.csv:19 | zhou_name,客人
M3 | 中 | 可能 | game\text\zh.csv:22 | zhou_ask_1,……我是从营里跑出来的。能在你摊子后面躲一晚吗？
M3 | 中 | 可能 | game\data\characters\zhou.json:10 | "day6": [ "zhou_ask_1" ]
M3 | 中 | 可能 | game\README.md:29 | - 设定：老周的来历在第 6 天以前不能让玩家知道。
M3 | 中 | 可能 | project.json:133 | "第 6 天以前，玩家看得到的文字里不出现老周的来历。",
M4 | 中 | 确定 | game\text\zh.csv:5 | guide_page_1,茶摊同时最多招待三位客人。客人等久了会走。
M4 | 中 | 确定 | game\text\en.csv:5 | guide_page_1,The stall can serve up to three guests at once. Guests leave if they wait too long.
M4 | 中 | 确定 | game\data\settings.json:2 | "stall": { "seats": 2, "days": 7 },
M4 | 中 | 确定 | game\README.md:8 | 2. 摆摊。茶摊有两个座位（`data\settings.json` 的 `stall.seats`）。
M5 | 中 | 确定 | game\data\characters\zhou.json:10 | "day6": [ "zhou_ask_1" ]
M5 | 中 | 确定 | game\data\characters\zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },
M5 | 中 | 确定 | game\text\zh.csv:24 | zhou_stay_thanks,（占位）谢谢。
M5 | 中 | 确定 | game\text\en.csv:23 | zhou_stay_thanks,(placeholder) Thanks.
M5 | 中 | 确定 | game\text\zh.csv:31 | btn_shelter,让他躲一晚
M6 | 中 | 确定 | game\data\characters\zhou.json:15 | { "button": "btn_refuse", "reply": "zhou_refused" },
M6 | 中 | 确定 | game\text\zh.csv:22 | zhou_ask_1,……我是从营里跑出来的。能在你摊子后面躲一晚吗？
M6 | 中 | 确定 | game\text\zh.csv:30 | btn_refuse,不卖
M6 | 中 | 确定 | game\text\zh.csv:31 | btn_shelter,让他躲一晚
M6 | 中 | 确定 | game\text\zh.csv:32 | btn_report,去报官
M6 | 中 | 确定 | game\text\en.csv:28 | btn_refuse,Refuse
M6 | 中 | 确定 | game\README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。
M7 | 中 | 确定 | game\data\characters\zhou.json:15 | { "button": "btn_refuse", "reply": "zhou_refused" },
M7 | 中 | 确定 | game\text\zh.csv:25 | zhou_refused,……知道了。
M7 | 中 | 确定 | game\text\en.csv:22 | zhou_ask_1,...I ran from the camp. Can I hide behind your stall for a night?
M7 | 中 | 确定 | game\text\en.csv:23 | zhou_stay_thanks,(placeholder) Thanks.
M7 | 中 | 确定 | game\text\en.csv:28 | btn_refuse,Refuse
M8 | 中 | 确定 | game\data\characters\granny.json:13 | { "when": "flag:zhou_taken", "line": "granny_last_cold" },
M8 | 中 | 确定 | game\data\characters\granny.json:14 | { "when": "discounts>=2", "line": "granny_last_warm" }
M8 | 中 | 确定 | game\data\characters\granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }
M8 | 中 | 确定 | game\text\zh.csv:16 | granny_last_warm,这是我自己晒的花，你拿去泡。
M8 | 中 | 确定 | game\text\en.csv:15 | granny_last_cold,...They took someone away last night. I won't have tea.
M8 | 中 | 确定 | game\text\en.csv:16 | granny_last_warm,这是我自己晒的花，你拿去泡。
M8 | 中 | 确定 | game\README.md:36 | - 阿婆第 7 天说的话要看老周怎样了：他被带走，她说一句冷话；否则说家常。
M9 | 中 | 可能 | game\data\characters\granny.json:13 | { "when": "flag:zhou_taken", "line": "granny_last_cold" },
M9 | 中 | 可能 | game\data\characters\granny.json:14 | { "when": "discounts>=2", "line": "granny_last_warm" }
M9 | 中 | 可能 | game\data\characters\granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }
M9 | 中 | 可能 | game\data\characters\zhou.json:16 | { "button": "btn_report", "sets": "flag:zhou_taken" }
M9 | 中 | 可能 | game\data\characters\zhou.json:20 | "summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }
M9 | 中 | 可能 | game\text\zh.csv:15 | granny_last_cold,……他们昨夜把人带走了。茶我不喝了。
M9 | 中 | 可能 | game\text\zh.csv:16 | granny_last_warm,这是我自己晒的花，你拿去泡。
M9 | 中 | 可能 | game\text\zh.csv:33 | summary_taken,昨夜有人被带走。
M9 | 中 | 可能 | game\README.md:36 | - 阿婆第 7 天说的话要看老周怎样了：他被带走，她说一句冷话；否则说家常。
W1 | 想要 | 确定没有 | game\README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。
W1 | 想要 | 确定没有 | game\text\zh.csv:28 | btn_sell,照价卖
W1 | 想要 | 确定没有 | game\text\zh.csv:29 | btn_discount,少收一点
W1 | 想要 | 确定没有 | game\text\zh.csv:30 | btn_refuse,不卖
W1 | 想要 | 确定没有 | game\data\settings.json:3 | "prices": { "jasmine": 12, "coarse": 4 },
W1 | 想要 | 确定没有 | game\data\settings.json:4 | "discount": 3,
W1 | 想要 | 确定没有 | game\data\characters\granny.json:6 | "budget": 10,
W1 | 想要 | 确定没有 | game\data\characters\granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }
W2 | 想要 | 确定没有 | game\README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。
W2 | 想要 | 确定没有 | game\data\settings.json:3 | "prices": { "jasmine": 12, "coarse": 4 },
W2 | 想要 | 确定没有 | game\data\characters\granny.json:5 | "wants": "jasmine",
W2 | 想要 | 确定没有 | game\data\characters\granny.json:6 | "budget": 10,
W2 | 想要 | 确定没有 | game\data\characters\granny.json:17 | "leaveForever": { "refusedInARow": 2 },
W2 | 想要 | 确定没有 | game\data\items.json:4 | "coarse": { "image": "images\\items\\coarse_brick.png", "where": "shelf" },
W2 | 想要 | 确定没有 | game\data\characters\zhou.json:5 | "wants": "coarse",
W2 | 想要 | 确定没有 | game\text\zh.csv:14 | granny_warn,你今天不卖我……下回再这样，我就不来了。
D1 | 要老板定 | 设计 | game\data\characters\granny.json:4 | "visits": { "firstDay": 1, "everyDays": 2 },
D1 | 要老板定 | 设计 | game\data\characters\granny.json:6 | "budget": 10,
D1 | 要老板定 | 设计 | game\data\characters\granny.json:17 | "leaveForever": { "refusedInARow": 2 },
D1 | 要老板定 | 设计 | game\data\characters\granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }
D1 | 要老板定 | 设计 | game\data\settings.json:3 | "prices": { "jasmine": 12, "coarse": 4 },
D1 | 要老板定 | 设计 | game\README.md:27 | - **阿婆**（`granny`）：每两天来一次，要一壶茉莉。钱不多。连着两次被"不卖"，她就不再来（第一次被拒绝时她会说一句警告）。少收过她两次以上，第 7 天她会送一包自己晒的花。
D1 | 要老板定 | 设计 | game\text\zh.csv:14 | granny_warn,你今天不卖我……下回再这样，我就不来了。
D1 | 要老板定 | 设计 | game\README.md:34 | - 好结局：阿婆送了花，而且老周没有被带走。
