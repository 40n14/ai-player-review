# A real round in English (Tea Stall) · 真跑的一轮（英文项目）

[中文](#中文)

Tea Stall is a fictional mini-game (`examples\tea-stall`). The game's own text is Chinese; the project language was set to English, so everything the assistant delivered is in English. This is the unedited output of the first English round, not a hand-picked best run.

- **Who ran it**: Codex CLI (gpt-6.2-sol, extra-high reasoning), following `for-ai/en/PLAYBOOK.md` in one chat, with no background jobs.
- **Settings**: the evaluation version of Tea Stall (persona overlay without hints) with `"language": "en"`, five default groups (A, B, Q, S, M) plus the work map and the merge.
- **How**: `prk prepare` wrote the task files; the map and five reviewers ran as sub-agents; `prk cite` ran before the merge; the merger sent 15 claims to independent checkers.
- **Result**: 28 findings from five groups merged into 15 (1 severe, 5 medium, 3 minor, 2 needing a decision, 4 wanted-but-missing). Every citation matched the source (222 checked). All report headings are English.
- **Score** (`_score.md`, rough matching against `answers.json`): all 12 planted issues and all 3 planted gaps found in the merged report; 1 of 6 decoys reported. One run on a small example with an answer key we wrote ourselves: it shows the process works in English and the citations are real, not an accuracy figure.
- **Page**: `review.html` is the offline page from `prk page`, before any decisions. `review.md` is the one-page summary.
- **Still in Chinese**: quotes from the game's own text (the game is Chinese), the static tables (`_summary.md`, `_text_checks.md`, `_image_hits.md`: input for the reviewers) and the work map's file names (`_map/`).

This folder lives under `eval\`, which the example project's `neverRead` blocks, so future reviewers of Tea Stall cannot read these conclusions.

## 中文

茶摊是虚构的小游戏。游戏本身的文字是中文，项目语言设成了英文，所以 AI 交出来的东西都是英文。这是第一次英文项目的原样输出，不是挑出来的。

- Codex CLI（gpt-6.2-sol，推理 xhigh）照 `for-ai/en/PLAYBOOK.md` 在一场对话里做，默认五组 + 作品地图 + 合并。
- 五组原报 28 条，合并成 15 条；222 处出处全对上；报告标题全是英文。
- 粗配打分：合并报告 12 个真问题、3 个缺口全找到，6 个诱饵报了 1 个。只跑了一次，不能当准确率。
- 还是中文的：引用的游戏原文、静态表（给审查员读的）、作品地图的文件名。
