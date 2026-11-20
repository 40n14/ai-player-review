"""给一轮（或几轮）审查打分：对着答案表，看埋的问题找到了几个、诱饵被报了几次（只读，不花钱）。

为什么要有它：改了提示词、换了模型、加了环节，是变好还是变坏，不量就只能凭感觉。
同一份提示跑几次，找到的东西并不一样，所以**每个配置至少跑三次**，一起打分。

用法：python -I eval\\score.py --answers eval\\tea-stall\\answers.json [--out 输出.md] <一轮的文件夹> [更多轮的文件夹 ...]
  每个文件夹 = 一轮审查的输出（里面是各组的报告和合并报告）。
  读的是每份报告最后的「索引」一节（编号 | 严重 | 把握 | 文件:行 | 原文）。

怎么算「找到了」：一条发现的索引里有一行，文件名和答案对得上，而且那一行的原文里有答案的某个词。
这是粗配：对上了不等于说对了。分数出来以后，人要翻一遍「对不上答案表的」和几条对上的，看是不是真说到了点上。
分两处算：审查员的报告（几份合起来）和最后的合并报告（负责人真正看到的那一份）。
"""
import json
import os
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KIT, 'static'))   # -I drops the script folder from the path
sys.dont_write_bytecode = True
from check_citations import index_rows  # noqa: E402
from report_format import existing_reports, is_merged, named_path  # noqa: E402
from projfile import load_project  # noqa: E402


def hits(entry, rows):
    """Does any index row of one finding point at this answer?"""
    places = [entry] + list(entry.get('also') or [])
    for _id, _sev, _conf, path, _line, text in rows:
        base = os.path.basename(path.replace('\\', '/')).lower()
        for pl in places:
            if base == pl['file'].lower() and any(tok in text for tok in pl['tokens']):
                return True
    return False


def findings_of(report):
    """{finding id: (severity, confidence, rows)} from one report's index section."""
    rows = index_rows(report)
    out = {}
    for r in rows or []:
        out.setdefault(r[0], [r[1], r[2], []])[2].append(r)
    return out, rows is not None


def score_set(reports, answers):
    targets = answers['issues'] + (answers.get('wants') or [])
    found = {a['id']: [] for a in targets}
    decoyed = {d['id']: [] for d in answers.get('decoys') or []}
    unmatched, no_index, sure_wrong, total = [], [], 0, 0
    for rp in reports:
        fs, has_index = findings_of(rp)
        name = os.path.basename(rp)
        if not has_index:
            no_index.append(name)
            continue
        for fid, (_sev, conf, rows) in fs.items():
            total += 1
            # a "want" (W…) is only matched against the wants; everything else against the planted problems
            pool = (answers.get('wants') or []) if fid.upper().startswith('W') else answers['issues']
            got = [a['id'] for a in pool if hits(a, rows)]
            for a in got:
                found[a].append('%s %s' % (name, fid))
            if got:
                continue
            dec = [d for d in answers.get('decoys') or [] if hits(d, rows)]
            dec = [d for d in dec if not (d.get('designOk') and fid.upper().startswith('D'))]
            for d in dec:
                decoyed[d['id']].append('%s %s' % (name, fid))
            if dec and ('确定' in conf or conf.strip('[]').casefold() in ('confirmed', 'definitely missing')):
                sure_wrong += 1
            if not dec:
                unmatched.append('%s %s（%s）' % (name, fid, rows[0][3] if rows else ''))
    return {'found': found, 'decoyed': decoyed, 'unmatched': unmatched, 'no_index': no_index, 'sure_wrong': sure_wrong, 'total': total}


def main():
    args = sys.argv[1:]
    answers_path, out_path, project_path, runs = None, None, None, []
    i = 0
    while i < len(args):
        if args[i] == '--answers':
            answers_path = args[i + 1]; i += 2
        elif args[i] == '--out':
            out_path = args[i + 1]; i += 2
        elif args[i] == '--project':
            project_path = args[i + 1]; i += 2
        else:
            runs.append(args[i]); i += 1
    if not answers_path or not runs:
        sys.exit(__doc__.strip())
    with open(answers_path, encoding='utf-8-sig') as f:
        answers = json.load(f)
    issues, decoys = answers['issues'], answers.get('decoys') or []

    project = load_project(project_path)[0] if project_path else {}
    per_run = []
    for d in runs:
        files = existing_reports(d, project)
        merged = [p for p in files if is_merged(os.path.basename(p), project)]
        primary = named_path(project, d, 'merged')
        final = [primary] if primary in merged else merged[-1:]
        reviewers = [p for p in files if p not in merged]
        per_run.append((os.path.basename(os.path.normpath(d)), score_set(reviewers, answers), score_set(final, answers) if final else None))

    n = len(per_run)
    out = ['# 评测打分', '', '答案表：`%s`（真问题 %d 个，缺口 %d 个，诱饵 %d 个）。一共 %d 轮：%s' % (
        answers_path, len(issues), len(answers.get('wants') or []), len(decoys), n, '、'.join(r[0] for r in per_run)), '',
        '粗配：按「文件名 + 原文里的词」对。对上了不等于说对了，人要抽看。', '']
    for label, idx in (('审查员的报告（几份合起来）', 1), ('最后的合并报告', 2)):
        sets = [r[idx] for r in per_run if r[idx]]
        if not sets:
            out += ['## %s' % label, '', '（没有）', '']
            continue
        out += ['## %s' % label, '', '| 题 | 是什么 | 该由谁找到 | 静态表能抓 | 找到几轮 / %d | 在哪找到的（第一轮） |' % len(sets), '|---|---|---|---|---|---|']
        ever = all_ = 0
        for a in issues:
            k = sum(1 for s in sets if s['found'][a['id']])
            ever += 1 if k else 0
            all_ += 1 if k == len(sets) else 0
            first = next((s['found'][a['id']] for s in sets if s['found'][a['id']]), [])
            out.append('| %s%s | %s | %s | %s | %d | %s |' % (a['id'], '（软）' if a.get('soft') else '', a['what'], '、'.join(a.get('kinds') or []),
                                                          '能' if a.get('static') else '不能', k, '；'.join(first[:3])))
        out += ['', '- 至少一轮找到：**%d / %d**；每一轮都找到：**%d / %d**' % (ever, len(issues), all_, len(issues))]
        wants = answers.get('wants') or []
        if wants:
            w_ever = sum(1 for w in wants if any(s['found'][w['id']] for s in sets))
            out.append('- 埋好的缺口（玩家想要、作品没给的）：至少一轮找到 **%d / %d**（%s）' % (w_ever, len(wants), '、'.join(
                '%s×%d' % (w['id'], sum(1 for s in sets if s['found'][w['id']])) for w in wants)))
        dec_total = sum(len(v) for s in sets for v in s['decoyed'].values())
        out.append('- 诱饵被当成问题报了 **%d** 次（%s）；其中标【确定】的 %d 次' % (
            dec_total, '、'.join('%s×%d' % (d['id'], sum(len(s['decoyed'][d['id']]) for s in sets)) for d in decoys) or '没有诱饵',
            sum(s['sure_wrong'] for s in sets)))
        out.append('- 发现一共 %d 条；对不上答案表的 %d 条（人看：可能是没埋但真的问题，补进答案表；也可能是误报）' % (
            sum(s['total'] for s in sets), sum(len(s['unmatched']) for s in sets)))
        for s, r in zip(sets, [r for r in per_run if r[idx]]):
            if s['unmatched']:
                out.append('  - %s：%s' % (r[0], '；'.join(s['unmatched'][:12])))
            if s['no_index']:
                out.append('  - %s：这几份报告没有「索引」一节，没法打分：%s' % (r[0], '、'.join(s['no_index'])))
        out.append('')
    text = '\n'.join(out) + '\n'
    if out_path:
        with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        print('score written: %s' % out_path)
    else:
        print(text)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    main()
