"""花费总账：每个任务一行，跨轮次存下来（只用标准库，不调 API，不花钱）。

为什么要有它：每一轮的文件夹里有一张 `_花费.md`，只管那一轮。要回答"这个月一共花了多少""换了模型以后
每个任务贵了多少""哪一类任务最费钱"，得有一张不随轮次走的表。这张表就是：`<项目的 reviewOutDir>\\花费记录.csv`。

每个任务一行：审查、建地图、合并、内容提案、问向导、修（prk fix 派出去改作品的），都记。数从任务的日志里读（启动脚本写的第一行，和
Claude Code 最后给的那一行结果 JSON），不估、不补：日志里没有的就空着。
同一轮重记多少次都一样（按"轮次 + 日志名"更新各行），所以每个任务结束时记一次、整轮结束再记一次都没关系。
假 runner 的日志不记（数字是假的）。

用法：
  python -I cost_ledger.py --project <项目设置.json> <一轮的文件夹> [更多]    把这几轮记进总账
  python -I cost_ledger.py --project <项目设置.json> --rebuild               reviewOutDir 下所有轮次重记一遍（老的轮次也补进来）
  python -I cost_ledger.py --ledger <csv> --round <名字> --log <日志.txt>     只记一个日志（问向导用）
  加 --ledger <csv> 可以把总账写到别处；--local <机器设置> 指定价目表从哪读。

两种钱数：
  CLI估的USD   Claude Code 自己照 Anthropic 的价目算的（官方 API 时和账单一致；接别家的模型时不是账单）。
  按价目表     照机器设置的 prices 算的（每百万 token 的价，各家自己的币种）。没写价目表就空着。
"""
import csv
import errno
import json
import os
import re
import sys
import tempfile
import time
from contextlib import contextmanager

if os.name == 'nt':
    import msvcrt
else:
    import fcntl

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'static'))   # -I drops the script folder from the path
sys.dont_write_bytecode = True

from report_format import language, named_path, names  # noqa: E402

LEDGER_NAME = '花费记录.csv'
HEAD = ['开始时间', '轮次', '任务', '类别', '提供方', '模型', '谁付的', 'CLI估的USD', '按价目表', '币种', '步数', '用时秒',
        '输入token', '输出token', '缓存写token', '缓存读token', '结果', '日志']
HEAD_EN = ['Start time', 'Round', 'Task', 'Kind', 'Provider', 'Model', 'Paid by', 'CLI estimate (USD)',
           'At listed prices', 'Currency', 'Turns', 'Duration (s)', 'Input tokens', 'Output tokens',
           'Cache write tokens', 'Cache read tokens', 'Result', 'Log']
VALUE_EN = {
    '轮次': {'修': 'Fix', '向导': 'Guide'},
    '类别': {'作品地图': 'Map', '合并': 'Merge', '内容提案': 'Content proposal', '向导': 'Guide', '修': 'Fix', '审查': 'Review'},
    '提供方': {'订阅': 'Subscription'},
    '谁付的': {'订阅': 'Subscription', '服务商的账号': 'Provider account', '假 runner': 'Fake runner',
             '没写（旧记录）': 'Unknown (legacy record)'},
    '结果': {'成': 'Succeeded', '有花费，结果不明': 'Charged, result unknown', '失败（没有新报告）': 'Failed (no new report)',
           '失败（登录过期）': 'Failed (sign-in expired)', '失败（余额不够）': 'Failed (insufficient credit)'},
}
RESULT_PATTERNS = (
    ('失败（退出码 %s）', 'Failed (exit code %s)'),
    ('失败（API 报错%s）', 'Failed (API error%s)'),
    ('失败（%s）', 'Failed (%s)'),
    ('没有结果（退出码 %s）', 'No result (exit code %s)'),
)
OLD_NAMES = {'花费USD': 'CLI估的USD', **dict(zip(HEAD_EN, HEAD))}     # ledgers written before the columns were renamed
PAID = {'api key': 'API key', 'subscription login': '订阅', 'provider account': '服务商的账号'}


def task_kind(name):
    n = name.lower()
    if n.startswith('map'):
        return '作品地图'
    if n.startswith('merge'):
        return '合并'
    if n.startswith('expand'):
        return '内容提案'
    if n.startswith('guide'):
        return '向导'
    if n.startswith('fix'):
        return '修'
    return '审查'


def loose_result(line):
    """The result line as far as it can be read when it is not valid JSON (older runs wrote the CLI's output through
    a console code page, and the answer text inside it can break the JSON). Top-level number and word fields only;
    (?<!\\) skips the same names inside an escaped string."""
    def field(name, pat):
        m = re.search(r'(?<!\\)"' + name + r'"\s*:\s*(' + pat + ')', line)
        return m.group(1) if m else None
    cost = field('total_cost_usd', r'[\d.eE+-]+')
    if cost is None:
        return None
    out = {'total_cost_usd': float(cost)}
    for name in ('num_turns', 'duration_ms'):
        v = field(name, r'\d+')
        if v is not None:
            out[name] = int(v)
    v = field('is_error', r'true|false')
    if v is not None:
        out['is_error'] = v == 'true'
    v = field('subtype', r'"[a-z_]+"')
    if v is not None:
        out['subtype'] = v.strip('"')
    v = field('api_error_status', r'\d+')
    if v is not None:
        out['api_error_status'] = int(v)
    usage = {}
    for name in ('input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'):
        v = field(name, r'\d+')         # the first one is the run's total (usage comes before the per-model table)
        if v is not None:
            usage[name] = int(v)
    if usage:
        out['usage'] = usage
    return out


def price_of(prices, model, provider, u):
    """(amount, currency) from the price table, or ('', ''). Prices are per million tokens:
    { "<model id>" or "<provider>/<model id>": { "currency": "CNY", "input": 2, "output": 8, "cacheWrite": 2, "cacheRead": 0.5 } }.
    A cache price that is not given is charged as input."""
    if not prices:
        return '', ''
    p = prices.get('%s/%s' % (provider, model)) or prices.get(model) or prices.get(re.sub(r'\[[^\]]*\]$', '', model or ''))
    if not isinstance(p, dict):
        return '', ''
    def n(k):
        try:
            return float(u.get(k) or 0)
        except (TypeError, ValueError):
            return 0.0
    inp = float(p.get('input') or 0)
    amount = (n('input_tokens') * inp + n('output_tokens') * float(p.get('output') or 0) +
              n('cache_creation_input_tokens') * float(p.get('cacheWrite', inp) or 0) +
              n('cache_read_input_tokens') * float(p.get('cacheRead', inp) or 0)) / 1e6
    return '%.4f' % amount, str(p.get('currency') or 'USD')


def parse_log(path, prices=None):
    """One row (a dict keyed by HEAD) from one task log, or None when the log is a fake runner's or the task has not
    produced anything to record yet. prices: the machine settings' price table (see price_of)."""
    try:
        with open(path, encoding='utf-8-sig', errors='replace') as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    if not lines:
        return None
    first = lines[0]
    m = re.match(r'^started (\S+?), model (.+?)(?:, workdir (.*))?$', first)
    if not m:
        return None
    rest = m.group(3) or ''
    if ', readonly ' in rest and not os.environ.get('PLAYER_REVIEW_LEDGER_FAKE'):
        return None                                   # the fake runner's first line: its numbers are made up
    prov = re.search(r', provider (.+)$', rest)
    rest = rest[:prov.start()] if prov else rest
    provider = prov.group(1).strip() if prov else ''
    paid = re.search(r', paid by (.+)$', rest)
    who = PAID.get(paid.group(1).strip(), paid.group(1).strip()) if paid else ('假 runner' if ', readonly ' in rest else '没写（旧记录）')
    if not provider:
        provider = '订阅' if who == '订阅' else ('anthropic' if who in ('API key', '没写（旧记录）') else '')
    res, finished = None, None
    missing_report = 'report status: missing or unchanged' in lines
    for ln in reversed(lines):
        if finished is None:
            f2 = re.match(r'^finished \S+, exit (-?\d+)', ln)
            if f2:
                finished = int(f2.group(1))
        if res is None and ln.lstrip().startswith('{') and '"type"' in ln and '"result"' in ln:
            try:
                res = json.loads(ln)
            except ValueError:
                res = loose_result(ln)
    if res is None and finished is None:
        return None                                   # still running
    name = re.sub(r'^log_', '', os.path.splitext(os.path.basename(path))[0])
    row = {k: '' for k in HEAD}
    row.update({'开始时间': m.group(1).replace('T', ' '), '任务': name, '类别': task_kind(name), '提供方': provider,
                '模型': m.group(2).strip(), '谁付的': who, '日志': os.path.basename(path)})
    if res:
        u = res.get('usage') or {}
        cost = res.get('total_cost_usd')
        row['按价目表'], row['币种'] = price_of(prices, row['模型'], provider, u)
        row.update({'CLI估的USD': '' if cost is None else ('%.4f' % float(cost)),
                    '步数': res.get('num_turns', ''),
                    '用时秒': '' if res.get('duration_ms') is None else int(round(float(res['duration_ms']) / 1000)),
                    '输入token': u.get('input_tokens', ''), '输出token': u.get('output_tokens', ''),
                    '缓存写token': u.get('cache_creation_input_tokens', ''), '缓存读token': u.get('cache_read_input_tokens', '')})
        if 'is_error' in res or 'subtype' in res:
            ok = res.get('is_error') is False and res.get('subtype') == 'success'
            if ok and missing_report:
                row['结果'] = '失败（没有新报告）'
            elif ok and finished not in (0, None):
                row['结果'] = '失败（退出码 %s）' % finished
            elif ok:
                row['结果'] = '成'
            elif res.get('is_error') and res.get('subtype') == 'success':
                # the run ended normally but the API refused a request (credit, auth, quota ...)
                said = str(res.get('result') or '')
                if re.search(r'claude auth login|setup-token|reached its time limit|OAuth token has expired|Please run /login', said, re.I):
                    row['结果'] = '失败（登录过期）'
                elif re.search(r'Credit balance is too low', said, re.I):
                    row['结果'] = '失败（余额不够）'
                else:
                    row['结果'] = '失败（API 报错%s）' % (' %s' % res['api_error_status'] if res.get('api_error_status') else '')
            else:
                row['结果'] = '失败（%s）' % (res.get('subtype') or '?')
        else:
            row['结果'] = '有花费，结果不明'
    else:
        row['结果'] = '没有结果（退出码 %s）' % finished
    return row


def rows_for_round(folder, prices=None):
    out = []
    if not os.path.isdir(folder):
        return out
    rnd = os.path.basename(os.path.normpath(folder))
    rnd = '修' if rnd in names({}, 'fixDir') else rnd               # the fixes' folder (prk fix): recorded as round 修 when they run
    for name in sorted(os.listdir(folder)):
        if name.startswith('log_') and name.endswith('.txt') and not name.endswith(('.err.txt', '.out.txt')):
            r = parse_log(os.path.join(folder, name), prices)
            if r:
                r['轮次'] = rnd
                out.append(r)
    return out


def ledger_value(key, value, english):
    translations = VALUE_EN.get(key, {})
    if not english:
        translations = {en: zh for zh, en in translations.items()}
    if value in translations:
        return translations[value]
    if key == '结果':
        for zh, en in RESULT_PATTERNS:
            old, new = (zh, en) if english else (en, zh)
            match = re.fullmatch(re.escape(old).replace('%s', '(.*)', 1), value)
            if match:
                return new % match[1]
    return value


def read_ledger(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    if not rows:
        return []
    head = [OLD_NAMES.get(h, h) for h in rows[0]]
    return [{k: ledger_value(k, v, False) for k, v in zip(head, r + [''] * (len(head) - len(r)))}
            for r in rows[1:] if r]


def write_ledger(path, rows, lang=None):
    english = (lang == 'en') if lang else os.path.basename(path) == names({'language': 'en'}, 'ledger')[0]
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    rows = sorted(rows, key=lambda r: (r.get('开始时间', ''), r.get('轮次', ''), r.get('任务', '')))
    # Keep the temporary file on the same volume for an atomic replace. The BOM is for spreadsheets.
    file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8-sig', newline='', dir=directory,
                                       prefix=os.path.basename(path) + '.', suffix='.tmp', delete=False)
    try:
        with file:
            w = csv.writer(file)
            w.writerow(HEAD_EN if english else HEAD)
            w.writerows([[ledger_value(k, r.get(k, ''), True) if english else r.get(k, '') for k in HEAD] for r in rows])
        try:
            os.replace(file.name, path)
        except OSError:  # some security software refuses renames in the user's AppData (WinError 17): copy the bytes over
            with open(file.name, 'rb') as a, open(path, 'wb') as b:
                b.write(a.read())
    finally:
        try:
            os.remove(file.name)
        except FileNotFoundError:
            pass


@contextmanager
def ledger_lock(path, timeout=10):
    lock_path = path + '.lock'
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    deadline = time.monotonic() + timeout
    # Keep one lock file so all processes lock the same file. The OS releases abandoned locks
    # when a process dies, so a leftover file cannot block the next writer.
    with open(lock_path, 'a+b', buffering=0) as lock:
        while True:
            try:
                if os.name == 'nt':
                    lock.seek(0)
                    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as e:
                if e.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    raise
                if time.monotonic() >= deadline:
                    raise TimeoutError('Timed out waiting for the cost ledger lock: %s' % lock_path) from e
                time.sleep(0.1)
        yield


def update(path, new_rows, rounds=(), *, lang=None):
    """Put these rows in the ledger. Rows of the named rounds that are no longer in new_rows are dropped (a round is
    always recorded whole); other rows are kept. Returns the number of rows written for them."""
    path = os.path.realpath(path)
    with ledger_lock(path):
        return update_locked(path, new_rows, rounds, lang=lang)


def update_locked(path, new_rows, rounds, *, lang=None):
    rounds = {'修' if r in names({}, 'fixDir') else r for r in rounds}
    keys = {(r['轮次'], r['日志']) for r in new_rows}
    previous = read_ledger(path)
    keep = [r for r in previous if r.get('轮次') not in rounds and (r.get('轮次'), r.get('日志')) not in keys]
    if new_rows or len(keep) != len(previous):
        write_ledger(path, keep + list(new_rows), lang)
    return len(new_rows)


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def is_failed(r):
    return str(r.get('结果') or '').startswith(('失败', '没有结果'))


def summarize(rows):
    """Totals for showing: by provider, by who paid, by model, by kind of task, by day.
    usd = Claude Code's own estimate (list prices of Anthropic's models; for another provider's models it is not the bill).
    priced = sums from the price table, one per currency."""
    def bucket(key):
        out = {}
        for r in rows:
            k = key(r) or '（没写）'
            b = out.setdefault(k, {'tasks': 0, 'usd': 0.0, 'turns': 0, 'failed': 0, 'priced': {}})
            b['tasks'] += 1
            b['usd'] += num(r.get('CLI估的USD'))
            if r.get('按价目表') not in (None, ''):
                cur = r.get('币种') or 'USD'
                b['priced'][cur] = round(b['priced'].get(cur, 0.0) + num(r.get('按价目表')), 4)
            b['turns'] += int(num(r.get('步数')))
            b['failed'] += 1 if is_failed(r) else 0
        return [dict(v, name=k, usd=round(v['usd'], 4)) for k, v in sorted(out.items(), key=lambda kv: -kv[1]['usd'])]
    real = [r for r in rows if r.get('谁付的') != '订阅']
    priced = {}
    for r in real:
        if r.get('按价目表') not in (None, ''):
            cur = r.get('币种') or 'USD'
            priced[cur] = round(priced.get(cur, 0.0) + num(r.get('按价目表')), 4)
    return {'tasks': len(rows), 'usd': round(sum(num(r.get('CLI估的USD')) for r in real), 4), 'priced': priced,
            'usdSubscription': round(sum(num(r.get('CLI估的USD')) for r in rows if r.get('谁付的') == '订阅'), 4),
            'byProvider': bucket(lambda r: r.get('提供方')),
            'failed': len([r for r in rows if is_failed(r)]),
            'byPaid': bucket(lambda r: r.get('谁付的')), 'byModel': bucket(lambda r: r.get('模型')),
            'byKind': bucket(lambda r: r.get('类别')), 'byDay': sorted(bucket(lambda r: (r.get('开始时间') or '')[:10]), key=lambda b: b['name'], reverse=True),
            'byRound': sorted(bucket(lambda r: r.get('轮次')), key=lambda b: b['name'], reverse=True)}


def month_usage(rows, month):
    """One month's use ('YYYY-MM', by 开始时间), for the page's small box and the first line of prk costs.
    usd: paid by use, in US dollars: per task the price table's amount when it is in USD, else Claude Code's own
    estimate (one of the two, never both). other: price-table amounts in other currencies. The subscription side costs
    nothing extra: its tokens (input, output, cache write, cache read added up) and Claude Code's estimate, not charged.
    How much of the plan's quota is left is not known here: only what this kit used."""
    out = {'month': month, 'usd': 0.0, 'other': {}, 'tasks': 0, 'subTasks': 0, 'subTokens': 0, 'subUsd': 0.0}
    for r in rows:
        if not str(r.get('开始时间') or '').startswith(month):
            continue
        if r.get('谁付的') == '订阅':
            out['subTasks'] += 1
            out['subTokens'] += int(sum(num(r.get(k)) for k in ('输入token', '输出token', '缓存写token', '缓存读token')))
            out['subUsd'] += num(r.get('CLI估的USD'))
            continue
        out['tasks'] += 1
        if r.get('按价目表') not in (None, ''):
            cur = r.get('币种') or 'USD'
            if cur == 'USD':
                out['usd'] += num(r.get('按价目表'))
            else:
                out['other'][cur] = round(out['other'].get(cur, 0.0) + num(r.get('按价目表')), 4)
        else:
            out['usd'] += num(r.get('CLI估的USD'))
    out['usd'], out['subUsd'] = round(out['usd'], 4), round(out['subUsd'], 4)
    return out


def load_prices():
    """The price table of the machine settings (prices), or {}."""
    try:
        from projfile import load_local
        return load_local().get('prices') or {}
    except (ImportError, OSError, ValueError):
        return {}


def ledger_path(proj):
    return named_path(proj, proj.get('reviewOutDir') or '.', 'ledger')


def main():
    args = sys.argv[1:]
    project = ledger = rnd = log = None
    rebuild, folders = False, []
    i = 0
    while i < len(args):
        a = args[i]
        if a in ('--project', '--ledger', '--round', '--log', '--local'):
            v = args[i + 1]
            if a == '--local':
                os.environ['PLAYER_REVIEW_LOCAL'] = v
            project, ledger, rnd, log = (v if a == '--project' else project, v if a == '--ledger' else ledger,
                                         v if a == '--round' else rnd, v if a == '--log' else log)
            i += 2
        elif a == '--rebuild':
            rebuild = True
            i += 1
        else:
            folders.append(a)
            i += 1
    proj = None
    if project:
        from projfile import load_project
        proj, _ = load_project(project)
        ledger = ledger or ledger_path(proj)
    if not ledger:
        sys.exit(__doc__.strip())
    prices = load_prices()
    lang = language(proj) if proj else None
    if log:
        r = parse_log(log, prices)
        if r:
            r['轮次'] = rnd or '向导'
            update(ledger, [r], lang=lang)
        print('ledger: %d row -> %s' % (1 if r else 0, ledger))
        return
    if rebuild:
        base = proj.get('reviewOutDir') if proj else None
        if not base or not os.path.isdir(base):
            sys.exit('没有 reviewOutDir，没法重记。')
        ledger = os.path.realpath(ledger)
        with ledger_lock(ledger):
            folders = [os.path.join(base, d) for d in sorted(os.listdir(base)) if os.path.isdir(os.path.join(base, d))]
            rows = [row for d in folders for row in rows_for_round(d, prices)]
            n = update_locked(ledger, rows, [os.path.basename(d) for d in folders], lang=lang)
    else:
        n = update(ledger, [row for d in folders for row in rows_for_round(d, prices)], lang=lang)
    print('ledger: %d rows from %d rounds -> %s' % (n, len(folders), ledger))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    main()
