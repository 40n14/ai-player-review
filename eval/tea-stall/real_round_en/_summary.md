# 静态表：先看哪里

生成：2026-11-19 18:13；项目：Tea Stall (a real round)

几张表都是只读文件、按字和正则找出来的线索，不是结论。审查员拿它当地图，每条都回代码和文本里核对。

这次跑的表：`_text_checks.md`（text）、`_image_hits.md`（images）

| 先看 | 是什么 | 标题（条数） |
|---|---|---|
| `_text_checks.md` | 玩家看得见的文字问题，多数一眼能定 | 一、可疑（7 条） |
| `_image_hits.md` | 图大半是透明的：玩家可能点不中、拿不起来（要回代码查游戏按什么判定点中） | 一、可疑：点得到的不到 50%（3 张） |

脚本输出：

- `text`：wrote review_out\20261119_181306\_text_checks.md (7 suspicious: 只在中文 1, 英文漏翻 1, 占位符 1, 露出草稿字样 1, 剧透 1, 说明和设置不符 2; 1 placeholder-section candidates, 2 keys)
- `images`：wrote review_out\20261119_181306\_image_hits.md (5 张图；点得到的不到 50% 的 3 张；没量的 0 张)
