# Player review · B (2026-11-19)

- **Scope** All seven days of the Granny and Old Zhou routes, including the closing outcomes and the report, shelter, and refusal branches. English localization with Chinese evidence preserved as written.
- **Review method** Persona review. Persona 21, Reporter, sells at full price and reports Old Zhou. Persona 18, Rapid clicker, skips dialogue and the recap, tries the first listed choices, and picks up gifts quickly in a separate variant where that conflicts with reporting. Persona 14, Repeated reloader, attempts replay at the Granny refusal, Old Zhou decision, and day-seven close.
- **Project map** `_map/_map.md` and the routes, choice, state, ending, text, and cross-route tables. **Static checks** `_summary.md`, `_text_checks.md`, and `_image_hits.md`.

## Conclusion

The report branch produces a next-morning recap and an ordinary ending by design. The first configured shelter choice can lead to a day-seven collectible that disappears at closing after a missed click. Three text findings cover a possible early spoiler, a missing English reply, and an explicit placeholder. There are 1 Severe, 3 Medium, 0 Minor, 1 Needs your decision, and 1 Wanted but missing. Save, replay, and same-frame input cannot be confirmed from the supplied materials.

## Player feedback

### 21 Reporter
- Confused: If I check the hint setting early, it may tell me who Old Zhou is before I meet him. (M1)
- Done right: I chose Report him, and the next morning my recap said someone was taken away. (`game/text/en.csv:31` `summary_taken,Someone was taken away last night.`)
- Wants: I'd like the recap to say what came of my report and who was taken. (W1)
- Feels unfair: Even if I help Granny enough for her to bring flowers, reporting him leaves me with the ordinary ending. (D1)

### 14 Repeated reloader
- In one line: I'd try the choices from the same point so I could compare the next day, but this design sample does not establish that I can reload a scene. (`game/README.md:3` `这是给审查工具包做演示用的假游戏。没有可以运行的程序，只有设计、数据和文本。`)

### 18 Rapid clicker
- Confused: I tapped near the edge of the old button and it stayed on the table. When I closed up, it was gone. (S1)
- Done right: I could pick up the coarse tea by clicking the shelf square. (`game/README.md:20` ``- **货架**：茶在货架的格子里。玩家点格子就拿起来（按整格判定，`data\settings.json` 的 `shelf.hit` = `cell`）。``)

## Issues at a glance

| ID | Severity | Confidence | Character | What the player sees | Persona |
|---|---|---|---|---|---|
| S1 | Severe | [Confirmed] | Old Zhou | Uncollected old button disappears at the final close | 18 |
| M1 | Medium | [Possible] | Old Zhou | The hint tooltip states his secret before the story reveal if it opens early | 21 |
| M2 | Medium | [Confirmed] | Old Zhou | The day-six refusal reply has no English localization | 21, branch comparison |
| M3 | Medium | [Confirmed] | Old Zhou | The day-six shelter reply includes a visible placeholder | 21, branch comparison |

## Issues

### S1 A missed click can cost Old Zhou's gift at the last closing
- Severity: Severe
- Confidence: [Confirmed]
- Character: Old Zhou
- Persona: 18 Rapid clicker
- How you get there: Select Let him stay the night on day six. On day seven, click a transparent part of the old button image, then close the stall without the button going into the cabinet.
- What the player sees: The copper button stays on the table after a click on a transparent pixel. At closing it is swept away and the seven-day run ends. The supplied image check measured 60 of 1,024 pixels as nontransparent. The corner at local coordinate (0,0) lies outside the reported nontransparent bounding box.
- Why it is wrong: A click within the image bounds can fail to collect an ending-day reward that the player has already earned. The relevant impact is loss at closing.
- Cross-check: Whole-cell pickup applies to the tea shelf only. The gift entry explicitly puts the button on the table. Closing sweep is explicit and the project documents no repeat gift after day seven. The exact rendered scale and pointer feedback require a runnable build.
- Suggestion: Give table gifts a larger pickup area or move uncollected one-time gifts to the cabinet at the final close.
- Source: `game/data/characters/zhou.json:14` `{ "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },`, `game/data/characters/zhou.json:19` `"gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },`, `game/data/items.json:6` `"old_button": { "image": "images\\items\\old_button.png", "where": "table" }`, `game/data/settings.json:6` `"table": { "hit": "pixel", "sweepAtClose": true },`, `game/README.md:14` `一局 7 天。第 7 天收摊以后出结局。`

### M1 The Show hints tooltip gives away Old Zhou's day-six reveal
- Severity: Medium
- Confidence: [Possible]
- Character: Old Zhou
- Persona: 21 Reporter
- How you get there: At the start of a fresh run, open the Show hints tooltip before day six if the options screen permits it.
- What the player sees: The configured tooltip in both languages identifies Old Zhou as a deserter. His main dialogue with the disclosure is scheduled for day six.
- Why it is wrong: The design and project invariant both reserve the player's first encounter with that information for day six.
- Cross-check: The configured hints object defines an icon and disables clicks on the icon, with no day gate shown. The English tooltip contains the disclosure in plain text. The example supplies no settings renderer, so the binding and earliest time it appears are unverified.
- Suggestion: Keep the tooltip about what the switch does. Any identity-specific example can wait for the reveal.
- How to reproduce: Start a fresh run, access Show hints on days one through five, and inspect the tooltip before speaking to Old Zhou on day six.
- Source: `game/text/en.csv:4` `option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey.`, `game/text/zh.csv:4` `option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。`, `game/README.md:29` `- 设定：老周的来历在第 6 天以前不能让玩家知道。`, `project.json:133` `"第 6 天以前，玩家看得到的文字里不出现老周的来历。",`

### M2 The refusal branch lacks its English reply
- Severity: Medium
- Confidence: [Confirmed]
- Character: Old Zhou
- Persona: 21 Reporter, comparison with the other day-six choices
- How you get there: Use English text, answer the day-six shelter request, and select Refuse.
- What the player sees: The choice requests `zhou_refused` and the Chinese table has a reply. No row supplies the corresponding English line. Display behavior for the missing key is unspecified.
- Why it is wrong: English lacks a configured line that Chinese supplies for the same story choice.
- Cross-check: Read the full English CSV and searched all game JSON, CSV, and Markdown for `zhou_refused`. There is one branch reference and one Chinese translation, with no English entry or documented fallback.
- Suggestion: Add the English refusal reply and verify that localization renders it.
- Source: `game/data/characters/zhou.json:15` `{ "button": "btn_refuse", "reply": "zhou_refused" },`, `game/text/zh.csv:25` `zhou_refused,……知道了。`

### M3 The shelter reply shows a draft marker
- Severity: Medium
- Confidence: [Confirmed]
- Character: Old Zhou
- Persona: 21 Reporter, comparison with the other day-six choices
- How you get there: Select Let him stay the night in the day-six shelter dialogue and read Old Zhou's reply.
- What the player sees: English `zhou_stay_thanks` says "(placeholder) Thanks." The Chinese reply also begins with a placeholder marker.
- Why it is wrong: A directly referenced branch reply contains draft text after a major choice.
- Cross-check: The branch names that reply explicitly. The full text tables contain one row per language for that key and there is no separate replacement reply in the supplied game data.
- Suggestion: Finalize the line in both languages.
- Source: `game/data/characters/zhou.json:14` `{ "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },`, `game/text/en.csv:23` `zhou_stay_thanks,(placeholder) Thanks.`, `game/text/zh.csv:24` `zhou_stay_thanks,（占位）谢谢。`

## Wanted but missing

### W1 The reporter wants a recap that confirms what happened to Old Zhou
- Who wants it: Persona 21, who checks the next morning's recap for the outcome of reporting.
- Where it happens: The day-seven recap after choosing Report him during the day-six shelter request.
- Options today: Let him stay the night, Refuse, and Report him. The report outcome is paired with "Someone was taken away last night." Granny's cold line, if she arrives, also says "someone."
- Without it: The player can infer what happened from the timing. None of the supplied recap or dialogue text ties the outcome explicitly to Old Zhou or to the report.
- Similar options elsewhere: The ledger records earnings and visitors. A report-history view is not described.
- Confidence: [Possibly missing]. The configured entries and text are available, but the actual recap and any additional report interface are not implemented in the supplied materials. Searched `summary_taken`, `zhou_taken`, `btn_report`, `recap`, and the two Chinese terms for the recap and ledger.
- How to add it: After an intentional report, have the recap link the outcome to that action or identify Old Zhou. Preserve the anonymous version where the player has no reason to know.
- Source: `game/data/characters/zhou.json:16` `{ "button": "btn_report", "sets": "flag:zhou_taken" }`, `game/data/characters/zhou.json:20` `"summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }`, `game/text/en.csv:30` `btn_report,Report him`, `game/text/en.csv:31` `summary_taken,Someone was taken away last night.`

## Needs your decision

### D1 Reporting excludes the good ending even when Granny brings flowers
- Confidence: [Design]
- How you get there: Charge Granny less on two earlier visits so she can bring flowers on day seven. Choose Report him on day six and close on day seven.
- What the player sees: The day-seven recap acknowledges an arrest. The designed ending rule gives this run the ordinary ending even if Granny brought flowers. The choice label communicates the action, with no supplied copy about the ending condition.
- Cross-check: The report sets `zhou_taken`, while the flower gift requires two discounts and is not gated on `zhou_taken`. The ending explicitly requires both flowers and Old Zhou not being taken.
- Options: Keep the ending rule and give some advance story feedback that a report changes the outcome, or keep the consequence implicit and let the ordinary ending communicate it retrospectively.
- Source: `game/data/characters/granny.json:18` `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`, `game/data/characters/zhou.json:16` `{ "button": "btn_report", "sets": "flag:zhou_taken" }`, `game/README.md:34` `- 好结局：阿婆送了花，而且老周没有被带走。`, `game/README.md:35` `- 普通结局：别的情况。`

## Checked and fine

- Reporter: Days two and four have coarse-tea orders and no configured reporting choice. Day six is the one place the project overlay directs this persona to report. The day-seven recap follows that report. Granny's cold dialogue and the public recap both describe an unnamed person being taken last night. The supplied sources do not establish that she knows a secret identity.
- Rapid clicker: Coarse tea is on the shelf and uses a cell hit area. The hint icon is display-only. Their low opaque area does not establish a pickup failure. Granny's first-refusal warning exists even if this persona skips it.
- Route comparison: Refusing shelter sets neither branch flag in the supplied choice. The design describes no later reply event for that path. Sheltering produces the button and reporting produces the recap. The data contains no basis for assuming both happen after a single selection.

## Not covered this time

- Personas 14 and 18 lack a project overlay entry and were derived from the general persona definitions. Persona 14 needs a runnable build with save or reload support. Save at the start of day six if available, choose each branch, and reload between choices. Compare recap, cabinet, day-seven dialogue, and ending across replays. Also force-close before and after the day-seven recap and close to check for duplicate messages or flags.
- Runtime dispatch, actual button order, and double-submit guards are absent. In a runnable build, compare one click with same-frame double clicks on sale, dialogue advance, shelter choice, and pickup. Confirm one transaction, one dialogue step, one branch, and one gift.
- Visit handling when Granny cannot pay full price is unspecified. The two-refusal variant deliberately uses Refuse; it does not assume an unaffordable attempt counts as a refusal. The precedence of Granny's cold and warm last-day lines when both requirements hold is unspecified.
- Layout, UI fallback for the missing English key, first tooltip availability, and item click feedback require an in-game check. No save, build, tests, or gameplay were run.

## Index

| ID | Severity | Confidence | File:line | Quote |
|---|---|---|---|---|
| S1 | Severe | [Confirmed] | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" }, |
| S1 | Severe | [Confirmed] | game/data/characters/zhou.json:19 | "gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" }, |
| S1 | Severe | [Confirmed] | game/data/items.json:6 | "old_button": { "image": "images\\items\\old_button.png", "where": "table" } |
| S1 | Severe | [Confirmed] | game/data/settings.json:6 | "table": { "hit": "pixel", "sweepAtClose": true }, |
| S1 | Severe | [Confirmed] | game/README.md:14 | 一局 7 天。第 7 天收摊以后出结局。 |
| M1 | Medium | [Possible] | game/text/en.csv:4 | option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey. |
| M1 | Medium | [Possible] | game/text/zh.csv:4 | option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。 |
| M1 | Medium | [Possible] | game/README.md:29 | - 设定：老周的来历在第 6 天以前不能让玩家知道。 |
| M1 | Medium | [Possible] | project.json:133 | "第 6 天以前，玩家看得到的文字里不出现老周的来历。", |
| M2 | Medium | [Confirmed] | game/data/characters/zhou.json:15 | { "button": "btn_refuse", "reply": "zhou_refused" }, |
| M2 | Medium | [Confirmed] | game/text/zh.csv:25 | zhou_refused,……知道了。 |
| M3 | Medium | [Confirmed] | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" }, |
| M3 | Medium | [Confirmed] | game/text/en.csv:23 | zhou_stay_thanks,(placeholder) Thanks. |
| M3 | Medium | [Confirmed] | game/text/zh.csv:24 | zhou_stay_thanks,（占位）谢谢。 |
| W1 | Wanted | [Possibly missing] | game/data/characters/zhou.json:16 | { "button": "btn_report", "sets": "flag:zhou_taken" } |
| W1 | Wanted | [Possibly missing] | game/data/characters/zhou.json:20 | "summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" } |
| W1 | Wanted | [Possibly missing] | game/text/en.csv:30 | btn_report,Report him |
| W1 | Wanted | [Possibly missing] | game/text/en.csv:31 | summary_taken,Someone was taken away last night. |
| D1 | Needs your decision | [Design] | game/data/characters/granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" } |
| D1 | Needs your decision | [Design] | game/data/characters/zhou.json:16 | { "button": "btn_report", "sets": "flag:zhou_taken" } |
| D1 | Needs your decision | [Design] | game/README.md:34 | - 好结局：阿婆送了花，而且老周没有被带走。 |
| D1 | Needs your decision | [Design] | game/README.md:35 | - 普通结局：别的情况。 |

