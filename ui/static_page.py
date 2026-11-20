"""Build the standalone review documents from one round without starting the UI service."""

import hashlib
import json
import os
import re
import shutil
import subprocess
import webbrowser
from collections import Counter
from html import escape, unescape
from pathlib import Path
from string import Template
from urllib.parse import quote


LABELS = {'S': '严重', 'M': '中', 'L': '轻', 'D': '要你定的', 'W': '想要但没有的'}
BUTTONS = ('要修', '以后再说', '本来就这样', '不是问题', 'AI 看错了')
BUTTONS_EN = ('Fix', 'Later', 'By design', 'Not an issue', 'AI got it wrong')


ENGLISH = {
    '玩家视角审查': 'Player review',
    '切换浅色': 'Switch to light',
    '切换深色': 'Switch to dark',
    '在这里点好，复制给你的 AI，它会记下来。': 'Choose your decisions, then copy them to your AI to record.',
    '一页纸': 'Review summary',
    '结论': 'Conclusion',
    '最要紧的问题': 'Top findings',
    '待定': 'Pending',
    '花费': 'Cost',
    '出处核对': 'Citation check',
    '报告': 'Reports',
    '玩家说了什么': 'Player feedback',
    '要处理的问题': 'Issues to review',
    '严重程度': 'Severity',
    '全部': 'All',
    '决定': 'Decision',
    '已定': 'Decided',
    '没有符合条件的问题。': 'No issues match these filters.',
    '想要但没有的': 'Wanted but missing',
    '没有符合条件的条目。': 'No entries match these filters.',
    '文件': 'Files',
    '浏览器没能自动复制，请选中下面的文字复制。': 'Automatic copying failed. Select and copy the text below.',
    '收起复制框': 'Close copy box',
    '已选 0 条': '0 selected',
    '复制给 AI': 'Copy for AI',
    '严重': 'Severe',
    '中': 'Medium',
    '轻': 'Minor',
    '要你定的': 'Needs your decision',
    '原因（可不填）': 'Reason (optional)',
    '还没修的': 'Open fixes',
    '修好等确认的': 'Fixed and awaiting verification',
    '待修清单': 'Fix list',
    '还没有玩家反馈。': 'No player feedback yet.',
    '还没有结论。': 'No conclusion yet.',
    '还没有问题条目。': 'No findings yet.',
    '还没有这类反馈。': 'No missing options reported.',
    '上一轮反馈的去向': 'Follow-up on last round',
    '示范检查': 'Sample review',
    '检查 · ': 'Review · ',
    '这次检查': 'Review',
    '没核成': 'Check unavailable',
    '没有发现缺失的报告': 'No missing reports',
    '打开离线页面': 'Open the offline page',
}


def word(text, lang):
    return ENGLISH.get(text, text) if lang == 'en' else text


def label_text(lang):
    return {kind: word(label, lang) for kind, label in LABELS.items()}


def pending_line(count, lang):
    return '%d awaiting your decision' % count if lang == 'en' else '%d 条等你定' % count


def read_text(path):
    return Path(path).read_text(encoding='utf-8-sig', errors='replace')


def link(m):
    """[text](target) from already-escaped text. Only a relative file in this round's folder (or below) becomes a
    link; anything else (a scheme, an absolute path, '..') stays plain text."""
    label, target = m[1], unescape(m[2])
    path = target.split('#', 1)[0]
    if (not path or re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', target) or target.startswith(('/', '\\'))
            or '..' in re.split(r'[\\/]', path)):
        return label
    return '<a href="%s">%s</a>' % (escape(quote(target.replace('\\', '/'), safe='/#'), quote=True), label)


def inline(text):
    safe = escape(text)
    safe = re.sub(r'`([^`]+)`|\*\*(.+?)\*\*',
                  lambda m: '<code>%s</code>' % m[1] if m[1] else '<strong>%s</strong>' % m[2], safe)
    return re.sub(r'\[([^\]\n]+)\]\(([^)\s]+)\)', link, safe)


def table_html(lines):
    """A pipe table: header row, a |---| row, body rows. Cells go through inline() like any other text."""
    def cells(line):
        return [c.strip() for c in re.split(r'(?<!\\)\|', line.strip().strip('|'))]
    head = ''.join('<th>%s</th>' % inline(c) for c in cells(lines[0]))
    body = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in cells(line)) for line in lines[2:])
    return '<div class="table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (head, body)


def paragraph_html(paragraph):
    lines = [re.sub(r'^#{1,6}\s+', '', line) for line in paragraph.splitlines()]
    if (len(lines) >= 2 and all(l.lstrip().startswith('|') for l in lines)
            and re.match(r'^\s*\|?\s*:?-{3,}', lines[1])):
        return table_html(lines)
    if all(re.match(r'^\s*[-*]\s+', l) for l in lines):
        return '<ul>%s</ul>' % ''.join('<li>%s</li>' % inline(re.sub(r'^\s*[-*]\s+', '', l)) for l in lines)
    if all(re.match(r'^\s*\d+[.)]\s+', l) for l in lines):
        return '<ol>%s</ol>' % ''.join('<li>%s</li>' % inline(re.sub(r'^\s*\d+[.)]\s+', '', l)) for l in lines)
    return '<p>%s</p>' % '<br>'.join(inline(l) for l in lines)


def formatted(text):
    """Render just the report formatting we use: paragraphs, bold, code, fenced blocks, pipe tables, lists and
    links to files in the same round. All source text is escaped before adding markup."""
    blocks = []
    for i, part in enumerate(re.split(r'(?m)^```[^\n]*\n?', text)):
        if i % 2:
            blocks.append('<pre>%s</pre>' % escape(part.rstrip()))
            continue
        for paragraph in re.split(r'\n\s*\n', part.strip()):
            if paragraph:
                blocks.append(paragraph_html(paragraph))
    return '<div class="prose">%s</div>' % ''.join(blocks)


def md_text(text):
    return re.sub(r'([\\`*{}\[\]()#+!_|])', r'\\\1', escape(text, quote=False))


def relative(folder, path):
    return os.path.relpath(path, folder).replace(os.sep, '/')


def checked_path(prk, folder, name):
    path = os.path.join(folder, name)
    if not prk.round_member(folder, path):
        raise ValueError('输出路径不在页面文件夹里：%s' % name)
    return path


def markdown_files(prk, folder, never):
    for root, dirs, files in os.walk(folder):
        dirs[:] = sorted(n for n in dirs if prk.round_member(folder, os.path.join(root, n))
                         and not prk.protected_path(os.path.join(root, n), never)
                         and os.path.normcase(os.path.join(root, n)) == os.path.normcase(os.path.realpath(os.path.join(root, n))))
        for name in sorted(files):
            path = os.path.join(root, name)
            if (name.lower().endswith('.md') and prk.round_member(folder, path)
                    and not prk.protected_path(path, never) and os.path.isfile(path)):
                yield relative(folder, path)


def citation_result(prk, ctx, folder, dest, reports):
    if not reports:
        return None
    out = checked_path(prk, dest, '_citations.md')
    try:
        result = subprocess.run(prk.cite_cmd(ctx, folder, out=out, reports=reports), capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if not prk.cite_written(result, out):
        return None
    totals = re.search(rb'^citations: \d+ reports, \d+ places, (\d+) not matching -> ', result.stdout, re.M)
    return int(totals[1]) if totals else None


def task_output(prk, proj, folder, task):
    """Get the intended output for a task in the older background runner's cost table."""
    taskfile = os.path.join(folder, 'task_' + task + '.md')
    if prk.output_written(folder, taskfile):
        match = re.search(r'(?m)^- (?:合并报告|报告|地图)写到[：:]\s*([^\r\n]+)', read_text(taskfile))
        if match:
            path = re.split(r'（(?:合并说明里|这是总览文件)', match[1], maxsplit=1)[0].strip()
            return next((os.path.join(folder, name) for name in prk.report_aliases(proj, os.path.basename(path))
                         if prk.output_written(folder, os.path.join(folder, name))), path)
    names = proj.get('reportNames') or {}
    if task == 'map':
        return os.path.join(folder, '_map', '_map.md')
    if task == 'merge':
        return prk.named_path(proj, folder, 'merged')
    if task.startswith('merge_'):
        pattern = prk.names(proj, 'groupMerged')[0]
        name = pattern.format(task[6:])
        return next((os.path.join(folder, n) for n in prk.report_aliases(proj, name)
                     if prk.output_written(folder, os.path.join(folder, n))), os.path.join(folder, name))
    group = prk.names(proj, 'group')[0]
    for part in proj.get('characterSplits') or ():
        suffix = '_' + part['id']
        if task.endswith(suffix):
            pattern = names.get('split') or group.replace('{0}', '{0}_{1}')
            label = part['id'] if prk.language(proj) == 'en' and not (names.get('split') or names.get('group')) else part['name']
            name = pattern.format(task[:-len(suffix)], label)
            break
    else:
        name = group.format(task)
    return next((os.path.join(folder, n) for n in prk.report_aliases(proj, name)
                 if prk.output_written(folder, os.path.join(folder, n))), os.path.join(folder, name))


def missing_reports(prk, proj, folder, never):
    tasks = prk.prepared_tasks(folder, never)
    if tasks is not None:
        paths = [task['writes'] for task in tasks if not prk.task_written(proj, folder, task, never)]
    else:
        cost = prk.named_path(proj, folder, 'cost')
        paths = []
        if prk.output_written(folder, cost) and not prk.protected_path(cost, never):
            for line in read_text(cost).splitlines():
                cells = [cell.strip() for cell in line.strip('|').split('|')]
                if not line.startswith('|') or len(cells) != 7:
                    continue
                log = re.fullmatch(r'log_(.+)\.txt', cells[-1])
                if log:
                    taskfile = os.path.join(folder, 'task_' + log[1] + '.md')
                    if os.path.basename(taskfile) != 'task_' + log[1] + '.md' or prk.protected_path(taskfile, never):
                        continue
                    path = task_output(prk, proj, folder, log[1])
                    if cells[2] not in ('写了', 'Written') or not prk.output_written(folder, path):
                        paths.append(path)
    return list(dict.fromkeys(relative(folder, p) for p in paths if prk.round_member(folder, p)))


def cost_text(prk, ctx, rid, sample):
    en = prk.language(ctx['proj']) == 'en'
    ledger = prk.ledger_mod()
    rows = [] if sample else [r for r in ledger.read_ledger(prk.ledger_file(ctx)) if r.get('轮次') == rid]
    if not rows:
        return 'No separate costs recorded for this round' if en else '这一轮是在对话里跑的，没有单独记账'
    totals = ledger.month_usage(rows, '')  # rows are already limited to this round
    amounts = []
    if totals['tasks']:
        money = [('USD', totals['usd'])] if totals['usd'] or not totals['other'] else []
        money += sorted(totals['other'].items())
        label, separator = ('Usage charges ', ', ') if en else ('按次付费 ', '、')
        amounts.append(label + separator.join('%s %.4f' % item for item in money))
    if totals['subTasks']:
        if en:
            amounts.append('Subscription: %d tasks, %s tokens' % (totals['subTasks'], format(totals['subTokens'], ',')))
        else:
            amounts.append('会员额度 %d 个任务，用了 %s token' % (totals['subTasks'], prk.wan(totals['subTokens'])))
    return (', ' if en else '；').join(amounts)


def page_entries(prk, proj, reports, sample):
    lang = prk.language(proj)
    decisions = prk.decisions_by_entry(proj, sample)
    entries = prk.decision_entries(reports)
    counts = Counter(e['id'] for e in entries)
    for i, entry in enumerate(entries, 1):
        key = (prk.report_identity(proj, entry['report']), entry['id'])
        entry['decision'] = prk.decision_word(decisions.get(key, {}).get('决定', ''), lang)
        entry['why'] = decisions.get(key, {}).get('一句原因', '')
        entry['anchor'] = 'issue-%d' % i
        entry['duplicate'] = counts[entry['id']] > 1
    return entries


def player_cards(data, entries, lang):
    anchors = {(os.path.basename(e['report']), e['id']): e['anchor'] for e in entries}
    players = {}
    for row in data['feedback']:
        lines = players.setdefault(row['player'], [])
        for remark in row['says']:
            refs = []
            for ident in dict.fromkeys(remark['refs']):
                anchor = anchors.get((row['report'], ident))
                if anchor:
                    refs.append('<a class="tag" href="#%s">%s</a>' % (anchor, escape(ident)))
            kind = '<strong>%s</strong>　' % inline(remark['kind']) if remark['kind'] else ''
            lines.append('<li>%s%s %s</li>' % (kind, inline(remark['text']), ' '.join(refs)))
    if not players:
        return formatted(data['feedbackMarkdown']) if data['feedbackMarkdown'] else empty_text('还没有玩家反馈。', lang)
    return '<div class="players">%s</div>' % ''.join(
        '<article class="card"><h3>%s</h3><ul>%s</ul></article>' % (inline(name), ''.join(lines))
        for name, lines in players.items())


def issue_card(entry, decisions, lang, labels):
    e = entry
    file_name = os.path.basename(e['report'])
    data = {'id': e['id'], 'report': file_name, 'decision': e['decision'], 'why': e['why'],
            'kind': e['id'][0], 'duplicate': 'yes' if e['duplicate'] else 'no'}
    attrs = ' '.join('data-%s="%s"' % (key, escape(value)) for key, value in data.items())
    buttons = ''.join('<button type="button" data-choice="%s" aria-pressed="%s">%s</button>' %
                      (escape(choice), str(e['decision'] == choice).lower(), label)
                      for choice, label in decisions)
    status = (word('已定', lang) + ' · ' + e['decision']) if e['decision'] else word('待定', lang)
    return ('<details class="issue card" id="{anchor}" {attrs}><summary><span class="tag sev-{kind}">{id} · {label}</span>'
            '<span class="issue-title">{title}</span><span class="muted status">{status}</span></summary>'
            '<div class="detail"><p class="muted">{confidence} {report}</p>{body}'
            '<div class="choices">{buttons}</div><label class="reason">{reason} '
            '<input type="text" value="{why}"></label></div></details>').format(
                anchor=e['anchor'], attrs=attrs, kind=e['id'][0], id=escape(e['id']), label=labels[e['id'][0]], reason=word('原因（可不填）', lang),
                title=inline(e['title']), status=escape(status), confidence=escape(e['confidence']), report=escape(file_name),
                body=formatted(e['body']), buttons=buttons, why=escape(e['why']))


def fix_section(fixes, lang):
    if not fixes:
        return ''
    groups = []
    for done, heading in [(False, '还没修的'), (True, '修好等确认的')]:
        items = [x for x in fixes if bool(x['done']) == done]
        if items:
            groups.append('<h3>%s</h3>' % word(heading, lang))
        for item in items:
            groups.append('<article class="card fix"><span>%s · %s</span>'
                          '<button type="button" data-copy="%s">%s</button></article>' %
                          (escape(item['id']), inline(item['title']), escape(item['copy']), word('复制给 AI', lang)))
    return '<section><h2>%s</h2>%s</section>' % (word('待修清单', lang), ''.join(groups))


def summary_lines(data, result, cost, important):
    lang = result['language']
    counts = ' · '.join('%s %d' % (label, data['counts'][kind]) for kind, label in label_text(lang).items())
    lines = ['# ' + word('这次检查', lang) + ' · ' + md_text(result['round']), '', counts, '',
             '## ' + word('结论', lang), '', md_text(data['conclusion']) or word('还没有结论。', lang),
             '', '## ' + word('最要紧的问题', lang), '']
    lines += (['- [%s](review.html#%s) %s' % (e['id'], e['anchor'], md_text(e['title'])) for e in important]
              or [word('还没有问题条目。', lang)])
    lines += ['', '- ' + pending_line(result['undecided'], lang), '- ' + word('花费', lang) + ' · ' + cost,
              '- ' + word('出处核对', lang) + ' · ' + citations_line(result, lang),
              '- ' + word('报告', lang) + ' · ' + md_text(missing_line(result, lang)),
              '', '[%s](review.html)' % word('打开离线页面', lang), '']
    return '\n'.join(lines)


def citations_line(result, lang):
    bad = result['citationsBad']
    if bad is None:
        return word('没核成', lang)
    return ('%d unmatched' if lang == 'en' else '%d 处对不上') % bad


def missing_line(result, lang):
    if not result['missing']:
        return word('没有发现缺失的报告', lang)
    if lang == 'en':
        return 'Still missing: ' + ', '.join(result['missing'])
    return '还没写出来：' + '、'.join(result['missing'])


def empty_text(text, lang):
    return '<p class="muted">%s</p>' % escape(word(text, lang))


def script_words(lang, decisions):
    en = lang == 'en'
    values = {
        'choices': [choice for choice, _ in decisions],
        'dark': word('切换深色', lang), 'light': word('切换浅色', lang), 'pending': word('待定', lang),
        'decided': word('已定', lang), 'chosen': 'Selected' if en else '已选',
        'picked': '{n} selected' if en else '已选 {n} 条',
        'copied': 'Copied · {n} selected' if en else '已复制 · 已选 {n} 条',
        'reason': ' (reason: {why})' if en else '（原因：{why}）',
        'copyHeading': 'Please record these decisions (round {round}):' if en else '请把这些决定记进决定记录（轮次 {round}）：',
        'copyReport': 'Report: {report} (use --from)' if en else '报告：{report}（请用 --from 指定）',
    }
    return json.dumps(values, ensure_ascii=False).replace('<', r'\u003c')


def render(data, result, entries, fixes, decisions, files, cost, key, sample):
    lang = result['language']
    labels = label_text(lang)
    important = sorted(entries, key=lambda e: 'SMLDW'.index(e['id'][0]))[:5]
    options = ''.join('<option value="%s">%s</option>' % pair for pair in labels.items())
    problems = [issue_card(e, decisions, lang, labels) for e in entries if not e['id'].startswith('W')]
    wants = [issue_card(e, decisions, lang, labels) for e in entries if e['id'].startswith('W')]
    heading = word('示范检查', lang) if sample else word('检查 · ', lang) + result['round']
    html_words = {
        'site_title': '玩家视角审查',
        'light': '切换浅色',
        'intro': '在这里点好，复制给你的 AI，它会记下来。',
        'overview': '一页纸',
        'conclusion': '结论',
        'important': '最要紧的问题',
        'pending': '待定',
        'cost': '花费',
        'citations': '出处核对',
        'reports': '报告',
        'feedback': '玩家说了什么',
        'issues': '要处理的问题',
        'severity': '严重程度',
        'all': '全部',
        'decision': '决定',
        'decided': '已定',
        'no_problems': '没有符合条件的问题。',
        'wants': '想要但没有的',
        'no_wants': '没有符合条件的条目。',
        'files': '文件',
        'copy_fallback': '浏览器没能自动复制，请选中下面的文字复制。',
        'close_copy': '收起复制框',
        'picked': '已选 0 条',
        'copy': '复制给 AI',
    }
    localized = {'label_' + key: escape(word(text, lang)) for key, text in html_words.items()}
    html = Template(read_text(Path(__file__).with_name('page_template.html'))).substitute(
        heading=escape(heading), round_id=escape(result['round']), storage_key=key,
        numbers=''.join('<div class="stat sev-%s"><strong>%d</strong><span>%s</span></div>' % (k, data['counts'][k], v)
                        for k, v in labels.items()),
        conclusion=formatted(data['conclusion']) if data['conclusion'] else empty_text('还没有结论。', lang),
        important='<ol>%s</ol>' % ''.join('<li><a href="#%s">%s · %s</a></li>' %
                                         (e['anchor'], e['id'], inline(e['title'])) for e in important)
                  if important else empty_text('还没有问题条目。', lang),
        lang='en' if lang == 'en' else 'zh-CN', script_words=script_words(lang, decisions),
        undecided=pending_line(result['undecided'], lang), cost=escape(cost), citations=escape(citations_line(result, lang)),
        missing=escape(missing_line(result, lang)), players=player_cards(data, entries, lang), options=options,
        problems=''.join(problems) or empty_text('还没有问题条目。', lang),
        wants=''.join(wants) or empty_text('还没有这类反馈。', lang),
        last_round='<section><h2>%s</h2>%s</section>' % (word('上一轮反馈的去向', lang), formatted(data['lastRound']))
                   if data['lastRound'] else '',
        fixes=fix_section(fixes, lang), **localized,
        files=''.join('<li><a href="./%s">%s</a></li>' % (quote(path, safe='/'), escape(path)) for path in files))
    return html, summary_lines(data, result, cost, important)


def generate(prk, ctx):
    a, proj = ctx['args'], ctx['proj']

    def error(message, code):
        prk.out_json({'ok': False, 'error': message, **prk.output_metadata(proj)}) if prk.want_json(ctx) else prk.say(message)
        return code

    folder, sample = prk.check_round(proj, a.get('round'))
    if not folder:
        if 'round' in a:
            return error('找不到指定的检查轮次。', 2)
        return error('还没有检查或示范轮。', 1)
    machine = tuple(prk.machine_never_read(ctx))
    readable = machine if sample else tuple(proj.get('neverRead') or ()) + machine
    if prk.protected_path(folder, readable):
        return error('这一轮在不许读的路径里。', 2)
    key = hashlib.sha256(os.fsencode(os.path.normcase(folder))).hexdigest()
    rid = os.path.basename(folder)
    dest = os.path.join(prk.STATE_DIR, 'sample_pages', key) if sample else folder
    # Sample data is read-only. Mirror the Markdown into the page's folder so every link stays local.
    try:
        os.makedirs(dest, exist_ok=True)
        result = {'ok': True, 'round': rid, 'dir': dest, 'html': checked_path(prk, dest, 'review.html'),
                  'md': checked_path(prk, dest, 'review.md'), **prk.output_metadata(proj, folder)}
        reports = prk.round_reports(proj, folder, readable)
        data = prk.collect_feedback(dict(ctx, args={'dir': folder}), with_sources=True, never=readable)
        if not data:
            data = dict(counts=dict.fromkeys(LABELS, 0), reports=[], conclusion='', lastRound='', feedback=[], feedbackMarkdown='')
        entries = page_entries(prk, proj, data['reports'], sample)
        files = list(markdown_files(prk, folder, readable))
        if sample:
            for name in files:
                if name in ('review.md', '_citations.md'):
                    continue
                target = checked_path(prk, dest, name)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copyfile(os.path.join(folder, name), target)
            files = [name for name in files if name != '_citations.md']
        result.update(counts=data['counts'], undecided=sum(not e['decision'] for e in entries),
                      missing=missing_reports(prk, proj, folder, readable),
                      citationsBad=citation_result(prk, ctx, folder, dest, reports))
        if result['citationsBad'] is not None and '_citations.md' not in files:
            files.append('_citations.md')
        files = sorted(set(files) | {'review.md'})
        fixes = prk.fix_list(proj, sample)['items']
        cost = cost_text(prk, ctx, rid, sample)
        decisions = tuple(zip(prk.DECISIONS_EN, BUTTONS_EN)) if prk.language(proj) == 'en' else tuple(zip(prk.DECISIONS, BUTTONS))
        result['language'] = prk.language(proj)
        html, md = render(data, result, entries, fixes, decisions, files, cost, key, sample)
        for name, content in [('md', md), ('html', html)]:
            Path(result[name]).write_text(content, encoding='utf-8')
    except (OSError, ValueError, KeyError) as exc:
        return error('页面没写成：%s' % exc, 1)
    if a.get('open'):
        try:
            opened = webbrowser.open(Path(result['html']).as_uri())
        except (OSError, webbrowser.Error):
            opened = False
        if not opened:
            result['openError'] = '浏览器没打开，可以双击 review.html。'
    if prk.want_json(ctx):
        prk.out_json(result)
    else:
        prk.say('页面：%s' % result['html'])
        prk.say('一页纸：%s' % result['md'])
        if result.get('openError'):
            prk.say(result['openError'])
    return 0
