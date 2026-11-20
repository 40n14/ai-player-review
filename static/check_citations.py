"""引文核验：报告里写的出处，作品里是不是真有（只读，几秒钟，不花钱）。

每份审查报告最后有一节「索引」，一行一处出处：
    编号 | 严重 | 把握 | 文件:行 | 那一行的原文
这个脚本逐行去查：文件在不在、那一行是不是这句原文。它只查"引得对不对"，不查"问题成不成立"。
出处写错、行号编造是最便宜就能抓到的一类错；对不上的条目交给核对的人重点看。

结果：
  对          那一行里有这句原文
  行号偏了    原文在附近几行（写了差几行）
  行号错      原文在这个文件别的地方（写了在第几行）
  找不到原文  这个文件里没有这句话
  找不到文件  路径对不上任何文件
  没法查      这一行索引写得不全（没有行号或没有原文）

用法：python -I check_citations.py [--project 项目设置.json] [--never 路径 ...] [--out 输出.md] <文件夹或报告文件> [更多报告 ...]
  给文件夹：查里面每一份报告（不算 _ 开头的、task_ 开头的、草稿）。
  不写 --out：写到（第一个）文件夹里的 _citations.md。
  路径怎么找：绝对路径；不是的话依次相对于项目文件夹、作品源码、项目设置所在的文件夹、报告所在的文件夹；
  还找不到就在作品源码里按文件名找（只有一个同名文件才算）。
"""
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)   # -I drops the script folder from the path
sys.dont_write_bytecode = True
from report_format import existing_reports, language  # noqa: E402
from projfile import inside, load_project, md_cell, never_read_guard, path_key, walk_files  # noqa: E402

NEAR = 5


def norm(s):
    return re.sub(r'\s+', ' ', s.replace('﻿', '')).strip().strip('`').strip()


def index_rows(report):
    """Rows of the last "索引" section: (id, severity, confidence, file, line or None, quoted text)."""
    with open(report, encoding='utf-8-sig', errors='replace') as f:
        lines = f.read().splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.match(r'^#{1,4}\s*(?:索引|Index\b)', ln.strip(), re.I):
            start = i
    if start is None:
        return None
    rows = []
    for ln in lines[start + 1:]:
        if re.match(r'^#{1,4}\s', ln):
            break
        s = ln.strip()
        if '|' not in s or re.match(r'^[\s|:\-]+$', s):
            continue
        # The quoted line is the last column and can hold "|" itself (code like `a || b`): split off the first
        # four columns only, and drop one table border at each end (only when the row is written as a table).
        if s.startswith('|'):
            s = s[1:]
            if s.endswith('|') and not s.endswith('\\|'):
                s = s[:-1]
        parts = [p.strip() for p in s.split('|', 4)]
        if len(parts) < 4 or parts[0].casefold() in ('编号', '#', 'id'):
            continue
        ident, sev, conf, where = parts[0], parts[1], parts[2], parts[3]
        text = parts[4].replace('\\|', '|') if len(parts) > 4 else ''
        where = where.strip('`').strip()
        m = re.match(r'^(.*?):(\d+)(?:-\d+)?$', where)
        path, line = (m.group(1), int(m.group(2))) if m else (where, None)
        rows.append((ident, sev, conf, path.strip(), line, text))
    return rows


def make_finder(proj, project_path, never_read=None):
    base = os.path.dirname(os.path.abspath(project_path)) if project_path else os.getcwd()
    roots = [r for r in (proj.get('projectRoot'), proj.get('modSource'), base if project_path else None) if r]
    is_blocked = never_read_guard(proj, project_path, never_read)
    by_name = {}

    def names():
        if not by_name:
            for root in (proj.get('modSource'), proj.get('projectRoot')):
                if not root:
                    continue
                for path in walk_files(root, (), is_blocked):
                    real = os.path.realpath(path)
                    if os.path.isfile(real):
                        by_name.setdefault(os.path.basename(path).lower(), set()).add(real)
            by_name.setdefault('', set())
        return by_name

    def resolve(path, report_dir):
        path = path.replace('/', os.sep)
        search_roots = roots + [report_dir]
        allowed = [path_key(os.path.realpath(root)) for root in search_roots]
        candidates = [path] if os.path.isabs(path) else [os.path.join(root, path) for root in search_roots]
        for candidate in candidates:
            if is_blocked(candidate):
                return None, True
            real = os.path.realpath(candidate)
            if any(inside(path_key(real), root) for root in allowed) and os.path.isfile(real):
                return real, False
        if os.path.isabs(path) or '..' in path.split(os.sep):
            return None, False
        hits = names().get(os.path.basename(path).lower(), set())
        tail = path.lower().lstrip('.' + os.sep)
        hits = [h for h in hits if h.lower().endswith(tail)] or list(hits)
        return (hits[0] if len(hits) == 1 else None), False

    def find(path, report_dir, *, with_status=False):
        real, denied = resolve(path, report_dir)
        return (real, denied) if with_status else real

    find.is_blocked = is_blocked
    return find


def check(rows, find, report_dir, cache, lang='zh'):
    out = []
    en = lang == 'en'
    for ident, sev, conf, path, line, text in rows:
        real, denied = find(path, report_dir, with_status=True)
        where = path if line is None else '%s:%d' % (path, line)
        if denied:
            out.append((ident, where, '', 'Protected; skipped' if en else '不许读，没核', ''))
            continue
        want = norm(text)
        if line is None or not want:
            out.append((ident, where, text, 'Cannot check' if en else '没法查',
                        'The index row has no line number or quote' if en else '索引这一行没有行号或没有原文'))
            continue
        if not real:
            out.append((ident, where, text, 'File not found' if en else '找不到文件', ''))
            continue
        if real not in cache:
            with open(real, encoding='utf-8-sig', errors='replace') as f:
                cache[real] = [norm(x) for x in f.read().splitlines()]
        src = cache[real]

        def hit(i):
            return 0 <= i < len(src) and src[i] and (want in src[i] or (len(src[i]) >= 6 and src[i] in want))

        if hit(line - 1):
            out.append((ident, where, text, 'Match' if en else '对', ''))
            continue
        near = [d for d in range(-NEAR, NEAR + 1) if d and hit(line - 1 + d)]
        if near:
            d = min(near, key=abs)
            out.append((ident, where, text, 'Nearby line' if en else '行号偏了',
                        ('Quote found on line %d (%+d)' if en else '原文在第 %d 行（差 %+d）') % (line + d, d)))
            continue
        anywhere = [i + 1 for i in range(len(src)) if hit(i)]
        if anywhere:
            out.append((ident, where, text, 'Wrong line' if en else '行号错',
                        ('Quote found on line(s) %s' if en else '原文在第 %s 行') %
                        (', ' if en else '、').join(str(x) for x in anywhere[:4])))
        else:
            got = src[line - 1] if 0 < line <= len(src) else ('(file has %d lines)' if en else '（文件只有 %d 行）') % len(src)
            out.append((ident, where, text, 'Quote not found' if en else '找不到原文',
                        ('Line %d contains: %s' if en else '第 %d 行实际是：%s') % (line, got[:80])))
    return out


def main():
    args = sys.argv[1:]
    project, out_path, inputs = None, None, []
    never_read = []
    i = 0
    while i < len(args):
        if args[i] == '--project':
            project = args[i + 1]; i += 2
        elif args[i] == '--out':
            out_path = args[i + 1]; i += 2
        elif args[i] == '--never':
            never_read.append(args[i + 1]); i += 2
        else:
            inputs.append(args[i]); i += 1
    if not inputs:
        sys.exit(__doc__.strip())
    proj, project = load_project(project)
    find = make_finder(proj, project, never_read)
    reports, skipped = [], []
    for p in inputs:
        if find.is_blocked(p):
            skipped.append(p)
            continue
        if os.path.isdir(p):
            for rp in existing_reports(p, proj, find.is_blocked):
                (skipped if find.is_blocked(rp) else reports).append(rp)
            out_path = out_path or os.path.join(p, '_citations.md')
        elif os.path.isfile(p):
            reports.append(p)
    if not reports:
        if skipped:
            sys.exit('没有可读的报告：要核的报告或轮次都在不许读的路径里。')
        sys.exit('没有找到要核的报告。')
    if not out_path:
        out_path = os.path.join(os.path.dirname(os.path.abspath(reports[0])), '_citations.md')
    if find.is_blocked(out_path):
        sys.exit('不许写入引文核验表：%s' % out_path)
    lang = language(proj)
    en = lang == 'en'
    cache, total, bad_total = {}, 0, 0
    out = ['# 引文核验', '',
           '脚本逐行查了各报告「索引」里的出处：文件在不在、那一行是不是这句原文。只查引得对不对，不查问题成不成立。',
           '「对」以外的条目，核对时重点看：出处对不上，结论多半也要重查。', '']
    if en:
        out = ['# Citation check', '',
               'Checks whether each report index points to the quoted source text at the stated location.',
               'Investigate mismatches when verifying the findings.', '']
    summary = []
    for rp in skipped + reports:
        name = os.path.basename(rp)
        if rp in skipped or find.is_blocked(rp):
            summary.append('| %s | %s | | |' % (md_cell(name), 'Protected; skipped' if en else '不许读，没核'))
            continue
        rows = index_rows(rp)
        if rows is None:
            summary.append('| `%s` | %s | | |' % (name, 'No Index section' if en else '没有「索引」一节'))
            continue
        res = check(rows, find, os.path.dirname(os.path.abspath(rp)), cache, lang)
        bad = [r for r in res if r[3] != ('Match' if en else '对')]
        total += len(res); bad_total += len(bad)
        summary.append('| `%s` | %d | %d | %s |' % (name, len(res), len(bad), (', ' if en else '、').join(sorted({r[0] for r in bad})) or '—'))
        if bad:
            title = ('## %s (%d unmatched)' if en else '## %s（%d 处对不上）') % (name, len(bad))
            columns = '| ID | Cited location | Quote | Result | Details |' if en else '| 编号 | 报告写的出处 | 报告写的原文 | 结果 | 说明 |'
            out += [title, '', columns, '|---|---|---|---|---|']
            out += ['| %s | `%s` | %s | **%s** | %s |' % (r[0], r[1], md_cell(r[2][:90]), r[3], md_cell(r[4])) for r in bad]
            out.append('')
    heading = '## Summary' if en else '## 汇总'
    columns = '| Report | Citations | Unmatched | Affected IDs |' if en else '| 报告 | 出处共几处 | 对不上几处 | 对不上的条目 |'
    head = [heading, '', columns, '|---|---|---|---|'] + summary + ['']
    out = out[:5] + head + out[5:]
    folder = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(folder, exist_ok=True)
    f = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=folder, delete=False)
    try:
        with f:
            f.write('\n'.join(out) + '\n')
        try:
            os.replace(f.name, out_path)
        except OSError:  # some security software refuses renames in the user's AppData (WinError 17): copy the bytes over
            with open(f.name, 'rb') as a, open(out_path, 'wb') as b:
                b.write(a.read())
    finally:
        if os.path.exists(f.name):
            os.remove(f.name)
    print('citations: %d reports, %d places, %d not matching -> %s' % (len(reports), total, bad_total, out_path))
    print('citations-written')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    main()
