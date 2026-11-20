"""玩家视角审查用的文字检查表（只读，只写输出的 .md）。只看两个文本表（csv，每行 键,文字）和项目设置，任何项目都能用。

玩家看得见的文字问题：
  可疑（多半要改）：英文漏翻 / 和中文一样 / 空；中英文 {0} 对不上；只在一个 csv 里的键；
                    中英文意思可能不一样（一边有"以前 / 又一次"一边没有、关系词只在一边、一边是问句一边不是、数字不一样）；
                    文字里露出"草稿 / TODO"；剧透词出现在玩家早早就看得到的地方（选项说明、开局弹窗、说明册子……）；
                    藏起来的名字出现在别的台词里；说明里的数字和设置对不上。
  候选清单（不算问题）：csv 注释说是"占位 / 草稿"的段落，和其中几个键在代码 / JSON 里点了名（玩家看不看得到要再核对）。
必需的输入（两个 csv）找不到就报错退出，不会写一张"没有问题"的空表。

词表、哪些键算"早早看得到"、要核对的数字，都在项目设置的 "static" 一节（见 projects\\_template.json），脚本里只有默认值。

用法：python -I review_text_checks.py [--project 项目设置.json] [--prefix 键前缀_,键前缀_] [输出.md]
  不写输出 = 项目设置的 staticOutDir\\text_checks.md。
"""
import json
import os
import re
import sys
from collections import OrderedDict, defaultdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # -I drops the script folder from the path
sys.dont_write_bytecode = True
from projfile import (LITERAL, get_field, load_jsonc, load_project, machine_never_read, md_cell, need_path,
                      need_project_paths, never_read_guard, walk_files)  # noqa: E402


DEFAULTS = {
    'historyWords': {
        'zhStrong': ['上次', '上回', '上周', '又', '老样子', '以前', '那天', '好久', '这周也', '每回', '照旧', '跟往常'],
        'enStrong': ['last time', 'again', 'as usual', 'as always', 'this week too', 'every time', 'the other day',
                     'last week', 'used to', 'back then', 'like before', 'anymore', 'any more'],
        'zhWeak': ['还', '再'],
        'enWeak': ['still', 'before'],
        # only for "one language says it, the other doesn't": words that carry the same idea loosely
        'zhLoose': ['接着', '照常', '回来', '前', '一样', '老', '常', '重新', '也'],
        'enLoose': ['previous', 'back', 'usual', 'same', 'more', 'ago', 'earlier', 'once', 'other day', 'these days',
                    'last', 'old', 'long time', 'too'],
        'asymmetryIgnore': ['anymore', 'any more'],
    },
    'pairedWords': [],
    'draftMarkers': ['草稿', 'DRAFT', 'TODO', 'TBD', 'FIXME', '待改', '（占位）'],
    'draftSectionMarkers': ['占位', '草稿', 'DRAFT', '待改', 'placeholder'],
    'sectionBanner': r'^#\s*=+',
    'spoilers': [],
    'hiddenNameKeys': [],
    'claims': [],
    'ignoreKeys': [],
    # files of the work that may name a text key (for the draft-section list); a project can set its own
    'sourceExts': ['.cs', '.json', '.lua', '.py', '.js', '.ts', '.gd', '.xml', '.yaml', '.yml', '.rpy', '.ink'],
}

CJK = re.compile(r'[㐀-鿿　-〿！-｠]')
LATIN_WORD = re.compile(r'[A-Za-z]{3,}')
PLACEHOLDER = re.compile(r'\{\d+(?::[^}]*)?\}')
ZH_NUM = {'一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
EN_NUM = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
          'eleven': 11, 'twelve': 12, 'twenty': 20, 'thirty': 30, 'hundred': 100, 'twice': 2,
          'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6, 'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10}
ZH_MEASURE = '个天次周针条人碗节张样回年月岁块件瓶桶趟层页把枚只位份顿档卷包盒罐袋家'
ZH_IDIOM_BEFORE = '这前那头过'      # 这两天 / 前两天 / 过两天 = "these days", "the other day": not a count


def load_csv_full(path):
    """key -> (text, line no.), and the comment that heads each key: key -> (comment line, text of the nearest
    comment above, text of the banner it sits under). Quotes around a value are removed for checking."""
    d, heads = OrderedDict(), {}
    need_path(path, ' csv')          # a wrong path stops here instead of reading as "no problems"
    last_comment, banner = (0, ''), (0, '')
    with open(path, encoding='utf-8-sig') as f:
        for no, line in enumerate(f, 1):
            line = line.rstrip('\r\n')
            s = line.strip()
            if not s:
                last_comment = (0, '')      # a comment heads the keys right below it, up to a blank line
                continue
            if s.startswith('#'):
                last_comment = (no, s)
                if re.match(DEFAULTS['sectionBanner'], s):
                    banner = (no, s)
                continue
            if ',' not in line:
                continue
            k, v = line.split(',', 1)
            v = v.strip()
            if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
                v = v[1:-1].replace('""', '"')
            d[k.strip()] = (v, no)
            heads[k.strip()] = (last_comment, banner)
    return d, heads


def short(s, n):
    s = s.replace('\\n', ' / ')
    return s if len(s) <= n else s[:n - 1] + '…'


def has_word(text, word, en):
    if en:
        return re.search(r'(?<![A-Za-z])%s(?![A-Za-z])' % re.escape(word), text, re.I) is not None
    return word in text


def numbers(text, en):
    """Numbers a player would read (1 is left out: 一个 / a / one say nothing)."""
    t = PLACEHOLDER.sub(' ', text)
    out = [int(x) for x in re.findall(r'(?<![0-9A-Za-z.])(\d+)(?![0-9A-Za-z]|\.\d)', t)]
    if en:
        for w, n in EN_NUM.items():
            out += [n] * len(re.findall(r'(?<![A-Za-z])%s(?![A-Za-z])' % w, t, re.I))
    else:
        for m in re.finditer(r'(第?)([一二两三四五六七八九十]{1,3})(?=[%s])' % ZH_MEASURE, t):
            s = m.group(2)
            if s == '两' and m.start() > 0 and t[m.start() - 1] in ZH_IDIOM_BEFORE and t[m.end():m.end() + 1] == '天':
                continue
            if s == '十':
                n = 10
            elif s.startswith('十'):
                n = 10 + ZH_NUM.get(s[1:], 0)
            elif s.endswith('十'):
                n = ZH_NUM.get(s[0], 0) * 10
            elif '十' in s:
                a, b = s.split('十', 1)
                n = ZH_NUM.get(a, 0) * 10 + ZH_NUM.get(b, 0)
            else:
                n = ZH_NUM.get(s[-1], 0)
            # 一两天 / 三五天: a range, not two numbers the English has to repeat
            if len(s) == 2 and '十' not in s:
                continue
            out.append(n)
    return sorted(x for x in out if x != 1)


def json_path(obj, path):
    for part in path.split('.'):
        if isinstance(obj, dict) and part in obj:
            obj = obj[part]
        else:
            return None
    return obj


def to_number(s):
    s = s.strip().lower()
    if s.isdigit():
        return int(s)
    if s in ZH_NUM:
        return ZH_NUM[s]
    if s in EN_NUM:
        return EN_NUM[s]
    if s in ('one', 'a', 'an'):
        return 1
    return None


def main():
    args = sys.argv[1:]
    project, prefix_filter, out_path = None, None, None
    i = 0
    while i < len(args):
        if args[i] == '--project':
            project = args[i + 1]; i += 2
        elif args[i] == '--prefix':
            prefix_filter = tuple(x.strip() for x in args[i + 1].split(',') if x.strip()); i += 2
        else:
            out_path = args[i]; i += 1
    proj, project = load_project(project)
    is_blocked = never_read_guard(proj, project, machine_never_read())
    cfg = dict(DEFAULTS)
    cfg.update(proj.get('static') or {})
    hw = dict(DEFAULTS['historyWords'])
    hw.update({k: v for k, v in (cfg.get('historyWords') or {}).items() if not k.startswith('_')})
    DEFAULTS['sectionBanner'] = cfg.get('sectionBanner', DEFAULTS['sectionBanner'])
    if not out_path:
        out_path = os.path.join(proj['staticOutDir'], 'text_checks.md')
    text_fields = ['csv.zh', 'csv.en']
    if any(get_field(proj, name) and is_blocked(get_field(proj, name)) for name in text_fields):
        sys.exit('必需的文字表在禁读范围内，这张表没生成。')
    need_project_paths(proj, text_fields)

    zh, zh_heads = load_csv_full(proj['csv']['zh'])
    en, _ = load_csv_full(proj['csv']['en'])
    ignore = [re.compile(p) for p in cfg.get('ignoreKeys') or []]

    def wanted(k):
        if any(p.search(k) for p in ignore):
            return False
        return not prefix_filter or k.startswith(prefix_filter)

    probs = []   # (kind, key, zh text, en text, why, where)

    def add(kind, k, why):
        zt, zl = zh.get(k, ('', 0))
        et, el = en.get(k, ('', 0))
        where = ' '.join(x for x in ('zh:%d' % zl if zl else '', 'en:%d' % el if el else '') if x)
        probs.append([kind, k, short(zt, 60), short(et, 90), why, where])

    keys = [k for k in list(zh) + [x for x in en if x not in zh] if wanted(k)]

    # ---- 1. missing / untranslated
    for k in keys:
        if k in zh and k not in en:
            add('只在中文', k, '英文版会显示键名')
            continue
        if k in en and k not in zh:
            add('只在英文', k, '中文版会显示键名（或英文）')
            continue
        zt, et = zh[k][0], en[k][0]
        if zt.strip() and not et.strip():
            add('英文空', k, '英文是空的')
        elif et.strip() and not zt.strip():
            add('中文空', k, '中文是空的')
        elif CJK.search(et):
            add('英文漏翻', k, '英文里有中文字或中文标点：%s' % ''.join(sorted(set(CJK.findall(et))))[:20])
        elif zt == et and (LATIN_WORD.search(zt) or CJK.search(zt)):
            add('中英一样', k, '两边文字完全一样，多半有一边没翻')
        elif not CJK.search(zt) and len(LATIN_WORD.findall(zt)) >= 2:
            add('中文漏翻', k, '中文里没有中文字')

    both = [k for k in keys if k in zh and k in en]
    # ---- 2. placeholders
    for k in both:
        a, b = sorted(PLACEHOLDER.findall(zh[k][0])), sorted(PLACEHOLDER.findall(en[k][0]))
        if a != b:
            add('占位符', k, '中文 %s，英文 %s' % (' '.join(a) or '无', ' '.join(b) or '无'))

    # ---- 3. meaning drift between the two languages
    for k in both:
        zt, et = zh[k][0], en[k][0]
        # one side says "again / last time", the other has nothing like it (loose words count as "something like it")
        zs = [w for w in hw['zhStrong'] if w in zt]
        es = [w for w in hw['enStrong'] if has_word(et, w, True) and w not in hw.get('asymmetryIgnore', [])]
        z_any = zs or any(w in zt for w in hw.get('zhWeak', []) + hw.get('zhLoose', []))
        e_any = [w for w in hw['enStrong'] + hw.get('enWeak', []) + hw.get('enLoose', []) if has_word(et, w, True)]
        if zs and not e_any:
            add('来过的意思只在一边', k, '中文有「%s」，英文没有这层意思' % '、'.join(zs))
        elif es and not z_any:
            add('来过的意思只在一边', k, '英文有 "%s"，中文没有这层意思' % ', '.join(es))
        for pw in cfg.get('pairedWords') or []:
            zhit = [w for w in pw.get('zh', []) if has_word(zt, w, False)]
            ehit = [w for w in pw.get('en', []) if has_word(et, w, True)]
            if bool(zhit) != bool(ehit):
                add('关系词只在一边', k, '「%s」：%s' % (pw.get('name', ''), ('中文有 %s，英文没有' % '、'.join(zhit)) if zhit
                                                       else ('英文有 %s，中文没有' % ', '.join(ehit))))
        # a question in Chinese that became a statement in English (the other way round is mostly a rhetorical "?")
        zq = zt.count('？') + zt.count('?')
        eq = et.count('?')
        if zq and not eq:
            add('问句只在一边', k, '中文是问句（%d 个问号），英文没有问号' % zq)
        zn, enn = numbers(zt, False), numbers(et, True)
        if zn != enn:
            add('数字不一样', k, '中文 %s，英文 %s' % (zn or '无', enn or '无'))

    # ---- 4. draft markers in the text itself
    for k in keys:
        for side, d in (('中文', zh), ('英文', en)):
            if k in d:
                hit = [m for m in cfg['draftMarkers'] if m.lower() in d[k][0].lower()]
                if hit:
                    add('露出草稿字样', k, '%s里有「%s」，玩家会看到' % (side, '、'.join(hit)))

    # ---- 5. spoilers on things the player sees early
    for sp in cfg.get('spoilers') or []:
        pats = [re.compile(p) for p in sp.get('keys', [])]
        allow = [re.compile(p) for p in sp.get('exceptKeys', [])]
        for k in keys:
            if not any(p.search(k) for p in pats) or any(p.search(k) for p in allow):
                continue
            hit = [w for w in sp.get('words', []) if (k in zh and has_word(zh[k][0], w, False)) or
                   (k in en and has_word(en[k][0], w, True))]
            if hit:
                add('剧透', k, '%s：出现「%s」。%s' % (sp.get('name', ''), '、'.join(hit), sp.get('why', '')))

    # ---- 6. hidden names
    for hk in cfg.get('hiddenNameKeys') or []:
        for side, d, en_side in (('中文', zh, False), ('英文', en, True)):
            name = d.get(hk, ('', 0))[0].strip()
            if len(name) < 2:
                continue
            for k in keys:
                if k != hk and k in d and has_word(d[k][0], name, en_side):
                    add('藏起来的名字', k, '%s里出现「%s」（%s 的文字，设定上不给玩家看）' % (side, name, hk))

    # ---- 7. what the texts claim vs the settings
    claim_rows = []
    for c in cfg.get('claims') or []:
        if c.get('file') and is_blocked(c['file']):
            continue
        try:
            conf, _ = load_jsonc(c['file'])
            want = json_path(conf, c['path'])
        except (OSError, ValueError, KeyError) as e:
            # the settings file itself is unreadable: say so, don't call every sentence wrong
            claim_rows.append([c.get('name', ''), '（设置文件读不了）', '', '', '%s：%s' % (c.get('file', '?'), e.__class__.__name__),
                               '**要看**：项目设置 static.claims 的 file 路径'])
            continue
        if want is None:
            claim_rows.append([c.get('name', ''), '（设置里没有这一项）', '', '', '%s 里没有 %s' % (os.path.basename(c['file']), c['path']),
                               '**要看**：static.claims 的 path'])
            continue
        unit = c.get('unit', 1)
        pat_k = re.compile(c.get('keys', '.'))
        for side, d, pat in (('中文', zh, c.get('zh')), ('英文', en, c.get('en'))):
            if not pat:
                continue
            rx = re.compile(pat, re.I)
            for k in keys:
                if not pat_k.search(k) or k not in d:
                    continue
                for m in rx.finditer(d[k][0]):
                    n = to_number(m.group('n'))
                    said = n * unit if n is not None else None
                    ok = want is not None and said == want
                    claim_rows.append([c.get('name', ''), k, side, m.group(0), '%s=%s' % (c['path'], want), '对' if ok else '**不对**'])
                    if not ok:
                        add('说明和设置不符', k, '%s：%s说「%s」，设置 %s = %s（%s）' % (
                            c.get('name', ''), side, m.group(0), c['path'], want, os.path.basename(c['file'])))
        if not any(r[0] == c.get('name', '') for r in claim_rows):
            claim_rows.append([c.get('name', ''), '（没找到这句话）', '', '', '%s=%s' % (c['path'], want), '要看：文字改了，正则要跟着改'])

    # ---- 8. candidates: csv comments that say "placeholder / draft" (a file name that happens to hold the word
    # is not a draft, and a comment alone doesn't prove the player sees the lines)
    sect = OrderedDict()
    marks = [m.lower() for m in cfg['draftSectionMarkers']]
    final_marks = [m.lower() for m in cfg.get('finalMarkers', ['定稿', 'final'])]
    file_name = re.compile(r'[^\s，。、；：（）()「」]+\.(?:txt|md|csv|json|docx?|png)', re.I)

    def says_draft(text):
        """'draft', 'mixed' (the comment also says part of it is final), or None."""
        t = file_name.sub(' ', text).lower()
        if not any(m in t for m in marks):
            return None
        return 'mixed' if any(m in t for m in final_marks) else 'draft'

    mixed = set()
    for k in zh:
        if not wanted(k):
            continue
        (cno, ctext), (bno, btext) = zh_heads.get(k, ((0, ''), (0, '')))
        head = None
        for no_, text_ in ((cno, ctext), (bno, btext)):
            v = says_draft(text_) if text_ else None
            if v:
                head = (no_, text_)
                if v == 'mixed':
                    mixed.add(head)
                break
        if head:
            sect.setdefault(head, []).append(k)
    # how many of those keys anything in the mod names (literal in .cs / .json; keys built in code are missed)
    used_lits = set()
    src_root = proj.get('modSource')
    if sect and src_root:
        exts = tuple(cfg.get('sourceExts') or DEFAULTS['sourceExts'])
        for p in walk_files(src_root, exts, is_blocked):
            try:
                with open(p, encoding='utf-8-sig', errors='replace') as f:
                    used_lits |= set(LITERAL.findall(f.read()))
            except OSError:
                pass

    # ---------- write
    out = []
    w = out.append
    w('# 文字检查（玩家视角审查用）')
    w('')
    w('生成：%s；项目：%s；脚本：`%s`%s' % (datetime.now().strftime('%Y-%m-%d %H:%M'), proj.get('name', ''),
                                         os.path.abspath(__file__), '；只看前缀 ' + ', '.join(prefix_filter) if prefix_filter else ''))
    w('')
    w('只读两个 csv 和项目设置的 static 一节。"可疑"是玩家会看到的文字问题，多数一眼能定；"意思可能不一样"那几类是提示，要人对着读。')
    w('行号：zh:N = zh.csv 第 N 行，en:N = en.csv 第 N 行。')
    w('')
    order = ['只在中文', '只在英文', '英文空', '中文空', '英文漏翻', '中文漏翻', '中英一样', '占位符', '露出草稿字样', '剧透',
             '藏起来的名字', '说明和设置不符', '关系词只在一边', '来过的意思只在一边', '问句只在一边', '数字不一样']
    probs.sort(key=lambda r: (order.index(r[0]) if r[0] in order else 99, r[5]))
    by_kind = defaultdict(int)
    for r in probs:
        by_kind[r[0]] += 1
    w('## 一、可疑（%d 条）' % len(probs))
    w('')
    if by_kind:
        w('分类：' + '；'.join('%s %d' % (k, by_kind[k]) for k in order if by_kind.get(k)))
        w('')
        w('| 类 | 键 | 中文 | 英文 | 为什么 | 行 |')
        w('|---|---|---|---|---|---|')
        for r in probs:
            w('| ' + ' | '.join(md_cell(x) for x in r) + ' |')
    else:
        w('没有。')
    w('')
    w('## 二、说明里的数字（和设置对照）')
    w('')
    if claim_rows:
        w('| 说的什么 | 键 | 语言 | 原文 | 设置 | 对不对 |')
        w('|---|---|---|---|---|---|')
        for r in claim_rows:
            w('| ' + ' | '.join(md_cell(x) for x in r) + ' |')
    else:
        w('没有可核对的说明（static.claims）。')
    w('')
    n_draft = sum(len(v) for v in sect.values())
    n_named = sum(1 for v in sect.values() for k in v if k in used_lits or k.split('@')[0] in used_lits)
    w('## 三、候选清单：csv 注释说是"占位 / 草稿"的段落（%d 段，%d 个键，其中 %d 个在代码 / JSON 里点了名；不算问题）' % (len(sect), n_draft, n_named))
    w('')
    w('只是**候选**：注释说是占位，不等于玩家这一版会看到。按 csv 注释算：一行注释管它下面连着的键（到下一行注释或空行为止），`# ====` 横幅管到下一个横幅，可能多算几个。'
      '注释里的文件名（如 `某某草稿.txt`）不算；同一行注释里也写了"定稿"的标「部分定稿」（例：前两句定稿、最后一句是草稿）。"点了名" = 作品源码里有这个键的字面量（代码里拼出来的键数不到）；'
      '玩家看不看得到，还要看那段代码走不走得到（审查员去核对）。发布前给负责人看的清单。')
    w('')
    if sect:
        w('| zh.csv 行 | 段落说明 | 键数 | 点了名的 | 键（前几个） |')
        w('|---|---|---|---|---|')
        for (no, text), ks in sect.items():
            named = sum(1 for k in ks if k in used_lits or k.split('@')[0] in used_lits)
            w('| %d | %s%s | %d | %d | %s |' % (no, '「部分定稿」' if (no, text) in mixed else '', md_cell(short(text.lstrip('# '), 70)), len(ks), named,
                                            md_cell(', '.join(ks[:6]) + ('……' if len(ks) > 6 else ''))))
    else:
        w('没有。')
    w('')
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    print('wrote %s (%d suspicious: %s; %d placeholder-section candidates, %d keys)' % (
        out_path, len(probs), ', '.join('%s %d' % (k, by_kind[k]) for k in order if by_kind.get(k)) or '-', len(sect), n_draft))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    main()
