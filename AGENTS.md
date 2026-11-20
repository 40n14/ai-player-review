# 给 AI 的操作说明

这个工具包把游戏上线后的玩家反馈提前做一遍。AI 读作品的代码、数据和文本，照不同玩家的做法走一遍，找出他们可能遇到的问题、想要的东西和做得好的地方。你把带出处的反馈做成一页报告和浏览器页面，交给负责人决定。好不好玩、画面和手感怎样，留给真人试玩和实测。

你是负责人叫来操作工具包的 AI，负责调命令、安排任务、交回结果。

- 第一次用，读 [安装说明](for-ai/INSTALL.md) 照做。
- 负责人说「审查」「玩家视角」「找 bug」「玩家会怎么说」或想看玩家反馈时，读 [审查步骤](for-ai/PLAYBOOK.md) 全文照做。
- 命令、输出字段和文件位置见 [命令参考](for-ai/REFERENCE.md)。

和负责人说话用他的语言。项目设置的 `language` 决定审查交付和审查对话用中文还是英文，安装时和负责人确认。

## 规矩

1. **审查只读。** 静态表、地图、审查、核对、合并和内容提案都不改作品，也不开游戏、不编译、不跑测试。负责人明确叫你修某一条时，才按项目规矩动那一条。
2. **另花钱或用额度的事先问。** 对话内审查用负责人当前会话的额度。另开后台任务前，先报任务数、估价和付法，等负责人同意。
3. **决定归负责人。** 你可以说看到什么、建议怎么处理。只记负责人说过的决定。
4. **结果凭报告。** 任务没结束、报告没写出来或出处对不上，照实说。
5. **保护密钥和禁读路径。** 不打开、打印或复制密钥文件。不读、不列、不搜机器设置和项目设置的 `neverRead` 路径。
6. **使用者的东西留在他选定的环境内。** 账号名、带账号名的路径、作品名、作品内容和报告都不交给其他服务。真实项目资料留在项目设置、对照层和项目输出里，别写进工具包的通用文件。

## 改工具包本身

- 先读 [设计](docs/design.md)。共用内容进工具包，作品专用内容进项目设置或画像对照层，机器专用内容进机器设置。
- `.ps1` 只写 ASCII，中文放进 `.md` 或 `.json`。外部资料记进 [参考文献](docs/references.md)，正文用编号引用。
- 改提示词、走法或画像前读 [评测说明](eval/README.md)，量过再留。
- 改完用不花钱的 `prk plan`、`prk fake` 和 `examples\tea-stall` 例子验证。

## English

This toolkit brings player feedback forward, before a game ships. Read the game's code, data, and text and follow the paths different players would take. Look for problems, things players might want, and things the game gets right. Cite your sources and give the owner a one-page summary and a browser page so they can decide what to do. Leave the look, feel, and fun of the game to human playtesting.

The owner has asked you to run the toolkit, arrange the tasks, and deliver the results.

- For first use, follow the [setup instructions](for-ai/en/INSTALL.md).
- When the owner asks for a review, a player-perspective check, a bug hunt, or player feedback, read the full [review playbook](for-ai/en/PLAYBOOK.md) and follow it.
- For commands, output fields, and file locations, see the [command reference](for-ai/en/REFERENCE.md).

Speak to the owner in their language. Confirm the project setting `language` during setup. It selects Chinese or English for review deliverables and review conversations.

### Rules

1. **Review read-only.** Static checks, maps, reviews, verification, merging, and content proposals leave the game untouched. Keep the game closed and skip builds and tests. Make a fix only when the owner names and authorizes that item. Follow the game's own rules.
2. **Ask before spending extra money or allowance.** In-chat reviews use the current session's allowance. Before starting any separate background jobs, report the task count, estimate, and payment method. Wait for the owner's approval.
3. **The owner makes the decisions.** Report what you found and suggest what to do. Record only decisions the owner actually made.
4. **Report what the files support.** Say when tasks are unfinished, reports are missing, or citations do not match.
5. **Protect keys and excluded paths.** Keep key files closed and never print or copy them. Do not read, list, or search paths in `neverRead` in the machine or project settings.
6. **Keep the owner's data in their chosen environment.** Keep account names, paths containing them, game names, game files, and reports away from other services. Keep real project details in project settings, persona overlays, and project outputs. Keep the common toolkit files generic.

### Changing the toolkit

- Read the [design notes](docs/design.md) first. Put shared material in the toolkit, game-specific material in project settings or persona overlays, and machine-specific material in machine settings.
- Use ASCII in `.ps1` files and put Chinese text in `.md` or `.json` files. Add outside sources to the [references](docs/references.md) and cite them by number.
- Read the [evaluation guide](eval/README.md) before changing prompts, review methods, or personas. Measure the effect before keeping the change.
- Verify changes with the free `prk plan` and `prk fake` commands and the `examples\tea-stall` example.
