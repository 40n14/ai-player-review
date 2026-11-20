# Player review · Q, Missing options

- Scope: All seven days, both guest routes, stall interactions, options, and records.
- Review method: Missing options.
- Persona: 1 Kindhearted, 2 Shrewd merchant, 21 Reporter, 28 Contrarian.
- Project map: `_map/`.
- Static checks: `_summary.md`, `_text_checks.md`, and `_image_hits.md`.

## Conclusion

The merchant cannot make a sale at Granny’s exact budget. Reporting Old Zhou has a next-morning response that leaves the person unnamed, and accepting shelter gives the contrarian a later gift with no documented way to return it. The ending rules also give Sam one decision about how clearly to signal the cost of reporting. This group found 0 severe, 0 medium, 0 minor, 1 needs a decision, and 3 wanted but missing.

## Player feedback

### 1 Kindhearted
- Done right: “I could charge Granny less. The next time she talked about the lower price, she remembered what I’d done.” `game/data/characters/granny.json:10` `"afterDiscount": [ "granny_thanks" ],`; `game/text/en.csv:13` `granny_thanks,You charged me less last time. I remember.`
- Done right: “I could let the guest stay overnight, and he left an old button the next day.” `game/text/en.csv:29` `btn_shelter,Let him stay the night`; `game/data/characters/zhou.json:19` `"gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },`

### 2 Shrewd merchant
- Wants: “I could sell Granny the pot for 9 or refuse. I wanted to ask her for 10 and still make the sale.” (W1)
- Done right: “Granny warned me what would happen if I refused again.” `game/text/en.csv:14` `granny_warn,You won't sell to me today... Do it again and I won't come back.`

### 21 Reporter
- Wants: “I reported the guest. The morning recap said someone was taken. I wanted it to tell me whether that was him.” (W2)
- Done right: “The recap changed after I reported him.” `game/text/en.csv:31` `summary_taken,Someone was taken away last night.`; `game/data/characters/zhou.json:20` `"summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }`

### 28 Contrarian
- Wants: “On the run where I let him stay, I could keep the button or let closing sweep it away. I wanted to give it back.” (W3)
- Done right: “Granny told me she wouldn’t come back if I refused again, and after another refusal she stopped visiting.” `game/text/en.csv:14` `granny_warn,You won't sell to me today... Do it again and I won't come back.`; `game/data/characters/granny.json:17` `"leaveForever": { "refusedInARow": 2 },`

## Gaps at a glance

| ID | Gap | Personas | Without it |
|---|---|---:|---|
| W1 | Name a price Granny can pay | 1 | Accept a lower price or turn away the sale. Repeated refusals end the route. |
| W2 | See whom a report affected | 1 | Infer the guest’s fate from an unnamed recap. |
| W3 | Give back an unwanted gift | 1 | Keep the button or leave it to the closing sweep. |

## Issues at a glance

No issue entries in this group. The focus was choices and responses players might want.

## Wanted but missing

### W1 The merchant wants to sell Granny jasmine for 10

- Who wants it: 2 Shrewd merchant. The persona wants to make a sale without leaving available money on the table. The project overlay says to refuse when Granny cannot pay full price.
- Where it happens: Granny’s jasmine order on day one and any later order she still attends.
- Options today: `game/text/en.csv:26` `btn_sell,Sell at price`; `game/text/en.csv:27` `btn_discount,Charge less`; `game/text/en.csv:28` `btn_refuse,Refuse`. Jasmine costs 12, the concession is 3, and Granny has 10. `game/data/settings.json:3` `"prices": { "jasmine": 12, "coarse": 4 },`; `game/data/settings.json:4` `"discount": 3,`; `game/data/characters/granny.json:6` `"budget": 10,`.
- Without it: The attainable documented sale price is 9. If the merchant refuses the order twice in a row, Granny stops visiting. `game/data/characters/granny.json:17` `"leaveForever": { "refusedInARow": 2 },`.
- Similar options elsewhere: The coarse-tea order uses the same generic options. Old Zhou’s budget already matches its full price. `game/data/characters/zhou.json:6` `"budget": 4,`.
- Confidence: [Definitely missing] from the documented sale choices. Read both button lists and searched all game design, data, and strings for other buttons, adjustable prices, bargaining, and credit. The guide and data describe a fixed discount.
- How to add it: Add an offer at the guest’s budget to underfunded orders. Specify whether a partial discount counts toward Granny’s gifts.

### W2 The reporter wants the recap to identify the result of the report

- Who wants it: 21 Reporter. The persona checks the next recap to see the effect of reporting.
- Where it happens: Day six after the shelter request and the following morning.
- Options today: `game/text/en.csv:29` `btn_shelter,Let him stay the night`; `game/text/en.csv:28` `btn_refuse,Refuse`; `game/text/en.csv:30` `btn_report,Report him`. The report choice has no reply field. `game/data/characters/zhou.json:16` `{ "button": "btn_report", "sets": "flag:zhou_taken" }`.
- Without it: The supplied next-morning recap says only that someone was taken. It leaves the guest’s identity and the link to the report implicit. `game/data/characters/zhou.json:20` `"summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" }`; `game/text/en.csv:31` `summary_taken,Someone was taken away last night.`
- Similar options elsewhere: Shelter and refusal have direct reply fields. `game/data/characters/zhou.json:14` `{ "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" },`; `game/data/characters/zhou.json:15` `{ "button": "btn_refuse", "reply": "zhou_refused" },`.
- Confidence: [Possibly missing]. A search of both guest definitions, both text tables and the design for reporting, receipts, confirmation, and recap text found no explicit confirmation. A generic runtime receipt cannot be checked.
- How to reproduce: Report the guest on day six and watch the same-day UI and next morning’s recap for a specific confirmation.
- How to add it: Add a short confirmation following the existing report action or refer to the shelter request in the day-seven recap.

### W3 The contrarian wants to return the old button after accepting shelter

- Who wants it: 28 Contrarian. On the alternate run where this player accepts requests, they still prefer to decline optional rewards.
- Where it happens: Day seven after sheltering Old Zhou on day six.
- Options today: Pick up the gift into the cabinet or leave it on the table. `game/README.md:21` — - **桌上**：客人送的东西留在桌上。玩家点它，收进柜子。点在图的透明处不算点中（按图的形状判定，`table.hit` = `pixel`）。
- Without it: The button is swept at close when left uncollected. Neither described action returns the gift to Old Zhou. `game/data/characters/zhou.json:19` `"gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" },`; `game/data/settings.json:6` `"table": { "hit": "pixel", "sweepAtClose": true },`.
- Similar options elsewhere: The day-six request has a direct refusal, `game/text/en.csv:28` `btn_refuse,Refuse`. The other day-seven gift also uses the table rule. `game/data/items.json:5` `"dried_flowers": { "image": "images\\items\\dried_flowers.png", "where": "table" },`.
- Confidence: [Definitely missing] from the documented gift interactions. Searched item data, both character files, both text tables, and design for gift actions, returning or refusing a gift, and cleanup.
- How to add it: Offer a return action that flags the gift as declined before the closing sweep. If the giver is already gone, add a way to leave it for him.

## Needs your decision

### D1 Decide what to tell players about the ending cost of reporting

- Confidence: [Design].
- Source: `game/README.md:34` `- 好结局：阿婆送了花，而且老周没有被带走。`; `game/README.md:35` `- 普通结局：别的情况。`; `game/data/characters/zhou.json:16` `{ "button": "btn_report", "sets": "flag:zhou_taken" }`.
- What the player sees: When the guest requests shelter, the report button says “Report him.” If Granny gives flowers on a mixed route where the player reports him, the stated ending rule still yields the ordinary ending. `game/text/en.csv:30` `btn_report,Report him`; `game/data/characters/granny.json:18` `"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }`.
- Cross-check: The flower rule and the reported state are independent. No documented exception in the ending rule preserves the good ending after both occur.
- Options: (1) Signal during the day-six choice that reporting has lasting consequences for the stall’s story. (2) Keep the surprise and explain the deciding events in the ending. (3) Add a distinct ending for the combination of the gift and the report.

## Checked and fine

- The fixed discount is sufficient for Granny at the documented prices. `game/data/settings.json:3` `"prices": { "jasmine": 12, "coarse": 4 },`; `game/data/settings.json:4` `"discount": 3,`; `game/data/characters/granny.json:6` `"budget": 10,`.
- A direct refusal already exists for both guest orders and the lodging request. Granny has a warning and a stopping threshold. `game/text/en.csv:28` `btn_refuse,Refuse`; `game/data/characters/zhou.json:15` `{ "button": "btn_refuse", "reply": "zhou_refused" },`; `game/text/en.csv:14` `granny_warn,You won't sell to me today... Do it again and I won't come back.`
- A pre-reveal reporting choice would conflict with the stated story timing. The no-follow-up refusal ending is also explicit. `game/README.md:29` `- 设定：老周的来历在第 6 天以前不能让玩家知道。`; `game/README.md:30` `- 答应：第 7 天他留下一枚旧铜扣。拒绝：他走了，没有后话。报官：第 7 天早上的小结写"昨夜有人被带走"。`
- Ignoring a gift already gives the contrarian a passive discard route. The hint icon is designed to be informational. `game/data/settings.json:6` `"table": { "hit": "pixel", "sweepAtClose": true },`; `game/data/settings.json:7` `"hints": { "icon": "images\\ui\\hint_icon.png", "clickable": false }`.

## Not covered this time

- The available materials contain no executable. The exact outcome of clicking full price for a guest who cannot pay, gift return affordances from generic UI, timing of runtime notices, and save, undo, pause, or accessibility controls require a runnable implementation. The settings pass checked the supplied Show hints copy, the noninteractive icon, two language resources, the recap, and the ledger. No persona in this group established a required accessibility setting.
- Timing test for W1 and W3 once playable: Check all day-one sale controls with Granny’s budget, including any adjustable amount outside the three buttons. Shelter Old Zhou, then check whether any context menu or table control can decline or return the day-seven gift before closing.

## Index

| ID | Severity | Confidence | File:line | Quote |
|---|---|---|---|---|
| W1 | Wanted | Definitely missing | game/text/en.csv:26 | btn_sell,Sell at price |
| W1 | Wanted | Definitely missing | game/text/en.csv:27 | btn_discount,Charge less |
| W1 | Wanted | Definitely missing | game/text/en.csv:28 | btn_refuse,Refuse |
| W1 | Wanted | Definitely missing | game/data/settings.json:4 | "discount": 3, |
| W1 | Wanted | Definitely missing | game/data/characters/granny.json:6 | "budget": 10, |
| W2 | Wanted | Possibly missing | game/text/en.csv:28 | btn_refuse,Refuse |
| W2 | Wanted | Possibly missing | game/text/en.csv:29 | btn_shelter,Let him stay the night |
| W2 | Wanted | Possibly missing | game/text/en.csv:30 | btn_report,Report him |
| W2 | Wanted | Possibly missing | game/data/characters/zhou.json:16 | { "button": "btn_report", "sets": "flag:zhou_taken" } |
| W2 | Wanted | Possibly missing | game/text/en.csv:31 | summary_taken,Someone was taken away last night. |
| W3 | Wanted | Definitely missing | game/README.md:21 | - **桌上**：客人送的东西留在桌上。玩家点它，收进柜子。点在图的透明处不算点中（按图的形状判定，`table.hit` = `pixel`）。 |
| W3 | Wanted | Definitely missing | game/data/settings.json:6 | "table": { "hit": "pixel", "sweepAtClose": true }, |
| D1 | Decision | Design | game/README.md:34 | - 好结局：阿婆送了花，而且老周没有被带走。 |
| D1 | Decision | Design | game/README.md:35 | - 普通结局：别的情况。 |
| D1 | Decision | Design | game/data/characters/zhou.json:16 | { "button": "btn_report", "sets": "flag:zhou_taken" } |
