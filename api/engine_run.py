"""Run one task with another reviewer program than Claude Code (only the standard library).

Which program does the review is decided by the provider (api\\providers.json, `engine`):
  claude-code   Claude Code (run_api_task.ps1 runs it itself; this file is not used)
  codex         OpenAI Codex CLI   (`codex exec`)       — GPT models
  gemini        Google Gemini CLI  (`gemini -p`)         — Gemini models

These programs run **read-only** here: they read the work and the task, and do not write anything. Every file the task
asks for (the report, the draft, the map's tables) comes back in their final answer, each part headed by a line
    =====FILE: <path>=====
and this script writes the parts — only inside the folder of the task file (the round's folder). A part that points
anywhere else is not written and is noted in the log. An answer without such lines is the report itself.

The log is written like run_api_task.ps1 writes Claude Code's: a first line "started …, model …, workdir …, paid by …,
provider …", the program's own output, one result line in Claude Code's JSON shape (type "result", subtype, is_error,
num_turns, duration_ms, usage; total_cost_usd is null: these programs do not report money — the price table of the
machine settings does), and "finished …, exit N". So run_result.ps1, the cost table and the ledger read it unchanged.

Called by run_api_task.ps1 (which has already set the key and the isolation variables); not meant to be run by hand.
  python -I engine_run.py --engine codex|gemini --task <task.md> --log <log.txt> --workdir <dir> [--model m]
         [--exe path] [--max-turns n] [--never-read "a;b"] [--read-only "a;b"] [--answer] [--paid "api key"] [--provider p]
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

MARK = re.compile(r'^=====FILE:\s*(.+?)\s*=====\s*$', re.M)
# The task templates put the primary deliverable on a "- …写到：…" line.
REPORT_LINE = re.compile(r'^-[ \t]+[^：:\r\n]*写到[：:][ \t]*'
                         r'[\x60"\x27]?([^\r\n]+\.md)[\x60"\x27]?[ \t]*(?:[（(][^\r\n]*)?$', re.M | re.I)


def now():
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def find_exe(name, given):
    if given:
        if os.path.isdir(given):
            for n in (name + '.cmd', name + '.exe', name):
                p = os.path.join(given, n)
                if os.path.exists(p):
                    return p
        return given if os.path.exists(given) else None
    return shutil.which(name)


def contract(task_dir, answer):
    """What the program is told about writing (it cannot write: every file comes back in the answer)."""
    if answer:
        return ('You cannot write or change any file, and you must not run commands that change anything. '
                'Print only the answer, in the delivery language requested in the task file.')
    return ('You cannot write files in this run: do NOT try to create or edit any file, and do not run commands that '
            'change anything. Read what you need with your read and search tools. When the task says to write a file '
            '(the report, a draft, tables), put its whole content into your final answer instead, each file starting '
            'with its own line exactly like\n=====FILE: <the full path the task gives>=====\nfollowed by the file\'s '
            'content. Only paths inside %s are accepted. Write nothing else outside these file blocks except one short '
            'summary line at the very end. The static tables the task mentions already exist: read them, do not try '
            'to run scripts.' % task_dir)


def prompt_for(task, workdir, never, readonly, answer):
    task_dir = os.path.dirname(os.path.abspath(task))
    text = 'Read the task file %s (UTF-8) and do exactly what it says, working in %s. ' % (task, workdir)
    if answer:
        rel = os.path.relpath(task, workdir) if os.path.abspath(task).lower().startswith(os.path.abspath(workdir).lower()) else task
        text = 'Read the task file %s (UTF-8). It holds a question and how to answer it. Read only files inside the current folder. ' % rel
    if never and not answer:
        text += 'Never read, list or search anything under %s. ' % ', '.join(never)
    if readonly and not answer:
        text += "Don't modify %s. " % ', '.join(readonly)
    return text + contract(task_dir, answer)


# ---------- the programs ----------

def run_codex(exe, a, prompt, out_last):
    # read-only sandbox, no approvals asked (exec never asks), no git check, the final message into a file, JSON events
    cmd = [exe, 'exec', '--json', '-s', 'read-only', '--skip-git-repo-check', '-C', a['workdir'], '-o', out_last]
    if a.get('model'):
        cmd += ['-m', a['model']]
    cmd += ['-']                     # the prompt comes on stdin (no length or quoting trouble)
    return cmd, prompt


def parse_codex(stdout, out_last):
    usage = {'input_tokens': 0, 'output_tokens': 0, 'cache_read_input_tokens': 0}
    turns, failed, errors = 0, False, []
    for ln in stdout.splitlines():
        ln = ln.strip()
        if not ln.startswith('{'):
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        t = ev.get('type', '')
        if t == 'turn.completed':
            turns += 1
            u = ev.get('usage') or {}
            usage['input_tokens'] += int(u.get('input_tokens') or 0) - int(u.get('cached_input_tokens') or 0)
            usage['cache_read_input_tokens'] += int(u.get('cached_input_tokens') or 0)
            usage['output_tokens'] += int(u.get('output_tokens') or 0) + int(u.get('reasoning_output_tokens') or 0)
        elif t in ('turn.failed', 'error'):
            failed = True
            errors.append(str(ev.get('message') or ev.get('error') or t)[:300])
    text = ''
    try:
        with open(out_last, encoding='utf-8', errors='replace') as f:
            text = f.read()
    except OSError:
        pass
    return text, usage, turns, failed, errors


def run_gemini(exe, a, prompt, home):
    # read tools only (the write and shell tools are taken out in the settings below), JSON output
    cmd = [exe, '-o', 'json', '--approval-mode', 'default']
    if a.get('model'):
        cmd += ['-m', a['model']]
    task_dir = os.path.dirname(os.path.abspath(a['task']))
    if not os.path.abspath(task_dir).lower().startswith(os.path.abspath(a['workdir']).lower()):
        cmd += ['--include-directories', task_dir]
    cmd += ['-p', 'Follow the instructions given on standard input.']
    settings = {'tools': {'exclude': ['write_file', 'replace', 'run_shell_command', 'web_fetch', 'google_web_search']},
                'model': {'maxSessionTurns': int(a.get('max_turns') or 200)}}
    os.makedirs(os.path.join(home, '.gemini'), exist_ok=True)
    with open(os.path.join(home, '.gemini', 'settings.json'), 'w', encoding='utf-8') as f:
        json.dump(settings, f)
    return cmd, prompt


def parse_gemini(stdout):
    usage = {'input_tokens': 0, 'output_tokens': 0, 'cache_read_input_tokens': 0}
    i = stdout.find('{')
    data = None
    while i >= 0 and data is None:
        try:
            data = json.loads(stdout[i:])
        except ValueError:
            i = stdout.find('\n{', i + 1)
            i = i + 1 if i >= 0 else -1
    if not isinstance(data, dict):
        return '', usage, 0, True, ['no JSON in the output']
    turns = 0

    def walk(o):                     # token counts by name, wherever they sit under stats (the layout is per model)
        nonlocal turns
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    kl = k.lower()
                    if kl in ('prompt', 'input', 'prompt_tokens', 'input_tokens'):
                        usage['input_tokens'] += int(v)
                    elif kl in ('candidates', 'output', 'candidates_tokens', 'output_tokens', 'thoughts'):
                        usage['output_tokens'] += int(v)
                    elif kl in ('cached', 'cached_tokens'):
                        usage['cache_read_input_tokens'] += int(v)
                    elif kl in ('totalrequests', 'total_requests'):
                        turns += int(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(data.get('stats') or {})
    usage['input_tokens'] = max(0, usage['input_tokens'] - usage['cache_read_input_tokens'])
    err = data.get('error')
    return str(data.get('response') or ''), usage, turns, bool(err), ([json.dumps(err, ensure_ascii=False)[:300]] if err else [])


# ---------- writing what came back ----------

def report_path(task):
    with open(task, encoding='utf-8-sig', errors='replace') as f:
        match = REPORT_LINE.search(f.read())
    return match.group(1) if match else None


def write_parts(text, task, report):
    """Write the =====FILE: path===== parts inside the task's folder. Returns (written, refused)."""
    root = os.path.realpath(os.path.dirname(os.path.abspath(task)))
    marks = list(MARK.finditer(text))
    parts = []
    if marks:
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
            body = text[m.end():end].strip('\n')
            if body.strip():
                parts.append((m.group(1).strip().strip('`"\''), body + '\n'))
    else:
        if report and text.strip():
            parts.append((report, text.strip() + '\n'))
    written, refused = [], []
    for path, body in parts:
        full = os.path.realpath(path if os.path.isabs(path) else os.path.join(root, path))
        try:
            inside = full != root and os.path.normcase(os.path.commonpath([root, full])) == os.path.normcase(root)
        except ValueError:            # another drive
            inside = False
        if not inside:
            refused.append(path)
            continue
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8', newline='\n') as f:
            f.write(body)
        written.append(full)
    return written, refused


def main():
    args = sys.argv[1:]
    a = {}
    i = 0
    while i < len(args):
        k = args[i].lstrip('-').replace('-', '_')
        if k in ('answer',):
            a[k] = True
            i += 1
        elif i + 1 >= len(args) or args[i + 1].startswith('--'):
            a[k] = ''                 # Windows PowerShell drops empty arguments: a flag without its value means ''
            i += 1
        else:
            a[k] = args[i + 1]
            i += 2
    engine, task, log = a['engine'], os.path.abspath(a['task']), a['log']
    never = [x for x in (a.get('never_read') or '').split(';') if x.strip()]
    readonly = [x for x in (a.get('read_only') or '').split(';') if x.strip()]
    with open(log, 'w', encoding='utf-8') as lf:
        lf.write('started %s, model %s, workdir %s, paid by %s, provider %s\n' % (
            now(), a.get('model') or '(cli default)', a['workdir'], a.get('paid') or 'api key', a.get('provider') or engine))
    if a.get('paid') == 'subscription login':
        folder = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(folder, 'providers.json'), encoding='utf-8-sig') as f:
            blocked = json.load(f).get('subscriptionUnsupported') or {}
        if engine in blocked:
            with open(os.path.join(folder, 'texts.json'), encoding='utf-8-sig') as f:
                message = json.load(f)[blocked[engine]]
            with open(log, 'a', encoding='utf-8') as lf:
                lf.write('%s\nfinished %s, exit 2\n' % (message, now()))
            sys.stderr.write(message + '\n')
            return 2
    exe = find_exe({'codex': 'codex', 'gemini': 'gemini'}[engine], a.get('exe'))
    if not exe:
        with open(log, 'a', encoding='utf-8') as lf:
            lf.write('%s not found: install it, or set %sExe in the machine settings.\nfinished %s, exit 127\n' % (engine, engine, now()))
        sys.stderr.write('%s not found\n' % engine)
        return 127
    prompt = prompt_for(task, a['workdir'], never, readonly, a.get('answer'))
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix='prk_%s_' % engine) as tmp:
        env = dict(os.environ)
        out_last = os.path.join(tmp, 'last.txt')
        if engine == 'codex':
            cmd, stdin = run_codex(exe, a, prompt, out_last)
        else:
            env['GEMINI_CLI_HOME'] = tmp
            cmd, stdin = run_gemini(exe, a, prompt, tmp)
        try:
            r = subprocess.run(cmd, input=stdin, capture_output=True, text=True, encoding='utf-8', errors='replace',
                               cwd=a['workdir'], env=env, timeout=int(a.get('timeout') or 7200))
            out, err, code = r.stdout or '', r.stderr or '', r.returncode
        except subprocess.TimeoutExpired as e:
            out, err, code = (e.stdout or '') if isinstance(e.stdout, str) else '', 'timeout', 124
        except OSError as e:
            out, err, code = '', str(e), 1
        if engine == 'codex':
            text, usage, turns, failed, errors = parse_codex(out, out_last)
        else:
            text, usage, turns, failed, errors = parse_gemini(out)
    written, refused = [], []
    try:
        if not a.get('answer'):
            report = report_path(task)
            written, refused = write_parts(text, task, report)
            expected = os.path.normcase(os.path.realpath(os.path.join(os.path.dirname(task), report))) if report else None
            if expected not in {os.path.normcase(p) for p in written}:
                errors.append('required report was not written: %s' % (report or 'no report path in the task'))
                failed = True
    except (OSError, ValueError) as e:  # the result line below must still be written
        written, refused = [], []
        errors.append('could not write the files of the answer: %s' % e)
        failed = True
    ok = code == 0 and not failed and bool(text.strip())
    code = 0 if ok else (code or 1)
    result = {'type': 'result', 'subtype': 'success' if ok else 'error_during_execution', 'is_error': not ok,
              'total_cost_usd': None, 'num_turns': turns, 'duration_ms': int((time.time() - t0) * 1000), 'usage': usage,
              'engine': engine, 'result': text if a.get('answer') else (text[-400:] if text else '; '.join(errors)),
              'files_written': len(written), 'files_refused': refused}
    with open(log, 'a', encoding='utf-8') as lf:
        lf.write(err[-4000:] + ('\n' if err and not err.endswith('\n') else ''))
        for e in errors:
            lf.write('error: %s\n' % e)
        for p in refused:
            lf.write('refused to write outside the round folder: %s\n' % p)
        lf.write(json.dumps(result, ensure_ascii=False) + '\n')
        lf.write('finished %s, exit %d\n' % (now(), code))
    return code


if __name__ == '__main__':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.exit(main())
