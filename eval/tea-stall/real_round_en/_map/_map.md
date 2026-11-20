# Project map

Tea Stall is a fictional standalone stall-management design for demonstrating a review toolkit. The project contains design notes, JSON, images, and localization data, with no executable or host integration described. Source: `game/README.md:1-3`.

## Overview

A round is a seven-day playthrough. Each day goes from the morning recap to opening the stall, guests arriving and speaking, an order and the sell/discount/refuse choice, guests leaving, closing, and the night ledger. The ending follows day seven's close. This follows `project.json` keys `playUnit` and `playLoop` and `game/README.md:5-14`. The two character routes are Granny and Old Zhou, with shared stall interactions and an outcome carried across routes. Sources: `game/README.md:25-36`, `game/data/characters/granny.json:2-5`, `game/data/characters/zhou.json:2-5`.

| Table | Rows | Sources and confidence |
|---|---:|---|
| `01_线.md` | 10 | README and both character files. Scheduled events and explicit conditions are documented. Within-day ordering is unspecified. |
| `02_选择点.md` | 10 | README, settings, item and character files, and both CSV files. Actions are documented. Runtime effects and undo are partly unspecified. |
| `03_标记和状态.md` | 8 | README and both character files. Conditions are explicit where given. Storage, initialization, and resets are mostly unspecified. |
| `04_东西.md` | 4 | Items, settings, README, character files, and round image table. Item types, images and hit rules are explicit. |
| `05_结局和必经点.md` | 7 | README and both character files. Ending predicates and branch gates are documented. Runtime evaluation order is unspecified. |
| `06_数值.md` | 10 | README, settings, characters and both CSV files. Arithmetic uses configured inputs. Repetition and enforcement without runtime remain unknown. |
| `07_文本.md` | 17 | Both CSV files, README, settings and character files. Literal references and table presence are directly checkable. Runtime key construction is unspecified. |
| `08_互相牵连.md` | 3 | README and both character files. Cross-route effects are explicit. Competing day-seven line precedence is unspecified. |
| `10_顺手看到的.md` | 12 | Design, data, CSV and round static sources. These are source observations and leads for reviewers. |
| `11_设置和便利.md` | 2 | README, settings and both CSV files. UI copy and data identify hints and language resources. Actual controls and persistence are unspecified. |

## Invariants

| Setting in `project.json:131-135` | Table and rows |
|---|---|
| Granny can afford her requested item at least with the discount. | `06_数值.md`, Jasmine and Granny's budget rows. |
| Player-visible text before day six never discloses Old Zhou's background. | `01_线.md`, Day six disclosure. `07_文本.md`, `option_` row. |
| Granny's day-seven dialogue references only what she could know. | `07_文本.md`, `granny_last_` row. `08_互相牵连.md`, report-to-dialogue row. |

## Materials not available

Both routes, all text and JSON under `game`, and the two design documents were read. PNG filenames were inventoried and transparency measurements were taken from the supplied static report. No runnable game, host, execution code, or save format is present in the game materials (`game/README.md:3`). There is no host integration table for this standalone design. Exact visibility timing, UI text fallback, state persistence and day-seven condition order remain unspecified.
