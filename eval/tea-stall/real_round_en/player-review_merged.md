# Player review

## Conclusion

A missed click can leave an earned gift on the table until the final sweep. The design makes Old Zhou's one-time button particularly easy to miss, with a hit area of 60 pixels out of 1,024. Readers and traders can encounter a three-seat guide for a two-seat stall, and the authored English dialogue has an untranslated line, a draft reply, and an absent reply. The hint copy contains the day-six reveal. Its availability on earlier days needs an in-game check. The round retained 1 Severe, 5 Medium, 3 Minor, 2 Needs your decision, and 4 Wanted but missing items.

- Scope: The entire seven-day stall loop, both guest routes, shelter/refuse/report, both endings, both table gifts, English and Chinese text, and the supplied settings. This is the first round.
- Review method and inputs: A followed the kindhearted player (1), trader (2), and close reader (17) in `player-review_A.md`. B followed the reporter (21), repeated reloader (14), and rapid clicker (18) in `player-review_B.md`. Q checked missing options for the kindhearted player, trader, reporter, and contrarian (28) in `player-review_Q.md`. S checked progression with the careless player (4) in `player-review_S.md`. M checked prices and repeat gains with the trader in `player-review_M.md`.
- Project map and static checks: `_map/_map.md`, `_summary.md`, `_text_checks.md`, `_image_hits.md`, and `_citations.md`. All five named reports were present. Their 125 index quotations matched, and 15 consolidated claims were independently checked against the original sources. The game is a design sample with no executable (`game/README.md:3`).
- Accounting: 28 group entries = 15 retained + 13 duplicates + 0 dismissed group entries + 0 previously reported + 0 resolved. Of 16 group issue entries (S/M/L), 9 remain and 7 were duplicates. Of 5 design entries, 2 remain and 3 were duplicates. Of 7 missing-option entries, 4 remain and 3 were duplicates. Source leads screened out before publication are listed below.

## Player feedback summary

| Player type (persona) | What they would say | Related IDs | Groups that played this persona |
|---|---|---|---|
| 1 Kindhearted player | “I helped Granny twice and her last line came up in Chinese. I'd like to give her the tea for free. I'd also want the button I earned to make it safely into the cabinet.” | M5, W3, S1 | A, Q |
| 2 Trader | “I'd sell Granny the pot for 10 if I could. I passed on two sales at the posted price and she stopped coming. I'd also expect three seats from what the guide says.” | W1, D1, M2 | A, Q, M |
| 17 Close reader | “Why did she say ‘the usual’ at the new stall? In Chinese, turning down a place to hide reads as refusing a sale. If hints help opens early, it gives away the guest's story (to confirm).” | L1, L2, M1 | A |
| 21 Reporter | “The recap said someone was taken. I wanted it to confirm who. I could still get Granny's flowers after reporting and the ending would be ordinary.” | W2, D2 | B, Q |
| 14 Repeated reloader | “I'd replay from the day-six choice to check each reply and the ending, including whether the gift returns after a reload.” Save support is unspecified (`game/README.md:3`). | M3, M4, D2, S1 | B |
| 18 Rapid clicker | “I tapped near the edge of the button and it stayed on the table. When I closed up, it was gone.” | S1 | B |
| 28 Contrarian | “After I let him stay, I could keep the button or leave it to the sweep. I wanted to give it back.” | W4 | Q |
| 4 Careless player | “I missed the button and closed without it. I also turned Granny away twice and couldn't make it up to her on a later day.” | S1, D1 | S |

- **Shared across personas** The kindhearted player, rapid clicker, and careless player have a stake in reliable gift pickup (S1). The close reader, reporter, and careless player could encounter the tooltip spoiler (M1, to confirm). The trader, careless player, and contrarian encounter the two-refusal consequence (D1).
- **Serious for one persona** No severe item was unique to one persona.
- **Done right** The kindhearted player gets an affordable discount (W1, `game/data/settings.json:3–4`, `game/data/characters/granny.json:6`). The trader, contrarian, and careless player have a warning before Granny leaves (D1, `game/text/en.csv:14`). The reporter has a branch-specific next-morning recap (W2, `game/data/characters/zhou.json:20`, `game/text/en.csv:31`). Rapid clickers can select shelf tea by the whole cell (`game/README.md:20`, `game/data/settings.json:5`).

## Issues at a glance

| ID | Severity | Confidence | What the player encounters | Reported by |
|---|---|---|---|---|
| S1 | Severe | [Confirmed] | An uncollected gift can be lost at the final close | A-S1, B-S1, S-S1 |
| M1 | Medium | [Possible] | Hints help may reveal Old Zhou's background early | A-M2, B-M1, S-M1 |
| M2 | Medium | [Confirmed] | The guide advertises three seats for a two-seat stall | A-M3, M-M1 |
| M3 | Medium | [Confirmed] | Old Zhou's shelter refusal has no English reply | A-M4, B-M2 |
| M4 | Medium | [Confirmed] | Old Zhou's shelter reply contains a draft marker | A-L2, B-M3 |
| M5 | Medium | [Confirmed] | Granny's English flower line is still in Chinese | A-M1 |
| L1 | Minor | [Confirmed] | Granny's first greeting sounds like a repeat visit | A-L1 |
| L2 | Minor | [Confirmed] | The Chinese shelter refusal reads as refusing a sale | A-L3 |
| L3 | Minor | [Possible] | The English thank-you may leave out the discount amount | M-L1 |

## Issues

### S1 An uncollected gift can be lost at the final close

- Severity: Severe
- Confidence: [Confirmed]
- Reported by: A-S1, B-S1, S-S1
- Character: Old Zhou, Granny, and the stall
- Persona: Kindhearted player (1), rapid clicker (18), careless player (4)
- How you get there: Discount Granny on days one and three and shelter Zhou on day six. On day seven click a transparent part of a gift, leave it on the table, and close.
- What the player sees: The gift stays on the table after the missed click and is absent from the cabinet at the final close. The copper button has 60 nontransparent pixels of 1,024 (5.9%). The flowers have 624 of 1,024 (60.9%).
- Why it is wrong: Pixel-based pickup followed by the final sweep can remove an earned, one-time reward. The button's small hit target makes it particularly easy to miss.
- Source: `game/README.md:14`, `game/README.md:21`, `game/README.md:22`, `game/data/settings.json:6`, `game/data/items.json:5`, `game/data/items.json:6`, `game/data/characters/zhou.json:19`, `game/data/characters/granny.json:18`, `review_out/20261119_181306/_image_hits.md:25`, `review_out/20261119_181306/_image_hits.md:29`
- Cross-check: Both gifts use the table hit and sweep rules. Full-cell pickup applies only to shelves. The rules still advance through day-seven close to the ending.
- Verification: Holds for the documented design and both PNGs. The independent count matches the image table. The supplied material has no post-close recovery rule. Live hit drawing, pickup feedback, and save or reload behavior remain to be checked.
- Suggestion: Use a more forgiving table target and warn before sweeping uncollected gifts. Another option is to transfer them to the cabinet at the final close.
- How to reproduce: Earn both gifts, click transparent and opaque pixels, and compare cabinet contents and ending on paired closings. If saving is supported, reload before pickup and after closing.

### M1 Hints help may reveal Old Zhou's background early

- Severity: Medium
- Confidence: [Possible]
- Reported by: A-M2, B-M1, S-M1
- Character: Old Zhou and Settings
- Persona: Close reader (17), reporter (21), careless player (4)
- How you get there: Start a fresh run and expose Show hints help before day six if available.
- What the player sees: The authored `option_hints_tip` calls him a deserter in both languages.
- Why it is wrong: The help can give away the disclosure that the story reserves for his day-six request.
- Source: `game/text/en.csv:4`, `game/text/en.csv:22`, `game/text/zh.csv:4`, `game/README.md:23`, `game/README.md:29`, `game/data/characters/zhou.json:10`, `game/data/settings.json:7`
- Cross-check: The hints flag marks the icon over a guest as noninteractive. It says nothing about menu access, tooltip timing or default state.
- Verification: Inconclusive for early access. Both text values disclose the identity. Day-six dialogue and the written invariant set the intended timing.
- Suggestion: Describe what the hints setting does without identifying a guest.
- How to reproduce: Inspect launch-menu and in-run help before day six in English and Chinese, with default and toggled hints. Reload if supported and compare with the day-six dialogue.

### M2 The guide advertises three seats for a two-seat stall

- Severity: Medium
- Confidence: [Confirmed]
- Reported by: A-M3, M-M1
- Character: Stall
- Persona: Trader (2), close reader (17)
- How you get there: Read guide page one and compare it with the authored stall capacity.
- What the player sees: Both guide strings say three guests can be served at once.
- Why it is wrong: Players plan from a capacity the stall settings do not provide.
- Source: `game/text/en.csv:5`, `game/text/zh.csv:5`, `game/data/settings.json:2`, `game/README.md:8`
- Cross-check: The design and configuration agree on two seats. The named guests visit on alternating days, so a live queue of three is unproved.
- Verification: Holds. Both localized guide rows disagree with the single configured capacity. No override was found.
- Suggestion: Say two in both guide rows or generate the value from settings. Configure a third seat if the extra capacity is intentional.
- How to reproduce: Check the first guide page in both locales and the number of usable seats in a build.

### M3 Old Zhou's shelter refusal has no English reply

- Severity: Medium
- Confidence: [Confirmed]
- Reported by: A-M4, B-M2
- Character: Old Zhou
- Persona: Trader (2), reporter (21) in the branch comparison
- How you get there: On day six, choose Refuse in English after Zhou asks for shelter.
- What the player sees: The choice calls `zhou_refused`. The English table supplies no row for it.
- Why it is wrong: The authored English branch has no localized acknowledgement for the player's answer.
- Source: `game/data/characters/zhou.json:15`, `game/text/zh.csv:25`, `game/text/en.csv:28`, `game/README.md:30`
- Cross-check: The Chinese table has that key. Shelter has its own reply. Refusal sets neither the shelter nor the report flag, and the design says Zhou leaves.
- Verification: Holds for the absent row. The English fallback and actual transition have no supplied implementation.
- Suggestion: Supply the localized refusal reply and check that Zhou can leave after it.
- How to reproduce: Select Refuse in English and Chinese. Capture the reply, any missing-string fallback, and progress through the end of the visit.

### M4 Old Zhou's shelter reply contains a draft marker

- Severity: Medium
- Confidence: [Confirmed]
- Reported by: A-L2, B-M3
- Character: Old Zhou
- Persona: Kindhearted player (1), close reader (17), reporter (21) in the branch comparison
- How you get there: Choose Let him stay the night on day six and read the reply.
- What the player sees: The English `zhou_stay_thanks` value is “(placeholder) Thanks.” The Chinese value also includes a marker.
- Why it is wrong: A visible author marker interrupts the shelter scene.
- Source: `game/data/characters/zhou.json:14`, `game/data/characters/zhou.json:19`, `game/text/en.csv:23`, `game/text/zh.csv:23`, `game/text/zh.csv:24`
- Cross-check: The shelter choice names this reply directly. No alternative reply is authored. The later gift uses a separate flag check.
- Verification: Holds. The draft marker is literal text in both configured reply values.
- Suggestion: Finalize both reply values and retain the shelter flag.
- How to reproduce: Shelter Zhou in each locale, read his reply, then check that the gift appears on day seven.

### M5 Granny's English flower line is still in Chinese

- Severity: Medium
- Confidence: [Confirmed]
- Reported by: A-M1
- Character: Granny
- Persona: Kindhearted player (1)
- How you get there: Use English, discount Granny on days one and three, and shelter Zhou on day six. Read her day-seven flower dialogue.
- What the player sees: `granny_last_warm` says “这是我自己晒的花，你拿去泡。” in both locales.
- Why it is wrong: English readers may miss what Granny brought and how to use it.
- Source: `game/data/characters/granny.json:13`, `game/data/characters/granny.json:14`, `game/data/characters/granny.json:18`, `game/data/characters/zhou.json:14`, `game/data/characters/zhou.json:16`, `game/text/en.csv:16`, `game/text/zh.csv:16`
- Cross-check: The second discount reaches the warm and gift gates, and sheltering avoids the taken flag and cold dialogue predicate.
- Verification: Holds. English and Chinese values match exactly. No English override was found.
- Suggestion: Translate the English row and retain the information about what she dried and how to use it.
- How to reproduce: Repeat the warm route in English and compare the line and gift with the Chinese run.

### L1 Granny's first greeting sounds like a repeat visit

- Severity: Minor
- Confidence: [Confirmed]
- Reported by: A-L1
- Character: Granny
- Persona: Kindhearted player (1), close reader (17)
- How you get there: Serve Granny on day one and read her two first-visit lines.
- What the player sees: She says “The usual. A pot of jasmine.” and then “This stall is new, isn't it?”
- Why it is wrong: The juxtaposition can make a new player wonder whether a prior visit was skipped.
- Source: `game/data/characters/granny.json:4`, `game/data/characters/granny.json:8`, `game/data/characters/granny.json:9`, `game/text/en.csv:10`, `game/text/en.csv:11`
- Cross-check: Local familiarity or a joke could explain the wording. Later visits have a separate line array.
- Verification: Holds for the first-visit wording. The source leaves her intent open.
- Suggestion: Make the first order more direct, or make her intended joke clear.
- How to reproduce: Read both lines on a fresh run and compare with her repeat greeting.

### L2 The Chinese shelter refusal reads as refusing a sale

- Severity: Minor
- Confidence: [Confirmed]
- Reported by: A-L3
- Character: Old Zhou
- Persona: Close reader (17)
- How you get there: Use Chinese and inspect the three buttons after Zhou asks to hide on day six.
- What the player sees: The shared `btn_refuse` is labeled “不卖” next to the shelter and report choices.
- Why it is wrong: The label describes declining a sale while the player is answering a request for shelter.
- Source: `game/data/characters/zhou.json:15`, `game/text/zh.csv:22`, `game/text/zh.csv:30`, `game/text/en.csv:28`, `game/README.md:10`
- Cross-check: The same label fits the ordinary sale context. English “Refuse” is usable in both contexts.
- Verification: Holds. The Chinese day-six button reuses the sale label with no authored scene override.
- Suggestion: Supply a shelter-specific Chinese label.
- How to reproduce: Read the sale menu and shelter menu in Chinese and verify that refusing shelter uses the intended text and reply.

### L3 The English thank-you may leave out the discount amount

- Severity: Minor
- Confidence: [Possible]
- Reported by: M-L1
- Character: Granny
- Persona: Trader (2)
- How you get there: Discount Granny on day one, then compare her next greeting and thank-you across English and Chinese.
- What the player sees: The configured English `granny_thanks` says “You charged me less last time. I remember.” The Chinese value includes `{0}` for the amount.
- Why it is wrong: If that reply appears, English readers receive less precise feedback about what Granny remembers.
- Source: `game/data/characters/granny.json:9`, `game/data/characters/granny.json:10`, `game/text/en.csv:13`, `game/text/zh.csv:13`
- Cross-check: Both values share the same key. JSON has repeat and after-discount arrays, but provides no priority order or formatting implementation.
- Verification: Inconclusive for visible behavior. The authored amount difference is certain. No formatting exception is established.
- Suggestion: Include the amount in both values if the thank-you is meant to show it.
- How to reproduce: Compare day-three replies after a day-one discount in English and Chinese. Record the chosen line, formatting, and persistence after reload if supported.

## Wanted but missing

| ID | Missing option | Player type | What happens today |
|---|---|---|---|
| W1 | Charge Granny 10 | Trader (2) | The merchant can charge 9 or turn Granny away. |
| W2 | Get explicit reporting feedback | Reporter (21) | An anonymous recap leaves the guest and the link to the report implicit. |
| W3 | Give Granny her tea | Kindhearted player (1) | The cheapest documented offer still charges 9. |
| W4 | Return the unwanted button | Contrarian (28) | The player can collect the button or let closing remove it. |

### W1 Charge Granny exactly 10

- Severity: Wanted
- Confidence: [Definitely missing]
- Reported by: A-W2, Q-W1, M-W1
- Who wants it: Trader (2), who wants the highest price Granny can pay.
- Where it happens: Granny's order screen before making a sale.
- Options today: Sell at price charges 12, Charge less is configured to charge 9, and Refuse ends the sale. Granny has 10.
- Without it: The trader accepts a larger discount than needed or passes on the sale.
- Source: `game/README.md:10`, `game/text/en.csv:26`, `game/text/en.csv:27`, `game/text/en.csv:28`, `game/data/settings.json:3`, `game/data/settings.json:4`, `game/data/characters/granny.json:6`
- Verification: Holds. The three documented choices provide no preset or editable quote at 10. No later price-adjustment entrance was found.
- How to add it: Offer a two-coin reduction or an adjustable price that allows 10, and specify whether it increments the discount counter.

### W2 Give explicit feedback on the report

- Severity: Wanted
- Confidence: [Definitely missing]
- Reported by: B-W1, Q-W2
- Who wants it: Reporter (21), who wants to see the result of the report.
- Where it happens: Immediately after reporting and in the day-seven recap.
- Options today: The reporting choice sets the flag with no reply field. The recap says someone was taken. Granny's cold line also leaves the person unnamed.
- Without it: The player can infer the outcome. The authored feedback leaves the link to Zhou or to the report implicit.
- Source: `game/data/characters/zhou.json:16`, `game/data/characters/zhou.json:20`, `game/text/en.csv:15`, `game/text/en.csv:30`, `game/text/en.csv:31`, `game/data/characters/granny.json:13`
- Verification: Holds for the authored content. No direct confirmation naming Zhou or the action was found in either locale. Actual generic feedback in a playable UI remains unverified.
- How to add it: Add an immediate acknowledgement or let the next-morning recap explicitly connect the report and its outcome.

### W3 Give Granny the tea for free

- Severity: Wanted
- Confidence: [Definitely missing]
- Reported by: A-W1
- Who wants it: Kindhearted player (1), who wants to help without charging.
- Where it happens: Granny's order screen before choosing how to pay.
- Options today: The menu offers full price, a fixed three-coin discount, or refusal. Gifts shown elsewhere are guest-to-player.
- Without it: The cheapest documented jasmine sale still charges 9.
- Source: `game/README.md:10`, `game/text/en.csv:26`, `game/text/en.csv:27`, `game/text/en.csv:28`, `game/data/settings.json:3`, `game/data/settings.json:4`, `game/data/characters/granny.json:18`
- Verification: Holds. No zero-price tea gift action appeared in the supplied menus, strings or data.
- How to add it: Add a gift action and define whether comping the price counts toward Granny's gratitude.

### W4 Return the unwanted button to Old Zhou

- Severity: Wanted
- Confidence: [Definitely missing]
- Reported by: Q-W3
- Who wants it: Contrarian (28), who may offer shelter while wanting to refuse a later reward.
- Where it happens: Day seven, after accepting the shelter request on day six.
- Options today: Table pickup stores the gift in the cabinet, or the closing sweep removes the uncollected gift.
- Without it: Neither action returns the button or lets Old Zhou know the gift was declined.
- Source: `game/data/characters/zhou.json:4`, `game/data/characters/zhou.json:14`, `game/data/characters/zhou.json:19`, `game/data/items.json:6`, `game/data/settings.json:6`, `game/README.md:21`, `game/README.md:22`
- Verification: Holds. No return action, cabinet return, or day-seven Zhou visit is documented.
- How to add it: Offer a return or decline action. If he has already left, offer a way to set the gift aside for him.

## Needs your decision

### D1 Decide how two refusals should affect Granny's route

- Severity: Decision
- Confidence: [Design]
- Reported by: A-D1, S-D1, M-D1
- How you get there: Refuse Granny's orders on days one and three. Open the stall on day five and continue to the ending.
- What the player sees: The first refusal warns that she will not come back. After two consecutive refusals her visits end. On this path no discounts were given, so the flower gate is unreached.
- Source: `game/data/characters/granny.json:4`, `game/data/characters/granny.json:6`, `game/data/characters/granny.json:11`, `game/data/characters/granny.json:17`, `game/data/characters/granny.json:18`, `game/text/en.csv:14`, `game/README.md:14`, `game/README.md:27`, `game/README.md:34`, `game/README.md:35`
- Verification: Holds. The warning and consecutive-refusal counter implement the design's trade-off. The ordinary ending remains available. An unsuccessful payment has unspecified effects.
- Options: 1. Keep deliberate refusals consequential and show the affordable charge before deciding. Players can weigh margin against keeping Granny. 2. Offer a distinct skip option that preserves her visits. Players can decline a sale without ending the relationship. 3. Keep the current warning and rules. Players learn the consequence after the first refusal.

### D2 Decide how to signal the ending cost of reporting

- Severity: Decision
- Confidence: [Design]
- Reported by: B-D1, Q-D1
- How you get there: Discount Granny on days one and three, choose Report him on day six, collect the flowers on day seven, and close.
- What the player sees: Reporting sets up the recap. Granny can still bring flowers, but the documented ending for that combination is ordinary.
- Source: `game/data/characters/zhou.json:16`, `game/data/characters/zhou.json:20`, `game/data/characters/granny.json:13`, `game/data/characters/granny.json:14`, `game/data/characters/granny.json:18`, `game/README.md:34`, `game/README.md:35`, `game/text/en.csv:30`, `game/text/en.csv:31`
- Verification: Holds. The day-seven gift and report predicates are separate. The good ending requires flowers and that Old Zhou was not taken. Neither the button text nor the supplied choice data signals the ending consequence. Dialogue precedence when both predicates hold needs a playable build.
- Options: 1. Hint at lasting story consequences before reporting. Players get a reason to pause without learning the precise condition. 2. Keep the choice disclosure unchanged and explain the result at the ending. Players discover the consequence later. 3. Give the mixed route its own ending. Players see the helping and reporting choices acknowledged together.

## Needs an in-game check

Tests to run when a playable build is available.

- **Stall and both guests (S1)** Earn both gifts, try transparent and opaque pixels on each, inspect the cabinet, then close with a gift uncollected. Check pickup feedback, whether closing offers a recovery path, and whether day seven still produces an ending. In an otherwise identical run, collect both gifts. If saving is supported, reload before placement, before pickup, and after close to compare duplication or recovery.
- **Old Zhou (M1)** On a fresh English profile, check launch-menu Help and in-run Settings before the first visit and on days one through five. Inspect the hint note with default settings and after toggling hints. Repeat in Chinese and after reload if supported. Compare the first possible disclosure with his day-six request.
- **Old Zhou (M3, M4, D2, W2, W4)** Compare the three day-six choices in both locales. Note the refusal's actual missing-key fallback, the shelter reply, and immediate reporting feedback. On day seven compare the morning recap, gift and return controls, Granny's dialogue, cabinet and ending. Test a single input against quick repeat inputs if the interface permits.
- **Granny (M5, L3, D1, W1, W3)** Discount on day one and compare the next visit in each locale, taking care to record whether the default repeat line or thank-you appears. If available, save and reload before that visit. Use two separate runs to compare making the second discount on day three with making it on day seven. Try full price at a budget of 10, then “Charge less,” and record which actions charge, count as a refusal, and update the ledger. Compare an explicit pair of refusals against a failed purchase and verify the day-five visit and ending.

## Checked and fine

- **Persona and route coverage** The kindhearted, trader, and close-reader pass followed the helping and refusal paths. The reporter covered report, contrasted its next morning with shelter and refusal, and the rapid clicker and careless player traced pickup, missed dialogue and sweep scenarios. Replay attempts were traced up to the missing save interface. The contrarian compared refusing the request with keeping or leaving a gift on a separate shelter path.
- **Required progression points** Read the morning recap, open the stall, reach a sale or a refusal, advance through the day-six choice, close with or without gifts, and reach a day-seven ending in the documented loop. Shelter sets the gift flag. Reporting sets the recap flag. Refusal sets neither (`game/data/characters/zhou.json:14–20`). Granny's departure ends her route while the ordinary ending remains available (`game/README.md:14,27,34–35`).
- **Economy review** The documented income comes from successful tea sales, with Granny's 12 asking price reduced to 9 against a 10 budget and Old Zhou's 4 reduced to 1 against a 4 budget. The discount gives up 3 per successful discounted sale. The cabinet receives gifts and closing removes uncollected ones. The design specifies neither a gift sale channel nor a repeat-profit loop (`game/data/settings.json:2–6`, `game/data/characters/granny.json:4–6,18`, `game/data/characters/zhou.json:4–6,19`, `game/README.md:12,21–22`).
- **Missing-option pass** Ordinary refusal and shelter refusal already have configured choices. A passive discard path exists for unwanted gifts. W2 concerns explicit identity or causality, since the report already produces a recap. W4 concerns returning the gift to the giver (`game/text/en.csv:28–31`, `game/data/characters/zhou.json:14–20`, `game/README.md:21–22`).

## Dismissed and not reported

- **Small coarse tea and hints icon as pickup bugs.** The shelf uses whole-cell selection. The hints icon is display-only. Neither low opacity is evidence of a broken interaction (`game/data/items.json:4`, `game/data/settings.json:5,7`, `game/README.md:20,23`).
- **Automatic route lock from gift loss, Granny's departure, or the missing refusal reply.** The documented ending proceeds after closing, the ordinary ending has a catch-all rule, and Zhou is scripted to leave on refusal (`game/README.md:14,27,30,34–35`). The gift loss, design choice, and missing translation remain individually tracked.
- **An English fallback that prints the missing key or a crash from the unpaired numeric placeholder.** The static table makes a fallback prediction and flags the placeholder difference. UI fallback, formatting, and line order have no implementation in the sample. M3 retains the missing row and L3 retains the wording difference with a test (`_text_checks.md:14,16`, `game/text/en.csv:13`, `game/text/zh.csv:13,25`).
- **Granny knows Zhou's identity from a private event.** Her cold line and the report recap both mention an unnamed person. The narrative does not establish how Granny learned it or that she could not know it (`game/text/en.csv:15,31`, `game/data/characters/granny.json:13`).
- **Three guests jam the stall, or replay duplicates cash or gifts.** The guide conflicts with the two-seat configuration (M2). The supplied guests are scheduled on alternating days, with no three-guest reproduction in the files. No save, reentry, or input implementation establishes a repeat gain (`game/data/characters/granny.json:4`, `game/data/characters/zhou.json:4`, `game/README.md:3,8–9`).
- **The refusal already has a separate visible placeholder.** The draft-section comment covers two Chinese keys, but the refusal value itself is “……知道了。” Only the shelter reply includes a literal marker. The refusal's English row remains missing (M3, M4, `game/text/zh.csv:23–25`).

## Not covered this time

- Exact settings and guide visibility, queue limits and releases, insufficient-funds handling, visit timeouts, text dispatch and fallback, and same-frame input or cancel behavior require a runtime. The overlapping Granny day-seven lines, exact timing of a day-seven discount before the gift check, and dependence of the ending on collecting flowers remain to be observed.
- Saving, reloading, undo, pause, host integration, generic context menus, inventory limits, and accessibility controls are unverified. Personas 14, 17, and 18 used their general definitions where a project overlay was absent.
- Rendering scale, visual and audio cues, layout, animation, camera, collision and performance were outside static coverage. Image checks measured original alpha rather than device-scale usability. No executable is supplied.

## Index

| ID | Severity | Confidence | File:line | Quote |
|---|---|---|---|---|
| S1 | Severe | [Confirmed] | game/README.md:14 | 一局 7 天。第 7 天收摊以后出结局。 |
| S1 | Severe | [Confirmed] | game/README.md:21 | - **桌上**：客人送的东西留在桌上。玩家点它，收进柜子。点在图的透明处不算点中（按图的形状判定，`table.hit` = `pixel`）。 |
| S1 | Severe | [Confirmed] | game/README.md:22 | - 收摊时，桌上还没收的东西会被扫掉（`table.sweepAtClose`）。 |
| S1 | Severe | [Confirmed] | game/data/settings.json:6 | "table": { "hit": "pixel", "sweepAtClose": true }, |
| S1 | Severe | [Confirmed] | game/data/items.json:5 | "dried_flowers": { "image": "images\\items\\dried_flowers.png", "where": "table" }, |
| S1 | Severe | [Confirmed] | game/data/items.json:6 | "old_button": { "image": "images\\items\\old_button.png", "where": "table" } |
| S1 | Severe | [Confirmed] | game/data/characters/zhou.json:19 | "gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" }, |
| S1 | Severe | [Confirmed] | game/data/characters/granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" } |
| S1 | Severe | [Confirmed] | review_out/20261119_181306/_image_hits.md:25 | 5.9%（60 个像素） |
| S1 | Severe | [Confirmed] | review_out/20261119_181306/_image_hits.md:29 | 60.9%（624 个像素） |
| M1 | Medium | [Possible] | game/text/en.csv:4 | option_hints_tip,When on, guests get a small icon. Old Zhou is a deserter, so his icon is grey. |
| M1 | Medium | [Possible] | game/text/en.csv:22 | zhou_ask_1,...I ran from the camp. Can I hide behind your stall for a night? |
| M1 | Medium | [Possible] | game/text/zh.csv:4 | option_hints_tip,打开以后，客人头上会有小图标。老周是逃兵，他的图标是灰色的。 |
| M1 | Medium | [Possible] | game/README.md:23 | - 客人头上的提示图标只是给玩家看的，点它没有反应（`hints.clickable` = `false`）。 |
| M1 | Medium | [Possible] | game/README.md:29 | - 设定：老周的来历在第 6 天以前不能让玩家知道。 |
| M1 | Medium | [Possible] | game/data/characters/zhou.json:10 | "day6": [ "zhou_ask_1" ] |
| M1 | Medium | [Possible] | game/data/settings.json:7 | "hints": { "icon": "images\\ui\\hint_icon.png", "clickable": false } |
| M2 | Medium | [Confirmed] | game/text/en.csv:5 | guide_page_1,The stall can serve up to three guests at once. Guests leave if they wait too long. |
| M2 | Medium | [Confirmed] | game/text/zh.csv:5 | guide_page_1,茶摊同时最多招待三位客人。客人等久了会走。 |
| M2 | Medium | [Confirmed] | game/data/settings.json:2 | "stall": { "seats": 2, "days": 7 }, |
| M2 | Medium | [Confirmed] | game/README.md:8 | 2. 摆摊。茶摊有两个座位（`data\settings.json` 的 `stall.seats`）。 |
| M3 | Medium | [Confirmed] | game/data/characters/zhou.json:15 | { "button": "btn_refuse", "reply": "zhou_refused" }, |
| M3 | Medium | [Confirmed] | game/text/zh.csv:25 | zhou_refused,……知道了。 |
| M3 | Medium | [Confirmed] | game/text/en.csv:28 | btn_refuse,Refuse |
| M3 | Medium | [Confirmed] | game/README.md:30 | - 答应：第 7 天他留下一枚旧铜扣。拒绝：他走了，没有后话。报官：第 7 天早上的小结写"昨夜有人被带走"。 |
| M4 | Medium | [Confirmed] | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" }, |
| M4 | Medium | [Confirmed] | game/data/characters/zhou.json:19 | "gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" }, |
| M4 | Medium | [Confirmed] | game/text/en.csv:23 | zhou_stay_thanks,(placeholder) Thanks. |
| M4 | Medium | [Confirmed] | game/text/zh.csv:23 | # 占位：等作者写 |
| M4 | Medium | [Confirmed] | game/text/zh.csv:24 | zhou_stay_thanks,（占位）谢谢。 |
| M5 | Medium | [Confirmed] | game/data/characters/granny.json:13 | { "when": "flag:zhou_taken", "line": "granny_last_cold" }, |
| M5 | Medium | [Confirmed] | game/data/characters/granny.json:14 | { "when": "discounts>=2", "line": "granny_last_warm" } |
| M5 | Medium | [Confirmed] | game/data/characters/granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" } |
| M5 | Medium | [Confirmed] | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" }, |
| M5 | Medium | [Confirmed] | game/data/characters/zhou.json:16 | { "button": "btn_report", "sets": "flag:zhou_taken" } |
| M5 | Medium | [Confirmed] | game/text/en.csv:16 | granny_last_warm,这是我自己晒的花，你拿去泡。 |
| M5 | Medium | [Confirmed] | game/text/zh.csv:16 | granny_last_warm,这是我自己晒的花，你拿去泡。 |
| L1 | Minor | [Confirmed] | game/data/characters/granny.json:4 | "visits": { "firstDay": 1, "everyDays": 2 }, |
| L1 | Minor | [Confirmed] | game/data/characters/granny.json:8 | "first": [ "granny_first_1", "granny_first_2" ], |
| L1 | Minor | [Confirmed] | game/data/characters/granny.json:9 | "again": [ "granny_again_1" ], |
| L1 | Minor | [Confirmed] | game/text/en.csv:10 | granny_first_1,The usual. A pot of jasmine. |
| L1 | Minor | [Confirmed] | game/text/en.csv:11 | granny_first_2,This stall is new, isn't it? |
| L2 | Minor | [Confirmed] | game/data/characters/zhou.json:15 | { "button": "btn_refuse", "reply": "zhou_refused" }, |
| L2 | Minor | [Confirmed] | game/text/zh.csv:22 | zhou_ask_1,……我是从营里跑出来的。能在你摊子后面躲一晚吗？ |
| L2 | Minor | [Confirmed] | game/text/zh.csv:30 | btn_refuse,不卖 |
| L2 | Minor | [Confirmed] | game/text/en.csv:28 | btn_refuse,Refuse |
| L2 | Minor | [Confirmed] | game/README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。 |
| L3 | Minor | [Possible] | game/data/characters/granny.json:9 | "again": [ "granny_again_1" ], |
| L3 | Minor | [Possible] | game/data/characters/granny.json:10 | "afterDiscount": [ "granny_thanks" ], |
| L3 | Minor | [Possible] | game/text/en.csv:13 | granny_thanks,You charged me less last time. I remember. |
| L3 | Minor | [Possible] | game/text/zh.csv:13 | granny_thanks,上回你少收了我{0}文，我记着呢。 |
| W1 | Wanted | [Definitely missing] | game/README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。 |
| W1 | Wanted | [Definitely missing] | game/text/en.csv:26 | btn_sell,Sell at price |
| W1 | Wanted | [Definitely missing] | game/text/en.csv:27 | btn_discount,Charge less |
| W1 | Wanted | [Definitely missing] | game/text/en.csv:28 | btn_refuse,Refuse |
| W1 | Wanted | [Definitely missing] | game/data/settings.json:3 | "prices": { "jasmine": 12, "coarse": 4 }, |
| W1 | Wanted | [Definitely missing] | game/data/settings.json:4 | "discount": 3, |
| W1 | Wanted | [Definitely missing] | game/data/characters/granny.json:6 | "budget": 10, |
| W2 | Wanted | [Definitely missing] | game/data/characters/zhou.json:16 | { "button": "btn_report", "sets": "flag:zhou_taken" } |
| W2 | Wanted | [Definitely missing] | game/data/characters/zhou.json:20 | "summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" } |
| W2 | Wanted | [Definitely missing] | game/text/en.csv:15 | granny_last_cold,...They took someone away last night. I won't have tea. |
| W2 | Wanted | [Definitely missing] | game/text/en.csv:30 | btn_report,Report him |
| W2 | Wanted | [Definitely missing] | game/text/en.csv:31 | summary_taken,Someone was taken away last night. |
| W2 | Wanted | [Definitely missing] | game/data/characters/granny.json:13 | { "when": "flag:zhou_taken", "line": "granny_last_cold" }, |
| W3 | Wanted | [Definitely missing] | game/README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。 |
| W3 | Wanted | [Definitely missing] | game/text/en.csv:26 | btn_sell,Sell at price |
| W3 | Wanted | [Definitely missing] | game/text/en.csv:27 | btn_discount,Charge less |
| W3 | Wanted | [Definitely missing] | game/text/en.csv:28 | btn_refuse,Refuse |
| W3 | Wanted | [Definitely missing] | game/data/settings.json:3 | "prices": { "jasmine": 12, "coarse": 4 }, |
| W3 | Wanted | [Definitely missing] | game/data/settings.json:4 | "discount": 3, |
| W3 | Wanted | [Definitely missing] | game/data/characters/granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" } |
| W4 | Wanted | [Definitely missing] | game/data/characters/zhou.json:4 | "visits": { "days": [ 2, 4, 6 ] }, |
| W4 | Wanted | [Definitely missing] | game/data/characters/zhou.json:14 | { "button": "btn_shelter", "sets": "flag:zhou_sheltered", "reply": "zhou_stay_thanks" }, |
| W4 | Wanted | [Definitely missing] | game/data/characters/zhou.json:19 | "gift": { "day": 7, "when": "flag:zhou_sheltered", "item": "old_button" }, |
| W4 | Wanted | [Definitely missing] | game/data/items.json:6 | "old_button": { "image": "images\\items\\old_button.png", "where": "table" } |
| W4 | Wanted | [Definitely missing] | game/data/settings.json:6 | "table": { "hit": "pixel", "sweepAtClose": true }, |
| W4 | Wanted | [Definitely missing] | game/README.md:21 | - **桌上**：客人送的东西留在桌上。玩家点它，收进柜子。点在图的透明处不算点中（按图的形状判定，`table.hit` = `pixel`）。 |
| W4 | Wanted | [Definitely missing] | game/README.md:22 | - 收摊时，桌上还没收的东西会被扫掉（`table.sweepAtClose`）。 |
| D1 | Decision | [Design] | game/data/characters/granny.json:4 | "visits": { "firstDay": 1, "everyDays": 2 }, |
| D1 | Decision | [Design] | game/data/characters/granny.json:6 | "budget": 10, |
| D1 | Decision | [Design] | game/data/characters/granny.json:11 | "afterRefused": [ "granny_warn" ], |
| D1 | Decision | [Design] | game/data/characters/granny.json:17 | "leaveForever": { "refusedInARow": 2 }, |
| D1 | Decision | [Design] | game/data/characters/granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" } |
| D1 | Decision | [Design] | game/text/en.csv:14 | granny_warn,You won't sell to me today... Do it again and I won't come back. |
| D1 | Decision | [Design] | game/README.md:14 | 一局 7 天。第 7 天收摊以后出结局。 |
| D1 | Decision | [Design] | game/README.md:27 | - **阿婆**（`granny`）：每两天来一次，要一壶茉莉。钱不多。连着两次被"不卖"，她就不再来（第一次被拒绝时她会说一句警告）。少收过她两次以上，第 7 天她会送一包自己晒的花。 |
| D1 | Decision | [Design] | game/README.md:34 | - 好结局：阿婆送了花，而且老周没有被带走。 |
| D1 | Decision | [Design] | game/README.md:35 | - 普通结局：别的情况。 |
| D2 | Decision | [Design] | game/data/characters/zhou.json:16 | { "button": "btn_report", "sets": "flag:zhou_taken" } |
| D2 | Decision | [Design] | game/data/characters/zhou.json:20 | "summary": { "day": 7, "when": "flag:zhou_taken", "line": "summary_taken" } |
| D2 | Decision | [Design] | game/data/characters/granny.json:13 | { "when": "flag:zhou_taken", "line": "granny_last_cold" }, |
| D2 | Decision | [Design] | game/data/characters/granny.json:14 | { "when": "discounts>=2", "line": "granny_last_warm" } |
| D2 | Decision | [Design] | game/data/characters/granny.json:18 | "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" } |
| D2 | Decision | [Design] | game/README.md:34 | - 好结局：阿婆送了花，而且老周没有被带走。 |
| D2 | Decision | [Design] | game/README.md:35 | - 普通结局：别的情况。 |
| D2 | Decision | [Design] | game/text/en.csv:30 | btn_report,Report him |
| D2 | Decision | [Design] | game/text/en.csv:31 | summary_taken,Someone was taken away last night. |
