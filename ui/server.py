"""The page's service (prk ui, or the .exe in the kit folder): the kit in a window, on this computer only.
People do everything here; the terminal (prk) is for AI and scripts. Every page action calls the same functions of
prk.py as the matching command.

Same data as the terminal: it reads the round folders, the reports, the decision record. What it writes:
  - the decision record (one row per decision, the same file `prk decide` writes),
  - the fix list (待修清单.md: a decision 修 puts the entry on it; the page ticks and unticks items, as prk fix does),
  - the guide's task and log files (in the kit's state folder), when the guide is asked,
  - the choices of the settings page (project, provider, model, how to pay, the monthly budget) in the state file, as prk does,
  - the machine settings (prk provider setup's form: where a provider's key is, never the key; where Python and
    Claude Code are) and a new project file (prk new's form),
  - a check started from the page: a new round folder (as prk run makes), with the orchestrator's output in
    _运行记录.txt, and the kit's state folder's run_job.json (which check is running, so a new service finds it again).
The state file is read again on every request: what the terminal changed meanwhile is seen, and not overwritten.
It starts nothing that costs money by itself. A check (开始检查, 只派一类玩家, 写加内容的建议), asking the guide, and
「让 AI 直接修」use quota or money: the page says so and asks first (for a check: how many AIs, how it is paid, about
how much, from the cost ledger), and every such call goes through a POST the person clicks, with confirmed: true.
A check runs in the background: the request returns at once, the page asks /api/jobs for its progress, and the
service does not stop by itself while it runs (closing the window does not stop it either).「停下」ends the
orchestrator only: queued tasks never start; tasks already running finish on their own and are paid for.

Safety of a local server:
  - listens on 127.0.0.1 only;
  - every /api call must carry the token the page was served with (a web page elsewhere cannot read it or send the
    header), and the Host header must be this server;
  - files are served only from inside the round folders of the project (and the sample round), text files only.

Lifetime: one service per computer. Starting it again while one runs only opens another window on the running one.
The page sends a heartbeat; when no window has been open for a while (and no question to the guide, no fix, no check
is running), the service stops by itself, so closing the window is enough. The page's「退出」button stops it at once
(a running check goes on; the next service shows it again).

Only the standard library. Started by prk.py (which passes itself in as `prk`), not run directly.
"""
import base64
import contextlib
import csv
import datetime
import hashlib
import json
import time
import urllib.request
import os
import re
import secrets
import shutil
import subprocess
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))     # the ui folder: this file and index.html
IDLE_STOP = 150       # seconds without a heartbeat (after a window was open) before the service stops
NEVER_OPENED = 300    # seconds to wait for the first window
SAMPLE_ID = '__sample__'
TEXT_EXTS = ('.md', '.csv', '.txt', '.json')
SEVERITY = {'S': '严重', 'M': '中', 'L': '轻', 'D': '要定', 'W': '想要但没有的'}
RUN_LOG = '_运行记录.txt'                 # in the round folder: what the orchestrator printed (a check started here)
JOB_FILE = 'run_job.json'                # in the kit's state folder: the check started from the page
TASK_STALE = 30 * 60
STOP_GRACE = 10
# prk's options of one check; the page sets them for one request only (args_as)
RUN_KEYS = ('groups', 'split', 'no_map', 'no_merge', 'parallel', 'model', 'kind', 'out', 'items', 'map_dir', 'scope', 'max_turns', 'from', 'dir')
# Windows: no console window, and not in the group of the console the service was started from (its Ctrl+C)
NO_WINDOW = (0x08000000 | 0x00000200) if os.name == 'nt' else 0
_COST = {}
_LOGS = {}


def cost_words():
    """The words of the cost table (api\\texts.json, cost): its status column is read back here."""
    if not _COST:
        try:
            with open(os.path.join(os.path.dirname(HERE), 'api', 'texts.json'), encoding='utf-8-sig') as f:
                _COST.update(json.load(f).get('cost') or {})
        except (OSError, ValueError):
            pass
    return _COST


def decode_lines(data):
    """Output of PowerShell (the console's code page) and of this service (UTF-8) in one file, line by line, as text."""
    out = []
    for raw in data.splitlines():
        for enc in ('utf-8', 'oem', 'mbcs', 'latin-1'):
            try:
                out.append(raw.decode(enc))
                break
            except (UnicodeDecodeError, LookupError):
                continue
    return out


def log_state(path, since=0.0):
    """(state, usd, tokens, finished, last write) from one task's log."""
    try:
        st = os.stat(path)
    except OSError:
        return 'pending', None, None, False, None
    if st.st_mtime < since - 2:
        return 'pending', None, None, False, None
    key = (path, st.st_mtime, st.st_size)
    if key in _LOGS:
        return _LOGS[key]
    try:
        with open(path, 'rb') as f:
            if st.st_size > 262144:
                f.seek(-262144, 2)
            lines = f.read().decode('utf-8', 'replace').splitlines()
    except OSError:
        return 'running', None, None, False, st.st_mtime
    res, finished = None, False
    for ln in reversed(lines):
        if not finished and re.match(r'^finished \S+, exit -?\d+', ln):
            finished = True
        if res is None and ln.lstrip().startswith('{') and '"type"' in ln and '"result"' in ln:
            try:
                res = json.loads(ln)
            except ValueError:
                res = None
        if res is not None and finished:
            break
    if isinstance(res, dict):
        ok = res.get('is_error') is False and res.get('subtype') == 'success'
        u = res.get('usage') or {}
        tok = sum(int(u.get(k) or 0) for k in ('input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'))
        usd = res.get('total_cost_usd')
        out = ('ok' if ok else 'failed', float(usd) if isinstance(usd, (int, float)) else None, tok, finished, st.st_mtime)
    else:
        out = ('failed' if finished else 'running', None, None, finished, st.st_mtime)
    if finished:
        if len(_LOGS) > 500:
            _LOGS.clear()
        _LOGS[key] = out
    return out


def _kernel32():
    import ctypes
    from ctypes import wintypes
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.OpenProcess.restype = wintypes.HANDLE
    k.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    k.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
    k.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
    k.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
    k.CloseHandle.argtypes = (wintypes.HANDLE,)
    return ctypes, wintypes, k


def process_creation(ctypes, wintypes, kernel, handle):
    times = [wintypes.FILETIME() for _ in range(4)]
    if kernel.GetProcessTimes(handle, *[ctypes.byref(x) for x in times]):
        return (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
    return None


def proc_info(pid):
    """(alive, creation time) of a process, without touching it. On Windows never os.kill: there it ends the process."""
    if os.name != 'nt':
        try:
            os.kill(int(pid), 0)
            return True, None
        except (OSError, ValueError):
            return False, None
    ctypes, wintypes, k = _kernel32()
    h = k.OpenProcess(0x1000, False, int(pid))          # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return False, None
    try:
        code = wintypes.DWORD()
        alive = bool(k.GetExitCodeProcess(h, ctypes.byref(code))) and code.value == 259     # STILL_ACTIVE
        return alive, process_creation(ctypes, wintypes, k, h)
    finally:
        k.CloseHandle(h)


PROCESS_UNKNOWN = '认不出是不是那个进程'


def proc_kill(pid, created):
    """Verify and terminate a recovered orchestrator using the same Windows handle."""
    if os.name != 'nt' or created is None:
        raise OSError(PROCESS_UNKNOWN)
    ctypes, wintypes, k = _kernel32()
    h = k.OpenProcess(0x1001, False, int(pid))          # QUERY_LIMITED_INFORMATION | TERMINATE
    if not h:
        raise OSError(PROCESS_UNKNOWN)
    try:
        if process_creation(ctypes, wintypes, k, h) != created:
            raise OSError(PROCESS_UNKNOWN)
        if not k.TerminateProcess(h, 1):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        k.CloseHandle(h)


def process_identity(pid, expected):
    alive, created = proc_info(pid)
    if not alive or (created is not None and expected is not None and created != expected):
        return 'gone'
    return 'live' if created is not None and expected is not None else 'unknown'


def new_round_dir(base):
    """<reviewOutDir>\\<yyyyMMdd_HHmmss> (_2, _3 ... when taken), the way player_review_api.ps1 names a round."""
    stamp = time.strftime('%Y%m%d_%H%M%S')
    d, k = os.path.join(base, stamp), 2
    while os.path.exists(d):
        d, k = os.path.join(base, '%s_%d' % (stamp, k)), k + 1
    return d


def job_with_receipt(cmd, receipt, gate, runners):
    """Wait for the saved job before running the script, then save its exit code for another UI session."""
    file_arg = cmd.index('-File')
    args = iter(cmd[file_arg + 2:])
    switches = ('-Subscription', '-SplitByCharacters', '-Parallel', '-NoMap', '-NoMerge', '-Expand')
    params = {flag[1:]: True if flag in switches else next(args) for flag in args}
    env = dict(os.environ, PRK_PAGE_JOB=json.dumps({
        'script': cmd[file_arg + 1], 'params': params, 'receipt': receipt, 'gate': gate, 'runners': runners,
    }))
    script = """
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$ProgressPreference = 'SilentlyContinue'
$job = $env:PRK_PAGE_JOB | ConvertFrom-Json
Remove-Item Env:PRK_PAGE_JOB
$deadline = [DateTime]::UtcNow.AddSeconds(60)
while (-not [IO.File]::Exists($job.gate)) {
    if ([DateTime]::UtcNow -ge $deadline) { exit 2 }
    Start-Sleep -Milliseconds 50
}
[IO.File]::Delete($job.gate)
$env:PRK_RUNNER_RECORDS = $job.runners
$params = @{}
foreach ($p in $job.params.PSObject.Properties) { $params[$p.Name] = $p.Value }
$global:LASTEXITCODE = 0
try {
    & $job.script @params 3>&1 6>&1 | ForEach-Object { [Console]::WriteLine([string]$_) }
    $status = $LASTEXITCODE
} catch {
    Write-Error -ErrorAction Continue $_
    $status = 1
}
$tmp = $job.receipt + '.tmp'
[IO.File]::WriteAllText($tmp, [string]$status)
[IO.File]::Move($tmp, $job.receipt)
exit $status
"""
    encoded = base64.b64encode(script.encode('utf-16-le')).decode('ascii')
    return cmd[:file_arg] + ['-OutputFormat', 'Text', '-EncodedCommand', encoded], env


class App:
    def __init__(self, prk, ctx):
        self.prk, self.ctx = prk, ctx
        for k in ('pay', 'mode'):          # the page pays the way the settings say, not a one-off flag of the command line
            ctx['args'].pop(k, None)
        self.lock = threading.Lock()       # ctx is shared: one request at a time touches it
        self.token = secrets.token_urlsafe(24)
        self.started = time.time()
        self.last_ping = None              # time of the last heartbeat from a window
        self.busy = 0                      # questions to the guide being answered right now
        self.stop = threading.Event()
        self.job = None                    # the check started from the page (see start_job), kept in JOB_FILE
        self.job_lock = threading.RLock()
        self.active_fixes = set()          # (project path, fix id), checked under self.lock
        self._job_proj = (None, None)
        self.pending_ledgers = {}
        self.load_job()
        self.load_pending_ledgers()
        self.retry_ledgers()

    # ----- rounds -----

    def rounds(self):
        """[(id, folder, is_sample)]: the project's round folders, newest first, then the sample round if it has one."""
        proj = self.ctx.get('proj')
        if not proj:
            return []
        out = [(os.path.basename(d), d, False) for d in self.prk.review_dirs(proj)[:40]]
        s = proj.get('sampleRound')
        if s and os.path.isdir(s):
            out.append((SAMPLE_ID, s, True))
        return out

    def round_dir(self, rid):
        for i, d, sample in self.rounds():
            if i == rid:
                return d, sample
        return None, False

    def collect(self, d):
        a = self.ctx['args']
        keep = {k: a.pop(k, None) for k in ('dir', 'from')}
        a['dir'] = d
        try:
            return self.prk.collect_feedback(self.ctx)
        finally:
            a.pop('dir', None)
            a.update({k: v for k, v in keep.items() if v is not None})

    def cost_total(self, d):
        p = os.path.join(d, self.prk.cost_name(self.ctx['proj']))
        if not os.path.exists(p):
            return None
        with open(p, encoding='utf-8-sig', errors='replace') as f:
            m = re.findall(r'\*\*([\d.]+)\*\*', f.read())
        return float(m[-1]) if m else None

    def decisions_for(self, reports, sample):
        """{(report file name, entry id): latest decision} for the reports of one round, and every row of the record.
        Keyed by report too: reports that are not merged yet each have their own M1."""
        rows = self.prk.read_decisions(self.prk.decisions_file(self.ctx['proj'], sample))
        want = {os.path.normcase(os.path.abspath(r)) for r in reports}
        mine = {}
        for r in rows:
            if os.path.normcase(os.path.abspath(r['合并报告'])) in want:
                mine[(os.path.basename(r['合并报告']), r['编号'])] = {'decision': r['决定'], 'why': r['一句原因'], 'date': r['日期']}
        return mine, rows

    def round_summary(self, rid, d, sample):
        data = self.collect(d)
        row = {'id': rid, 'name': '样例（手写的）' if sample else rid, 'sample': sample, 'cost': self.cost_total(d),
               'hasReport': bool(data), 'merged': False, 'reports': 0, 'counts': {k: 0 for k in 'SMLDW'}, 'decided': 0, 'entries': 0}
        if data:
            mine, _ = self.decisions_for(data['reports'], sample)
            keys = {(e['report'], e['id']) for e in data['entries']}
            row.update({'merged': data['merged'], 'reports': len(data['reports']), 'counts': data['counts'],
                        'entries': len(keys), 'decided': len([k for k in keys if k in mine])})
        return row

    def files_of(self, d):
        proj = self.ctx['proj']
        merged = (proj.get('reportNames') or {}).get('merged') or '玩家视角审查_合并.md'
        groups = [('合并报告', []), ('审查员的报告', []), ('内容提案', []), ('引文核验', []), ('花费', []), ('静态表', []),
                  ('作品地图', []), ('草稿', []), ('任务文件', []), ('日志', []), ('别的', [])]
        g = dict(groups)

        def put(rel, size):
            name = os.path.basename(rel)
            low = name.lower()
            if rel.startswith('_map'):
                g['作品地图'].append(rel)
            elif name == merged or ('合并' in name and low.endswith('.md') and not name.startswith('_')):
                g['合并报告'].append(rel)
            elif '草稿' in name:
                g['草稿'].append(rel)
            elif '提案' in name or '拓展' in name:
                g['内容提案'].append(rel)
            elif name.startswith('_citations'):
                g['引文核验'].append(rel)
            elif name == self.prk.cost_name(proj):
                g['花费'].append(rel)
            elif name.startswith('task_'):
                g['任务文件'].append(rel)
            elif name.startswith('log_') or name.startswith('_运行记录'):
                if size and not low.endswith(('.err.txt', '.out.txt')):
                    g['日志'].append(rel)
            elif name.startswith('_'):
                g['静态表'].append(rel)
            elif low.endswith('.md'):
                g['审查员的报告'].append(rel)
            else:
                g['别的'].append(rel)

        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            if os.path.isfile(p) and name.lower().endswith(TEXT_EXTS):
                put(name, os.path.getsize(p))
            elif os.path.isdir(p) and name == '_map':
                for n2 in sorted(os.listdir(p)):
                    if n2.lower().endswith(TEXT_EXTS):
                        put(os.path.join('_map', n2), 1)
        return [{'group': k, 'files': v} for k, v in groups if v]

    def round_detail(self, rid):
        d, sample = self.round_dir(rid)
        if not d:
            return None
        data = self.collect(d) or {'reports': [], 'merged': False, 'counts': {k: 0 for k in 'SMLDW'}, 'entries': [],
                                   'feedback': [], 'feedbackMarkdown': '', 'lastRound': '', 'conclusion': '', 'dir': d}
        # the full text of every entry, for the detail panel
        bodies = {}
        for rp in data['reports']:
            with open(rp, encoding='utf-8-sig', errors='replace') as f:
                text = f.read()
            for eid, body in self.prk.entry_bodies(text).items():
                bodies[(os.path.basename(rp), eid)] = body
        mine, _all = self.decisions_for(data['reports'], sample)
        entries = []
        for e in data['entries']:
            entries.append(dict(e, kind=e['id'][0], severity=SEVERITY.get(e['id'][0], ''), body=bodies.get((e['report'], e['id']), ''),
                                decision=mine.get((e['report'], e['id']))))
        cites = None
        for name in sorted(os.listdir(d)):
            if name.startswith('_citations') and name.endswith('.md'):
                with open(os.path.join(d, name), encoding='utf-8-sig', errors='replace') as f:
                    head = f.read(1500)
                m = re.search(r'(\d+)\s*处[^\n]*?对不上[^\n]*?(\d+)', head) or re.search(r'对不上[^\d\n]*(\d+)', head)
                cites = {'file': name, 'summary': (m.group(0) if m else '').strip()}
        return {'id': rid, 'sample': sample, 'dir': d, 'merged': data['merged'], 'reports': [os.path.basename(r) for r in data['reports']],
                'counts': data['counts'], 'conclusion': data['conclusion'], 'feedback': data['feedback'],
                'feedbackMarkdown': data['feedbackMarkdown'], 'lastRound': data['lastRound'], 'entries': entries,
                'files': self.files_of(d), 'cost': self.cost_total(d), 'citations': cites,
                'decisionsFile': self.prk.decisions_file(self.ctx['proj'], sample), 'choices': self.prk.DECISIONS}

    # ----- pages of data -----

    def overview(self):
        prk, ctx = self.prk, self.ctx
        pay, gpay, separate = prk.pay_state(ctx['state'])
        out = {'kit': {'kinds': len(prk.load_kinds()), 'personas': len(prk.load_personas())},
               'projects': [{'path': p, 'title': prk.project_title(p)} for p in prk.find_projects(ctx['state'])],
               'project': None, 'rounds': [], 'next': prk.next_steps(ctx),
               'pay': pay, 'guidePay': gpay, 'payGuideSeparate': separate, 'home': os.path.expanduser('~')}
        m, src = prk.current_model(ctx)
        pv, psrc = prk.current_provider(ctx)
        out['model'] = {'current': m, 'source': src, 'remembered': prk.remembered_models(ctx['state']).get(pv) or '', 'choices': prk.model_choices(ctx, pv),
                        'provider': pv, 'providerSource': psrc}
        out['providers'] = [{k: d.get(k) for k in ('id', 'name', 'kind', 'engine', 'configured', 'keyReady', 'signin', 'signinWith', 'signinReady', 'signinProblem',
                                                   'program', 'docs', 'checked', 'note', 'models', 'model')} for d in prk.load_providers(ctx).values()]
        out['engineNames'] = dict(prk.ENGINE_NAMES)
        out['payProblem'] = prk.pay_problem(ctx, pay, pv)
        info = prk.local_info(ctx)         # the page only needs yes / no
        out['local'] = {k: (info[k] if k == 'apiKey' else bool(info[k])) for k in ('file', 'claude', 'apiKey', 'powershell')}
        out['local'].update({k: info.get(k) for k in ('provider', 'providerName', 'providerReady', 'providerSignin', 'program', 'engine')})
        out['usage'] = prk.month_use(ctx)        # this month: paid by use (and the budget), tokens on the plan
        out['machine'] = prk.machine_paths(ctx)  # where Python and Claude Code are (the settings page's form)
        out['reviewKinds'] = [{'id': k['id'], 'name': k.get('name') or k['id']} for k in prk.load_kinds() if (k.get('role') or 'review') == 'review']
        if ctx.get('path'):
            todo = lambda s: len([x for x in prk.read_fixes(prk.fix_file(ctx['proj'], s))['items'] if not x['done']])
            out['fixTodo'] = {'real': todo(False), 'sample': todo(True)}
            proj = ctx['proj']
            problems, notes = prk.check_data(ctx)
            out['project'] = {'name': proj.get('name') or proj.get('id'), 'file': ctx['path'], 'owner': proj.get('ownerName') or '负责人',
                              'playUnit': proj.get('playUnit') or '', 'problems': problems, 'notes': notes,
                              'groups': [{'id': g.get('id'), 'name': g.get('name'), 'kind': prk.group_kind(g), 'personas': g.get('personas') or []}
                                         for g in prk.groups_of(proj)],
                              'defaultGroups': proj.get('defaultGroups') or [], 'splits': [s.get('name') or s.get('id') for s in proj.get('characterSplits') or []],
                              'splitUnit': proj.get('splitUnitName') or '份', 'reviewOutDir': proj.get('reviewOutDir')}
            out['rounds'] = [self.round_summary(i, d, s) for i, d, s in self.rounds()]
        return out

    def library(self):
        prk = self.prk
        proj = self.ctx.get('proj') or {}
        return {'kinds': prk.load_kinds(), 'presets': prk.load_presets(), 'projectPresets': proj.get('presets') or [],
                'personas': [{'n': n, 'name': name, 'cls': cls, 'file': f} for n, name, cls, f in prk.load_personas()]}

    def read_file(self, rid, name):
        d, _sample = self.round_dir(rid)
        if not d or not name.lower().endswith(TEXT_EXTS):
            return None
        root = os.path.realpath(d)
        p = os.path.realpath(os.path.join(d, name))
        if os.path.commonpath([root, p]) != root or not os.path.isfile(p):
            return None
        if os.path.getsize(p) > 3 * 1024 * 1024:
            return {'name': name, 'text': '（这个文件超过 3 MB，页面不显示。在文件夹里打开：%s）' % p, 'path': p}
        with open(p, encoding='utf-8-sig', errors='replace') as f:
            return {'name': name, 'text': f.read(), 'path': p}

    def decide(self, body):
        rid, ident, decision = body.get('round'), str(body.get('id') or ''), body.get('decision')
        rep = str(body.get('report') or '')
        if decision not in self.prk.DECISIONS:
            return {'ok': False, 'error': '决定只能是：%s' % '、'.join(self.prk.DECISIONS)}
        det = self.round_detail(rid)
        entry = next((e for e in (det or {}).get('entries', []) if e['id'] == ident and (not rep or e['report'] == rep)), None)
        if not entry:
            return {'ok': False, 'error': '这一轮里没有 %s' % ident}
        chk = re.search(r'(?m)^- 核对：\s*(.+)$', entry.get('body') or '')
        report = os.path.join(det['dir'], entry['report'])
        why = str(body.get('why') or '').replace('\r', ' ').replace('\n', ' ').strip()[:300]
        self.prk.write_decisions(det['decisionsFile'], [[datetime.date.today().isoformat(), report, ident, entry.get('confidence') or '',
                                                          (chk.group(1).strip()[:60] if chk else ''), decision, why]])
        out = {'ok': True, 'file': det['decisionsFile']}
        try:                               # 修 = on the fix list; another decision takes it off unless it is fixed already
            out.update(self.prk.fix_sync(self.ctx['proj'], det['sample'], report, ident, decision, entry['title'], entry.get('body') or '', why))
        except OSError as e:
            out['fixError'] = '决定记下了，但没写进待修清单：%s' % e
        return out

    # ----- the fix list -----

    def paid_binding(self):
        prk, ctx = self.prk, self.ctx
        return {'project': ctx.get('path'), 'provider': prk.current_provider(ctx)[0],
                'model': prk.current_model(ctx)[0], 'pay': prk.pay_state(ctx['state'])[0]}

    def binding_error(self, sent, current):
        sent = sent if isinstance(sent, dict) else {}
        changed = [k for k, v in current.items() if k not in sent or sent[k] != v]
        if changed:
            return {'ok': False, 'changed': changed, 'error': '确认时的信息变了，请看过新的确认框再继续。'}
        return None

    def fix_binding(self, rid, item):
        base = self.ctx['proj'].get('reviewOutDir')
        action = self.fix_action_binding(rid, item)
        report = os.path.join(base, item['round'], item['report']) if base and item['round'] and item['report'] else None
        if action['sample'] or not action['viewRound'] or not report or not os.path.isfile(report):
            report = None
        return dict(self.paid_binding(), **action, report=report, entry=item['entry'])

    def fix_action_binding(self, rid, item):
        selected, sample = self.round_dir(rid)
        return {'project': self.ctx['path'], 'viewRound': selected, 'round': item['round'],
                'id': item['id'], 'title': item['title'], 'sample': sample}

    def fix_key(self, fid):
        return os.path.normcase(os.path.realpath(self.ctx['path'])), fid

    def fixes(self, rid):
        proj = self.ctx.get('proj')
        if not proj:
            return {'ok': False, 'error': '先选一个游戏。'}
        sample = self.round_dir(rid)[1] if rid else False
        d = self.prk.fix_list(proj, sample)
        pay = self.prk.pay_state(self.ctx['state'])[0]
        d['runProblem'] = '这是示范数据，不能让 AI 直接修（它会去改例子游戏的文件）。可以复制给 AI 看看样子。' if sample else self.prk.fix_cannot(self.ctx, pay)
        for item in d['items']:
            item['actionBinding'] = self.fix_action_binding(rid, item)
        if not sample:
            ai = self.prk.load_providers(self.ctx).get(self.prk.current_provider(self.ctx)[0]) or {}
            d['providerName'] = ai.get('name')
            for item in d['items']:
                item['confirmation'] = self.fix_binding(rid, item)
        d['ok'] = True
        return d

    def fix_action(self, body):
        """done / reopen / undo: quick, under the lock."""
        proj = self.ctx.get('proj')
        fid, act = str(body.get('id') or '').upper(), body.get('action')
        sent = body.get('confirmation')
        err = self.binding_error(sent, {'project': self.ctx.get('path')})
        if err:
            return err
        if not proj or not re.match(r'^F\d+$', fid):
            return {'ok': False, 'error': '没有这一条。'}
        rid = str(body.get('round') or '')
        selected, sample = self.round_dir(rid)
        if rid and not selected:
            return {'ok': False, 'changed': ['viewRound'], 'error': '找不到确认的轮次，请刷新后重新确认。'}
        path = self.prk.fix_file(proj, sample)
        item = next((x for x in self.prk.read_fixes(path)['items'] if x['id'] == fid), None)
        if item is None:
            return {'ok': False, 'changed': ['id'], 'error': '待修清单里已经没有这一条。'}
        err = self.binding_error(sent, self.fix_action_binding(rid, item))
        if err:
            return err
        if self.fix_key(fid) in self.active_fixes:
            return {'ok': False, 'error': '这条正在修，等它修完。'}
        if act in ('done', 'reopen'):
            ok = self.prk.fix_mark(path, fid, act == 'done')
            return {'ok': ok, 'error': '' if ok else '清单里没有 %s 了（文件可能被别处改过），点「刷新」。' % fid}
        if act == 'undo':
            if sample:
                return {'ok': False, 'error': '示范数据没有备份，没法撤回。'}
            return self.prk.fix_undo(self.ctx, fid)
        return {'ok': False, 'error': '不认识的动作。'}

    def fix_run(self, body):
        """An AI changes the game's files for one item (slow: minutes). The lock is held only while checking."""
        fid = str(body.get('id') or '').upper()
        with self.lock:
            if self.stop.is_set():
                return {'ok': False, 'error': '页面正在退出。'}
            self.prk.refresh_state(self.ctx)
            sent = body.get('confirmation')
            err = self.binding_error(sent, self.paid_binding())
            if err:
                return err
            if not self.ctx.get('proj') or not re.match(r'^F\d+$', fid):
                return {'ok': False, 'error': '没有这一条。'}
            key = self.fix_key(fid)
            if key in self.active_fixes:
                return {'ok': False, 'error': '这条正在修，等它修完。'}
            it = next((x for x in self.prk.read_fixes(self.prk.fix_file(self.ctx['proj']))['items'] if x['id'] == fid), None)
            if not it:
                return {'ok': False, 'changed': ['id'], 'error': '待修清单里已经没有这一条。'}
            binding = self.fix_binding(str(body.get('round') or ''), it)
            err = self.binding_error(sent, binding)
            if err:
                return err
            if not binding['viewRound'] or not binding['report']:
                return {'ok': False, 'error': '找不到确认的轮次或原报告，无法直接修。'}
            pay = binding['pay']
            err = self.prk.fix_cannot(self.ctx, pay)
            if err:
                return {'ok': False, 'error': err}
            ctx = dict(self.ctx, args=dict(self.ctx['args'], provider=binding['provider'], model=binding['model']),
                       state=dict(self.ctx['state']))
            self.active_fixes.add(key)
            self.busy += 1
        try:
            return self.prk.fix_run(ctx, fid, pay, expected_item=it)
        finally:
            with self.lock:
                self.active_fixes.remove(key)
                self.busy -= 1

    def set_project(self, body):
        p = str(body.get('path') or '')
        known = {os.path.normcase(os.path.abspath(x)) for x in self.prk.find_projects(self.ctx['state'])}
        if os.path.normcase(os.path.abspath(p)) not in known:
            return {'ok': False, 'error': '只能选列表里的项目设置。别的先在终端里用 prk -p <文件> 打开一次。'}
        try:
            self.prk.set_project(self.ctx, p)
        except SystemExit as e:
            return {'ok': False, 'error': str(e.code)}
        return {'ok': True}

    def set_pay(self, body):
        """{pay?: sub|api, guidePay?: sub|api|same}: remember how the checks and the guide are paid (as prk pay)."""
        pay, guide = body.get('pay'), body.get('guidePay')
        if pay is None and guide is None:
            return {'ok': False, 'error': '没说要改成什么。'}
        err = self.prk.set_pay(self.ctx, pay=None if pay is None else str(pay), guide=None if guide is None else str(guide))
        if err:
            return {'ok': False, 'error': err}
        p, g, separate = self.prk.pay_state(self.ctx['state'])
        return {'ok': True, 'pay': p, 'guidePay': g, 'payGuideSeparate': separate}

    def guide(self, body):
        q = str(body.get('question') or '').strip()
        if not q:
            return {'ok': False, 'error': '先写问题。'}
        if len(q) > 2000:
            return {'ok': False, 'error': '问题太长了（最多 2000 个字）。'}
        with self.lock:                    # the slow part (a model answers) runs outside the lock
            if self.stop.is_set():
                return {'ok': False, 'error': '页面正在退出。'}
            self.prk.refresh_state(self.ctx)
            mode = self.prk.pay_state(self.ctx['state'])[1]     # the guide's pay in effect: its own, else the shared one
            if mode not in ('sub', 'api'):
                return {'ok': False, 'error': '先选问 AI 用什么付：对话框左下角，或「设置」里的「怎么付」。'}
            if body.get('mode') and body.get('mode') != mode:
                return {'ok': False, 'error': '付钱的方式刚刚在别处改过了，页面已经刷新，再点一次发送。', 'stale': True}
            state = self.prk.guide_state(self.ctx)
            ctx = dict(self.ctx, args=dict(self.ctx['args']), state=dict(self.ctx['state']))
            self.busy += 1
        try:
            hist = [{'q': str(h.get('q', ''))[:1000], 'a': str(h.get('a', ''))[:2000]} for h in (body.get('history') or [])[-3:] if isinstance(h, dict)]
            return self.prk.ask_guide(ctx, q, mode, hist, state)
        finally:
            with self.lock:
                self.busy -= 1

    def request_quit(self):
        with self.lock:
            if self.active_fixes:
                return {'ok': False, 'error': 'AI 正在直接修，等它修完再退出。'}
            if self.busy:
                return {'ok': False, 'error': '向导正在回答，等它答完再退出。'}
            self.stop.set()
            return {'ok': True}

    # ----- settings by form (what prk provider setup, prk new and prk local ask in the terminal) -----

    def provider_form(self, name):
        name = name or self.prk.current_provider(self.ctx)[0]
        if name not in self.prk.load_providers(self.ctx):
            return {'ok': False, 'error': '没有这一家：%s' % name}
        return dict(self.prk.provider_form(self.ctx, name), ok=True)

    def provider_setup(self, body):
        name = str(body.get('name') or '')
        if name not in self.prk.load_providers(self.ctx):
            return {'ok': False, 'error': '没有这一家：%s' % name}
        vals = body.get('values') if isinstance(body.get('values'), dict) else {}
        dst, err = self.prk.save_provider(self.ctx, name, vals)
        if err:
            return {'ok': False, 'error': err}
        return {'ok': True, 'file': dst, 'form': self.prk.provider_form(self.ctx, name)}

    def new_project(self, body):
        vals = body.get('values') if isinstance(body.get('values'), dict) else {}
        dst, err, missing = self.prk.new_project(vals, str(body.get('folder') or ''), strict=True)
        if err:
            return {'ok': False, 'error': err, 'missing': missing}
        try:
            self.prk.set_project(self.ctx, dst)
        except SystemExit as e:
            return {'ok': False, 'error': str(e.code)}
        return {'ok': True, 'file': dst}

    def cite(self, body):
        """The citation check of one round (free, a few seconds; prk cite). The script runs outside the lock."""
        with self.lock:
            self.prk.refresh_state(self.ctx)
            proj = self.ctx.get('proj')
            if not proj:
                return {'ok': False, 'error': '先选一个游戏。'}
            rid = str(body.get('round') or '')
            d, sample = self.round_dir(rid)
            if rid and not d:
                return {'ok': False, 'error': '找不到这一轮的报告。'}
            if not d:
                d = (self.prk.review_dirs(proj) or [None])[0]
            if sample:
                return {'ok': False, 'error': '这是示范数据，不用核对。'}
            if not d:
                return {'ok': False, 'error': '还没有检查过。'}
            cmd = self.prk.cite_cmd(self.ctx, d)
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=600, creationflags=NO_WINDOW, cwd=self.prk.KIT)
        except (OSError, subprocess.TimeoutExpired) as e:
            return {'ok': False, 'error': '核对不了：%s' % e}
        if not self.prk.cite_written(r, os.path.join(d, '_citations.md')):
            tail = [x for x in decode_lines((r.stdout or b'') + b'\n' + (r.stderr or b'')) if x.strip()][-6:]
            return {'ok': False, 'error': '没核成。' + self.prk.mask_home(' '.join(tail))[:500]}
        return {'ok': True, 'round': os.path.basename(d), 'file': '_citations.md'}

    # ----- a check started from the page -----

    @contextlib.contextmanager
    def args_as(self, opts):
        """prk's options of one check, for this request only (the lock is held by the caller)."""
        a = self.ctx['args']
        keep = {k: a.pop(k) for k in RUN_KEYS if k in a}
        a.update(opts)
        try:
            yield
        finally:
            for k in RUN_KEYS:
                a.pop(k, None)
            a.update(keep)

    def run_options(self, body, what):
        """The page's choices for one check as prk's options, checked. Returns (options, error text)."""
        prk, proj = self.prk, self.ctx['proj']
        out = {}
        try:
            out['parallel'] = max(1, min(12, int(body.get('parallel') or 4)))
        except (TypeError, ValueError):
            out['parallel'] = 4
        model = str(body.get('model') or '').strip()
        if model:
            if not prk.MODEL_ID.match(model):
                return None, '型号写得不对：只能是字母、数字和 . _ - : / [ ] @ ~。'
            out['model'] = model
        if what == 'quick':
            groups, _who, err = prk.quick_groups(str(body.get('who') or ''))
            if err or not groups or ',' in groups:
                return None, err or '快速检查只能派一组玩家。'
            out.update(groups=groups, no_merge=True, no_map=True)
            kind = str(body.get('kind') or '').strip()
            if kind and kind != 'persona':
                if kind not in {k['id'] for k in prk.load_kinds() if (k.get('role') or 'review') == 'review'}:
                    return None, '没有这种检查方法：%s' % kind
                out['kind'] = kind
        elif what == 'expand':
            out.pop('parallel')
            items = re.sub(r'\s', '', str(body.get('items') or '')).upper()
            if items and not re.match(r'^[SMLDW]\d+(,[SMLDW]\d+)*$', items):
                return None, '要写建议的条目写得不对（例：W1,W3）。'
            if items:
                out['items'] = items
            if body.get('round') or body.get('report'):
                rid = str(body.get('round') or '')
                d, sample = self.round_dir(rid)
                merged = (proj.get('reportNames') or {}).get('merged') or '玩家视角审查_合并.md'
                report = os.path.join(d, merged) if d else ''
                if not report or sample or report != body.get('report') or not os.path.isfile(report):
                    return None, '找不到这一轮的合并报告。'
                out['from'] = report
        elif what == 'run':
            known = [str(g.get('id')) for g in prk.groups_of(proj)]
            gs = [str(x) for x in body.get('groups') or []]
            bad = [g for g in gs if g not in known]
            if bad:
                return None, '这个游戏没有这几组：%s' % '、'.join(bad)
            if not gs:
                return None, '至少勾一组玩家。'
            out['groups'] = ','.join(gs)
            if body.get('split') and proj.get('characterSplits'):
                out['split'] = True
            if body.get('map') is False:
                out['no_map'] = True
        else:
            return None, '不认识要做什么：%s' % what
        return out, ''

    def pay_info(self, tasks, what):
        """For the confirm box: how it is paid, which AI and model, about how much (the cost ledger), what is missing."""
        prk, ctx = self.prk, self.ctx
        pv = prk.current_provider(ctx)[0]
        d = prk.load_providers(ctx).get(pv) or {}
        m, msrc = prk.current_model(ctx)
        return {'pay': prk.pay_state(ctx['state'])[0], 'model': m, 'modelSource': msrc,
                'provider': {'id': pv, 'name': d.get('name') or pv, 'signin': bool(d.get('signin')),
                             'signinWith': d.get('signinWith') or '', 'signinProblem': d.get('signinProblem') or ''},
                'payLine': {p: prk.pay_line(ctx, p) for p in prk.PAYS},
                'cannot': {p: prk.run_cannot(ctx, p, what) for p in prk.PAYS},
                'estimate': prk.estimate(ctx, tasks)}

    def plan(self, body):
        """「先试一下」: a dry run (prk plan: no AI, no money) with the page's choices; the task list, and what the
        confirm box needs. The dry run itself runs outside the lock."""
        prk = self.prk
        mode = body.get('mode') if body.get('mode') in ('run', 'quick', 'expand') else ('quick' if str(body.get('who') or '').strip() else 'run')
        os.makedirs(prk.STATE_DIR, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='plan_', dir=prk.STATE_DIR) as preview:
            return self.plan_in(body, mode, preview)

    def plan_in(self, body, mode, preview):
        prk = self.prk
        cmd = None
        with self.lock:
            prk.refresh_state(self.ctx)
            if body.get('project') and body['project'] != self.ctx.get('path'):
                return self.binding_error(body, {'project': self.ctx.get('path')})
            if not self.ctx.get('proj'):
                return {'ok': False, 'error': '先选一个游戏。'}
            version = self.project_version()
            if 'projectVersion' in body:
                err = self.binding_error(body, {'projectVersion': version})
                if err:
                    return err
            if not version:
                return {'ok': False, 'error': '读不到项目设置。'}
            try:
                self.ctx['proj'] = prk.projfile.load_project(self.ctx['path'])[0]
            except (OSError, ValueError, SystemExit):
                return (self.binding_error({'projectVersion': version}, {'projectVersion': self.project_version()})
                        or {'ok': False, 'error': '读不到项目设置，请检查文件后重试。'})
            opts, err = self.run_options(body, mode)
            if err:
                return {'ok': False, 'error': err}
            with self.args_as(opts):
                binding = self.run_binding(mode, opts)
                err = self.binding_error({'projectVersion': version}, {'projectVersion': binding['projectVersion']})
                if err:
                    return err
                if mode == 'expand':
                    if not binding['report']:
                        return {'ok': False, 'error': '还没有汇总好的报告，没法写加内容的建议。'}
                else:
                    cmd = prk.api_args(self.ctx, ['-DryRun', '-OutDir', preview], binding['pay'] or None)
                    if not cmd:
                        return {'ok': False, 'error': '找不到 PowerShell（Windows 自带；别的系统装 pwsh）。'}
        tasks = ['expand']
        if cmd:
            try:
                r = subprocess.run(cmd, capture_output=True, timeout=300, creationflags=NO_WINDOW, cwd=prk.KIT)
            except (OSError, subprocess.TimeoutExpired) as e:
                return {'ok': False, 'error': '试不了：%s' % e}
            lines = decode_lines((r.stdout or b'') + b'\n' + (r.stderr or b''))
            d = prk.parse_plan('\n'.join(lines))
            if r.returncode != 0 or not d['tasks']:
                return {'ok': False, 'error': '试的时候出错了，下面是最后几行。',
                        'tail': prk.mask_home('\n'.join([x for x in lines if x.strip()][-10:]))}
            tasks = d['tasks']
        with self.lock:
            prk.refresh_state(self.ctx)
            with self.args_as(opts):
                err = self.binding_error(binding, self.run_binding(mode, opts))
                if err:
                    return err
                out = self.pay_info(tasks, mode)
            proj = self.ctx['proj']
        binding['tasks'] = tasks
        out.update({'ok': True, 'mode': mode, 'confirmation': binding, 'count': len(tasks),
                    'tasks': [{'name': t, 'label': prk.task_label(proj, t)} for t in tasks]})
        return out

    def run_binding(self, what, opts):
        binding = dict(self.paid_binding(), what=what, options=opts, projectVersion=self.project_version())
        if what == 'expand':
            rp = self.prk.merged_report(self.ctx) if self.ctx.get('proj') else None
            binding.update(report=rp, round=os.path.basename(os.path.dirname(rp)) if rp else None)
        return binding

    def project_version(self):
        try:
            with open(self.ctx['path'], 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except (OSError, TypeError):
            return None

    def job_path(self):
        return os.path.join(self.prk.STATE_DIR, JOB_FILE)

    def load_job(self):
        try:
            with open(self.job_path(), encoding='utf-8') as f:
                j = json.load(f)
        except (OSError, ValueError):
            return
        if isinstance(j, dict) and j.get('pid') and j.get('dir') and j.get('log'):
            if j.get('final') == 'done' and j.get('returncode') is None:
                j['final'] = ''  # Older pages only checked the completion line for ordinary runs.
            self.job = j

    def save_job(self):
        self.prk.atomic_json(self.job_path(), {k: v for k, v in self.job.items() if k != 'proc'})

    def job_process(self):
        """A recovered PID needs its creation time before it can be treated as this job."""
        j = self.job
        if not j or j.get('final'):
            return 'gone'
        p = j.get('proc')
        if p is not None:
            return 'live' if p.poll() is None else 'gone'
        return process_identity(j['pid'], j.get('created'))

    def pending_path(self, jid):
        return os.path.join(self.prk.STATE_DIR, 'ledger_pending_%s.json' % jid)

    def load_pending_ledgers(self):
        for name in os.listdir(self.prk.STATE_DIR):
            m = re.fullmatch(r'ledger_pending_([A-Za-z0-9_-]+)\.json', name)
            if m:
                with contextlib.suppress(OSError, ValueError):
                    self.pending_ledgers[m[1]] = self.prk.read_json(self.pending_path(m[1]))
        j = self.job
        if j and (j.get('ledgerPending') or (j.get('final') == 'stopped' and j.get('ledgerDone') is False)):
            self.pending_ledgers.setdefault(j['id'], {k: j[k] for k in ('dir', 'ledger', 'prices') if k in j})

    def record_ledger(self, data):
        try:
            if not os.path.isdir(data['dir']):
                return False
            cl = self.prk.ledger_mod()
            cl.update(data['ledger'], cl.rows_for_round(data['dir'], data.get('prices')))
            return True
        except (OSError, ValueError, KeyError, TypeError, csv.Error):
            return False

    def defer_ledger(self, j):
        data = {k: j[k] for k in ('dir', 'ledger', 'prices') if k in j}
        self.pending_ledgers[j['id']] = data
        j['ledgerPending'] = True
        with contextlib.suppress(OSError):
            self.prk.atomic_json(self.pending_path(j['id']), data)

    def retry_ledgers(self):
        for jid, data in list(self.pending_ledgers.items()):
            if not self.record_ledger(data):
                with contextlib.suppress(OSError):
                    self.prk.atomic_json(self.pending_path(jid), data)
                continue
            if self.job and self.job.get('id') == jid:
                self.job.update(ledgerPending=False, ledgerDone=True)
                with contextlib.suppress(OSError):
                    self.save_job()
            with contextlib.suppress(OSError):
                os.remove(self.pending_path(jid))
            del self.pending_ledgers[jid]

    def ledger_notice(self):
        return self.prk.api_text('ledgerPending') if self.pending_ledgers else ''

    def job_project(self, j):
        if self._job_proj[0] != j.get('project'):
            try:
                proj = self.prk.projfile.load_project(j['project'])[0]
            except (SystemExit, OSError, ValueError, KeyError, TypeError):
                proj = {}
            self._job_proj = (j.get('project'), proj)
        return self._job_proj[1]

    def job_tasks(self, j, draining=False):
        """The tasks of the page's check: from its cost table (the orchestrator lists every task there from the start and
        rewrites it as they finish); each task's own log tells what the table does not know yet (or no more, after
        「停下」). Before the table is there (the static tables run first) the list is empty."""
        d, since, rows = j['dir'], float(j.get('started') or 0), []
        if j.get('what') == 'expand':
            name = 'log_expand_%s.txt' % j['runId'] if j.get('runId') else 'log_expand.txt'
            rows = [{'name': 'expand', 'log': name, 'state': 'pending', 'usd': None}]
        else:
            table = os.path.join(d, j.get('costName') or '_花费.md')
            try:
                fresh = os.path.getmtime(table) >= since - 2
            except OSError:
                fresh = False
            if fresh:
                C = cost_words()
                with contextlib.suppress(OSError), open(table, encoding='utf-8-sig', errors='replace') as f:
                    for ln in f.read().splitlines():
                        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
                        if not ln.startswith('|') or '**' in ln or len(cells) < 7 or not re.match(r'^log_.+\.txt$', cells[6]):
                            continue
                        s = cells[1]
                        state = 'ok' if s == C.get('ok') else 'running' if s == C.get('running') else 'pending' if s == C.get('pending') \
                            else 'skipped' if s == C.get('skipped') else 'failed'
                        try:
                            usd = float(cells[3])
                        except ValueError:
                            usd = None
                        rows.append({'name': cells[6][4:-4], 'log': cells[6], 'state': state, 'usd': usd})
        records = {}
        if draining and j.get('runners') and os.path.isdir(j['runners']):
            for name in os.listdir(j['runners']):
                if re.fullmatch(r'log_.+\.txt\.json', name):
                    path = os.path.join(j['runners'], name)
                    with contextlib.suppress(OSError, ValueError):
                        records[name[:-5]] = (self.prk.read_json(path), os.path.getmtime(path))
        if draining and j.get('what') != 'expand':
            known = {r['log'] for r in rows}
            names = set(records)
            if os.path.isdir(d):
                names.update(os.listdir(d))
            for name in sorted(names):
                if re.fullmatch(r'log_.+\.txt', name) and name not in known and not name.endswith(('.out.txt', '.err.txt')):
                    rows.append({'name': name[4:-4], 'log': name, 'state': 'pending', 'usd': None})
        for r in rows:
            ls, usd, tok, finished, modified = log_state(os.path.join(d, r['log']), since)
            original = r['state']
            if r['state'] in ('pending', 'running') and ls != 'pending':
                r['state'] = ls
            if r['log'] in records:
                identity, registered = records[r['log']]
                runner = process_identity(identity['pid'], identity.get('created'))
                if runner == 'live' or (runner == 'unknown' and not finished):
                    last = modified if modified is not None else registered
                    r['state'] = 'stale' if time.time() - last >= TASK_STALE else 'running'
                elif not finished:
                    r['state'] = 'failed'
            elif draining and not finished and (modified is not None or original == 'running'):
                last = modified if modified is not None else j.get('stoppedAt', j['started'])
                r['state'] = 'stale' if time.time() - last >= TASK_STALE else 'running'
            if r['usd'] is None:
                r['usd'] = usd
            r['tokens'] = tok
            r['problem'] = self.sign_in(os.path.join(d, r['log'])) if r['state'] == 'failed' else ''
        return rows

    def sign_in(self, path):
        """A refused sign-in (an expired login, a wrong key) at the end of a failed task's log, said plainly; or ''."""
        try:
            with open(path, 'rb') as f:
                f.seek(max(0, os.path.getsize(path) - 3000))
                return self.prk.sign_in_problem(f.read().decode('utf-8', 'replace'))
        except OSError:
            return ''

    def run_log_lines(self, j):
        if j.get('what') == 'expand':
            return self.prk.expand_run_lines(j['log'], j.get('logOffset', 0))
        try:
            with open(j['log'], 'rb') as f:
                f.seek(max(0, os.fstat(f.fileno()).st_size - 200000))
                return decode_lines(f.read())
        except OSError:
            return []

    def job_exit_code(self, j):
        if j.get('proc') is not None:
            return j['proc'].poll()
        if j.get('receipt'):
            try:
                with open(j['receipt'], encoding='ascii') as f:
                    return int(f.read(16))
            except (OSError, ValueError):
                pass
        return j.get('returncode')

    def job_status(self):
        """The page's check now (or the last one, until the next starts or it is put away): state, tasks, money."""
        with self.job_lock:
            j = self.job
            if not j:
                return None
            process = self.job_process()
            active = alive = process == 'live'
            code = self.job_exit_code(j) if not alive else None
            if j.get('stopped') and not j.get('stoppedAt'):
                j['stoppedAt'] = j['started']
            draining = bool(j.get('stopped') or (not alive and code is None and not j.get('final')))
            rows = self.job_tasks(j, draining)
            lines = self.run_log_lines(j)
            state = j.get('final') or ('running' if rows else 'preparing')
            problem = next((r['problem'] for r in rows if r.get('problem')), '')
            if draining:
                for r in rows:
                    if j.get('stopped') and r['state'] == 'pending':
                        r['state'] = 'never'
                if any(r['state'] == 'stale' for r in rows):
                    problem = '有任务超过 30 分钟没有更新日志，按已中断处理。'
            if not alive and not j.get('final'):
                if j.get('stopped'):
                    active = (any(r['state'] == 'running' for r in rows)
                              or (not j.get('runners') and time.time() - j['stoppedAt'] < STOP_GRACE))
                    if not active:
                        j['final'] = 'stopped'
                        if not self.record_ledger(j):
                            self.defer_ledger(j)
                    state = 'stopping'
                elif process == 'unknown' and code is None:
                    active = any(r['state'] == 'running' for r in rows)
                    state = 'unverified'
                    problem = '无法确认原检查进程的身份。可刷新再核对运行记录。'
                elif code is None and any(r['state'] == 'running' for r in rows):
                    active = True
                    state = 'stopping'
                elif j.get('what') == 'expand':
                    j['final'] = 'done' if j.get('proposal') and self.prk.expand_ok(
                        lines, j.get('runId'), code, j['proposal'], j.get('proposalBefore')) else 'error'
                    if j['final'] == 'error':
                        problem = problem or self.prk.api_text('expandFailed')
                else:
                    j['final'] = 'done' if code == 0 else 'failed' if code is not None and any(
                        'all tasks finished' in line for line in lines) else 'error'
                    if code is None:
                        problem = '没有拿到这次检查的退出码，无法确认全部成功。'
                if j.get('final'):
                    if (not j.get('stopped') and (any(line.strip() == 'Ledger     : pending' for line in lines)
                                                or (code is None and rows))):
                        self.defer_ledger(j)
                    j['returncode'] = code
                    j['ended'] = time.strftime('%Y-%m-%d %H:%M')
                    try:
                        self.save_job()
                    except OSError:
                        problem = '这次任务已经结束，但没保存任务状态。'
                    else:
                        if j.get('receipt'):
                            with contextlib.suppress(OSError):
                                os.remove(j['receipt'])
                        if j.get('runners'):
                            self.clear_runner_records(j)
            state = j.get('final') or ('stopping' if j.get('stopped') else state)
            if state == 'error':
                for r in rows:
                    if r['state'] == 'pending':
                        r['state'] = 'never'          # the orchestrator is gone: it will not start these
                    elif j.get('what') == 'expand':
                        r['state'] = 'failed'
            proj = self.job_project(j)
            for r in rows:
                r['label'] = self.prk.task_label(proj, r['name'])
            n = lambda *s: len([r for r in rows if r['state'] in s])
            cur = self.ctx.get('path') or ''
            if state in ('failed', 'error') and not problem:      # was it the sign-in?
                problem = self.prk.sign_in_problem('\n'.join(lines[-30:]))
            return {'id': j.get('id'), 'what': j.get('what'), 'round': os.path.basename(j['dir']), 'dir': self.prk.mask_home(j['dir']),
                    'thisProject': os.path.normcase(os.path.abspath(cur)) == os.path.normcase(os.path.abspath(j.get('project') or '')) if cur else False,
                    'projectName': j.get('projectName') or '', 'started': j.get('startedText') or '', 'ended': j.get('ended') or '',
                    'pay': j.get('pay'), 'providerName': j.get('providerName') or j.get('provider') or '', 'model': j.get('model') or '',
                    'alive': active, 'canStop': alive and not j.get('stopped'), 'state': state, 'stopped': bool(j.get('stopped')),
                    'returncode': j.get('returncode'), 'ledgerPending': bool(j.get('ledgerPending')),
                    'total': len(rows) or int(j.get('expected') or 0), 'done': n('ok', 'failed', 'skipped', 'stale'), 'ok': n('ok'), 'failed': n('failed', 'stale'),
                    'running': n('running'), 'pending': n('pending'), 'never': n('never'), 'skipped': n('skipped'),
                    'usd': round(sum(r['usd'] for r in rows if r['usd'] is not None), 4), 'tokens': sum(r['tokens'] or 0 for r in rows),
                    'tasks': rows, 'problem': problem, 'tail': self.prk.mask_home('\n'.join([x for x in lines if x.strip()][-12:]))}

    def start_job(self, body):
        """开始检查 / 只派一类玩家 / 写加内容的建议: start the orchestrator in the background (a new round folder, its
        output in _运行记录.txt there) and return at once. One check at a time."""
        prk, ctx, what = self.prk, self.ctx, body.get('what')
        with self.job_lock:
            status = self.job_status()
            if status and status['alive']:
                return {'ok': False, 'busy': True, 'error': '上一次检查还在进行，等它结束后才能开始。'}
            self.retry_ledgers()
            sent = body.get('confirmation')
            with self.lock:
                err = self.binding_error(sent, {'project': ctx.get('path'), 'projectVersion': self.project_version()})
                if err:
                    return err
            verified = self.plan(dict(body, mode=what, project=sent['project'], projectVersion=sent['projectVersion']))
            if not verified['ok']:
                return verified
            tasks = verified['confirmation']['tasks']
            err = self.binding_error(sent, verified['confirmation'])
            if err:
                return err
            with self.lock:
                if self.stop.is_set():
                    return {'ok': False, 'error': '页面正在退出。'}
                prk.refresh_state(ctx)
                err = self.binding_error(sent, {'project': ctx.get('path'), 'projectVersion': self.project_version()})
                if err:
                    return err
                proj = ctx.get('proj')
                if not proj:
                    return {'ok': False, 'error': '先选一个游戏。'}
                opts, err = self.run_options(body, what)
                if err:
                    if what == 'expand' and sent.get('report'):
                        return {'ok': False, 'changed': ['round', 'report'], 'error': err}
                    return {'ok': False, 'error': err}
                attempt = prk.run_id()
                proposal = None
                with self.args_as(opts):
                    binding = self.run_binding(what, opts)
                    err = self.binding_error(sent, binding)
                    if err:
                        return err
                    pay = body.get('pay')
                    if pay not in prk.PAYS:
                        return {'ok': False, 'error': '先选用什么付（会员额度，还是按次付费）。'}
                    if binding['pay'] and binding['pay'] != pay:
                        return self.binding_error({'pay': pay}, {'pay': binding['pay']})
                    err = prk.run_cannot(ctx, pay, what)
                    if err:
                        return {'ok': False, 'error': err}
                    if not binding['pay']:
                        err = prk.set_pay(ctx, pay=pay)
                        if err:
                            return {'ok': False, 'error': err}
                    pv, model = binding['provider'], binding['model']
                    run_ctx = dict(ctx, args=dict(ctx['args'], provider=pv, model=model), state=dict(ctx['state']))
                    if what == 'expand':
                        rp = binding['report']
                        out = os.path.dirname(rp)
                        proposal = prk.expand_output(run_ctx, rp, attempt)
                        cmd = prk.expand_cmd(run_ctx, rp, pay, attempt)
                    else:
                        out = new_round_dir(proj['reviewOutDir'])
                        run_ctx['args']['out'] = out
                        cmd = prk.api_args(run_ctx, [], pay)
                    pv_name = (prk.load_providers(ctx).get(pv) or {}).get('name') or pv
                    head = ['这一次：%s 在页面上点了「%s」。' % (time.strftime('%Y-%m-%d %H:%M:%S'),
                                                        {'run': '开始检查', 'quick': '只派一类玩家', 'expand': '让 AI 写建议'}[what]),
                            prk.pay_line(ctx, pay), '哪家的 AI：%s；型号：%s。' % (pv_name, model or '默认'),
                            '下面是检查脚本自己写的（英文）。', '']
                    ledger = prk.ledger_file(ctx)
                    prices = prk.read_local(ctx).get('prices')
                project, pname, cost_name = ctx['path'], proj.get('name') or proj.get('id') or '', prk.cost_name(proj)
            if not cmd or not cmd[0]:
                return {'ok': False, 'error': '找不到 PowerShell（Windows 自带；别的系统装 pwsh）。'}
            receipt = os.path.join(prk.STATE_DIR, 'run_exit_%s.txt' % attempt)
            gate = os.path.join(prk.STATE_DIR, 'run_start_%s.json' % attempt)
            runners = os.path.join(prk.STATE_DIR, 'runners_' + attempt)
            cmd, env = job_with_receipt(cmd, receipt, gate, runners)
            log = os.path.join(out, RUN_LOG)
            started = time.time()
            try:
                os.makedirs(out, exist_ok=True)
                os.makedirs(runners)
                with open(log, 'ab') as f:
                    offset = f.tell()
                    f.write(('\n'.join(head) + '\n').encode('utf-8'))
                    f.flush()
                    p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                         cwd=prk.KIT, creationflags=NO_WINDOW, env=env)
            except OSError as e:
                with contextlib.suppress(OSError):
                    os.rmdir(runners)
                return {'ok': False, 'error': '开不了：%s' % e}
            previous = self.job
            self.job = {'id': attempt, 'pid': p.pid, 'created': proc_info(p.pid)[1], 'proc': p,
                        'what': what, 'dir': out, 'log': log, 'started': started, 'startedText': time.strftime('%Y-%m-%d %H:%M'),
                        'expected': len(tasks), 'pay': pay, 'provider': pv, 'providerName': pv_name, 'model': model,
                        'project': project, 'projectName': pname, 'costName': cost_name, 'ledger': ledger, 'prices': prices,
                        'runId': attempt, 'logOffset': offset, 'proposal': proposal, 'receipt': receipt, 'runners': runners,
                        'stopped': False, 'final': ''}
            try:
                self.save_job()
                prk.atomic_json(gate, True)
            except OSError as e:
                self.job = previous
                try:
                    if p.poll() is None:
                        p.terminate()
                        p.wait(10)
                except (OSError, subprocess.TimeoutExpired) as stop_error:
                    return {'ok': False, 'error': '检查未获准派任务，暂时无法确认等待进程已退出：%s' % stop_error}
                with contextlib.suppress(OSError):
                    os.rmdir(runners)
                    if previous:
                        self.save_job()
                    else:
                        os.remove(self.job_path())
                return {'ok': False, 'error': '没能保存或放行本次检查，未派出任务：%s' % e}
            return {'ok': True, 'job': self.job_status()}

    def stop_job(self):
        """「停下」: end the orchestrator. Queued tasks never start; running ones finish on their own (and are paid for)."""
        with self.job_lock:
            j = self.job
            if not j or j.get('final') or j.get('stopped'):
                return {'ok': False, 'error': '现在没有在跑的检查。'}
            try:
                if j.get('proc') is not None:
                    if j['proc'].poll() is not None:
                        return {'ok': False, 'error': '现在没有在跑的检查。'}
                    j['proc'].terminate()
                    try:
                        j['proc'].wait(10)
                    except subprocess.TimeoutExpired:
                        pass
                else:
                    proc_kill(j['pid'], j.get('created'))
            except OSError as e:
                return {'ok': False, 'error': '停不下来：%s' % e}
            j['stopped'] = True
            j['stoppedAt'] = time.time()
            try:
                with open(j['log'], 'ab') as f:
                    f.write(('\n（%s 在页面上点了「停下」：排着队的不再开始；已经开跑的会自己跑完，照样花钱或用额度。）\n'
                             % time.strftime('%H:%M:%S')).encode('utf-8'))
            except OSError:
                pass
            try:
                self.save_job()
            except OSError as e:
                return {'ok': False, 'error': '已停止派新任务，但没保存停止状态：%s' % e}
            return {'ok': True, 'job': self.job_status()}

    def clear_job(self):
        """「知道了」: put away a check that has ended (the page stops showing it)."""
        with self.job_lock:
            status = self.job_status()
            if status and status['alive']:
                return {'ok': False, 'error': '这次检查还在跑。'}
            try:
                os.remove(self.job_path())
            except FileNotFoundError:
                pass
            except OSError as e:
                return {'ok': False, 'error': '没能收起这次检查：%s' % e}
            if self.job and self.job.get('runners'):
                self.clear_runner_records(self.job)
            self.job = None
            return {'ok': True}

    def clear_runner_records(self, j):
        if not re.fullmatch(r'[A-Za-z0-9_-]+', j['id']):
            return
        folder = os.path.join(self.prk.STATE_DIR, 'runners_' + j['id'])
        with contextlib.suppress(OSError):
            for name in os.listdir(folder):
                if re.fullmatch(r'log_.+\.txt\.json(?:\.tmp)?', name):
                    os.remove(os.path.join(folder, name))
            os.rmdir(folder)


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'prk-ui'

        def log_message(self, fmt, *args):   # quiet: the terminal stays readable
            pass

        def send(self, code, body, ctype='application/json; charset=utf-8'):
            data = body if isinstance(body, bytes) else body.encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Content-Security-Policy', "frame-ancestors 'none'")
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(data)

        def json(self, obj, code=200):
            self.send(code, json.dumps(obj, ensure_ascii=False))

        def local_host(self):
            hosts = self.headers.get_all('Host') or []
            return len(hosts) == 1 and bool(re.fullmatch(r'(?:127\.0\.0\.1|localhost)(?::[0-9]+)?', hosts[0], re.I))

        def allowed(self):
            token = (self.headers.get('X-PRK-Token') or '').encode('utf-8')
            return self.local_host() and secrets.compare_digest(token, app.token.encode('ascii'))

        def do_GET(self):
            u = urlparse(self.path)
            if u.path == '/alive':          # for a second start: "is the service already running here?" (no data)
                return self.send(200, 'prk-ui', 'text/plain; charset=utf-8')
            if u.path in ('/', '/index.html'):
                if not self.local_host():
                    return self.json({'ok': False, 'error': 'forbidden'}, 403)
                with open(os.path.join(HERE, 'index.html'), encoding='utf-8') as f:
                    html = f.read().replace('__PRK_TOKEN__', app.token)
                return self.send(200, html, 'text/html; charset=utf-8')
            if not u.path.startswith('/api/'):
                return self.send(404, 'not found', 'text/plain; charset=utf-8')
            if not self.allowed():
                return self.json({'ok': False, 'error': 'forbidden'}, 403)
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            try:
                if u.path == '/api/ping':
                    app.last_ping = time.time()
                    return self.json({'ok': True})
                if u.path == '/api/jobs':        # reads the round's files only: no need to wait for the lock
                    return self.json({'ok': True, 'job': app.job_status(), 'ledgerNotice': app.ledger_notice()})
                if u.path == '/api/overview':    # the check's state is added outside the lock (start_job takes job_lock first)
                    with app.lock:
                        app.prk.refresh_state(app.ctx)
                        ov = app.overview()
                    ov['job'] = app.job_status()
                    ov['ledgerNotice'] = app.ledger_notice()
                    return self.json(ov)
                with app.lock:
                    app.prk.refresh_state(app.ctx)     # the terminal may have changed the choices meanwhile
                    if u.path == '/api/round':
                        r = app.round_detail(q.get('id', ''))
                        return self.json(r) if r else self.json({'ok': False, 'error': '没有这一轮'}, 404)
                    if u.path == '/api/file':
                        r = app.read_file(q.get('round', ''), q.get('name', ''))
                        return self.json(r) if r else self.json({'ok': False, 'error': '读不了这个文件'}, 404)
                    if u.path == '/api/library':
                        return self.json(app.library())
                    if u.path == '/api/costs':
                        cl = app.prk.ledger_mod()
                        path = app.prk.ledger_file(app.ctx)
                        rows = cl.read_ledger(path)
                        return self.json({'file': path, 'summary': cl.summarize(rows), 'rows': rows[-400:]})
                    if u.path == '/api/fixes':
                        return self.json(app.fixes(q.get('round', '')))
                    if u.path == '/api/decisions':
                        d, sample = app.round_dir(q.get('round', ''))
                        proj = app.ctx.get('proj')
                        path = app.prk.decisions_file(proj, sample) if proj else ''
                        return self.json({'file': path, 'rows': app.prk.read_decisions(path), 'sample': sample})
                    if u.path == '/api/provider/form':
                        return self.json(app.provider_form(q.get('name', '')))
                    if u.path == '/api/newproject':
                        return self.json({'ok': True, 'folder': os.path.join(app.prk.KIT, 'projects'),
                                          'questions': [{'key': k, 'label': t, 'default': dv, 'kind': w} for k, t, dv, w in app.prk.NEW_PROJECT_QUESTIONS]})
            except (OSError, ValueError, SystemExit) as e:
                return self.json({'ok': False, 'error': '%s: %s' % (type(e).__name__, e)}, 500)
            return self.json({'ok': False, 'error': 'not found'}, 404)

        def do_POST(self):
            u = urlparse(self.path)
            if not self.allowed():
                return self.json({'ok': False, 'error': 'forbidden'}, 403)
            try:
                n = int(self.headers.get('Content-Length') or 0)
                body = json.loads(self.rfile.read(n).decode('utf-8')) if 0 < n < 200000 else {}
            except ValueError:
                return self.json({'ok': False, 'error': 'bad request'}, 400)
            if not isinstance(body, dict):
                return self.json({'ok': False, 'error': 'bad request'}, 400)
            if u.path == '/api/quit':
                result = app.request_quit()
                if not result['ok']:
                    return self.json(result)
                try:
                    return self.json(result)
                finally:
                    self.server.shutdown()
            try:
                if u.path == '/api/guide':       # slow (a model answers): must not hold the lock the pages need
                    if not body.get('confirmed'):
                        return self.json({'ok': False, 'error': '要先在页面上点确认。'}, 400)
                    return self.json(app.guide(body))
                if u.path == '/api/fix' and body.get('action') == 'run':     # slow too: an AI changes files
                    if not body.get('confirmed'):
                        return self.json({'ok': False, 'error': '要先在页面上点确认。'}, 400)
                    return self.json(app.fix_run(body))
                if u.path == '/api/run':        # plan: a dry run, a few seconds; run / quick / expand: started in the background
                    what = body.get('what')
                    if what == 'plan':
                        return self.json(app.plan(body))
                    if what not in ('run', 'quick', 'expand'):
                        return self.json({'ok': False, 'error': 'what 只能是 plan、run、quick、expand。'}, 400)
                    if body.get('confirmed') is not True:
                        return self.json({'ok': False, 'error': '要先在页面上点确认。'}, 400)
                    return self.json(app.start_job(body))
                if u.path == '/api/jobs/stop':
                    return self.json(app.stop_job())
                if u.path == '/api/jobs/clear':
                    return self.json(app.clear_job())
                if u.path == '/api/cite':        # a few seconds, free; runs outside the lock
                    return self.json(app.cite(body))
                with app.lock:
                    app.prk.refresh_state(app.ctx)     # change what is in the file now, not an old copy of it
                    if u.path == '/api/decide':
                        return self.json(app.decide(body))
                    if u.path == '/api/fix':
                        return self.json(app.fix_action(body))
                    if u.path == '/api/budget':
                        err = app.prk.set_budget(app.ctx, body.get('budget'))
                        return self.json({'ok': not err, 'error': err})
                    if u.path == '/api/pay':
                        return self.json(app.set_pay(body))
                    if u.path == '/api/project':
                        return self.json(app.set_project(body))
                    if u.path == '/api/model':
                        err = app.prk.set_model(app.ctx, str(body.get('model') or ''))
                        return self.json({'ok': not err, 'error': err})
                    if u.path == '/api/provider':
                        err = app.prk.set_provider(app.ctx, str(body.get('provider') or ''))
                        return self.json({'ok': not err, 'error': err})
                    if u.path == '/api/provider/setup':
                        return self.json(app.provider_setup(body))
                    if u.path == '/api/local':
                        dst, err = app.prk.save_machine_paths(app.ctx, {k: body[k] for k in ('python', 'claudeExe') if k in body})
                        return self.json({'ok': not err, 'error': err, 'machine': app.prk.machine_paths(app.ctx)})
                    if u.path == '/api/newproject':
                        return self.json(app.new_project(body))
            except (OSError, ValueError, SystemExit) as e:
                return self.json({'ok': False, 'error': '%s: %s' % (type(e).__name__, e)}, 500)
            return self.json({'ok': False, 'error': 'not found'}, 404)

    return Handler


def open_window(url):
    """A window without tabs and an address bar when a Chromium browser is there (it looks like a program); otherwise
    the default browser."""
    names = ['msedge', 'chrome', 'chromium', 'brave']
    guesses = []
    for var in ('ProgramFiles(x86)', 'ProgramFiles', 'LOCALAPPDATA'):
        base = os.environ.get(var)
        if base:
            guesses += [os.path.join(base, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
                        os.path.join(base, 'Google', 'Chrome', 'Application', 'chrome.exe')]
    exe = next((shutil.which(n) for n in names if shutil.which(n)), None) or next((g for g in guesses if os.path.exists(g)), None)
    if exe:
        try:
            subprocess.Popen([exe, '--app=%s' % url, '--window-size=1280,860'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except OSError:
            pass
    return webbrowser.open(url)


def service_responds(url):
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url + 'alive', timeout=2) as r:
            return r.read(16) == b'prk-ui'
    except OSError:
        return False


def running_url(prk):
    """The address of a service that is already running on this computer, or None."""
    p = os.path.join(prk.STATE_DIR, 'ui.json')
    try:
        with open(p, encoding='utf-8') as f:
            marker = json.load(f)
        url, pid = marker['url'], int(marker['pid'])
        if not re.fullmatch(r'http://127\.0\.0\.1:\d+/', url):
            return None
        identity = process_identity(pid, marker.get('created'))
        if identity != 'gone' and service_responds(url):
            return url
    except (OSError, ValueError, AttributeError, TypeError, KeyError):
        return None
    if identity == 'live':
        raise OSError('已登记的页面进程还在，但没响应。等一下再打开。')
    return None


def watch(app, httpd):
    """Stop the service after an idle period if no work is running."""
    while not app.stop.wait(5):
        now = time.time()
        job = app.job_status() if app.job and not app.job.get('final') else None
        if app.busy or (job and job['alive']):
            continue
        if (app.last_ping is None and now - app.started > NEVER_OPENED
                or app.last_ping is not None and now - app.last_ping > IDLE_STOP):
            if app.request_quit()['ok']:
                return httpd.shutdown()


@contextlib.contextmanager
def startup_lock(prk):
    os.makedirs(prk.STATE_DIR, exist_ok=True)
    with open(os.path.join(prk.STATE_DIR, 'ui.lock'), 'a+b') as f:
        if os.name == 'nt':
            import msvcrt
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX)
            yield                         # closing the file releases the lock, including after a crash


def serve(prk, ctx, port=0, open_browser=True, keep=False):
    """keep disables idle shutdown; the page can always request an explicit exit."""
    marker = os.path.join(prk.STATE_DIR, 'ui.json')
    httpd = servicing = None
    try:
        with startup_lock(prk):
            url = running_url(prk)
            if not url:
                app = App(prk, ctx)
                httpd = ThreadingHTTPServer(('127.0.0.1', port), make_handler(app))
                httpd.daemon_threads = True
                url = 'http://127.0.0.1:%d/' % httpd.server_address[1]
                registration = {'url': url, 'pid': os.getpid(), 'created': proc_info(os.getpid())[1]}
                servicing = threading.Thread(target=httpd.serve_forever, daemon=True)
                servicing.start()
                if not service_responds(url):
                    raise OSError('页面服务启动后没有响应。')
                prk.atomic_json(marker, registration)
    except OSError as e:
        if servicing:
            httpd.shutdown()
            servicing.join()
        if httpd:
            httpd.server_close()
        prk.say('开不了页面（端口 %s）：%s' % (port or '自动', e))
        return 2
    if httpd is None:
        prk.say('页面已经开着：%s（又开了一个窗口）' % url)
        if open_browser:
            open_window(url)
        return 0
    prk.say('页面开在：%s' % url)
    prk.say('只有这台电脑能打开。' + ('可按 Ctrl+C 或点页面上的「退出」。' if keep else '关掉页面的窗口，过一会儿它自己停；页面上的「退出」马上停。'))
    if not keep:
        threading.Thread(target=watch, args=(app, httpd), daemon=True).start()
    try:
        if open_browser:
            open_window(url)
        while servicing.is_alive():
            servicing.join(0.5)
    except KeyboardInterrupt:
        prk.say()
    finally:
        httpd.shutdown()
        httpd.server_close()
        try:
            with startup_lock(prk):
                if prk.read_json(marker) == registration:
                    os.remove(marker)
        except (OSError, ValueError):
            pass
        prk.say('页面停了。')
    return 0
