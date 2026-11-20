# Player review · A · Kindhearted and Business-minded players (2026-11-19)

- Scope: Both guests across all seven days. The Kindhearted player discounted both guests and sheltered Old Zhou. The Business-minded player declined Granny's full-price-unaffordable order, sold to Old Zhou at full price, and refused shelter. Persona 17 read all available Chinese text on those branches. The two baseline path checks used English.
- Review method: Persona review through the day-seven ledger and documented ending.
- Project map: `_map/_map.md` and the route, choice, state, item, ending, value, text, cross-route and settings tables.
- Static checks: `_summary.md`, `_text_checks.md`, and `_image_hits.md`.

## Conclusion

One Severe, four Medium, three Minor, one Needs your decision, and two Wanted but missing items. The Kindhearted route reaches both gifts and satisfies the documented good-ending conditions, but an unsuccessful click may leave Zhou's one-time gift on the table to be swept. The Business-minded route reaches the ordinary ending after two deliberate refusals end Granny's visits. The authored dialogue and guide contradictions can be checked in the sources. Exact rendering, choice timing and missing-key fallback require a runnable game.

## Player feedback

### 1 Kindhearted player
- Confused: I charged Granny less, and on the last day her flower line was in Chinese. (M1)
- Confused: When I agreed to help the guest, he said “(placeholder) Thanks.” (L2)
- Wants: I'd give Granny her pot of tea for free if I could. (W1)
- Done right: Granny remembers when I charge her less. `game/text/en.csv:13` “granny_thanks,You charged me less last time. I remember.”

### 2 Business-minded player
- Feels unfair: Her budget falls short of full price. I declined twice and Granny stopped coming. (D1)
- Wants: I'd like to sell the tea at 10. The fixed drop is bigger than what I need to make the sale. (W2)
- Done right: Granny warned me what a second refusal would cost. `game/text/en.csv:14` “granny_warn,You won't sell to me today... Do it again and I won't come back.”

### 17 Close reader
- Confused: She opened with “the usual” and immediately asked whether the stall was new. (L1)
- Confused: In Chinese, the button for turning down a place to hide says I won't sell. (L3)
- Confused: The hints help already says who Zhou is. I wanted to learn that from him. (M2)
- Done right: The guest asked for the cheapest tea, then asked for the coarse tea again on his next visit. `game/text/zh.csv:20` “zhou_first_1,粗茶。最便宜的那种。” and `game/text/zh.csv:21` “zhou_again_1,还是粗茶。”

## Issues at a glance

| ID | Severity | Confidence | Character | What the player sees | Persona |
|---|---|---|---|---|---|
| S1 | Severe | [Possible] | Old Zhou | A click can miss his one-time gift and closing can remove it. | 1 |
| M1 | Medium | [Confirmed] | Granny | English flower dialogue is still Chinese. | 1 |
| M2 | Medium | [Possible] | Old Zhou | Hint help reveals his background before his confession if available at opening. | 17 |
| M3 | Medium | [Confirmed] | Stall | Guide says three guests, design and configuration give two seats. | 2, 17 |
| M4 | Medium | [Confirmed] | Old Zhou | No English translation is supplied for his refusal reply. | 2 |
| L1 | Minor | [Confirmed] | Granny | First greeting sounds like a return visit. | 1, 17 |
| L2 | Minor | [Confirmed] | Old Zhou | Thank-you after sheltering him contains a placeholder label. | 1, 17 |
| L3 | Minor | [Confirmed] | Old Zhou | Chinese shelter refusal button reads “Won't sell.” | 17 |

## Issues

### S1 Old Zhou's button can be missed and swept away
- Severity: Severe
- Confidence: [Possible]
- Character: Old Zhou. Persona 1.
- How you get there: Shelter Zhou on day six. On day seven try to collect his table gift by clicking in its transparent padding, then close after it remains uncollected.
- What the player sees: The click leaves the button where it was. Closing removes any gift still on the table and ends day seven. This could lose the physical gift. The documented ending has no dependency on collecting the button.
- Source: `game/data/characters/zhou.json:19` “{ "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" }”. `game/data/items.json:6` sets the button to `"where": "table"`. `game/data/settings.json:6` sets `"table": { "hit": "pixel", "sweepAtClose": true },`. The static image table at `review_out/20261119_181306/_image_hits.md:17` measures “5.9%（60 个像素）” of its 32×32 image as opaque. `game/README.md:21` says “点在图的透明处不算点中” and line 22 says “桌上还没收的东西会被扫掉”.
- Cross-check: Whole-cell pickup applies to shelf tea. The button is a table item with a single dated gift event. The supplied materials give no separate pickup entry or recovery after close. Rendering scale, retry cues and actual click handling remain unknown.
- Suggestion: Give this table gift a larger hit target or make the unclaimed gift visible before closing.
- How to reproduce: Shelter Zhou on day six. On day seven click inside the rendered sprite's transparent padding and inspect the table, then close with the gift uncollected. Check whether an affordance, confirmation or recovery protects the gift.

### M1 Granny's flower line stays Chinese in English
- Severity: Medium
- Confidence: [Confirmed]
- Character: Granny. Persona 1.
- How you get there: Discount Granny's orders on days one and three. Shelter Zhou on day six. Read Granny's flower dialogue on day seven in English.
- What the player sees: “这是我自己晒的花，你拿去泡。” The line explains what Granny has given and its use.
- Source: `game/data/characters/granny.json:14` “{ "when": "discounts>=2", "line": "granny_last_warm" }”. `game/text/en.csv:16` and `game/text/zh.csv:16` both contain “granny_last_warm,这是我自己晒的花，你拿去泡。”.
- Cross-check: Two affordable discounts satisfy the warm and gift conditions. Choosing shelter keeps the cold predicate off on this run. The English source contains no alternate translation of that key.
- Suggestion: Translate the English row while preserving the item explanation.

### M2 Hint help gives away Old Zhou's background
- Severity: Medium
- Confidence: [Possible]
- Character: Old Zhou. Persona 17 and English cross-check.
- How you get there: If options help is accessible before day six, read the Show hints tooltip.
- What the player sees: “Old Zhou is a deserter, so his icon is grey.” This reveals the background the game reserves for his day-six confession.
- Source: `game/text/en.csv:4` “option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey.”. `game/text/zh.csv:4` carries the same disclosure. `game/README.md:29` says “老周的来历在第 6 天以前不能让玩家知道。”.
- Cross-check: The supplied settings and string have no visible progress gate or safe alternate tooltip. The runtime route into that tooltip is undocumented.
- Suggestion: Describe what the toggle does without naming a guest or his backstory.
- How to reproduce: In a new English run, open options before the first visit. Check whether the tooltip is accessible and whether it names Zhou. Repeat in Chinese.

### M3 The guide promises three guest places with two seats
- Severity: Medium
- Confidence: [Confirmed]
- Character: Shared stall. Personas 2 and 17.
- How you get there: Read the first guide page and compare it with the authored stall capacity.
- What the player sees: “The stall can serve up to three guests at once.” The authored stall has two seats.
- Source: `game/text/en.csv:5` “guide_page_1,The stall can serve up to three guests at once. Guests leave if they wait too long.”. `game/data/settings.json:2` “"stall": { "seats": 2, "days": 7 },”. `game/README.md:8` likewise states “茶摊有两个座位”.
- Cross-check: Chinese help also promises three. The supplied design gives no third place or separate capacity modifier. Live queuing and the result of a third arrival are unspecified.
- Suggestion: Set both guide values to two, or generate the displayed capacity from the stall settings.

### M4 No English reply is supplied when the player refuses Zhou shelter
- Severity: Medium
- Confidence: [Confirmed]
- Character: Old Zhou. Persona 2.
- How you get there: On day six, after Zhou asks to hide, choose Refuse in English.
- What the player sees: The intended acknowledgement has no English text. The exact missing-string behavior is unknown.
- Source: `game/data/characters/zhou.json:15` “{ "button": "btn_refuse", "reply": "zhou_refused" },”. `game/text/zh.csv:25` “zhou_refused,……知道了。”.
- Cross-check: Checked the full English CSV. It assigns the alternative shelter reply at line 23 and the refusal button label at line 28. Neither serves as `zhou_refused`. Refusal has no later gift or report recap.
- Suggestion: Add an English localized row for the configured reply.

### L1 Granny says “the usual” at her first visit
- Severity: Minor
- Confidence: [Confirmed]
- Character: Granny. Personas 1 and 17.
- How you get there: Open the stall on day one and read Granny's two first-visit lines.
- What the player sees: “The usual. A pot of jasmine.” followed by “This stall is new, isn't it?” The greeting suggests a previous order at this stall. She could mean her personal usual, but the two adjacent lines make the intent ambiguous.
- Source: `game/data/characters/granny.json:8` “"first": [ "granny_first_1", "granny_first_2" ],”. `game/text/en.csv:10` “granny_first_1,The usual. A pot of jasmine.”. `game/text/en.csv:11` “granny_first_2,This stall is new, isn't it?”.
- Cross-check: The first visit index is day one and repeat visits have a separate line. Both languages have this wording.
- Suggestion: Ask for jasmine directly on the first visit and save “the usual” for a repeat visit.

### L2 Zhou's shelter thank-you contains a placeholder label
- Severity: Minor
- Confidence: [Confirmed]
- Character: Old Zhou. Personas 1 and 17.
- How you get there: On day six agree to let him stay.
- What the player sees: The configured immediate reply is “(placeholder) Thanks.” The marker interrupts the scene.
- Source: `game/data/characters/zhou.json:14` selects `"reply": "zhou_stay_thanks"`. `game/text/en.csv:23` “zhou_stay_thanks,(placeholder) Thanks.”. `game/text/zh.csv:24` “zhou_stay_thanks,（占位）谢谢。”.
- Cross-check: The word is in the response value itself. The refusal and report choices are separate and give no alternate shelter reply.
- Suggestion: Ship the final thank-you without the draft marker.

### L3 The Chinese shelter refusal is labeled as refusing a sale
- Severity: Minor
- Confidence: [Confirmed]
- Character: Old Zhou. Persona 17.
- How you get there: Use Chinese and read Zhou's day-six options after he asks to hide.
- What the player sees: “不卖” sits alongside the options to let him stay and report him. It describes declining a sale in a conversation about shelter.
- Source: `game/data/characters/zhou.json:15` “{ "button": "btn_refuse", "reply": "zhou_refused" },”. `game/text/zh.csv:22` “zhou_ask_1,……我是从营里跑出来的。能在你摊子后面躲一晚吗？”. `game/text/zh.csv:30` “btn_refuse,不卖”.
- Cross-check: The general sale choice on `game/README.md:10` is explicitly “不卖”. The shelter choice shares its key. English “Refuse” fits both contexts.
- Suggestion: Use a shelter-specific label in the Chinese menu.

## Wanted but missing

### W1 Give Granny her tea for free
- Who wants it: Persona 1, who favors giving guests help without payment.
- Where it happens: Granny's jasmine order on the first visit.
- Options today: `game/README.md:10` “玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。” The standard price is 12 and the one discount is 3. `game/data/settings.json:3` “"prices": { "jasmine": 12, "coarse": 4 },” and `game/data/settings.json:4` “"discount": 3,”.
- Without it: The most generous sale shown still charges Granny 9. Refusal provides no tea.
- Similar options elsewhere: Guests give day-seven gifts to the player on the specified branches. The sale menu has no player-to-guest gift.
- Confidence: [Definitely missing] from the supplied menus. Checked all sale buttons, both language tables, prices and gift entries. The gift entries only put guest gifts on the table.
- How to add it: Add a comp option that tells the player whether the gift counts toward Granny's gratitude.

### W2 Offer Granny a two-coin discount instead of three
- Who wants it: Persona 2, who wants to complete the sale at the highest price the guest can pay.
- Where it happens: Granny's jasmine order when full price is 12 and she has 10.
- Options today: `game/README.md:10` “玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。” `game/data/settings.json:4` “"discount": 3,” and `game/data/characters/granny.json:6` “"budget": 10,”.
- Without it: The only documented affordable price is 9. Keeping full price leads this persona to refuse the sale.
- Similar options elsewhere: The same price control covers coarse tea. No custom-price control is shown elsewhere in the supplied materials.
- Confidence: [Definitely missing] from the supplied menus. Checked standard and shelter choices, settings, and both button tables for a price-entry or intermediate discount key.
- How to add it: Add a fixed two-coin option or a negotiated price with a stated effect on the discount counter.

## Needs your decision

### D1 Declining two unaffordable full-price sales ends Granny's route
- Confidence: [Design]
- Design matches data: `game/README.md:27` says “连着两次被"不卖"，她就不再来” and `game/data/characters/granny.json:17` sets “"leaveForever": { "refusedInARow": 2 },”.
- Player impact: Persona 2 declines on days one and three, expects no sale, and then has no Granny visits or gift on days five and seven. Granny's first warning makes the second refusal an informed choice. Her disappearance and the absence of flowers lead to the ordinary ending.
- Options: Preserve the warning and consequence if asking players to choose between margin and the relationship is intentional. Or provide a way to skip the sale that preserves the relationship if helping Granny is meant to be optional within her route.
- Cross-check: `game/text/en.csv:14` “granny_warn,You won't sell to me today... Do it again and I won't come back.” `game/README.md:34` “- 好结局：阿婆送了花，而且老周没有被带走。” The affordable discount is 9. This is the specified consequence of the business choice.

## Checked and fine

- Kindhearted route: The 12 price less the 3 discount is 9, inside Granny's 10 budget. Two grants by day three meet the gift predicate. Zhou's shelter and button event are linked explicitly. `game/data/settings.json:3` “"prices": { "jasmine": 12, "coarse": 4 },”. `game/data/settings.json:4` “"discount": 3,”. `game/data/characters/granny.json:6` “"budget": 10,”.
- Business route: Zhou's 4 budget covers the 4 coarse tea. Granny warns before the repeat refusal and her later absence follows the described rule. `game/data/characters/zhou.json:6` “"budget": 4,”. `game/text/en.csv:14` “granny_warn,You won't sell to me today... Do it again and I won't come back.”
- Shared interaction: The coarse tea's low opacity does not impair the specified shelf-cell selection. The hint icon is decorative by design. `game/data/settings.json:5` “"shelf": { "hit": "cell" },” and `game/data/settings.json:7` “"hints": { "icon": "images\\ui\\hint_icon.png", "clickable": false }”.
- Close reading: The English file conveys the discount gratitude despite omitting the amount. Raw Chinese placeholder behavior is unknown. `game/text/en.csv:13` “granny_thanks,You charged me less last time. I remember.” and `game/text/zh.csv:13` “granny_thanks,上回你少收了我{0}文，我记着呢。”.

## Not covered this time

- Persona 17 has no project overlay. The Chinese close-reading overlay was inferred from the general persona, independently of the English artifact language.
- The game files contain design, data and text. Input scaling, dialogue replay, missing-localization fallback, persistence across saves, and actual order within day-six and day-seven events require a runtime.
- The reporting branch and its overlapping last-day predicates are outside these two choice paths. Group B covers reporting.

## Index

| ID | Severity | Confidence | File:line | Quote |
|---|---|---|---|---|
| S1 | Severe | [Possible] | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" }, |
| S1 | Severe | [Possible] | game/data/characters/zhou.json:19 | "gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" }, |
| S1 | Severe | [Possible] | game/data/items.json:6 | "old_button": { "image": "images\\items\\old_button.png", "where": "table" } |
| S1 | Severe | [Possible] | game/data/settings.json:6 | "table": { "hit": "pixel", "sweepAtClose": true }, |
| S1 | Severe | [Possible] | game/README.md:14 | 一局 7 天。第 7 天收摊以后出结局。 |
| S1 | Severe | [Possible] | game/README.md:21 | - **桌上**：客人送的东西留在桌上。玩家点它，收进柜子。点在图的透明处不算点中（按图的形状判定，`table.hit` = `pixel`）。 |
| S1 | Severe | [Possible] | game/README.md:22 | - 收摊时，桌上还没收的东西会被扫掉（`table.sweepAtClose`）。 |
| S1 | Severe | [Possible] | game/README.md:34 | - 好结局：阿婆送了花，而且老周没有被带走。 |
| M1 | Medium | [Confirmed] | game/data/characters/granny.json:14 | { "when": "discounts>=2", "line": "granny_last_warm" } |
| M1 | Medium | [Confirmed] | game/data/characters/granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" } |
| M1 | Medium | [Confirmed] | game/text/en.csv:16 | granny_last_warm,这是我自己晒的花，你拿去泡。 |
| M1 | Medium | [Confirmed] | game/text/zh.csv:16 | granny_last_warm,这是我自己晒的花，你拿去泡。 |
| M2 | Medium | [Possible] | game/text/en.csv:4 | option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey. |
| M2 | Medium | [Possible] | game/text/zh.csv:4 | option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。 |
| M2 | Medium | [Possible] | game/README.md:29 | - 设定：老周的来历在第 6 天以前不能让玩家知道。 |
| M2 | Medium | [Possible] | project.json:133 | "第 6 天以前，玩家看得到的文字里不出现老周的来历。", |
| M3 | Medium | [Confirmed] | game/text/en.csv:5 | guide_page_1,The stall can serve up to three guests at once. Guests leave if they wait too long. |
| M3 | Medium | [Confirmed] | game/text/zh.csv:5 | guide_page_1,茶摊同时最多招待三位客人。客人等久了会走。 |
| M3 | Medium | [Confirmed] | game/data/settings.json:2 | "stall": { "seats": 2, "days": 7 }, |
| M3 | Medium | [Confirmed] | game/README.md:8 | 2. 摆摊。茶摊有两个座位（`data\settings.json` 的 `stall.seats`）。 |
| M4 | Medium | [Confirmed] | game/data/characters/zhou.json:15 | { "button": "btn_refuse", "reply": "zhou_refused" }, |
| M4 | Medium | [Confirmed] | game/text/zh.csv:25 | zhou_refused,……知道了。 |
| M4 | Medium | [Confirmed] | game/text/en.csv:28 | btn_refuse,Refuse |
| L1 | Minor | [Confirmed] | game/data/characters/granny.json:8 | "first": [ "granny_first_1", "granny_first_2" ], |
| L1 | Minor | [Confirmed] | game/text/en.csv:10 | granny_first_1,The usual. A pot of jasmine. |
| L1 | Minor | [Confirmed] | game/text/en.csv:11 | granny_first_2,This stall is new, isn't it? |
| L1 | Minor | [Confirmed] | game/text/zh.csv:10 | granny_first_1,老样子，一壶茉莉。 |
| L1 | Minor | [Confirmed] | game/text/zh.csv:11 | granny_first_2,这摊子是新开的吧？ |
| L2 | Minor | [Confirmed] | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" }, |
| L2 | Minor | [Confirmed] | game/text/en.csv:23 | zhou_stay_thanks,(placeholder) Thanks. |
| L2 | Minor | [Confirmed] | game/text/zh.csv:24 | zhou_stay_thanks,（占位）谢谢。 |
| L3 | Minor | [Confirmed] | game/data/characters/zhou.json:15 | { "button": "btn_refuse", "reply": "zhou_refused" }, |
| L3 | Minor | [Confirmed] | game/text/zh.csv:22 | zhou_ask_1,……我是从营里跑出来的。能在你摊子后面躲一晚吗？ |
| L3 | Minor | [Confirmed] | game/text/zh.csv:30 | btn_refuse,不卖 |
| L3 | Minor | [Confirmed] | game/README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。 |
| W1 | Wanted | [Definitely missing] | game/README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。 |
| W1 | Wanted | [Definitely missing] | game/text/en.csv:26 | btn_sell,Sell at price |
| W1 | Wanted | [Definitely missing] | game/text/en.csv:27 | btn_discount,Charge less |
| W1 | Wanted | [Definitely missing] | game/text/en.csv:28 | btn_refuse,Refuse |
| W1 | Wanted | [Definitely missing] | game/data/settings.json:4 | "discount": 3, |
| W2 | Wanted | [Definitely missing] | game/README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。 |
| W2 | Wanted | [Definitely missing] | game/data/characters/granny.json:6 | "budget": 10, |
| W2 | Wanted | [Definitely missing] | game/data/settings.json:3 | "prices": { "jasmine": 12, "coarse": 4 }, |
| W2 | Wanted | [Definitely missing] | game/data/settings.json:4 | "discount": 3, |
| D1 | Needs your decision | [Design] | game/README.md:27 | - **阿婆**（`granny`）：每两天来一次，要一壶茉莉。钱不多。连着两次被"不卖"，她就不再来（第一次被拒绝时她会说一句警告）。少收过她两次以上，第 7 天她会送一包自己晒的花。 |
| D1 | Needs your decision | [Design] | game/data/characters/granny.json:17 | "leaveForever": { "refusedInARow": 2 }, |
| D1 | Needs your decision | [Design] | game/text/en.csv:14 | granny_warn,You won't sell to me today... Do it again and I won't come back. |
| D1 | Needs your decision | [Design] | game/README.md:34 | - 好结局：阿婆送了花，而且老周没有被带走。 |
