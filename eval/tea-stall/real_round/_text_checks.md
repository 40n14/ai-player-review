# 文字检查（玩家视角审查用）

生成：2026-11-19 15:30；项目：茶摊（真跑的一轮）；脚本：`static\review_text_checks.py`

只读两个 csv 和项目设置的 static 一节。"可疑"是玩家会看到的文字问题，多数一眼能定；"意思可能不一样"那几类是提示，要人对着读。
行号：zh:N = zh.csv 第 N 行，en:N = en.csv 第 N 行。

## 一、可疑（7 条）

分类：只在中文 1；英文漏翻 1；占位符 1；露出草稿字样 1；剧透 1；说明和设置不符 2

| 类 | 键 | 中文 | 英文 | 为什么 | 行 |
|---|---|---|---|---|---|
| 只在中文 | zhou_refused | ……知道了。 |  | 英文版会显示键名 | zh:25 |
| 英文漏翻 | granny_last_warm | 这是我自己晒的花，你拿去泡。 | 这是我自己晒的花，你拿去泡。 | 英文里有中文字或中文标点：。你去己我拿是晒泡的自花这， | zh:16 en:16 |
| 占位符 | granny_thanks | 上回你少收了我{0}文，我记着呢。 | You charged me less last time. I remember. | 中文 {0}，英文 无 | zh:13 en:13 |
| 露出草稿字样 | zhou_stay_thanks | （占位）谢谢。 | (placeholder) Thanks. | 中文里有「（占位）」，玩家会看到 | zh:24 en:23 |
| 剧透 | option_hints_tip | 打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。 | When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey. | 老周的来历：出现「逃兵、deserter」。设定：老周的来历要到第 6 天他自己说出来，设置说明和说明页不该先说。 | zh:4 en:4 |
| 说明和设置不符 | guide_page_1 | 茶摊同时最多招待三位客人。客人等久了会走。 | The stall can serve up to three guests at once. Guests leave if they wait too long. | 同时招待几位客人：中文说「同时最多招待三位」，设置 stall.seats = 2（settings.json） | zh:5 en:5 |
| 说明和设置不符 | guide_page_1 | 茶摊同时最多招待三位客人。客人等久了会走。 | The stall can serve up to three guests at once. Guests leave if they wait too long. | 同时招待几位客人：英文说「serve up to three guests」，设置 stall.seats = 2（settings.json） | zh:5 en:5 |

## 二、说明里的数字（和设置对照）

| 说的什么 | 键 | 语言 | 原文 | 设置 | 对不对 |
|---|---|---|---|---|---|
| 同时招待几位客人 | guide_page_1 | 中文 | 同时最多招待三位 | stall.seats=2 | **不对** |
| 同时招待几位客人 | guide_page_1 | 英文 | serve up to three guests | stall.seats=2 | **不对** |

## 三、候选清单：csv 注释说是"占位 / 草稿"的段落（1 段，2 个键，其中 2 个在代码 / JSON 里点了名；不算问题）

只是**候选**：注释说是占位，不等于玩家这一版会看到。按 csv 注释算：一行注释管它下面连着的键（到下一行注释或空行为止），`# ====` 横幅管到下一个横幅，可能多算几个。注释里的文件名（如 `某某草稿.txt`）不算；同一行注释里也写了"定稿"的标「部分定稿」（例：前两句定稿、最后一句是草稿）。"点了名" = 作品源码里有这个键的字面量（代码里拼出来的键数不到）；玩家看不看得到，还要看那段代码走不走得到（审查员去核对）。发布前给负责人看的清单。

| zh.csv 行 | 段落说明 | 键数 | 点了名的 | 键（前几个） |
|---|---|---|---|---|
| 23 | 占位：等作者写 | 2 | 2 | zhou_stay_thanks, zhou_refused |

