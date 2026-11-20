# 参考文献

这个工具包用了别人的研究、数据和方法。全部来源列在这一个文件里，别的文件只写编号，指到这里。

**怎么读**：
- 编号 **M** 开头的是测试方法的来源，**K** 开头的是审查种类调研的，**T** 开头的是提示词和准确度调研的，**P** 开头的是画像搜集的，**C** 开头的是接各家模型的；善恶画像调研的来源没有编号，按主题列。
- 每条写了我们是**打开读过原文**，还是**只看到搜索摘要 / 摘要页**。只看到摘要的，文档里用到它的地方也标了。照实写，没打开的不当成打开过。
- 文档里都是**转述**，不是原文；直接引用很少，每处不超过十几个词，带引号和编号。
- 引的数字（问卷比例、准确率、条数……）是那些来源自己的数据，条件和口径以原文为准。我们只拿它们当依据和提示，没有重新验证。
- 标了【推断】的结论是我们自己推的，不是来源说的。

**用了哪些东西、用在哪**：

| 用了什么 | 用在哪 | 来源在哪一节 |
|---|---|---|
| 探索式测试的做法（巡游、按时段测试、一致性启发式）、可用性评审的做法（认知走查）、文字游戏的自动测试经验、游戏 bug 的分类 | `method\方法.md`、`agent\player-bug-reviewer.md` 的清单和"算不算问题"、`kinds\tours.md`、`kinds\walkthrough.md` | 一、三 |
| 玩家按善恶和守不守规矩怎么分、各占多少的问卷和官方统计 | `method\画像.md` 的善恶画像（格子、常见度、优先级） | 二 |
| 玩家类型和动机模型 | `method\画像.md` 的 26–31 号画像 | 三 |
| 玩家分群和动机量表、无障碍准则和评测角度、本地化和平台合规的公开资料、测试团队的分工、各类游戏社区里的玩法 | 画像库 32–98（`method\画像_玩法.md`、`画像_动机.md`、`画像_处境.md`、`画像_类型专用.md`、`画像_测试者.md`）、并进 1–31 和各走法的「也照这个走」「另外也查」、`method\画像_索引.md` 的挑画像表 | 五 |
| 用自动化代理和大语言模型当测试玩家的研究、合成用户的局限 | `kinds\` 各走法里"定把握"和"小心"的部分、`kinds\ledger.md` | 三 |
| 软锁、经济漏洞、模组兼容、本地化、无障碍、内容分级的公开资料和准则 | `kinds\softlock.md`、`economy.md`、`modsurface.md`、`a11y.md`、`content.md` | 三 |
| 模型厂商的提示词和代理指南、用模型做代码审查和找漏洞的研究、角色提示有没有用的研究、评测的做法 | `agent\` 两个代理的提示词（工作顺序、草稿文件、例子、有原文才算数）、`skill\player-review\merge.md` 的核对、`kinds\map.md`、`static\check_citations.py`、`eval\` | 四 |
| Claude Code 接别家模型的环境变量、各服务商的 Anthropic 兼容接口地址和模型 id | `api\providers.json`、`api\run_api_task.ps1` 的 `-Provider`、README「接哪家的模型」 | 六 |

加了新的来源：写进下面对应的一节，接着编号；文档里用编号引。不要在别的文件里另开来源列表。

---

## 一、测试方法（`method\方法.md` 用的，编号 M）

打开看过的：

- [M1] Michael Bolton, "FEW HICCUPPS"（DevelopSense, 2012）. https://developsense.com/blog/2012/07/few-hiccupps
- [M2] James Bach, *Heuristic Test Strategy Model* v6.3（Satisfice, 2024，PDF，看了 Product Factors 一节）. https://www.satisfice.com/download/heuristic-test-strategy-model
- [M3] James Whittaker, "the touring test"（MSDN 博客存档, 2009）. https://learn.microsoft.com/en-us/archive/blogs/james_whittaker/the-touring-test
- [M5] Choice of Games, "Testing ChoiceScript Games Automatically". https://www.choiceofgames.com/make-your-own-games/testing-choicescript-games-automatically
- [M6] Choice of Games, "How to Get the Most Out of Automated Testing, Part 2"（2018）. https://www.choiceofgames.com/2018/01/how-to-get-the-most-out-of-automated-testing-part-2/
- [M7] wildwinter, Ink-Tester（GitHub）. https://github.com/wildwinter/Ink-Tester
- [M8] Failbetter Games, "Quality Assurance in Mask of the Rose". https://www.failbettergames.com/news/quality-assurance-in-mask-of-the-rose
- [M9] Jon Manning, "Compiling Your Story: Using Techniques from Compiler Design to Check Your Narrative"（GDC 2019，只看了摘要页）. https://gdcvault.com/play/1025981/Compiling-Your-Story-Using-Techniques
- [M10] Yarn Spinner, Story Solver（产品页，封闭测试中）. https://www.yarnspinner.dev/storysolver
- [M13] Emily Short, "GDC 2012 talk on dynamic dialogue"（讲 Valve 的 Elan Ruskin 那场）. https://emshort.blog/2012/03/16/gdc-2012-talk-on-dynamic-dialogue/ 。演讲页 https://gdcvault.com/play/1015528/AI-driven-Dynamic-Dialog-through ；幻灯片 PDF 太大，没打开。
- [M15] Cultured Vultures, "Supergiant's Hades Contains More Words Than The Iliad and Odyssey Combined". https://culturedvultures.com/?p=142587 ；另见 Game Developer, "How Supergiant weaves narrative rewards into Hades' cycle of perpetual death"（2020）. https://gamedeveloper.com/design/how-supergiant-weaves-narrative-rewards-into-i-hades-i-cycle-of-perpetual-death 。"按优先级挑对话"没找到一手资料。
- [M16] GamingBolt, "Baldur's Gate 3 Bug Resulted in a Companion Losing 1500 Dialogue Lines"（2023）. https://gamingbolt.com/baldurs-gate-3-bug-resulted-in-a-companion-losing-1500-dialogue-lines
- [M19] Bugnet, "How to prevent soft locks in your game"（工具厂商的博客，只当定义用）. https://bugnet.io/blog/how-to-prevent-soft-locks-in-your-game
- [M21] Yifei Chen, Sarra Habchi, Lili Wei, "MIMIC: Integrating Diverse Personality Traits for Better Game Testing Using Large Language Model"（ASE 2025，看了摘要）. https://arxiv.org/abs/2510.01635
- [M22] Chengjia Wang 等, "Leveraging LLM Agents for Automated Video Game Testing"（TITAN，看了摘要）. https://arxiv.org/abs/2509.22170v1
- [M23] Mohammad Reza Taesiri 等, "Large Language Models are Pretty Good Zero-Shot Video Game Bug Detectors"（2022，看了摘要）. https://arxiv.org/abs/2210.02506
- [M24] Taesiri 等, "GlitchBench: Can Large Multimodal Models Detect Video Game Glitches?"（CVPR 2024，看了摘要）. https://arxiv.org/abs/2312.05291
- [M25] Zhengran Zeng 等, "SWR-Bench: Assessing LLM Performance in Real-World Code Review Comment Generation"（看了摘要）. https://arxiv.org/abs/2509.01494
- [M27] Jenna 的星露谷合集指南, "Installing to Existing Saves". https://jenna-juffuffles.gitbook.io/svve/installation/installing-to-existing-saves
- [M29] 《Probably Stolen》Steam 论坛「Bugs and Technical Issues」：
  - "Mod support bug——have to re-enable all mods every time I play." https://steamcommunity.com/app/4348910/discussions/2/574932244729438179/
  - "Bug: Shutter won't open at the start of Day 211 (Vanilla / No Mods)" https://steamcommunity.com/app/4348910/discussions/2/574932244729439362/
  - 只看了第一页 15 个帖子的标题，没有找到关于剧情人物、重复台词、存档的帖子。

只看到检索摘要、没打开原文的（引用时只用了摘要里的意思）：

- [M4] 按时段的探索测试（SBTM）的二手介绍. https://ryancraventech.substack.com/p/session-based-test-management （原始出处 satisfice.com 的 SBTM 文章没打开）
- [M11] intfiction.org, "Automated testing for Inform 7 skeins?". https://intfiction.org/t/automated-testing-for-inform-7-skeins/59763
- [M12] Moreno-Ger 等, "Model-checking for adventure videogames"（*Information and Software Technology*, 2009）. https://www.academia.edu/16615766/Model_checking_for_adventure_videogames
- [M14] Emily Short, "Beyond Branching: Quality-Based, Salience-Based, and Waypoint Narrative Structures"（2016）. https://emshort.blog/2016/04/12/beyond-branching-quality-based-and-salience-based-narrative-structures/
- [M17] PC Gamer, "Mass Effect 3 face importing bug fix incoming…"（2012）. https://www.pcgamer.com/mass-effect-3-face-importing-bug-fix-incoming-bioware-suggest-alternative-solution
- [M20] Holmgård 等, "Monte-Carlo Tree Search for Persona Based Player Modeling"（AIIDE 2015）. https://ojs.aaai.org/index.php/AIIDE/article/view/12849
- [M26] CleverX, "Synthetic users for research: what they are and where they fall short"（厂商文章，观点，不是研究）. https://cleverx.com/blog/synthetic-users-for-research-what-they-are-and-where-they-fall-short/

---

## 二、玩家怎么按善恶分类（`method\调研_善恶画像.md` 用的，没有编号，按主题列）

玩家分类和社区

- Lange 问卷转述（Games Criticism）：https://gamescriticism.org/2023/07/14/youre-just-gonna-be-nice-how-players-engage-with-moral-choice-systems/
- ENWorld，murderhobo 讨论：https://www.enworld.org/goto/post?id=7300343
- ENWorld，Chaotic Neutral：https://www.enworld.org/threads/worlds-of-design-chaotic-neutral-is-the-worst.667279/
- Lily Autumn West，Lawful Stupid / Murderhobo：https://lilyautumnwest.substack.com/p/sir-lawful-stupid-and-the-chaotic
- RPG.net，Alignment：https://www.rpg.net/columns/charactermatters/charactermatters4.phtml
- Undertale Wiki，Genocide Route：https://undertale.wiki/w/Genocide%20Route

官方 / 开发者数据

- Larian 社区更新（首发周末）：https://baldursgate3.game/news/community-update-23-here-s-to-you_83
- PC Gamer，35% 走恶（只读到标题和搜索摘要）：https://www.pcgamer.com/i-cant-believe-35-of-baldurs-gate-3-players-already-took-the-evil-route
- Kotaku，BG3 三周年 / 阿尔菲拉：https://kotaku.com/baldurs-gate-3-player-stats-alfira-murderers-dark-urge-2000721639
- Everything Edinburgh，BG3 三周年数据：https://everythingedinburgh.com/games/news/baldurs-gate-3-third-anniversary-stats/
- PC Gamer，Larian 总监对首遍角色的建议：https://pcgamer.com/larian-ceos-advice-about-origin-characters-has-thrown-my-baldurs-gate-3-playthrough-plans-into-disarray
- 80.lv，BG3 走恶（5% 的说法，未核实）：https://80.lv/articles/if-you-re-truly-evil-in-baldur-s-gate-3-you-end-up-alone
- BG3 Wiki，Approval：https://bg3.wiki/wiki/Approval
- Fextralife，Companion Approval：https://baldursgate3.wiki.fextralife.com/Companion+Approval
- GamesRadar，BG3 作者谈 approval（只看到标题）：https://www.gamesradar.com/games/baldur-s-gate/baldurs-gate-3-writer-says-the-rpgs-reputation-system-exists-because-larian-cant-just-let-players-break-party-members-we-would-be-working-on-the-game-forever/
- PC Gamer，Larian 的反应式设计（只看到标题）：https://www.pcgamer.com/games/rpg/larian-gave-baldurs-gate-3-its-acclaimed-reactivity-by-approaching-it-as-weird-dungeon-masters
- Bleeding Cool，Ebenger 的 92% Paragon：https://www.bleedingcool.com/2020/02/23/newly-revealed-stats-show-most-mass-effect-players-chose-paragon/
- PCGamesN，Legendary Edition 单项统计：https://www.pcgamesn.com/mass-effect-legendary-edition/paragon-vs-renegade
- Game Informer，Telltale 道格 / 卡莉：https://gameinformer.com/b/news/archive/2013/03/28/telltale-why-fewer-people-saved-doug-in-the-walking-dead
- Shacknews，行尸走肉：https://shacknews.com/article/77278/spoiler-talk-the-walking-dead-and-survivors-guilt
- GamesBeat，行尸走肉统计：https://gamesbeat.com/telltale-games-the-walking-dead-statistics-trailer/
- Kotaku，血腥男爵任务：https://kotaku.com/the-story-behind-the-witcher-3s-bloody-baron-quest-1736090893
- Reddit，底特律流程图汇总（社区）：https://nyc1.lr.ggtyler.dev/r/DetroitBecomeHuman/comments/99b65j/all_100_flowcharts_with_global_stats_included
- Disco Elysium 开发日志，政治观系统：https://discoelysium.com/devblog/2019/11/13/the-political-alignment-system
- GamePressure，寒霜朋克 / 这是我的战争的道德：https://www.gamepressure.com/editorials/fifth-dont-kill-on-moral-dilemmas-in-video-games/zf4b9
- Steam 全球统计，Papers, Please：https://steamcommunity.com/stats/PapersPlease/achievements

Probably Stolen

- Steam 商店页：https://store.steampowered.com/app/4603730
- Game Developer（tinyBuild 新闻稿）：https://www.gamedeveloper.com/press-release/tinybuild-announces-probably-stolen-a-cyberpunk-pixel-art-shop-simulator-where-the-goods-aren-t-purely-legal
- DLCompare：https://www.dlcompare.com/gaming-news/probably-stolen-when-honesty-won-t-pay-the-rent-87597
- PlayNews，发售公告（只看到搜索摘要）：https://www.playnews.gg/en/announcements/probably-stolen-cyberpunk-shopkeeper-sim-launches-on-steam-october-28-2026

研究和其他框架

- Weaver & Lewis 2012，Mirrored Morality：https://pubmed.ncbi.nlm.nih.gov/23017118/
- Macquarie 大学，Ryan 等，道德计量表（只读到摘要）：https://researchers.mq.edu.au/en/publications/morality-meters-and-their-impacts-on-moral-choices-in-videogames-/
- TechXplore，同一研究的新闻稿：https://techxplore.com/news/2023-05-good-evil-gaming.amp
- Quantic Foundry：https://quanticfoundry.com/?p=1912

---

## 三、模拟玩家审查的种类（`method\调研_审查种类.md` 用的，编号 K）

"打开读过" = 我用抓取工具打开了这个网址，读到了正文（或正文的摘要）。"只看到搜索摘要" = 只在搜索结果里见到。

**玩家类型和动机**
- [K1] Hearts, Clubs, Diamonds, Spades: Players Who Suit MUDs。Richard Bartle，1996。https://mud.co.uk/richard/hcds.htm —— **打开读过**
- [K2] Gamer Motivation Model。Quantic Foundry（Nick Yee、Nicolas Ducheneaut），2015 起。https://quanticfoundry.com/gamer-motivation-model/ —— **只看到搜索摘要**（官网返回 403）
- [K3] BrainHex: A neurobiological gamer typology survey。Lennart Nacke、Chris Bateman、Regan Mandryk，2014。https://ub-ir.bolton.ac.uk/esploro/outputs/journalArticle/BrainHex-A-neurobiological-gamer-typology-survey/9911971008841 —— **只看到搜索摘要**
- [K4] Gamification User Types Hexad。Andrzej Marczewski，2012 / 2013 起。https://hexad.gamified.uk/ —— **打开读过**
- [K5] 4 Keys to Fun。Nicole Lazzaro（XEODesign），2004。https://learningdiscourses.com/subdiscourse/lazzaros-four-keys-to-fun/ —— 这页打开了，但只有归属信息；四个 key 的内容**只看到搜索摘要**
- [K6] A Trait Model and Scale of Game Playing Preferences。Tondello、Arrambide、Ribeiro、Cen、Nacke，2019。大学新闻稿 https://uwaterloo.ca/computer-science/news/researchers-create-player-trait-model-allowing-personalized —— 新闻稿**打开读过**；论文 PDF 下载了但工具读不出文字
- [K7] Player Experience of Need Satisfaction (PENS)。Ryan、Rigby、Przybylski，2006。https://selfdeterminationtheory.org/player-experience-of-needs-satisfaction-pens/ —— **打开读过**（页面很短）
- [K52] Designing Prototype Player Personas from a Game Preference Survey（CHI 2020，作者没记下）。https://pure.psu.edu/en/publications/designing-prototype-player-personas-from-a-game-preference-survey/ —— **只看到搜索摘要**

**AI / 自动化代理当测试玩家**
- [K8] Automated Playtesting with Procedural Personas through MCTS with Evolved Heuristics。Holmgård、Green、Liapis、Togelius，2018（期刊版 2019）。https://arxiv.org/abs/1802.06881 —— **打开读过摘要页**；代理名字来自搜索摘要
- [K9] Automated Video Game Testing Using Synthetic and Humanlike Agents。Arıyürek、Betin-Can、Sürer，2019（期刊版 2021）。https://ar5iv.labs.arxiv.org/html/1906.00317 —— **打开读过**（前 10 万字符）
- [K10] Artificial Players in the Design Process（PathOS）。Stahlke、Nova、Mirza-Babaei，2020。https://dblp.uni-trier.de/rec/conf/chiplay/StahlkeNM20.html —— **只看到搜索摘要**；内容经 K11 转述
- [K11] MIMIC: Integrating Diverse Personality Traits for Better Game Testing Using Large Language Model。Yifei Chen、Sarra Habchi、Lili Wei，2025。https://arxiv.org/html/2510.01635v1 —— **打开读过**
- [K12] Large Language Models are Pretty Good Zero-Shot Video Game Bug Detectors。Taesiri、Macklon、Wang、Shen、Bezemer，2022。https://arxiv.org/abs/2210.02506 —— **打开读过摘要页**
- [K13] LLMs May Not Be Human-Level Players, But They Can Be Testers。Chang Xiao、Brenda Z. Yang，2024。https://arxiv.org/abs/2410.02829 —— **打开读过摘要页**
- [K14] Leveraging LLM Agents for Automated Video Game Testing（TITAN）。Chengjia Wang 等，2025。https://arxiv.org/abs/2509.22170 —— **打开读过摘要页**
- [K15] GBQA: A Game Benchmark for Evaluating LLMs as Quality Assurance Engineers。Shufan Jiang、Chios Chen、Zhiyang Chen，2026。https://arxiv.org/abs/2604.02648 —— **打开读过摘要页**
- [K16] Towards Automated Crowdsourced Testing via Personified-LLM（PersonaTester）。Shengcheng Yu 等，2026。https://arxiv.org/html/2603.24160v1 —— **打开读过**（前 10 万字符）
- [K17] UXAgent: An LLM Agent-Based Usability Testing Framework for Web Design。作者没记下，2025。https://arxiv.org/abs/2502.12561 —— **打开读过摘要页**；"代理走最短路"那句来自搜索摘要
- [K18] Synthetic Users: If, When, and How to Use AI-Generated "Research"。Maria Rosala、Kate Moran（Nielsen Norman Group），2024。https://nngroup.com/articles/synthetic-users/ —— **打开读过**
- [K19] Finding Flawed Fictions: Evaluating Complex Reasoning in Language Models via Plot Hole Detection。Kabir Ahuja、Melanie Sclar、Yulia Tsvetkov，2025。https://arxiv.org/html/2504.11900v3 —— **打开读过**（前 10 万字符）
- [K53] Reducing False Positives in Static Bug Detection with LLMs: An Empirical Study in Industry。作者没记下，2026。https://arxiv.org/abs/2601.18844 —— **只看到搜索摘要**
- [K54] 几篇谈"AI 试玩代理"的业界 / 厂商博客，2025–2026。例：https://saucelabs.com/resources/blog/from-developer-crunch-to-synthetic-players-ai-is-changing-game-testing —— **只看到搜索摘要**；质量低，没引数字

**测试和评审方法**
- [K20] Exploratory Software Testing: Tips, Tricks, Tours, and Techniques to Guide Test Design。James Whittaker，2009。https://www.informit.com/store/exploratory-software-testing-tips-tricks-tours-and-9780132651226 —— **只看到搜索摘要**（书没读）
- [K21] Exploratory Testing Tours（对 Whittaker 巡游的二手整理）。Software Testing Help，作者和年份没记下。https://www.softwaretestinghelp.com/?p=22928 —— **打开读过**
- [K22] Session-based testing。维基百科（方法由 Jonathan Bach、James Bach 于 2000 年提出）。https://en.wikipedia.org/wiki/Session-based_testing —— **打开读过**
- [K23] Cognitive walkthrough。维基百科（方法出自 Wharton 等，1990 年代初；精简版出自 Spencer，2000）。https://en.wikipedia.org/wiki/Cognitive_walkthrough —— **打开读过**；Wharton 和 Spencer 的原文没打开
- [K24] RITE Method。维基百科（方法出自 Medlock、Wixon、Fulton、Terrano、Romero，2002）。https://en.wikipedia.org/wiki/RITE_Method —— **打开读过**
- [K25] Heuristics and Usability Guidelines for the Creation and Evaluation of Fun in Video Games。Melissa Federoff，2002（硕士论文）。没找到原文网址 —— **只看到搜索摘要**
- [K26] HEP：Using Heuristics to Evaluate the Playability of Games。Desurvire、Caplan、Toth，2004。https://hci.rwth-aachen.de/materials/conferences/CHI2004/2p1509.pdf —— PDF 下载了但读不出文字，**只看到搜索摘要**。PLAY：Game Usability Heuristics (PLAY) for Evaluating and Designing Better Games。Desurvire、Wiberg，2009。https://link.springer.com/doi/10.1007/978-3-642-02774-1_60 —— **只看到搜索摘要**（要登录）
- [K27] Heuristic Evaluation for Games: Usability Principles for Video Game Design。Pinelle、Wong、Stach，2008。https://unpaywall.org/10.1145%2F1357054.1357282 —— **只看到搜索摘要**（两个 PDF 链接都是 404）
- [K28] What Went Wrong: A Taxonomy of Video Game Bugs。Lewis、Whitehead、Wardrip-Fruin，2010。https://dblp.uni-trier.de/rec/conf/fdg/LewisWW10.html —— **只看到搜索摘要**；内容经 K29 转述
- [K29] Deriving and Evaluating a Detailed Taxonomy of Game Bugs。Butt、Sherin、Khan、Jilani、Iqbal，2023。https://arxiv.org/html/2311.16645v1 —— **打开读过**（前 10 万字符）
- [K30] We'll Fix It in Post: What Do Bug Fixes in Video Game Update Notes Tell Us?。Truelove、Santana de Almeida、Ahmed，2021。https://ar5iv.labs.arxiv.org/html/2103.03997 —— **打开读过**
- [K31] Players' Perception of Bugs and Glitches in Video Games: An Exploratory Study。Jessica Backus，2025。https://arxiv.org/abs/2504.15408 —— **打开读过摘要页**
- [K32] Compiling Your Story: Using Techniques from Compiler Design to Check Your Narrative。Jon Manning（Secret Lab），GDC 2019。https://gdcvault.com/play/1025981/Compiling-Your-Story-Using-Techniques —— **打开读过**（只有讲座简介，没看讲座本身）
- [K33] Softlock Detection for Super Metroid with Computation Tree Logic。Ross Mawhorter、Adam Smith，2021。没记下可用网址 —— **只看到搜索摘要**
- [K34] 软锁 / 无法通关状态的定义（几个游戏维基和条目）。例：https://www.mariowiki.com/Unwinnable_state 、https://www.giantbomb.com/unwinnable-state/3015-7607 —— **只看到搜索摘要**
- [K35] Video game exploit。维基百科。https://en.wikipedia.org/wiki/Video_game_exploit —— **打开读过**
- [K36] Duping (video games)。维基百科。https://en.wikipedia.org/wiki/Duping_(video_games) —— **打开读过**
- [K37] 谈游戏经济进项 / 出项和漏洞的厂商博客。例：https://bugnet.io/blog/how-to-fix-a-game-economy-exploit —— **只看到搜索摘要**
- [K38] 速通术语（跳关、出界、错误传送、任意代码执行）。例：https://zeldawiki.wiki/wiki/Wrong_Warp —— **只看到搜索摘要**（另一页返回 403）
- [K39] LQA: What Is Game Localization Testing and How to Do It Right。Game Developer 网站，作者和年份没记下。https://www.gamedeveloper.com/audio/lqa-what-is-game-localization-testing-and-how-to-do-it-right —— **打开读过**
- [K40] Game Accessibility Guidelines，基础级。2012 起。https://gameaccessibilityguidelines.com/basic/ —— **打开读过**
- [K41] Xbox Accessibility Guidelines，3.2 版。微软，2023。https://learn.microsoft.com/en-us/gaming/accessibility/guidelines —— 总览页**打开读过**；各条细则**只看到搜索摘要**
- [K42] Top failing test cases（Xbox 认证），3.0 版。微软，2026。https://learn.microsoft.com/gaming/gdk/docs/store/policies/console/console-topfailingtestcases —— **打开读过**
- [K43] Modding Tutorials / Compatibility。RimWorld Wiki，社区编写。https://www.rimworldwiki.com/wiki/Modding_Tutorials/Compatibility —— **打开读过**
- [K44] Modding: Player Guide / Troubleshooting。Stardew Valley Wiki。https://stardewvalleywiki.com/Modding:Player_Guide/Troubleshooting —— **只看到搜索摘要**（返回 403）
- [K45] Ratings Guide。ESRB。https://www.esrb.org/ratings-guide/ —— **打开读过**
- [K46] IARC / PEGI 的说明页。例：https://www.globalratings.com/ratingsguide.aspx 、https://www.pegi.info/what-do-the-labels-mean —— **只看到搜索摘要**
- [K47] Steam Refunds。Valve。https://store.steampowered.com/steam_refunds/ —— **打开读过**
- [K48] An Empirical Study of Game Reviews on the Steam Platform。Lin、Bezemer、Zou、Hassan，2018 / 2019。报道：https://pcgamer.com/steam-study-finds-users-leave-negative-reviews-more-quickly-than-positive-ones —— **只看到搜索摘要**（报道页只读到标题）
- [K49] 谈回归玩家的业界博客。例：https://adriancrook.com/?p=4909 、https://bugnet.io/blog/how-to-design-a-games-onboarding-for-returning-players —— **只看到搜索摘要**（第二个网址打开后是博客目录，没有正文）
- [K50] 谈"主播模式"的文章。例：https://www.digitalmusicnews.com/2020/11/19/games-adapt-streamer-friendly-mode/ —— **只看到搜索摘要**
- [K51] 谈首次体验（FTUE）的业界文章。例：https://create.roblox.com/docs/production/game-design/onboarding 、https://gameanalytics.com/blog/tips-for-a-great-first-time-user-experience-ftue-in-f2p-games —— **只看到搜索摘要**

---

## 四、提示词和准确度（`method\调研_提示词和准确度.md` 用的，编号 T）

"读法"一栏：
- **原文** = 我读到了页面原文。
- **转述** = 打开了页面，但我读到的是抓取工具对正文的转述，不是逐字原文。
- **摘要页** = 只打开了 arXiv 的摘要页（经转述），没读全文。
- **搜索摘要** = 没打开，只看到搜索结果里的介绍。

**Anthropic 文档和文章**

- **T1** Prompting best practices。Anthropic（Claude 平台文档）。页面无年份，2026-11 读取。https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices 。**原文**。
- **T2** Prompting Claude Fable 5.2。Anthropic（Claude 平台文档）。2026-11 读取。https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2 。**原文**。
- **T3** Reduce hallucinations。Anthropic（Claude 平台文档）。https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations 。**原文**。
- **T4** Increase output consistency。Anthropic（Claude 平台文档）。https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency 。**原文**。
- **T5** 成功标准和评测（develop-tests 页；页面标题我没记下）。Anthropic（Claude 平台文档）。https://platform.claude.com/docs/en/test-and-evaluate/develop-tests 。前半**转述**；"Grade your evaluations"一节读了**原文**的几行（三种打分法、模型打分的三条建议）。
- **T6** Create custom subagents（子代理文档）。Anthropic（Claude Code 文档）。https://code.claude.com/docs/en/sub-agents 。**转述**；页面最后约七分之一没读到。
- **T7** Run Claude Code programmatically（无界面模式）。Anthropic（Claude Code 文档）。https://code.claude.com/docs/en/headless 。**原文**。
- **T8** Best practices for Claude Code。Anthropic（Claude Code 文档）。https://code.claude.com/docs/en/best-practices 。**原文**，只读了几节：给一个能跑的检查、对照规格审查、子代理的代价、可以不再做的事。
- **T9** Code Review（托管的代码审查）。Anthropic（Claude Code 文档）。https://code.claude.com/docs/en/code-review 。**原文**。
- **T10** Review locally with /code-review。Anthropic（Claude Code 文档）。https://code.claude.com/docs/en/code-review-local 。**原文**。
- **T11** Building effective agents。Anthropic 工程博客。2024。https://www.anthropic.com/engineering/building-effective-agents 。**转述**。
- **T12** How we built our multi-agent research system。Anthropic 工程博客。2025。https://www.anthropic.com/engineering/multi-agent-research-system 。**转述**。
- **T13** Effective context engineering for AI agents。Anthropic 工程博客。2025。https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents 。**转述**。
- **T14** Writing effective tools for AI agents。Anthropic 工程博客。2025。https://www.anthropic.com/engineering/writing-tools-for-agents 。**转述**。
- **T15** Demystifying evals for AI agents。Anthropic 工程博客。2026（年份没在页面上核对）。https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents 。**转述**。
- **T16** Harness design for long-running application development。Anthropic 工程博客。2026（年份没在页面上核对）。https://www.anthropic.com/engineering/harness-design-long-running-apps 。**转述**。
- **T17** Effective harnesses for long-running agents。Anthropic 工程博客。2025。https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents 。**转述**。
- **T18** A statistical approach to model evaluations。Anthropic。2024。https://www.anthropic.com/research/statistical-approach-to-model-evals 。**转述**。
- **T19** claude-code-security-review（说明页，和其中的 `security-review.md` 审查提示）。Anthropic（GitHub）。2025。https://github.com/anthropics/claude-code-security-review 。**转述**（两页都打开了）。
- **T20** Code Review for Claude Code（发布文章）。Anthropic。2026-03-09。https://claude.com/blog/code-review 。**转述**。数字是厂商自己报的。
- **T21** 用模型找零日漏洞的文章（zero-days）。Anthropic Frontier Red Team。2026-02-05。https://www.anthropic.com/research/zero-days 。**转述**。

**角色和模拟**

- **T22** When "A Helpful Assistant" Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models。Zheng、Pei、Logeswaran、Lee、Jurgens。2023（EMNLP 2024 Findings）。https://arxiv.org/abs/2311.10054 。**摘要页**。
- **T23** Better Zero-Shot Reasoning with Role-Play Prompting。Kong 等。2023（NAACL 2024）。https://arxiv.org/abs/2308.07702 。**摘要页**。
- **T24** Bias Runs Deep: Implicit Reasoning Biases in Persona-Assigned LLMs。Gupta 等。2023（ICLR 2024）。https://arxiv.org/abs/2311.04892 。**摘要页**。
- **T25** Persona is a Double-edged Sword: Mitigating the Negative Impact of Role-playing Prompts in Zero-shot Reasoning Tasks。Kim、Yang、Jung。2024。https://arxiv.org/abs/2408.08631 。**摘要页**。
- **T26** Prompting Science Report 4: Playing Pretend: Expert Personas Don't Improve Factual Accuracy。Basil、Shapiro、Shapiro、Mollick、Mollick、Meincke（Wharton Generative AI Labs）。2025。https://arxiv.org/abs/2512.05858 。**摘要页**。
- **T27** Large language models that replace human participants can harmfully misportray and flatten identity groups。Wang、Morgenstern、Dickerson。2024（Nature Machine Intelligence）。https://arxiv.org/abs/2402.01908 。**摘要页**。
- **T28** LLM Agents Grounded in Self-Reports Enable General-Purpose Simulation of Individuals（早期版本题为 Generative Agent Simulations of 1,000 People）。Park 等。2024。https://arxiv.org/abs/2411.10109 。**摘要页**。
- **T29** CoMPosT: Characterizing and Evaluating Caricature in LLM Simulations。Cheng、Piccardi、Yang。2023（EMNLP）。https://arxiv.org/abs/2310.11501 。**摘要页**。
- **T30** The Story Shapes the Agent: Narrative Priors in LLM Behavior。Wang、Lester、Srivastava。2026（COLM 2026）。https://arxiv.org/abs/2607.18566 。**摘要页**。
- **T31** Impatient Users Confuse AI Agents: High-fidelity Simulations of Human Traits for Testing Agents。作者没记下。2025。https://arxiv.org/abs/2510.04491 。**搜索摘要**。

**找 bug 和代码审查**

- **T32** How I used o3 to find CVE-2025-37899, a remote zeroday vulnerability in the Linux kernel's SMB implementation。Sean Heelan（个人博客）。2025。https://sean.heelan.io/2025/05/22/how-i-used-o3-to-find-cve-2025-37899-a-remote-zeroday-vulnerability-in-the-linux-kernels-smb-implementation/ 。**转述**。
- **T33** Finding vulnerabilities in modern web apps using Claude Code and OpenAI Codex。Semgrep。2025。https://semgrep.dev/blog/2025/finding-vulnerabilities-in-modern-web-apps-using-claude-code-and-openai-codex/ 。**转述**。
- **T34** Building a better Bugbot（文章标题以页面为准）。Cursor。2026。https://cursor.com/blog/building-bugbot 。**转述**。数字是厂商自己报的。
- **T35** Project Naptime: Evaluating Offensive Security Capabilities of Large Language Models。Google Project Zero。2024。https://projectzero.google/2024/06/project-naptime.html 。**转述**。
- **T36** The Hitchhiker's Guide to Program Analysis: A Journey with Large Language Models（LLift）。Li、Hao、Zhai、Qian。2023。https://arxiv.org/abs/2308.00245 。**摘要页**。
- **T37** IRIS: LLM-Assisted Static Analysis for Detecting Security Vulnerabilities。Li、Dutta、Naik。2024。https://arxiv.org/abs/2405.17238 。**摘要页**。
- **T38** RepoAudit: An Autonomous LLM-Agent for Repository-Level Code Auditing。Guo、Wang、Xu、Su、Zhang。2025。https://arxiv.org/abs/2501.18160 。**摘要页**。
- **T39** LLMs Cannot Reliably Identify and Reason About Security Vulnerabilities (Yet?)。Ullah 等。2023（IEEE S&P 2024）。https://arxiv.org/abs/2312.12575 。**摘要页**。
- **T40** Reducing False Positives in Static Bug Detection with LLMs: An Empirical Study in Industry。Du 等（复旦大学、腾讯）。2026（ICSE 2026 SEIP）。https://arxiv.org/abs/2601.18844 。**摘要页**；"少样本最好"一句只来自**搜索摘要**。上一轮的 K53 可能是同一篇。
- **T41** Benchmarking and Studying the LLM-based Code Review（SWR-Bench）。作者没记下。2025。https://arxiv.org/abs/2509.01494 。**转述**（打开了全文页）。
- **T42** Is Agentic Code Review Helpful? Mining Developers' Feedback to CodeRabbit Reviews in the Wild。Lin、Liang、Thongtanunam、Tantithamthavorn。2026。https://arxiv.org/abs/2607.03316 。**摘要页**。
- **T43** Refute-or-Promote: An Adversarial Stage-Gated Multi-Agent Review Methodology for High-Precision LLM-Assisted Defect Discovery。Agarwal。2026。https://arxiv.org/abs/2604.19049 。**转述**（打开了全文页）。单人工作，没有独立复核。
- **T44** Refuted by Default: Dragos' Methodology for AI-Driven Vulnerability Detection in OT Security Software。Dragos（Garrett Bladow）。2026。https://www.dragos.com/blog/ai-vulnerability-detection-ot-security-methodology 。**转述**。从业者文章。
- **T45** Chain-of-Verification Reduces Hallucination in Large Language Models。Dhuliawala 等。2023。https://arxiv.org/abs/2309.11495 。**摘要页**。
- **T46** Large Language Models Cannot Self-Correct Reasoning Yet。Huang 等。2023（ICLR 2024）。https://arxiv.org/abs/2310.01798 。**摘要页**。

**多代理**

- **T47** Why Do Multi-Agent LLM Systems Fail?。Cemri 等。2025。https://arxiv.org/abs/2503.13657 。**摘要页**。
- **T48** Don't Build Multi-Agents。Cognition（Walden Yan）。2025。https://cognition.com/blog/dont-build-multi-agents 。**转述**。
- **T49** Towards a Science of Scaling Agent Systems。Kim 等。2025。https://arxiv.org/abs/2512.08296 。**摘要页**。
- **T50** Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models?。Choi、Zhu、Li。2025。https://arxiv.org/abs/2508.17536 。**摘要页**。

**长上下文**

- **T51** Lost in the Middle: How Language Models Use Long Contexts。Liu 等。2023。https://arxiv.org/abs/2307.03172 。**摘要页**。
- **T52** Context Rot: How Increasing Input Tokens Impacts LLM Performance。Hong、Troynikov、Huber（Chroma）。2025。https://www.trychroma.com/research/context-rot 。**转述**。
- **T53** Repository map（文档页）。Aider。无年份。https://aider.chat/docs/repomap.html 。**转述**。

**输出质量**

- **T54** Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs。Xiong 等。2023（ICLR 2024）。https://arxiv.org/abs/2306.13063 。**摘要页**。
- **T55** Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models。Tam 等。2024。https://arxiv.org/abs/2408.02442 。**摘要页**。

**评测**

- **T56** 讲怎么做"模型当评判"的指南（Critique Shadowing；页面标题我没记下）。Hamel Husain（个人博客）。年份没核对。https://hamel.dev/blog/posts/llm-judge/ 。**转述**。
- **T57** Mutation-Guided LLM-based Test Generation at Meta。Foster 等（Meta）。2025。https://arxiv.org/abs/2501.12862 。**摘要页**。
- **T58** How we built a real-world benchmark for AI code review。Qodo。2026。https://qodo.ai/blog/how-we-built-a-real-world-benchmark-for-ai-code-review 。**转述**。厂商自己做的基准，自己排第一，结论要打折。

---

## 五、玩家画像搜集（`method\调研_画像搜集.md` 和画像库 32–98 用的，编号 P）

"打开读过" = 用工具把网页取回来，工具给我的是这一页的摘要，不是逐字原文。"只看到搜索摘要" = 只看到搜索结果里的几句话，网页没打开或打不开。年份拿不准的写了"没核对"。

| 编号 | 标题 | 作者 / 机构 | 年份 | 网址 | 读到什么程度 |
|---|---|---|---|---|---|
| P1 | Player segments based on gaming motivations（九个玩家分群） | Quantic Foundry，登在 Game Developer | 2020 | https://www.gamedeveloper.com/business/player-segments-based-on-gaming-motivations | 打开读过。官网的同名页打不开（403）。 |
| P2 | A Model of Player Motivations（网游玩家动机的十个小项） | Nick Yee（The Daedalus Project） | 约 2005，没核对 | https://nickyee.com/daedalus/archives/print/001298.php | 打开读过 |
| P3 | Vorthos and Mel（卡牌玩家的几种心理画像） | Wizards of the Coast，Making Magic 专栏 | 2015 | https://magic.wizards.com/en/news/making-magic/vorthos-and-mel-2015-08-31 | 打开读过 |
| P4 | Newzoo 的玩家分群（八个画像的版本），二手报道 | Newzoo；报道见 Gamepressure | 2019 | https://www.gamepressure.com/newsroom/newzoo-analysts-have-divided-gamers-into-archetypes/zdb5f | 打开读过二手报道。Newzoo 原报告没打开；后来九个画像的版本只看到搜索摘要。 |
| P5 | MIMIC-Py 项目主页（里面有 PathOS 七个特质的定义表） | MIMIC 项目组 | 没核对 | https://mimic-persona.github.io/MIMIC-Py-Home-Page | 打开读过。PathOS 原论文没打开。 |
| P6 | Player motivations & archetypes（十二个动机、八个原型） | GameRefinery | 2020 | https://gamerefinery.com/gamerefinery-player-motivations-archetypes | 打开读过，但完整名单在图片里读不到；八个原型的名字来自搜索摘要，定义只读到三个。 |
| P7 | Water Finds a Crack（专栏） | Soren Johnson，Game Developer 杂志专栏，转载于 Designer Notes | 2011 | https://www.designer-notes.com/game-developer-column-17-water-finds-a-crack/ | 打开读过 |
| P8 | Player Modeling using Self-Organization in Tomb Raider: Underworld | Drachen、Canossa、Yannakakis | 2009 | https://www.um.edu.mt/library/oar/handle/123456789/22900 | 只看到搜索摘要（PDF 解不开）。摘要说从 1365 名通关玩家的行为数据里分出四类；四类的名字这次没核对到，文中没用。 |
| P9 | Digital Game Dynamics Preferences and Player Types | Vahlo、Kaakinen、Holm、Koponen | 2017 | https://research.utu.fi/converis/portal/detail/Publication/19221828?lang=en_GB | 只看到搜索摘要（五类玩法偏好、七种玩家类型；类型名没核对到，文中没用）。 |
| P10 | Inclusive 101 Guidebook（Persona Spectrum：永久的、临时的、情境的） | Microsoft Inclusive Design | 没核对 | https://inclusive.microsoft.design/articles/inclusive-101-guidebook | 打开读过（网页版只举了"一只手"这一行的例子） |
| P11 | Accessible Player Experiences：Access Patterns / Challenge Patterns | AbleGamers | 没核对 | https://accessible.games/accessible-player-experiences/access-patterns/ | 打开读过（做法的名字齐全；说明只读到三条） |
| P12 | Game Accessibility Guidelines：Full list | Game Accessibility Guidelines 项目组 | 2012 起，持续更新 | https://gameaccessibilityguidelines.com/full-list/ | 打开读过 |
| P13 | Xbox Accessibility Guidelines 总页（3.2 版） | Microsoft | 2023 | https://learn.microsoft.com/en-us/gaming/accessibility/guidelines | 打开读过 |
| P14 | Xbox Accessibility Guideline 109：Objective clarity | Microsoft | 2023 | https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/109 | 打开读过 |
| P15 | Xbox Accessibility Guideline 117：Visual distractions and motion settings | Microsoft | 2023 | https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/117 | 打开读过 |
| P16 | Xbox Accessibility Guideline 118：Photosensitivity | Microsoft | 2023 | https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/118 | 只看到搜索摘要 |
| P17 | From Checklists to Playability：把一家无障碍评测站的评测对到 GAG 上 | DiGRA 数字图书馆论文 | 约 2025–2026，没核对 | https://dl.digra.org/index.php/dl/article/view/2833 | 打开读过摘要页（只有摘要，正文没读） |
| P18 | Steam Deck and Steam Machine Compatibility Review Process | Valve，Steamworks 文档 | 持续更新 | https://partner.steamgames.com/doc/steamdeck/compat | 打开读过 |
| P19 | Certified Tester Game Testing（CT-GaMe）简介页 | ISTQB | 2022（大纲 1.0.1） | https://istqb.org/certifications/certified-tester-game-testing-ct-game/ | 打开读过简介页（只有章节名）。大纲 PDF 解不开。考试加时那条只看到搜索摘要。 |
| P20 | Types of Game Testing Techniques | QAwerk（测试公司博客） | 没核对 | https://qawerk.com/blog/types-of-game-testing-techniques/ | 打开读过 |
| P21 | QA branching dialogue and quest logic | PulseGeek（文章） | 没核对 | https://pulsegeek.com/articles/qa-branching-dialogue-and-quest-logic | 打开读过。直接引用的那一句出自这里。 |
| P22 | 叙事方向的测试岗位招聘启事（多条） | 测试外包公司的招聘页 | 没核对 | https://swooped.co/job-postings/qa-analyst-narrative-remote-testronic-12431 | 只看到搜索摘要 |
| P23 | Why sensitivity readers matter – and should be paid properly | The Conversation | 2022 | https://theconversation.com/why-sensitivity-readers-matter-and-should-be-paid-properly-183531 | 打开读过（讲的是出版业，提到游戏） |
| P24 | Sensitivity Reading 服务单页 | AbleGamers | 2022 | https://accessible.games/wp-content/uploads/2022/04/AbleGamers-Sensitivity-Reading-OneSheet.pdf | 只看到搜索摘要 |
| P25 | Games Localization Guide, Part 4: Culturalization（转述 IGDA 的本地化最佳实践） | Andovar（本地化公司博客） | 没核对 | https://blog.andovar.com/games-localization-guide-part-4 | 打开读过。IGDA 原件没打开。 |
| P26 | Localizing into Bidirectional Languages | Allcorrect（本地化公司） | 没核对 | https://allcorrectgames.com/insights/localizing-into-bidirectional-languages/ | 打开读过 |
| P27 | 本地化测试常见缺陷（几篇博客） | Bugnet 等 | 没核对 | https://bugnet.io/blog/game-localization-testing-common-bugs | 只看到搜索摘要（网页取回来是博客目录，不是正文） |
| P28 | Dotted and dotless I in computing | 维基百科 | 持续更新 | https://en.wikipedia.org/wiki/Dotted_and_dotless_I_in_computing | 打开读过 |
| P29 | 某种系统语言下游戏崩溃、存档小数读错的论坛帖和修补工具页（多条） | 玩家论坛、模组站 | 没核对 | https://forums.obsidian.net/topic/81070-localisation-issues-fixed | 只看到搜索摘要 |
| P30 | 输入法相关的缺陷记录（多条） | 几个引擎和游戏的缺陷跟踪站 | 没核对 | https://bugs.mojang.com/browse/MC-91132 | 只看到搜索摘要 |
| P31 | 超宽屏常见问题（几篇厂商和测试博客） | 显示器厂商博客、Bugnet 等 | 没核对 | https://bugnet.io/blog/qa-testing-for-ultrawide-monitor-support | 只看到搜索摘要 |
| P32 | The Skip Button – An Anatomy of Visual Novels | 个人博客 Towards the End Sky | 2024 | https://towardstheendsky.blogspot.com/2024/05/the-skip-button-anatomy-of-visual-novels.html | 打开读过 |
| P33 | 视觉小说该有哪些功能（开发者社区的帖子，多条） | itch.io 等社区 | 没核对 | https://itch.io/blog/689356/polishing-your-release-the-little-features-that-could | 只看到搜索摘要 |
| P34 | 恋爱向游戏的好感门槛和锁线（玩家社区帖子和攻略，多条） | 玩家社区 | 没核对 | 没逐条记网址 | 只看到搜索摘要 |
| P35 | What is a speedrun? | Speed Demos Archive 知识库 | 没核对 | https://kb.speeddemosarchive.com/What_is_a_speedrun%3F | 打开读过 |
| P36 | 速通玩家和开发者的关系（几篇报道） | Kotaku、Game Developer 等 | 没核对 | https://kotaku.com/the-game-developers-who-enable-speedrunners-to-break-th-1848179059 | 只看到搜索摘要 |
| P37 | Self-Imposed Challenge 词条；一篇编辑部问答 | TV Tropes；PC Gamer | 没核对 | https://tvtropes.org/pmwiki/pmwiki.php/Main/SelfImposedChallenge | 只看到搜索摘要。专门的研究没查到。 |
| P38 | A Cheating Mood: The Emotional and Psychological Benefits of Cheating in Single-Player Games | CHI PLAY 论文 | 2020 | 没拿到正式网址（摘要来自图书馆检索页） | 只看到搜索摘要 |
| P39 | Save-Scumming: A Novel Exploration of Video Game Play | DiGRA 扩展摘要 | 2025 | https://dl.digra.org/index.php/dl/article/view/2509 | 打开读过摘要页（没有给出结论，只说在做） |
| P40 | 放置类游戏的研究（一篇学位论文；一篇 2018 年论文的二手转述） | Rensselaer 学位论文；Alharthi 等 | 2025；2018 | https://dspace.rpi.edu/items/64643720-6def-468e-a497-754e607c4941 | 只看到搜索摘要 |
| P41 | Level Up or Game Over: Exploring How Dark Patterns Shape Mobile Games | arXiv 2412.05039 | 2024 | https://arxiv.org/html/2412.05039v1 | 打开读过。它用的分类来自 Zagal 等 2013 年的论文（原文没打开）。 |
| P42 | Compliance of Gacha Probability Disclosure Regulations: a Comparative Study across East Asia | DiGRA 会议论文 | 2026 | https://dl.digra.org/index.php/dl/article/view/2749 | 只看到搜索摘要 |
| P43 | 付费玩家分层（几篇数据公司的文章） | GameAnalytics、devtodev 等 | 没核对 | https://www.devtodev.com/education/articles/en/338/4-simple-methods-of-paying-audience-segmentation | 只看到搜索摘要。数字不引。 |
| P44 | Mobile Gaming Benchmarks | GameAnalytics | 2024 | https://gameindustrylibrary.com/documents/mobile-gaming-benchmarks-2024 | 只看到搜索摘要 |
| P45 | 坏掉的、过期不候的成就（新闻和论坛帖，多条） | 成就社区站、论坛、测试博客 | 没核对 | https://bugnet.io/blog/qa-testing-for-achievement-unlock-conditions | 只看到搜索摘要 |
| P46 | 拆包（datamining）的报道和评论（多条） | 游戏媒体 | 没核对 | https://filmstories.co.uk/features/remnant-2-archon-the-genius-of-hiding-secrets-for-dataminers-to-find/ | 只看到搜索摘要 |
| P47 | 主播模式的词条和官方帮助页（多条） | TV Tropes；几家游戏的帮助页 | 没核对 | https://tvtropes.org/pmwiki/pmwiki.php/Main/StreamerFriendlyMode | 只看到搜索摘要 |
| P48 | 学龄前儿童玩掌机的研究；给儿童做应用的指南 | Game Studies 期刊（2010）；Google 开发者文档 | 2010；没核对 | https://gamestudies.org/1001/articles/bryant_akerman_drell | 只看到搜索摘要（期刊页连不上） |
| P49 | 给五十岁以上的人做手游的设计建议 | JMIR Serious Games | 2021 | https://games.jmir.org/2021/2/e24449 | 只看到搜索摘要（网页取回来是空的） |
| P50 | 不玩游戏的人和"游戏素养"（一篇期刊文章、一篇硕士论文、几篇博客） | Game Studies 期刊；波尔图大学 | 2020；2021 | https://gamestudies.org/2003/articles/schmalzer | 只看到搜索摘要 |
| P51 | Promoting Family Play through Asymmetric Game Design | CSCW 论文 | 2024 | https://techandpeople.github.io/downloads/Promoting_Family_Play_through_Asymmetric_Game_Design.pdf | 只看到搜索摘要 |
| P52 | Define Your Players | gamesuserresearch.com（游戏用户研究从业者的站） | 没核对 | https://gamesuserresearch.com/define-your-players/ | 打开读过 |
| P53 | 色觉障碍玩家的研究和访谈（多条） | Carleton 大学的研究组；设计师访谈 | 2017–2025 | https://chorus.scs.carleton.ca/wp-content/papercite-data/pdf/napoli2018-colourblindgame-chilbw.pdf | 只看到搜索摘要 |
| P54 | 阅读障碍和游戏文字（指南条目、一位开发者的访谈） | Game Accessibility Guidelines；University XP | 2023 | https://universityxp.com/news/2023/4/12/lowtek-on-tackling-dyslexia-in-games | 只看到搜索摘要 |
| P55 | 避免必须长按（指南条目和玩家留言） | Game Accessibility Guidelines | 没核对 | https://gameaccessibilityguidelines.com/avoid-provide-alternatives-to-requiring-buttons-to-be-held-down/ | 只看到搜索摘要 |
| P56 | 生活模拟类玩家自己分的类型（官方论坛的帖子，多条） | 玩家论坛 | 没核对 | https://forums.ea.com/discussions/the-sims-4-general-discussion-en/what-type-of-player-are-you/1290551 | 只看到搜索摘要。没有正式调查。 |
| P57 | 按行为数据给玩家聚类（一场演讲、一篇论文） | Blizzard（GDC Online 2011）；Drachen 等（arXiv 1407.3950，2014） | 2011；2014 | https://gdcvault.com/play/1015152/Data-Mining-and-Machine-Learning | 只看到搜索摘要。文中没直接用。 |
| P58 | ISteamMatchmaking Interface | Valve | 未标，2026 查阅 | https://partner.steamgames.com/doc/api/isteammatchmaking?language=english | 打开过（11-17 核过网址和标题），内容是转述 |
| P59 | Xbox Accessibility Guideline 119: Speech-to-text/text-to-speech chat | Microsoft | 2026 年更新 | https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/119 | 打开过（11-17 核过网址和标题），内容是转述 |
| P60 | Minecraft Realms, Realms Plus, & Realms Pro: Play Together Online | Mojang Studios | 未标，2026 查阅 | https://www.minecraft.net/en-us/realms | 打开过（11-17 核过网址和标题），内容是转述 |
| P61 | Anonymous authentication & linking | Unity Technologies | 未标绝对年份，2026 查阅 | https://docs.unity.com/en-us/authentication/anonymous-auth-and-linking | 打开过（11-17 核过网址和标题），内容是转述 |
| P62 | Shopping Cart and private games - Now out of beta | Valve | 2024 | https://steamcommunity.com/games/593110/announcements/detail/4149575031731807336 | 打开过（11-17 核过网址和标题），内容是转述 |
| P63 | Step by Step: Achievements | Valve | 未标，2026 查阅 | https://partner.steamgames.com/doc/features/achievements/ach_guide | 打开过（11-17 核过网址和标题），内容是转述 |
| P64 | How to cancel an EA Play membership | Electronic Arts | 未标绝对年份，2026 查阅 | https://help.ea.com/en/articles/ea-account/how-to-cancel-ea-play/ | 打开过（11-17 核过网址和标题），内容是转述 |
| P65 | Xbox Accessibility Guideline 106: Screen narration | Microsoft | 2026 年更新 | https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/106 | 打开过（11-17 核过网址和标题），内容是转述 |
| P66 | Publishing from the Creator Portal | Epic Games | 未标，2026 查阅 | https://dev.epicgames.com/documentation/en-us/fortnite/publishing-from-the-creator-portal-in-fortnite-creative | 打开过（11-17 核过网址和标题），内容是转述 |
| P67 | Unpublishing Islands | Epic Games | 未标，2026 查阅 | https://dev.epicgames.com/documentation/en-us/fortnite/unpublishing-islands-in-fortnite-creative | 打开过（11-17 核过网址和标题），内容是转述 |
| P68 | XR-045 XBOX network and Account Privileges | Microsoft | 2023 年规则第 2 版，页面 2025 年更新 | https://learn.microsoft.com/en-us/gaming/gdk/docs/store/policies/xr/xr045?view=gdk-2604 | 打开过（11-17 核过网址和标题），内容是转述 |

P1–P57 共 57 条：打开读过 27 条（其中 P17、P39 只读到摘要页，P19 只读到简介页，P4 是二手报道，P6 的名单在图里）；只看到搜索摘要 30 条。P58–P68 是 11-17 补入的 11 条公开资料。

---

## 六、接哪家的模型（`api\providers.json` 和 `api\run_api_task.ps1` 用的，编号 C）

2026-11-14 核对。地址和模型 id 会变：`api\providers.json` 里每一项都写了出处和核对日期，用之前照出处再看一眼。

| 编号 | 是什么 | 出处 | 读没读过 |
|---|---|---|---|
| C1 | Claude Code 的环境变量：`ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`（比 `ANTHROPIC_API_KEY` 优先）、`ANTHROPIC_MODEL`、各档别名 `ANTHROPIC_DEFAULT_*_MODEL`、`CLAUDE_CODE_SUBAGENT_MODEL`、`API_TIMEOUT_MS`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`；`-p` 模式下设了 `ANTHROPIC_API_KEY` 就一定用它 | https://code.claude.com/docs/en/env-vars 、https://code.claude.com/docs/en/authentication | 打开读过（env-vars 后半部分只看到摘要） |
| C2 | 接网关和第三方：只设 `ANTHROPIC_BASE_URL` 时，存着的 claude.ai 登录还是生效的凭据 | https://code.claude.com/docs/en/llm-gateway 、https://code.claude.com/docs/en/third-party-integrations | 打开读过 |
| C3 | Amazon Bedrock：`CLAUDE_CODE_USE_BEDROCK`、`AWS_REGION`、`AWS_PROFILE`、`AWS_BEARER_TOKEN_BEDROCK` | https://code.claude.com/docs/en/amazon-bedrock | 打开读过（后半部分只看到摘要） |
| C4 | Google Cloud（Vertex）：`CLAUDE_CODE_USE_VERTEX`、`CLOUD_ML_REGION`、`ANTHROPIC_VERTEX_PROJECT_ID`、`GOOGLE_APPLICATION_CREDENTIALS` | https://code.claude.com/docs/en/google-vertex-ai | 打开读过 |
| C5 | Microsoft Foundry：`CLAUDE_CODE_USE_FOUNDRY`、`ANTHROPIC_FOUNDRY_RESOURCE` / `ANTHROPIC_FOUNDRY_BASE_URL`、`ANTHROPIC_FOUNDRY_API_KEY` | https://code.claude.com/docs/en/microsoft-foundry | 打开读过 |
| C6 | Claude Code 显示的花费是照 token 数和标价在本地算的估计 | https://code.claude.com/docs/en/costs | 打开读过 |
| C7 | DeepSeek 的 Anthropic 兼容接口和 Claude Code 配置 | https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code 、https://api-docs.deepseek.com/guides/anthropic_api | 打开读过 |
| C8 | Kimi（月之暗面）的 Claude Code 配置 | https://platform.kimi.com/docs/guide/claude-code-kimi.md | 打开读过 |
| C9 | 智谱 GLM 的 Claude Code 配置 | https://docs.bigmodel.cn/cn/guide/develop/claude | 打开读过 |
| C10 | MiniMax 的 Claude Code 配置 | https://platform.minimax.cn/docs/m-plan/claude-code.md | 打开读过 |
| C11 | 阿里云百炼（通义千问）的 Claude Code 配置 | https://help.aliyun.com/zh/model-studio/claude-code | 打开读过 |
| C12 | OpenRouter 的 Claude Code 配置（只保证 Anthropic 自家的模型） | https://openrouter.ai/docs/cookbook/coding-agents/claude-code-integration.md | 打开读过 |
| C13 | 用网关（LiteLLM 等）让 Claude Code 接 OpenAI、Gemini 这类模型 | 多篇第三方文章，例 https://www.morphllm.com/claude-code-litellm | 只看到搜索摘要 |
| C14 | OpenAI Codex CLI 的无界面模式：`codex exec`、`--json` 的事件（`turn.completed` 里的 token 数）、`-o`、`-s read-only`、`--skip-git-repo-check`、`CODEX_API_KEY`、`CODEX_HOME`；Windows 支持 | https://learn.chatgpt.com/docs/non-interactive-mode 、https://learn.chatgpt.com/docs/developer-commands 、https://learn.chatgpt.com/docs/auth 、https://learn.chatgpt.com/docs/windows/windows-sandbox （原来的 developers.openai.com/codex 跳转到这里） | 打开读过（部分页面后半只看到摘要） |
| C15 | Google Gemini CLI 的无界面模式：`gemini -p`、`-o json`（`response`、`stats`）、退出码、`--approval-mode`、`tools.exclude`、`model.maxSessionTurns`、`GEMINI_API_KEY`、`GEMINI_CLI_HOME`；页面横幅说 2026-06-18 起免费档和 Google One 用户换成了 Antigravity CLI。`GEMINI_CLI_SYSTEM_SETTINGS_PATH` 换掉的是整层系统设置所用的文件，CLI 本身仍有写用户设置的代码 | https://geminicli.com/docs/cli/headless/ 、https://geminicli.com/docs/cli/cli-reference/ 、https://geminicli.com/docs/reference/configuration/ 、https://geminicli.com/docs/get-started/authentication/ 、[设置读写源码](https://github.com/google-gemini/gemini-cli/blob/main/packages/cli/src/config/settings.ts) | 打开读过（configuration 后半只看到摘要；stats 下面每个字段的名字没查到，脚本按名字找） |

2026-11-19 核对。C16–C20 是 `for-ai\INSTALL.md` 对照表的官方资料，供查技能、项目指令和子代理的用法。

| 编号 | 是什么 | 出处 | 读没读过 |
|---|---|---|---|
| C16 | Claude Code 的技能放置和格式、`AGENTS.md` 的版本及配置条件、子代理 | [技能](https://code.claude.com/docs/en/skills)、[项目指令](https://code.claude.com/docs/en/memory)、[子代理](https://code.claude.com/docs/en/sub-agents) | 打开并核对相关段落 |
| C17 | Codex CLI 的技能放置和格式、`AGENTS.md` 发现规则、子代理 | [技能](https://learn.chatgpt.com/docs/build-skills)、[项目指令](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[子代理](https://learn.chatgpt.com/docs/agent-configuration/subagents) | 打开并核对相关段落 |
| C18 | Cursor 的技能放置和格式、项目规则与 CLI 的 `AGENTS.md`、子代理 | [技能](https://cursor.com/docs/skills)、[编辑器规则](https://cursor.com/docs/rules)、[CLI 规则](https://cursor.com/docs/cli/using)、[子代理](https://cursor.com/docs/subagents) | 打开并核对相关段落。CLI 的 `AGENTS.md` 子目录行为没核实 |
| C19 | Gemini CLI 的技能放置和格式、`GEMINI.md` 和 `context.fileName`、本地子代理 | [技能位置](https://geminicli.com/docs/cli/using-agent-skills/)、[技能格式](https://geminicli.com/docs/cli/creating-skills/)、[项目指令](https://geminicli.com/docs/cli/gemini-md/)、[子代理](https://geminicli.com/docs/core/subagents/) | 打开并核对相关段落 |
| C20 | GitHub Copilot CLI 的技能放置和格式、`AGENTS.md` 及子代理的指令继承、委派 | [技能](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)、[项目指令](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)、[子代理](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/invoke-custom-agents)、[CLI 命令参考](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference) | 打开并核对相关段落 |
