# Player review · S · Softlocks (2026-11-19)

- Scope: All seven days, both guest routes, all three final choices, both endings, both gifts and the shared stall.
- Review method: Softlocks. Persona 4 (careless player) supplied missed-click and missed-visit scenarios.
- Project map: This round's `_map/_map.md` and route, state, item and ending tables, checked against the game design and data.
- Static checks: This round's `_summary.md`, `_text_checks.md` and `_image_hits.md`.

## Conclusion

The design has a route to the day-seven ending even after Granny stops coming or either gift is missed. The largest loss comes from an opaque-pixel click requirement followed by a final-day sweep. Old Zhou's old copper button is the most exposed, with only 60 of its 1,024 image pixels available for a hit under the documented rule. The review found 1 Severe, 1 Medium, 0 Minor, 1 Needs your decision and 0 Wanted but missing. All conclusions are based on the design and data.

## Player feedback

### 4 Careless player

- Stuck: “I let him stay. The copper button was there on the last day, but my click missed. I closed up and it never made it into my cabinet.” (S1)
- Confused: “If I can open that hint setting at the start, it tells me what the guest is before he tells me himself.” (M1)
- Feels unfair: “I turned Granny away twice and didn't see her again, even though I still had days left to make up for it.” (D1)
- Done right: “After I turned Granny away I got a warning that doing it again would mean she wouldn't come back.” (`game/text/en.csv:14`, `granny_warn,You won't sell to me today... Do it again and I won't come back.`)

## Required progression points

| Required point | What it needs | How it could be lost | What happens next |
|---|---|---|---|
| Open, serve and close each day | Advance through the morning recap, stall, guest orders and night ledger | Skip a guest, miss a shelf click or leave the current action open | Cash and seat behavior after an unresolved action requires a build. The design describes a refusal exit, departures and closing. `game/README.md:7-14` |
| Granny sale, days 1, 3, 5, 7 | Scheduled visit and jasmine. Charge less costs 9 against a budget of 10 | Full price is 12, and two consecutive refusals remove future visits | A discount fits the budget. The first refusal has a warning and the second closes the branch. `game/data/settings.json:3-5`, `game/data/characters/granny.json:4-6`, `game/data/characters/granny.json:11`, `game/data/characters/granny.json:17` |
| Granny's gift on day 7 | Day-seven gift event and two discounts | Refuse twice or reach the final visit without two earlier discounts | No documented replacement visit. A second discount on the final visit needs an event-order check. `game/README.md:27`, `game/data/characters/granny.json:17-18` |
| Old Zhou's sales on days 2 and 4 | Scheduled visit and coarse tea. Four coins cover his full price | Aim at a transparent part of the tea image, decline to sell or miss the visit | Shelf selection uses the whole cell. The data shows a day-six visit with no prerequisite from earlier purchases. `game/data/characters/zhou.json:4-10`, `game/data/settings.json:3-5`, `game/README.md:20` |
| Old Zhou's decision on day 6 | Reach the day-six visit | Miss the visit or choose a different branch from the one desired | Shelter, Refuse and Report are listed. Shelter writes the button flag and Report writes the recap flag. Refusal sends him away. `game/data/characters/zhou.json:10-20`, `game/README.md:28-30` |
| Day-seven recap and Granny's dialogue | Report supplies the taken flag. Granny's warm line additionally tests two discounts | Missing the report means no taken recap, while two discounts and report can make both lines eligible | The named flag has a writer. The recap is present in both languages. Day-seven line precedence requires a build. `game/data/characters/zhou.json:16`, `game/data/characters/zhou.json:20`, `game/data/characters/granny.json:12-15`, `game/text/en.csv:15`, `game/text/en.csv:31` |
| Transfer the day-seven gifts to the cabinet | A gift on the table and a click on an opaque part of its image before close | Click a transparent pixel, then close without retrying | Closing sweeps uncollected table gifts. The day-seven cutoff leaves no later gift day. `game/data/items.json:5-6`, `game/data/settings.json:6`, `game/README.md:14`, `game/README.md:21-22` |
| End the run at the final close | Close on day seven. The good ending requires Granny to give flowers and Old Zhou to avoid being taken | Lose Granny's branch, miss the required discounts, report Old Zhou or leave flowers uncollected | The ordinary ending is defined for other cases. The design specifies that Granny gives the flowers. It leaves the actual ending implementation open. `game/README.md:14`, `game/README.md:34-35` |

## Issues at a glance

| ID | Severity | Confidence | Character | What the player sees |
|---|---|---|---|---|
| S1 | Severe | [Confirmed] | Old Zhou and Granny | A failed gift click can be followed by the last close, which sweeps the gift away. |
| M1 | Medium | [Possible] | Old Zhou | The hint tooltip contains the day-six reveal and may be available earlier. |

## Issues

### S1 A missed gift click can cost the player the reward at the final close

- Severity: Severe
- Confidence: [Confirmed]
- Character: Old Zhou and Granny
- How you get there:
  1. On day six pick “Let him stay the night.” The choice writes `zhou_sheltered` and the gift rule places the old copper button on day seven.
  2. On day seven click a transparent point inside its 32×32 image. The transparent pixel misses under the table rule, leaving the item on the table.
  3. Close without successfully collecting it. The close sweeps the table and ends the run.
  4. The same loss is reachable for the flowers after charging Granny less on days one and three, keeping her route open and missing the flower click on day seven.
- What the player sees: A gift on the table stays there after the click. After the final close the cabinet lacks that gift.
- Why it is wrong: The game has asked the player to click the gift to collect it. A miss in its transparent image area can silently cost the only reward of that branch. This affects collection. The documented ending condition does not use the button, and there is no stated cabinet check for the flowers.
- Source: `game/data/characters/zhou.json:14` `{ "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },` and `game/data/characters/zhou.json:19` `"gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },`. `game/data/characters/granny.json:18` `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`. Both items are assigned to the table in `game/data/items.json:5-6`. `game/data/settings.json:6` `"table": { "hit": "pixel", "sweepAtClose": true },` and `game/README.md:22` ``- 收摊时，桌上还没收的东西会被扫掉（`table.sweepAtClose`）。``. The static image report has 60 opaque pixels for the button and 623 for the flowers (`review_out/20261119_181306/_image_hits.md:25`, `review_out/20261119_181306/_image_hits.md:29`).
- Cross-check: The whole-cell rule is confined to shelf items. The design and data both use pixel hits for table gifts. Both gifts specify day seven. Searches for both item IDs and the sweep condition found no post-close recovery, pickup fallback or replacement day specified. The design leaves no later day in the run.
- Suggestion: Give table gifts a forgiving click target. At the final close, prompt the player to collect gifts still on the table or transfer them to the cabinet.
- Verification scope: The loss follows the stated design. A build would be needed to check hit-area scaling, exact sweep order and whether there is an extra UI warning.

### M1 The hints tooltip gives away Old Zhou's day-six reveal

- Severity: Medium
- Confidence: [Possible]
- Character: Old Zhou
- How you get there: On a new run, before day six, open the “Show hints” option and reveal its tooltip if it is accessible.
- What the player sees: “Old Zhou is a deserter, so his icon is grey.” (`game/text/en.csv:4`, `option_hints_tip`.) The Chinese tooltip gives the same information.
- Why it is wrong: The story and project invariant reserve the reveal for day six. The settings text contains the answer, independently of the day-six dialogue.
- Source: `game/text/en.csv:4` `option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey.`. `game/text/zh.csv:4` `option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。`. `game/README.md:29` `- 设定：老周的来历在第 6 天以前不能让玩家知道。`.
- Cross-check: The day-six visit has a dedicated dialogue key in `game/data/characters/zhou.json:10`, but nothing in the available settings or localization data limits the hints tooltip to that day. Its actual binding and unlock timing are missing.
- Suggestion: Describe the hint icons without naming what the colours reveal.
- How to reproduce: Start a fresh game in each language, check the hints tooltip in the start menu and on days one through five, then compare it with the day-six reveal. Confirm whether the tooltip can show early.

## Wanted but missing

No separate missing option was filed in this softlock review. The gift collection safeguards belong to S1.

## Needs your decision

### D1 Two consecutive refusals end Granny's visits and close access to her flowers

- Confidence: [Design]
- Character: Granny
- How you get there: Refuse on days one and three. The first refusal warns the player. The second reaches the consecutive-refusal threshold before the next scheduled visit.
- What the player sees: Granny stops visiting and the two-discount route to her day-seven gift closes for that playthrough. The ordinary ending remains available.
- Source: `game/data/characters/granny.json:17` `"leaveForever": { "refusedInARow": 2 },`. `game/text/en.csv:14` `granny_warn,You won't sell to me today... Do it again and I won't come back.`. `game/README.md:27` explicitly describes the warning and permanent departure.
- Options:
  1. Keep the rule and confirm that the warning appears on the first refusal. The early decision keeps its stated consequence.
  2. Explain the permanent departure at the second refusal before committing it. A player who missed the earlier warning can still back out.

## Checked and fine

- Granny's “Charge less” sale fits the affordability invariant. The configured price is 12, the discount is 3 and the budget is 10. The common “Refuse” action is a second exit in the design. `project.json:132`, `game/data/settings.json:3-4`, `game/data/characters/granny.json:6`, `game/README.md:10`.
- The small coarse-tea image uses a full-cell shelf target. Selecting the small hints icon is unnecessary, because the design marks it as display only. `game/data/items.json:4`, `game/data/settings.json:5`, `game/data/settings.json:7`, `game/README.md:20`, `game/README.md:23`.
- The day-six choices write both named flags that later events read. Reporting with flowers still meets the stated ordinary ending rule, while the good ending is available through a gift with no report. `game/data/characters/zhou.json:14-20`, `game/data/characters/granny.json:13`, `game/README.md:34-35`.
- The taken-event recap and Granny's cold line refer to the same event after reporting. No source establishes that Granny could not know about the event. `project.json:134`, `game/data/characters/granny.json:13`, `game/data/characters/zhou.json:16`, `game/data/characters/zhou.json:20`, `game/text/en.csv:15`, `game/text/en.csv:31`.
- An English reply is missing for Old Zhou's refusal. The choice is defined and the design says he leaves. The missing reply alone does not establish that the exit stalls. `game/data/characters/zhou.json:15`, `game/text/zh.csv:25`, `game/text/en.csv:18-31`, `game/README.md:30`.

## Not covered this time

- The project has no runnable game (`game/README.md:3`). Runtime visit timeouts, insufficient-funds exits, queue release, absent inventory or storage capacity, single-action gating, save/reload and dialogue fallback cannot be observed here.
- A playable build could cover: refuse before and after a failed sale, inspect the last-day gift and close with and without successful pickup, then compare the ending. Report after two Granny discounts and compare line selection and gift behavior against report with zero discounts. A second paired run with the second discount made on day seven would distinguish whether the gift check occurs before or after service.
- The guide claims guests leave if they wait too long and lists three seats (`game/text/en.csv:5`). The data sets two seats (`game/data/settings.json:2`). With the two documented guest schedules on different days and no wait threshold, the written sources do not establish a capacity-induced softlock.

## Index

| ID | Severity | Confidence | File:line | Quote |
|---|---|---|---|---|
| S1 | Severe | [Confirmed] | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" }, |
| S1 | Severe | [Confirmed] | game/data/characters/zhou.json:19 | "gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" }, |
| S1 | Severe | [Confirmed] | game/data/characters/granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" } |
| S1 | Severe | [Confirmed] | game/data/items.json:5 | "dried_flowers": { "image": "images\\items\\dried_flowers.png", "where": "table" }, |
| S1 | Severe | [Confirmed] | game/data/items.json:6 | "old_button": { "image": "images\\items\\old_button.png", "where": "table" } |
| S1 | Severe | [Confirmed] | game/data/settings.json:6 | "table": { "hit": "pixel", "sweepAtClose": true }, |
| S1 | Severe | [Confirmed] | game/README.md:14 | 一局 7 天。第 7 天收摊以后出结局。 |
| S1 | Severe | [Confirmed] | game/README.md:21 | - **桌上**：客人送的东西留在桌上。玩家点它，收进柜子。点在图的透明处不算点中（按图的形状判定，`table.hit` = `pixel`）。 |
| S1 | Severe | [Confirmed] | game/README.md:22 | - 收摊时，桌上还没收的东西会被扫掉（`table.sweepAtClose`）。 |
| M1 | Medium | [Possible] | game/text/en.csv:4 | option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey. |
| M1 | Medium | [Possible] | game/text/zh.csv:4 | option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。 |
| M1 | Medium | [Possible] | game/README.md:29 | - 设定：老周的来历在第 6 天以前不能让玩家知道。 |
| M1 | Medium | [Possible] | game/data/characters/zhou.json:10 | "day6": [ "zhou_ask_1" ] |
| M1 | Medium | [Possible] | project.json:133 | "第 6 天以前，玩家看得到的文字里不出现老周的来历。", |
| D1 | Decision | [Design] | game/data/characters/granny.json:17 | "leaveForever": { "refusedInARow": 2 }, |
| D1 | Decision | [Design] | game/text/en.csv:14 | granny_warn,You won't sell to me today... Do it again and I won't come back. |
| D1 | Decision | [Design] | game/README.md:27 | - **阿婆**（`granny`）：每两天来一次，要一壶茉莉。钱不多。连着两次被"不卖"，她就不再来（第一次被拒绝时她会说一句警告）。少收过她两次以上，第 7 天她会送一包自己晒的花。 |
| D1 | Decision | [Design] | game/README.md:35 | - 普通结局：别的情况。 |

