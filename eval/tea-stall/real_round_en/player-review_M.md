# Player review · M Economy and balance (2026-11-19)

- Scope: All documented stall, Granny, and Old Zhou routes.
- Review method: Economy and balance.
- Persona: 2, the shrewd trader, as a route prompt. The project overlay describes refusing Granny's unaffordable full-price order, selling at full price to Old Zhou, and refusing shelter on day six.
- Project map: `_map/_map.md` and the routes, choices, state, items, progression, values, and cross-route tables. Original sources were checked.
- Static checks: `_summary.md`, `_text_checks.md` and `_image_hits.md`.
- Value tables: `game/data/settings.json`, `game/data/characters/granny.json`, `game/data/characters/zhou.json` and `game/data/items.json`.

## Conclusion

The documented discounts produce positive, affordable prices for both orders. A fixed full-price policy loses Granny's sales, and two consecutive refusals close her route as designed. The guide overstates stall capacity and the English discount acknowledgment drops the numeric amount present in Chinese. No repeatable profit loop or reward duplication is demonstrated by the supplied design and data. This group reports 0 Severe, 1 Medium, 1 Minor, 1 decision, and 1 wanted option.

## Player feedback

### 2 Shrewd trader

- Confused: “The guide says three guests, but the stall has two seats.” (M1)
- Wants: “If she can't pay the listed price, let me charge just enough that the sale goes through.” (W1)
- Feels unfair: “I held to the asking price and turned her down twice. She warned me the first time, and then she stopped coming.” (D1)
- Done right: “At the end of the day I can check what I earned and who came by.” (`game/README.md:12` — ``6. 夜里看账本：今天赚了多少、谁来过。``)
- In one line: “The full-price orders worked for the guest ordering coarse tea. With Granny I'd like a price we can both agree on.” (`game/data/characters/zhou.json:6` — ``"budget": 4,``, `game/data/settings.json:3` — ``"prices": { "jasmine": 12, "coarse": 4 },``, W1)

## Economy review

### Sources

| Source | Amount | Condition | Repetition and timing | Evidence |
|---|---|---|---|---|
| Granny's jasmine tea sale | 12 full asking price, 9 discounted. Budget 10. | Completed sale. The listed budget covers the discount only. | Days 1, 3, 5, and 7 while eligible. No separate cooldown is specified. | `game/data/settings.json:3-4`, `game/data/characters/granny.json:4-6,17` |
| Old Zhou's coarse tea sale | 4 full price, 1 discounted. Budget 4. | Either listed quote fits the budget. | Days 2, 4, and 6 if the tea sale is offered and completed. Day-six order with the shelter decision is unspecified. | `game/data/settings.json:3-4`, `game/data/characters/zhou.json:4-6,10-17` |
| Granny remembers discounts | One discount toward a threshold of two documented discounts per distinct discounted visit. The English acknowledgment states it was remembered. | Use the discounted sale route with Granny. | On eligible visits. Counting and duplicate-input protection depend on the implementation. | `game/README.md:27`, `game/data/characters/granny.json:10,18`, `game/text/en.csv:13` |
| Dried flowers | One packet in the design. Resale amount unspecified. | Day seven and at least two discounts. The gift is available for table collection. | One documented day, with no stated repeat entry or cooldown. | `game/README.md:21,27`, `game/data/characters/granny.json:18`, `game/data/items.json:5` |
| Old copper button | One button in the design. Resale amount unspecified. | Shelter Old Zhou on day six, then collect the table gift on day seven. | One documented gift day. Persistence and deduplication are unspecified. | `game/README.md:21,30`, `game/data/characters/zhou.json:14,19`, `game/data/items.json:6` |

### Sinks

| Sink or opportunity cost | Amount | Condition | Repetition and timing | Evidence |
|---|---|---|---|---|
| Discount against list price | 3 off either quote | Choose “Charge less.” It gives up 3 receipts if full price was attainable. In Granny's case it makes the sale affordable. | Standard order options are offered per guest. No stacking is specified. | `game/README.md:9-10`, `game/data/settings.json:3-4`, `game/text/en.csv:27` |
| Refusal and lost repeat sales | Zero receipts on the refused order. A second consecutive Granny refusal removes later visits. | “Refuse” on two successive Granny visits. The first refusal has a warning. | One documented permanent exit. | `game/README.md:27`, `game/data/characters/granny.json:11,17`, `game/text/en.csv:14,28` |
| Table sweep | Any uncollected table gift | Close while a gift remains on the table. | Every close under the documented rule. Both gifts are configured for day seven. | `game/README.md:21-22`, `game/data/settings.json:6`, `game/data/characters/granny.json:18`, `game/data/characters/zhou.json:19` |

### Rate, limits, and replay

- Granny: `12 - 3 = 9 ≤ 10 < 12`. On days one and three, refusing realizes zero from her, and the second consecutive refusal removes the prospective days five and seven. Taking the discount twice instead produces 18 in gross receipts and meets the stated gift threshold ahead of day seven. Four completed discounted orders would yield 36.
- Old Zhou: `4 ≤ 4`, and `4 - 3 = 1`. Each full-price coarse sale earns 3 more than a discounted one. Days two and four give 8 if the orders complete, or 12 if a third full-price sale on day six also completes. The provided day-six choices do not set a sales order, and the shelter choice affects the gift rather than a documented cash payment.
- Combined: `(4 × 9) + (3 × 4) = 48` under the all-seven-sales scenario, versus `0 + (3 × 4) = 12` under the overlay's no-discount policy and two Granny refusals. If no day-six sale occurs, the corresponding receipts would be 44 and 8. These are conditional gross receipts. Inventory costs, replenishment, tax, and purchase enforcement are unspecified.
- Loop check: shelf tea → scheduled sale → possible day-seven gift → cabinet or sweep. There is no documented route from the cabinet to a resale, refund, another guest, or an extra day. A net-profit calculation would require stock costs and any resale prices. The configured seven-day window and nonoverlapping visitor days support a bounded receipts scenario.
- Reward and replay check: both gifts name day seven and their own qualifying condition. Neither gift record specifies a stored claim flag or persistence behavior. There is no documented save/load entry, random payout, rent, debt payment, or cash penalty to model. The defined daily deadline removes uncollected gifts instead of preserving them for later.

Arithmetic and limits use `game/data/settings.json:2-6`, `game/data/characters/granny.json:4-6,17-18`, `game/data/characters/zhou.json:4-6,13-20`, and `game/README.md:9-14,20-22,27-35`.

## Issues at a glance

| ID | Severity | Confidence | Character | What the player sees |
|---|---|---|---|---|
| M1 | Medium | [Confirmed] | Stall | A guide says three guests can be served at once. The stall has two configured seats. |
| L1 | Minor | [Confirmed] | Granny | The English follow-up acknowledges the discount but leaves out the amount retained in the Chinese wording. |

## Issues

### M1 The guide advertises three seats for a two-seat stall

- Severity: Medium
- Confidence: [Confirmed]
- Character: Shared stall
- How you get there: Read the first guide entry in either language, then compare its capacity with the stall design.
- What the player sees: The English guide says “The stall can serve up to three guests at once.” The Chinese guide promises the same number.
- Why it is wrong: The advertised capacity exceeds the configured and documented capacity by one seat.
- Source: `game/text/en.csv:5` — ``guide_page_1,The stall can serve up to three guests at once. Guests leave if they wait too long.``, `game/text/zh.csv:5` — ``guide_page_1,茶摊同时最多招待三位客人。客人等久了会走。``, `game/data/settings.json:2` — ``"stall": { "seats": 2, "days": 7 },``, `game/README.md:8` — ``2. 摆摊。茶摊有两个座位（`data\settings.json` 的 `stall.seats`）。``.
- Cross-check: Searched the supplied files for `stall.seats`, `guide_page_1`, capacity values and visit schedules. Both the design and configuration use two. The named guests visit on alternating days, so the material does not establish a playable three-guest queue.
- Suggestion: Say “two” in both guide entries, or document and configure a three-seat stall if that is the intended capacity.

### L1 Granny's English thank-you omits the discount amount

- Severity: Minor
- Confidence: [Confirmed]
- Character: Granny
- How you get there: Use “Charge less” on Granny's order, then compare the configured after-discount line in the two languages.
- What the player sees: “You charged me less last time. I remember.” The matching Chinese line has a slot for how much less.
- Why it is wrong: The English line loses numeric detail a player could use to reconcile the price change. The evidence establishes the wording difference. Whether the same information is available in a receipt or UI remains unverified.
- Source: `game/data/characters/granny.json:10` — ``"afterDiscount": [ "granny_thanks" ],``, `game/data/settings.json:4` — ``"discount": 3,``, `game/text/en.csv:13` — ``granny_thanks,You charged me less last time. I remember.``, `game/text/zh.csv:13` — ``granny_thanks,上回你少收了我{0}文，我记着呢。``.
- Cross-check: Both localized rows use the same key. The English row has no numeric argument. There is no executable for checking argument substitution or other screens.
- Suggestion: Keep the argument in both translations if Granny is meant to acknowledge the amount.

## Wanted but missing

### W1 A trader wants to set the smallest discount Granny can afford

- Who wants it: Persona 2, a trader comparing affordable sale prices.
- Where it happens: Granny's order on day one or a repeat visit.
- What they want to do and why: Charge 10, a discount of 2 from the asking price, so the sale fits the budget and brings in one more unit than the fixed discount. This is a player preference inferred from the trader's focus on pricing.
- Options today: `game/README.md:10` — ``4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。``, `game/text/en.csv:26` — ``btn_sell,Sell at price``, `game/text/en.csv:27` — ``btn_discount,Charge less``, `game/text/en.csv:28` — ``btn_refuse,Refuse``. The listed prices and budget are `game/data/settings.json:3` — ``"prices": { "jasmine": 12, "coarse": 4 },``, `game/data/settings.json:4` — ``"discount": 3,``, `game/data/characters/granny.json:6` — ``"budget": 10,``.
- Without it: The documented asking price is 12, the fixed discounted quote is 9, and refusal ends the transaction. Repeated refusal can end visits.
- Similar options elsewhere: Old Zhou uses the same sale choices. His budget exactly matches his base price. No adjustable price, credit or separate bargaining entry is documented.
- Confidence: [Definitely missing] in the enumerated offer. Searched the game text, design and data for sale and discount actions, alternate prices, credit, refunds and bargaining.
- How to add it: Provide a preset “charge 10” or an adjustable offer. If partial discounts affect Granny's gift, define which offers count.

## Needs your decision

### D1 Full-price play loses Granny as a regular

- Confidence: [Design]
- What the player sees: The asking price remains out of reach for Granny without a discount. After the first refusal she warns that she will stop coming. A second consecutive refusal ends future visits, so the trader cannot make later sales to her.
- Source: `game/data/settings.json:3` — ``"prices": { "jasmine": 12, "coarse": 4 },``, `game/data/settings.json:4` — ``"discount": 3,``, `game/data/characters/granny.json:6` — ``"budget": 10,``, `game/data/characters/granny.json:17` — ``"leaveForever": { "refusedInARow": 2 },``, `game/data/characters/granny.json:18` — ``"gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" }``, `game/README.md:27` — ``- **阿婆**（`granny`）：每两天来一次，要一壶茉莉。钱不多。连着两次被"不卖"，她就不再来（第一次被拒绝时她会说一句警告）。少收过她两次以上，第 7 天她会送一包自己晒的花。``, `game/text/en.csv:14` — ``granny_warn,You won't sell to me today... Do it again and I won't come back.``.
- Cross-check: The affordability invariant asks that she can buy at least with a discount. The 9 quote fits her budget of 10. The departure counter has an explicit threshold of two consecutive refusals.
- Options: 1. Keep the trade-off and show Granny's payable price when the sale options open. The trader can weigh a smaller sale against losing future visits. 2. Separate an unaffordable transaction from deliberate refusal. The trader could maintain the route without making a sale. 3. Keep the current rules and warning unchanged.

## Checked and fine

- Configured discounts leave both successful payments above zero. Old Zhou's full price equals his budget and Granny's discounted price is within budget.
- No resale or buy-back activity is specified for the tea or gifts. Gifts go to the cabinet on pickup and the documented close rule sweeps what is left.
- The mostly transparent coarse-tea image does not reduce the documented full-cell shelf target. See `game/data/items.json:4`, `game/data/settings.json:5`, and `game/README.md:20`.
- The seven-day end and named gift days impose the design's time boundaries. No recurring bill, debt, fine, random reward, or time-skip control appears in the supplied rules.

## Not covered this time

- The project has no runnable game, as stated in `game/README.md:3`. Budget enforcement, text interpolation, inventory limits, receipt accuracy, timing and save persistence remain unverified.
- In a build, complete the day-six coarse tea and shelter path and check the ledger against exactly one sale. On day seven, collect each eligible gift twice or reload between placement and pickup if saving is supported. Compare the cabinet and ledger after each action and after closing.
- In a build, use the displayed 12 quote with Granny, then try 9. Check refusal handling, deductions, feedback on insufficient funds and the actual discount amount in the two locales. Test closing before a pending transaction if the interface permits it.

## Index

| ID | Severity | Confidence | File:line | Quote |
|---|---|---|---|---|
| M1 | Medium | [Confirmed] | game/text/en.csv:5 | guide_page_1,The stall can serve up to three guests at once. Guests leave if they wait too long. |
| M1 | Medium | [Confirmed] | game/text/zh.csv:5 | guide_page_1,茶摊同时最多招待三位客人。客人等久了会走。 |
| M1 | Medium | [Confirmed] | game/data/settings.json:2 |   "stall": { "seats": 2, "days": 7 }, |
| M1 | Medium | [Confirmed] | game/README.md:8 | 2. 摆摊。茶摊有两个座位（`data\settings.json` 的 `stall.seats`）。 |
| L1 | Minor | [Confirmed] | game/data/characters/granny.json:10 |     "afterDiscount": [ "granny_thanks" ], |
| L1 | Minor | [Confirmed] | game/data/settings.json:4 |   "discount": 3, |
| L1 | Minor | [Confirmed] | game/text/en.csv:13 | granny_thanks,You charged me less last time. I remember. |
| L1 | Minor | [Confirmed] | game/text/zh.csv:13 | granny_thanks,上回你少收了我{0}文，我记着呢。 |
| W1 | Wanted | [Definitely missing] | game/README.md:10 | 4. 玩家有三个按钮：**照价卖**、**少收一点**、**不卖**。 |
| W1 | Wanted | [Definitely missing] | game/text/en.csv:26 | btn_sell,Sell at price |
| W1 | Wanted | [Definitely missing] | game/text/en.csv:27 | btn_discount,Charge less |
| W1 | Wanted | [Definitely missing] | game/text/en.csv:28 | btn_refuse,Refuse |
| W1 | Wanted | [Definitely missing] | game/data/settings.json:3 |   "prices": { "jasmine": 12, "coarse": 4 }, |
| W1 | Wanted | [Definitely missing] | game/data/settings.json:4 |   "discount": 3, |
| W1 | Wanted | [Definitely missing] | game/data/characters/granny.json:6 |   "budget": 10, |
| D1 | Decision | [Design] | game/data/settings.json:3 |   "prices": { "jasmine": 12, "coarse": 4 }, |
| D1 | Decision | [Design] | game/data/settings.json:4 |   "discount": 3, |
| D1 | Decision | [Design] | game/data/characters/granny.json:6 |   "budget": 10, |
| D1 | Decision | [Design] | game/data/characters/granny.json:17 |   "leaveForever": { "refusedInARow": 2 }, |
| D1 | Decision | [Design] | game/data/characters/granny.json:18 |   "gift": { "day": 7, "when": "discounts>=2", "item": "dried_flowers" } |
| D1 | Decision | [Design] | game/README.md:27 | - **阿婆**（`granny`）：每两天来一次，要一壶茉莉。钱不多。连着两次被"不卖"，她就不再来（第一次被拒绝时她会说一句警告）。少收过她两次以上，第 7 天她会送一包自己晒的花。 |
| D1 | Decision | [Design] | game/text/en.csv:14 | granny_warn,You won't sell to me today... Do it again and I won't come back. |

