# 真的模型跑出来的一轮（茶摊） · A real round (Tea Stall)

[English](#english)

例子游戏「茶摊」是虚构的小游戏（`examples\tea-stall`）。这一轮不是挑出来的最好结果，是第一次在对话里跑完整一轮的原样输出。

- **谁跑的**：Codex CLI（gpt-6.2-sol，推理高），照 `for-ai\PLAYBOOK.md` 在一场对话里做，没有后台任务。
- **用的设置**：茶摊的评测版（`examples\tea-stall\project.eval.json`：画像对照层不带提示），默认五组（A、B、Q、S、M）+ 作品地图 + 合并。
- **怎么做的**：`prk prepare` 写出 7 份任务文件；一个地图子代理、五个审查员子代理同时做；合并前跑 `prk cite`；合并员又给 16 条主张各派了一个独立核对员（只看主张和原文，不看审查员的推理）。
- **结果**：五组原报 31 条，合并成 18 条（严重 1、中 10、要定 2、想要但没有的 5），同一根源的 13 条并在一起，划掉 0 条。出处全部对得上。
- **打分**（`_score.md`，`eval\score.py` 对着 `answers.json` 粗配）：埋好的 12 个真问题、3 个缺口在合并报告里都找到了；6 个诱饵报了 1 个。**只跑了一次、例子很小、答案表是我们自己设计的、配对很粗**：说明流程走得通、出处是实的，不能当准确率。
- **页面**：`review.html` 是 `prk page` 生成的离线页面（还没记决定的样子）。`review.md` 是一页纸。

这个文件夹在 `eval\` 里：例子项目的 `neverRead` 挡着它，以后有人拿茶摊测试，审查员读不到这里的结论。

## English

Tea Stall is a fictional mini-game (`examples\tea-stall`). This is the unedited output of the first full in-chat round, not a hand-picked best run. The reports are in Chinese; English projects get English reports (see `docs/report-format.md`).

- **Who ran it**: Codex CLI (gpt-6.2-sol, high reasoning), following the playbook (`for-ai/PLAYBOOK.md`) in one chat, with no background jobs.
- **Settings**: the evaluation version of Tea Stall (persona overlay without hints), five default groups (A, B, Q, S, M) plus the work map and the merge.
- **How**: `prk prepare` wrote 7 task files; one map sub-agent and five reviewer sub-agents ran in parallel; `prk cite` ran before the merge; the merger sent 16 claims to independent checkers (claim and source only, no reviewer reasoning).
- **Result**: 31 findings from five groups merged into 18 (1 severe, 10 medium, 2 needing a decision, 5 wanted-but-missing); 13 same-root findings combined; none dismissed. Every citation matched the source.
- **Score** (`_score.md`, rough matching against `answers.json`): all 12 planted issues and all 3 planted gaps found in the merged report; 1 of 6 decoys reported. One run on a small example with an answer key we wrote ourselves: it shows the process works and the citations are real, not an accuracy figure.
- **Page**: `review.html` is the offline page from `prk page` (before any decisions). `review.md` is the one-page summary.

This folder lives under `eval\`, which the example project's `neverRead` blocks, so future reviewers of Tea Stall cannot read these conclusions.
