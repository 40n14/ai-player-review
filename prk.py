#!/usr/bin/env python3
"""玩家视角审查工具包的命令行。给 AI 和脚本用。

这个工具包替的是哪一段：游戏上线以后有一圈"玩家反馈 → 官方修改完善"。这里用 AI 把这一圈提前跑一部分：
  模拟不同的玩家去玩 → 他们的反馈 → 你决定（decide）→ 改作品 → 再来一轮，先核上一轮的反馈改好了没有。

  负责人：让自己的 AI 读 AGENTS.md，然后说「从玩家视角审查一下」。
  AI：用 prk prepare 准备任务，完成后用 prk page 生成离线报告页面。
  prk              进终端菜单
  prk <命令> ...   直接做一件事

一圈里的命令（按先后）：
  check      检查项目设置和机器设置
  static     跑静态表（不花钱）
  plan       演习：这样跑会有哪些任务（不花钱，不调 API）
  prepare    跑静态表、写这一轮的任务文件和 _prepared.json（不调 AI）。--who "15 + 18" 只派一类玩家
  run        正式跑一轮审查（用会员额度或按次付费，见 pay；会先问，--yes 不问）。跑完把玩家反馈显示在终端
  quick      只问一类玩家：prk quick "15 + 18"（画像编号；--kind 走法 id，不写 = persona）。一个任务，跑完直接显示他的反馈
  feedback   看玩家反馈：显示在终端；--save 文件 = 另存一份；--full = 整份报告（[文件夹] 或 --from 报告，不写 = 最近一次）
  cite       引文核验：报告里写的出处，作品里是不是真有（不花钱）
  page       核对出处并生成 review.md 和离线 review.html（--round 轮次；--open 打开）
  decide     记下每条决定（--set "S1=修; W1=放进待做: 等下个版本"；--round 轮次；支持 --json）
  fix        待修清单：prk fix = 列出还没修的和修好了的（还有一句交给你自己的 AI 的话）；
             prk fix F3 = 派 AI 去改游戏的文件，只修这一条（用额度或花钱；先备份，会先问，--yes 不问）；
             prk fix F3 --undo = 照备份改回去；--done = 手动标成修好了；--reopen = 放回还没修的
  expand     可选：把「想要但没有的」变成内容提案和草稿（用额度或花钱；--items W1,W3；不改作品）
怎么付：
  pay        prk pay = 看现在怎么付；prk pay sub = 用会员额度（这台电脑上登录的账号，不另外花钱，但会用掉额度）；
             prk pay api = 按次付费（用钥匙 key，按用量花钱）；prk pay guide sub|api = 问 AI 单独设；prk pay guide same = 跟检查一样。
             只这一次：run、quick、expand、guide 后面加 --pay sub|api。没设过又不在终端里：不跑（退出码 2）
             会员额度只有 anthropic（Claude Code 的登录）、openai（Codex 的 ChatGPT 登录）能用
模型：
  provider   用哪家的模型：prk provider = 列出能接的（Anthropic、DeepSeek、Kimi、智谱、MiniMax、通义、OpenRouter、自己的网关、
             Bedrock、Vertex、Foundry）；prk provider <名字> = 换并记住；prk provider setup <名字> = 写 key 放在哪
  model      用哪个模型：prk model = 看现在用的和可选的；prk model <id> = 换并记住（run、quick、expand、guide 都用它）；
             prk model default = 忘掉。只这一次用别的：命令后面加 --model <id>
页面和向导：
  ui         打开可选的本机页面（需要后台服务）：试一下、开始检查、看进度和玩家反馈、记决定、待修清单、
             设置（怎么付、哪家 AI、钥匙放在哪、这台电脑）、新加一个游戏、问向导，都在页面上点；--runner 给开始检查换 runner（测试用）
             关掉窗口，过一会儿它自己停；--keep = 一直开着直到 Ctrl+C；--port N；--no-open 不自动开窗口
  guide      不知道下一步：prk guide = 照文件算出现在该做什么（不花钱）；
             prk guide "问题" [--pay sub|api] = 问 AI 向导（不写 = prk pay 记住的；--mode 是 --pay 的旧名字）
看和配：
  presets    列预设（一类游戏一份现成的画像对照）
  kinds      列审查种类                   personas   列画像（--find 词）
  groups     列这个项目的审查组             suggest    这一类游戏该派哪些画像（suggest RPG）
  reports    列最近几次审查                 cost       看一轮的花费表
  costs      花费总账：每个任务一行、跨轮次（第一行是这个月的数；--rebuild = 把所有轮次重记一遍；
             --budget 20 = 每个月最多花 20 美元，只提醒、不拦；--budget 0 = 不设；--json）
  ask        查看该怎么请自己的 AI 在对话里审查
  fake       假 runner 走一遍排队和合并（不花钱，数字是假的）
设置：
  new        新建一份项目设置（向导；--fields 或 --from-json 文件 支持 --json）
  local      写机器设置（只问 key 放在哪，不问 key）
  install    可选：把指路牌和审查员装进项目的 .claude

公用的参数：-p / --project <项目设置.json>   --local <机器设置.json>
            --json   给 AI 和脚本读，见 for-ai/REFERENCE.md
run / quick / expand / guide / fix：--provider 名字  --model 模型  --pay sub|api（只这一次）
plan / fake / run / quick：--groups A,B  --split  --parallel N  --no-map  --map-dir 文件夹  --scope 文字
                           --out 文件夹  --model 模型  --no-merge  --max-turns N  --save 文件（跑完把反馈另存一份）
feedback / decide / expand：--from 报告  --items W1,W3

退出码：0 = 做成了；1 = 做了但有问题（检查没过、任务失败、没找到报告）；2 = 用法或环境不对。
花钱或用额度的命令（run、quick、expand、fix F3，和 guide "问题"）不在终端里时必须带 --yes，否则不跑；还要知道怎么付（--pay 或 prk pay）。
给 AI 的操作说明在 AGENTS.md。只用标准库。prepare、plan、run、quick、expand、fake、install 要 PowerShell（Windows 自带；别的系统装 pwsh）。
"""
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from collections import OrderedDict

KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(KIT, 'static'))   # -I drops the script folder from the path
sys.dont_write_bytecode = True
import projfile  # noqa: E402
from report_format import (CHECK, CONFIDENCE, LANGUAGES, SECTIONS, existing_reports, filename_warnings, is_merged,
                           language, named_path, names, report_aliases)  # noqa: E402

PREFERRED_STATE_DIR = os.path.abspath(os.environ.get('PLAYER_REVIEW_STATE') or os.path.join(
    os.environ.get('LOCALAPPDATA') or os.path.join(os.path.expanduser('~'), '.config'), 'PlayerReviewKit'))
STATE_DIR = PREFERRED_STATE_DIR
STATE_FILE = os.path.join(STATE_DIR, 'state.json')
STATE_TEMPORARY = False


def select_state_dir():
    global STATE_DIR, STATE_FILE, STATE_TEMPORARY

    def writable(folder):
        try:
            os.makedirs(folder, exist_ok=True)
            probe = os.path.join(folder, '.write-test-' + secrets.token_hex(12))
            # On Windows, tempfile can retry denied creates when os.access still says the directory is writable.
            with open(probe, 'xb'):
                pass
            os.remove(probe)
            path = os.path.join(folder, 'state.json')
            if os.path.lexists(path):
                with open(path, 'r+b'):
                    pass
            return True
        except OSError:
            return False

    if not writable(PREFERRED_STATE_DIR):
        try:
            STATE_DIR = os.path.join(tempfile.gettempdir(), 'PlayerReviewKit')
        except OSError:    # commands that only read can still work
            pass
        else:
            STATE_TEMPORARY = True
    STATE_FILE = os.path.join(STATE_DIR, 'state.json')
    os.environ['PLAYER_REVIEW_STATE'] = STATE_DIR


# ---------- small helpers ----------

def say(text=''):
    print(text)


def out_json(obj):
    """--json: the only thing on stdout is this."""
    if isinstance(obj, dict):
        obj = dict(obj, state={'dir': STATE_DIR, 'temporary': STATE_TEMPORARY})
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def output_metadata(proj, folder=None):
    data = {'language': (proj or {}).get('language', 'zh')}
    warnings = filename_warnings(proj, folder)
    if warnings:
        data['warnings'] = warnings
    return data


def delivery_task(proj, text, *, format_guide=None):
    text = re.sub(r'(?m)^> \[PRK language\][^\n]*\n\n', '', text)
    if language(proj) == 'en':
        guide = format_guide or os.path.join(KIT, 'docs', 'report-format.md')
        return '# Delivery language: English\n\n%s\n\nReport format guide: %s\n\n%s' % (
            api_text('deliveryInstruction'), guide, text)
    return text


def task_placeholder(filename, text):
    marker = re.search(r'\{\{[^{}]+\}\}', text)
    return '任务文件 %s 有没填上的记号 %s。' % (filename, marker[0]) if marker else ''


def want_json(ctx):
    return bool(ctx['args'].get('json'))


def rule(title=''):
    say()
    say('── ' + title + ' ' + '─' * max(4, 56 - len(title) * 2) if title else '─' * 60)


def ask(prompt, default=''):
    """One line from the user. Empty = default. Ctrl-Z / Ctrl-D / Ctrl-C = go back (returns None)."""
    try:
        s = input('%s%s: ' % (prompt, ' [%s]' % default if default else '')).strip()
    except (EOFError, KeyboardInterrupt):
        say()
        return None
    return s or default


def yes(prompt, default=False):
    a = ask(prompt + (' (Y/n)' if default else ' (y/N)'))
    if a is None:          # no answer at all (end of input, Ctrl-C) is never a yes: some of these questions spend money
        return False
    if a == '':
        return default
    return a.lower() in ('y', 'yes', '是', '好', '跑')


def pick(title, items, show=lambda x: str(x), allow_none=True):
    """Numbered list; returns the chosen item or None."""
    if not items:
        say('（没有可选的）')
        return None
    rule(title)
    for i, it in enumerate(items, 1):
        say('%3d  %s' % (i, show(it)))
    if allow_none:
        say('  0  返回')
    while True:
        a = ask('选哪个')
        if a is None or a == '0' or a == '':
            return None
        if a.isdigit() and 1 <= int(a) <= len(items):
            return items[int(a) - 1]
        say('输入上面的数字。')


def load_state():
    state_files = [STATE_FILE]
    if STATE_TEMPORARY:
        state_files.append(os.path.join(PREFERRED_STATE_DIR, 'state.json'))
    for path in state_files:
        try:
            with open(path, encoding='utf-8-sig') as f:
                st = json.load(f)
        except FileNotFoundError:
            continue
        except (OSError, ValueError):
            return {}
        break
    else:
        return {}
    if not isinstance(st, dict):
        return {}
    if 'guideMode' in st:         # older: how the guide was paid. Now: guidePay (the guide on its own), else pay.
        gm = norm_pay(st.pop('guideMode'))
        if gm in PAYS and 'guidePay' not in st:
            st['guidePay'] = gm
    return st


def refresh_state(ctx):
    """The menu and the page run for a long time with the state in memory. Read the file again before each step, so
    what another window changed (prk pay, --local, the provider) is seen here, and a later save does not write an
    old copy over it. A file that cannot be read right now (being written) leaves the copy in memory as it is."""
    st = load_state()
    if st or not os.path.exists(STATE_FILE):
        for k in [k for k in ctx['state'] if k not in st]:   # not clear(): a key in both is never missing, even for a moment
            ctx['state'].pop(k, None)
        ctx['state'].update(st)


def save_state(st):
    try:
        atomic_json(STATE_FILE, st)
    except OSError:
        pass


def read_json(path):
    with open(path, encoding='utf-8-sig') as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def api_text(key):
    return read_json(os.path.join(KIT, 'api', 'texts.json'))[key]


def atomic_json(path, data):
    """Replace a JSON file only after the complete new copy has been closed."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    temp_path = os.path.join(folder, '.json-' + secrets.token_hex(12))
    f = open(temp_path, 'x', encoding='utf-8')
    try:
        with f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        try:
            os.replace(temp_path, path)
        except OSError:  # some security software refuses renames in the user's AppData (WinError 17): copy the bytes over
            shutil.copyfile(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def run_id():
    seconds, nanos = divmod(time.time_ns(), 1_000_000_000)
    return '%s%09d_%s' % (time.strftime('%Y%m%d_%H%M%S', time.localtime(seconds)), nanos, secrets.token_hex(5))


def rel(path):
    """Shorter to read: relative to the kit when inside it."""
    try:
        r = os.path.relpath(path, KIT)
        return path if r.startswith('..') else r
    except ValueError:
        return path


# ---------- what the kit has ----------

def load_kinds():
    return read_json(os.path.join(KIT, 'kinds', 'kinds.json'))['kinds']


def load_personas():
    """[(number, name, class, file)] from every method\\画像*.md (candidates files are left out)."""
    out = []
    mdir = os.path.join(KIT, 'method')
    for dirpath, _dirs, files in os.walk(mdir):
        for name in sorted(files):
            if not (name.startswith('画像') and name.endswith('.md')) or '候选' in name:
                continue
            p = os.path.join(dirpath, name)
            with open(p, encoding='utf-8') as f:
                for line in f:
                    m = re.match(r'^## (\d+) (.+?)\s*$', line)
                    if m:
                        title = m.group(2)
                        cls = ''
                        c = re.search(r'[（(]([^（）()]+)[）)]\s*$', title)
                        if c:
                            cls = c.group(1)
                        out.append((int(m.group(1)), title, cls, rel(p)))
    return sorted(out)


def load_presets():
    """Presets of the kit: one folder per kind of game, each with a persona overlay for that kind (presets\\<id>\\preset.json)."""
    out = []
    pdir = os.path.join(KIT, 'presets')
    if os.path.isdir(pdir):
        for d in sorted(os.listdir(pdir)):
            p = os.path.join(pdir, d, 'preset.json')
            if os.path.exists(p):
                try:
                    j = read_json(p)
                except ValueError:
                    continue
                j.setdefault('id', d)
                j['overlayExists'] = os.path.exists(os.path.join(pdir, d, j.get('personaOverlay') or '画像对照.md'))
                out.append(j)
    return out


def find_projects(state):
    found = []
    pdir = os.path.join(KIT, 'projects')
    if os.path.isdir(pdir):
        found += [os.path.join(pdir, f) for f in sorted(os.listdir(pdir)) if f.endswith('.json') and not f.startswith('_')]
    edir = os.path.join(KIT, 'examples')
    if os.path.isdir(edir):
        for d in sorted(os.listdir(edir)):
            p = os.path.join(edir, d, 'project.json')
            if os.path.exists(p):
                found.append(p)
    for p in state.get('recent', []):
        if os.path.exists(p) and os.path.abspath(p) not in [os.path.abspath(x) for x in found]:
            found.append(p)
    return found


def project_title(path):
    try:
        d = read_json(path)
        return '%s  [%s]' % (d.get('name') or d.get('id') or '?', rel(path))
    except (OSError, ValueError) as e:
        return '%s  （读不了：%s）' % (rel(path), e.__class__.__name__)


def local_file(args, state):
    return args.get('local') or os.environ.get('PLAYER_REVIEW_LOCAL') or state.get('local') or \
        (os.path.join(KIT, 'local.json') if os.path.exists(os.path.join(KIT, 'local.json')) else '')


def read_local(ctx):
    lf = local_file(ctx['args'], ctx['state'])
    try:
        return read_json(lf) if lf and os.path.exists(lf) else {}
    except ValueError:
        return {}


def machine_never_read(ctx):
    lf = local_file(ctx['args'], ctx['state'])
    base = os.path.dirname(os.path.abspath(lf or 'local.json'))
    return [os.path.abspath(os.path.join(base, os.path.expandvars(p)))
            for p in read_local(ctx).get('neverRead') or [] if p]


def path_problem(field, path, kind, required=False):
    if not path:
        return '没写 %s' % field if required else ''
    if kind == 'out':
        if os.path.exists(path) and not os.path.isdir(path):
            return '%s 应该是文件夹：%s' % (field, path)
    elif '*' not in str(path) and not os.path.exists(path):
        return '%s 指的地方不存在：%s' % (field, path)
    elif kind == 'dir' and not os.path.isdir(path):
        return '%s 应该是文件夹：%s' % (field, path)
    elif kind == 'file' and not os.path.isfile(path):
        return '%s 应该是文件：%s' % (field, path)
    return ''


def provider_settings():
    try:
        return read_json(os.path.join(KIT, 'api', 'providers.json'))
    except (OSError, ValueError):
        return {}


def provider_catalog():
    """The kit's list of model providers (api\\providers.json)."""
    return provider_settings().get('providers') or {}


ENGINE_NAMES = {'claude-code': 'Claude Code', 'codex': 'Codex CLI（GPT）', 'gemini': 'Gemini CLI'}


def engine_program(local, engine):
    """Where the reviewer program of an engine is (machine settings <engine>Exe, else PATH), or None."""
    name = {'claude-code': 'claude', 'codex': 'codex', 'gemini': 'gemini'}.get(engine, engine)
    given = os.path.expandvars(str(local.get('claudeExe' if engine == 'claude-code' else engine + 'Exe') or ''))
    if given:
        return given if os.path.exists(given) else None
    return shutil.which(name)


def load_providers(ctx):
    """{name: provider}: the kit's catalog with the machine settings' own entries laid over it (key location, region, models).
    Each gets: keyReady (a key or another way to sign in is written down, and the reviewer program is there),
    signin (can be paid by the program's own login), signinReady (signin and the program is there), configured (ready
    for the pay in use: signinReady when it is "sub", else keyReady), mine (has an entry in the machine settings).
    Never the key itself, and the key's location only as "file" / "env"."""
    local = read_local(ctx)
    settings = provider_settings()
    cat, mine = settings.get('providers') or {}, local.get('providers') or {}
    blocked = settings.get('subscriptionUnsupported') or {}
    pay = pay_of(ctx)[0]
    out = OrderedDict()
    for name in list(cat) + [n for n in mine if n not in cat and not n.startswith('_')]:
        c, m = dict(cat.get(name) or {}), dict(mine.get(name) or {})
        if name == 'anthropic' and not m and (local.get('apiKeyFile') or local.get('apiKeyEnv') or local.get('defaultModel')):
            m = {'apiKeyFile': local.get('apiKeyFile'), 'apiKeyEnv': local.get('apiKeyEnv'), 'model': local.get('defaultModel')}
        d = OrderedDict(c)
        d.update({k: v for k, v in m.items() if v not in (None, '') and not k.startswith('_')})
        if name == 'anthropic' and local.get('modelChoices') and not m.get('models'):
            d['models'] = list(local['modelChoices'])
        kind = d.get('kind') or 'compatible'
        engine = d.get('engine') or 'claude-code'
        key = 'file' if d.get('apiKeyFile') else ('env' if d.get('apiKeyEnv') else None)
        way = key or (kind == 'bedrock' and d.get('awsProfile')) or (kind in ('vertex', 'foundry', 'google-vertex') and m)
        prog = engine_program(local, engine)
        key_ready = bool(way) and (kind != 'compatible' or bool(d.get('baseUrl'))) and bool(prog)
        signin_problem = api_text(blocked[engine]) if engine in blocked else ''
        signin = bool(d.get('signin')) and not signin_problem
        d.update({'id': name, 'kind': kind, 'engine': engine, 'key': key, 'mine': bool(m), 'program': bool(prog),
                  'signinProblem': signin_problem,
                  'signin': signin, 'signinWith': (d.get('signinWith') or ENGINE_NAMES.get(engine, engine)) if signin else '',
                  'keyReady': key_ready, 'signinReady': signin and bool(prog),
                  'configured': (signin and bool(prog)) if pay == 'sub' else key_ready})
        for k in ('apiKeyFile', 'apiKeyEnv', 'credentialsFile', 'awsProfile'):
            d.pop(k, None)
        out[name] = d
    return out


def current_provider(ctx):
    """(provider id, where it comes from): --provider, the remembered choice, the machine settings' defaultProvider, anthropic."""
    a, st = ctx['args'], ctx['state']
    if a.get('provider'):
        return a['provider'], '这条命令的 --provider'
    if st.get('provider'):
        return st['provider'], '记住的选择（prk provider 或页面的设置里改）'
    local = read_local(ctx)
    if local.get('defaultProvider'):
        return local['defaultProvider'], '机器设置的 defaultProvider'
    return 'anthropic', '默认'


def model_choices(ctx, provider=None):
    """Model ids to offer for a provider (its models in the machine settings, else in the kit's list). Any other id can be typed."""
    provider = provider or current_provider(ctx)[0]
    pv = load_providers(ctx).get(provider) or {}
    return [str(x) for x in pv.get('models') or []]


def remembered_models(st):
    m = st.get('models')
    if not isinstance(m, dict):
        m = {}
    if st.get('model') and 'anthropic' not in m:      # remembered before there were providers
        m['anthropic'] = st['model']
    return m


def current_model(ctx):
    """(model id or '', where it comes from) for the current provider. Order: this command's --model, the choice remembered
    for this provider (prk model / the page), the provider's model in the machine settings (for anthropic also the older
    defaultModel), the provider's model in the kit's list, Claude Code's own default."""
    a, st = ctx['args'], ctx['state']
    provider = current_provider(ctx)[0]
    if a.get('model'):
        return a['model'], '这条命令的 --model'
    rm = remembered_models(st).get(provider)
    if rm:
        return rm, '记住的选择（prk model 或页面的设置里改）'
    mine = (read_local(ctx).get('providers') or {}).get(provider) or {}
    if mine.get('model'):
        return mine['model'], '机器设置里这个服务商的 model'
    if provider == 'anthropic' and read_local(ctx).get('defaultModel'):
        return read_local(ctx)['defaultModel'], '机器设置的 defaultModel'
    cat = provider_catalog().get(provider) or {}
    if cat.get('model'):
        return cat['model'], '工具包的服务商表（api\\providers.json）'
    return '', 'Claude Code 自己的默认'


MODEL_ID = re.compile(r'^[A-Za-z0-9~][A-Za-z0-9._:\-\[\]/@~]{1,100}$')


def set_model(ctx, model, provider=None):
    """Remember a model for one provider ('' or 'default' = forget it). Returns an error text or ''."""
    provider = provider or current_provider(ctx)[0]
    model = (model or '').strip()
    st = ctx['state']
    models = remembered_models(st)
    st.pop('model', None)
    if model.lower() in ('', 'default', '默认', 'none'):
        models.pop(provider, None)
    elif not MODEL_ID.match(model):
        return '模型 id 只能是字母、数字和 . _ - : / [ ] @ ~（例：claude-sonnet-5-5、deepseek-flash[1m]）'
    else:
        models[provider] = model
    st['models'] = models
    save_state(st)
    return ''


def set_provider(ctx, provider):
    """Remember which provider runs use ('' / 'default' = forget). Returns an error text or ''."""
    provider = (provider or '').strip()
    st = ctx['state']
    if provider.lower() in ('', 'default', '默认'):
        st.pop('provider', None)
    elif provider not in load_providers(ctx):
        return '没有这个服务商：%s（有：%s）' % (provider, '、'.join(load_providers(ctx)))
    else:
        st['provider'] = provider
    save_state(st)
    return ''


# ---------- how it is paid ----------
# One choice for the checks (run, quick, expand) and the guide; the guide can have its own.
#   sub = the reviewer program's own login on this computer (Claude Code's, Codex's ChatGPT, Gemini CLI's Google login):
#         nothing extra is paid, but it uses that account's quota. Only providers with "signin": true in api\providers.json.
#   api = a key (machine settings), paid by use.
# Never chosen silently: both spend the owner's quota or money. Not set and not in a terminal = the command stops (exit 2).

PAYS = ('sub', 'api')
PAY_NAMES = {'sub': '会员额度', 'api': '按次付费'}
PAY_LONG = {'sub': '用会员额度（用这台电脑上登录的账号，不另外花钱，但会用掉你的额度）',
            'api': '按次付费（用钥匙 key，按用量花钱）'}


def norm_pay(v):
    v = str(v or '').strip().lower()
    return {'subscription': 'sub', 'signin': 'sub', '订阅': 'sub', '会员': 'sub', '会员额度': 'sub', '额度': 'sub',
            'key': 'api', '按次': 'api', '按次付费': 'api', '一样': 'same', '跟检查一样': 'same'}.get(v, v)


def pay_state(st):
    """(pay, the guide's pay in effect, the guide set on its own) from the remembered choice; '' = not chosen."""
    pay = st.get('pay') if st.get('pay') in PAYS else ''
    gp = st.get('guidePay') if st.get('guidePay') in PAYS else ''
    return pay, gp or pay, bool(gp)


def pay_of(ctx, guide=False):
    """(pay or '', where it comes from) for this command: --pay (the guide: also its older --mode), else remembered."""
    a = ctx['args']
    one = norm_pay(a.get('pay') or (a.get('mode') if guide else ''))
    if one in PAYS:
        return one, '这条命令的 --pay'
    pay, gp, separate = pay_state(ctx['state'])
    if guide and separate:
        return gp, '问 AI 单独设的（prk pay guide）'
    if pay:
        return pay, '记住的选择（prk pay 或页面的设置里改）'
    return '', '还没选'


def set_pay(ctx, pay=None, guide=None):
    """Remember how to pay: pay = 'sub' | 'api'; guide = 'sub' | 'api' | 'same'. Returns an error text or ''."""
    st = ctx['state']
    if pay is not None:
        pay = norm_pay(pay)
        if pay not in PAYS:
            return '怎么付只能是 sub（会员额度）或 api（按次付费）。'
    if guide is not None:
        guide = norm_pay(guide)
        if guide not in PAYS + ('same',):
            return '问 AI 怎么付只能是 sub（会员额度）、api（按次付费）或 same（跟检查一样）。'
    if pay is not None:
        st['pay'] = pay
    if guide == 'same':
        st.pop('guidePay', None)
    elif guide is not None:
        st['guidePay'] = guide
    st.pop('guideMode', None)
    save_state(st)
    return ''


def can_sign_in(ctx, provider):
    """Can this provider be paid by the reviewer program's own login (api\\providers.json: signin)?"""
    return bool((load_providers(ctx).get(provider) or {}).get('signin'))


def signin_providers(ctx):
    return [n for n, d in load_providers(ctx).items() if d.get('signin')]


def pay_problem(ctx, pay, provider=None):
    """Why this pay cannot run with this provider ('' when it can)."""
    provider = provider or current_provider(ctx)[0]
    d = (load_providers(ctx).get(provider) or {}) if pay == 'sub' else {}
    if pay == 'sub' and not d.get('signin'):
        if d.get('signinProblem'):
            return d['signinProblem'] + '。请改用按次付费，或换一家支持会员登录的服务商。'
        return ('「%s」（%s）只能按次付费（用钥匙 key），没有"用这台电脑上登录的账号"这种付法。\n'
                '要用会员额度：换回 anthropic（prk provider anthropic，或这一次加 --provider anthropic）。\n'
                '要用这一家：改成按次付费（prk pay api，或这一次加 --pay api）。\n'
                '能用会员额度的：%s。' % (provider, d.get('name', provider), '、'.join(signin_providers(ctx)) or '没有'))
    return ''


def need_pay(ctx, guide=False):
    """How this command pays: --pay, else remembered; never chosen: ask once in a terminal and remember it for
    everything. Returns 'sub' / 'api', or '' after saying why (the caller stops with exit code 2)."""
    pay, _src = pay_of(ctx, guide)
    if pay:
        return pay
    text = ('还没说用什么付（两种都会用掉额度或钱，所以不会替你挑）：\n'
            '  --pay sub  %s\n  --pay api  %s\n或者先记住一种：prk pay sub / prk pay api。' % (PAY_LONG['sub'], PAY_LONG['api']))
    if want_json(ctx) or not sys.stdin.isatty():
        if want_json(ctx):
            out_json({'ok': False, 'error': text})
        else:
            say(text)
        return ''
    say('还没选过怎么付（选一次就记住，以后 run、quick、expand、问 AI 都用它；改：prk pay）。')
    m = pick('用什么付', [PAY_LONG['sub'], PAY_LONG['api']])
    if m is None:
        return ''
    pay = 'sub' if m == PAY_LONG['sub'] else 'api'
    set_pay(ctx, pay)
    say('记住了：%s。' % PAY_NAMES[pay])
    return pay


def pay_line(ctx, pay, provider=None):
    """One line for the person: what pays this run."""
    provider = provider or current_provider(ctx)[0]
    d = load_providers(ctx).get(provider) or {}
    if pay == 'sub':
        return '用什么付：会员额度，用这台电脑上 %s 登录的账号。不另外花钱，但会用掉你的额度；额度用完会停下。' % (
            d.get('signinWith') or ENGINE_NAMES.get(d.get('engine'), 'Claude Code'))
    return '用什么付：按次付费，用「%s」的钥匙（key），按用量收钱。' % d.get('name', provider)


def runner_target(ctx):
    """[-Provider p, -Model m] for the PowerShell scripts: what current_provider / current_model resolve to."""
    out = []
    pv = current_provider(ctx)[0]
    if pv:
        out += ['-Provider', pv]
    m = current_model(ctx)[0]
    if m:
        out += ['-Model', m]
    return out


def cmd_model(ctx):
    """prk model                 which provider and model the runs use now, and the ids on offer
       prk model <id>            remember this model (for the current provider) for run / quick / expand / guide
       prk model default         forget it
       prk model <id> --provider deepseek   for that provider (and use that provider only for this command)"""
    word = (ctx['args'].get('word') or '').strip()
    pv = current_provider(ctx)[0]
    if word:
        err = set_model(ctx, word, pv)
        if err:
            say(err)
            return 2
    model, source = current_model(ctx)
    if want_json(ctx):
        out_json({'ok': True, 'provider': pv, 'model': model, 'source': source, 'choices': model_choices(ctx, pv)})
        return 0
    rule('用哪个模型')
    info = load_providers(ctx).get(pv) or {}
    say('服务商：%s %s（%s）' % (pv, info.get('name', ''), current_provider(ctx)[1]))
    say('模型　：%s（%s）' % (model or '没指定', source))
    ch = model_choices(ctx, pv)
    if ch:
        say('可以选：%s（也可以写别的 id）' % '、'.join(ch))
    say('换模型：prk model <id>　　忘掉：prk model default　　只这一次：命令后面加 --model <id>')
    say('换服务商：prk provider <名字>（有哪些：prk provider）')
    say('越大的模型越贵。换了模型，先只跑一个任务，看花费总账（prk costs）里那一行。')
    return 0


def cmd_provider(ctx):
    """prk provider                which providers the kit knows, which ones this computer has set up, which one is in use
       prk provider <name>         use it from now on (remembered)
       prk provider default        forget the choice
       prk provider setup <name>   write where its key is (and its region, address ...) into the machine settings"""
    words = (ctx['args'].get('word') or '').split()
    if words[:1] == ['setup']:
        return provider_setup(ctx, words[1] if len(words) > 1 else '')
    if words:
        err = set_provider(ctx, words[0])
        if err:
            say(err)
            return 2
    pv, src = current_provider(ctx)
    ps = load_providers(ctx)
    pay = pay_of(ctx)[0]
    if want_json(ctx):
        out_json({'ok': True, 'provider': pv, 'source': src, 'model': current_model(ctx)[0], 'pay': pay or None,
                  'payProblem': pay_problem(ctx, pay, pv) or None,
                  'providers': [{k: v for k, v in d.items()} for d in ps.values()]})
        return 0
    rule('模型服务商')
    say('现在用：%s（%s）；模型：%s' % (pv, src, current_model(ctx)[0] or '没指定'))
    say('怎么付：%s' % (PAY_LONG[pay] if pay else '还没选（prk pay sub 或 prk pay api）'))
    say()
    for name, d in ps.items():
        if d['configured']:
            why = '  （用这台电脑上 %s 登录的账号，不用钥匙）' % d['signinWith'] if pay == 'sub' else ''
        elif not d['program']:
            why = '  （没找到 %s）' % ENGINE_NAMES.get(d['engine'], d['engine'])
        elif pay == 'sub' and not d['signin']:
            why = '  （这家只能按次付费）'
        else:
            why = '  （这台电脑还没设好钥匙：prk provider setup %s）' % name
        say('%s %-13s %s%s' % ('→' if name == pv else ' ', name, d.get('name', ''), why))
        say('               %s；核对于 %s' % (d.get('docs', ''), d.get('checked', '?')))
    say()
    if pay == 'sub' and pay_problem(ctx, pay, pv):
        say(pay_problem(ctx, pay, pv))
        say()
    say('换：prk provider <名字>。设 key 放在哪：prk provider setup <名字>（只问放在哪，不问 key 本身；用会员额度时不用设）。')
    say('地址和模型 id 会变：用之前照上面的 docs 再看一眼。接别家的模型时，花费表里"CLI估的"不是账单，看"按价目表"那一列（价目表写在机器设置的 prices）。')
    return 0


# What each kind of provider needs besides the key: (field, question, default). prk provider setup asks these and the
# page's form shows them; save_provider writes them. A compatible endpoint also asks its address (provider_form).
PROVIDER_FIELDS = {
    'bedrock': [('region', '区域（AWS_REGION）', 'us-east-1'),
                ('awsProfile', 'AWS 配置名（AWS_PROFILE；不填 = 不用，改用钥匙）', '')],
    'vertex': [('region', '区域（CLOUD_ML_REGION）', 'global'), ('projectId', '项目 id（ANTHROPIC_VERTEX_PROJECT_ID）', ''),
               ('credentialsFile', '凭据文件（GOOGLE_APPLICATION_CREDENTIALS；不填 = 用 gcloud 的登录）', '')],
    'foundry': [('resource', '资源名（ANTHROPIC_FOUNDRY_RESOURCE）', '')],
    'google-vertex': [('projectId', '项目 id（GOOGLE_CLOUD_PROJECT）', ''), ('region', '区域（GOOGLE_CLOUD_LOCATION）', 'global'),
                      ('credentialsFile', '凭据文件（GOOGLE_APPLICATION_CREDENTIALS；不填 = 用 gcloud 的登录）', '')],
}
KEY_OPTIONAL = ('bedrock', 'vertex', 'foundry', 'google-vertex')    # these can sign in another way (load_providers: way)


def clean_text(v, limit=500):
    """One line the person typed: no line breaks, no quotes around it, not too long."""
    return re.sub(r'[\r\n\t]', ' ', str('' if v is None else v)).strip().strip('"').strip()[:limit]


def machine_file(ctx):
    """The machine settings file to write: the one in use, else <kit>\\local.json."""
    return local_file(ctx['args'], ctx['state']) or os.path.join(KIT, 'local.json')


def read_machine(dst):
    """(settings, error text): the machine settings file as it is now ({} when there is none yet)."""
    if not os.path.exists(dst):
        return OrderedDict(), ''
    try:
        d = read_json(dst)
    except (OSError, ValueError) as e:
        return None, '机器设置文件读不了（%s）：%s' % (e.__class__.__name__, mask_home(dst))
    return (d if isinstance(d, dict) else OrderedDict()), ''


def write_machine(dst, d):
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    with open(dst, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def key_check(key_file, key_env):
    """Is the key's place there: {fileFound} = the file exists, {envSet} = the variable has a value now (in this
    process). Never opens the file, never gives the value."""
    out = {}
    if key_file:
        out['fileFound'] = os.path.isfile(os.path.expandvars(key_file))
    if key_env:
        out['envSet'] = bool(os.environ.get(key_env))
    return out


def provider_form(ctx, name, kind=None):
    """What setting up one provider asks (prk provider setup and the page's form): the fields its kind needs, where the
    key is (a file's path or an environment variable's name, never the key), its default model, and for a reviewer
    that is not Claude Code whether "never read" may be only asked for in the prompt. Values are what the machine
    settings hold now."""
    c = provider_catalog().get(name) or {}
    dst = machine_file(ctx)
    d = read_machine(dst)[0] or {}
    old = dict((d.get('providers') or {}).get(name) or {})
    if name == 'anthropic' and not old:       # the older way of writing it (see load_providers)
        old = {k2: d.get(k1) for k1, k2 in (('apiKeyFile', 'apiKeyFile'), ('apiKeyEnv', 'apiKeyEnv'), ('defaultModel', 'model')) if d.get(k1)}
    kind = kind or c.get('kind') or old.get('kind') or ''
    engine = c.get('engine') or old.get('engine') or 'claude-code'
    fields = []
    if kind == 'compatible' and (not c.get('baseUrl') or old.get('baseUrl')):
        fields.append({'key': 'baseUrl', 'label': '接口地址（ANTHROPIC_BASE_URL）', 'value': old.get('baseUrl') or c.get('baseUrl') or ''})
    for k, label, default in PROVIDER_FIELDS.get(kind, []):
        fields.append({'key': k, 'label': label, 'value': str(old.get(k) or default)})
    kf, ke = str(old.get('apiKeyFile') or ''), str(old.get('apiKeyEnv') or '')
    return {'name': name, 'title': c.get('name') or name, 'known': bool(c), 'kind': kind, 'engine': engine,
            'engineName': ENGINE_NAMES.get(engine, engine), 'docs': c.get('docs') or '', 'checked': c.get('checked') or '',
            'note': c.get('note') or '', 'fields': fields, 'keyNeeded': kind not in KEY_OPTIONAL,
            'key': 'file' if kf else ('env' if ke else ''), 'keyFile': kf, 'keyEnv': ke, 'check': key_check(kf, ke),
            'model': str(old.get('model') or ''), 'modelDefault': c.get('model') or '', 'promptOnly': bool(old.get('promptOnlyNeverRead')),
            'program': bool(engine_program(read_local(ctx), engine)), 'file': dst}


def save_provider(ctx, name, values):
    """Write one provider's settings into the machine settings (machine_file). values: the fields of provider_form by
    their key; key = 'file' (+ keyFile) | 'env' (+ keyEnv) | 'none' (no key) | '' (as it is); model ('' = none);
    promptOnly (only for a reviewer that is not Claude Code); kind (only for a name the kit does not know).
    Only where the key is goes in, never the key. Returns (file, error text or '')."""
    if not name or not re.match(r'^[A-Za-z0-9_-]+$', name):
        return '', '名字只能用英文字母、数字、_、-。'
    dst = machine_file(ctx)
    d, err = read_machine(dst)
    if err:
        return dst, err
    form = provider_form(ctx, name, clean_text(values.get('kind')) or None)
    provs = d.get('providers') if isinstance(d.get('providers'), dict) else OrderedDict()
    e = OrderedDict((provs.get(name) or {}).items())
    if not form['known'] and values.get('kind'):
        e['kind'] = form['kind']
    for f in form['fields']:
        if f['key'] in values:
            v = clean_text(values[f['key']])
            if f['key'] == 'baseUrl' and v and not re.match(r'^https?://', v):
                return dst, '接口地址要以 http:// 或 https:// 开头。'
            e[f['key']] = v
    key = values.get('key') or ''
    if key == 'file':
        p = clean_text(values.get('keyFile'))
        if not p:
            return dst, '写上放钥匙的那个文本文件在哪。'
        e['apiKeyFile'] = p
        e.pop('apiKeyEnv', None)
    elif key == 'env':
        v = clean_text(values.get('keyEnv'), 100)
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', v):
            return dst, '环境变量的名字只能用英文字母、数字和 _，不能用数字开头。'
        e['apiKeyEnv'] = v
        e.pop('apiKeyFile', None)
    elif key == 'none':
        e.pop('apiKeyFile', None)
        e.pop('apiKeyEnv', None)
    if 'model' in values:
        m = clean_text(values.get('model'), 120)
        if m and not MODEL_ID.match(m):
            return dst, '型号写得不对：只能是字母、数字和 . _ - : / [ ] @ ~（例：claude-sonnet-5-5、deepseek-flash[1m]）。'
        if m:
            e['model'] = m
        else:
            e.pop('model', None)
    if form['engine'] != 'claude-code' and 'promptOnly' in values:
        if values.get('promptOnly'):
            e['promptOnlyNeverRead'] = True
        else:
            e.pop('promptOnlyNeverRead', None)
    provs[name] = e
    d['providers'] = provs
    try:
        write_machine(dst, d)
    except OSError as ex:
        return dst, '写不进机器设置：%s' % ex
    return dst, ''


def machine_paths(ctx):
    """Where Python and Claude Code are, as the machine settings say ('' = the default), and whether they are there."""
    local = read_local(ctx)
    py, exe = str(local.get('python') or ''), str(local.get('claudeExe') or '')
    return {'file': machine_file(ctx), 'python': py, 'claudeExe': exe,
            'pythonFound': bool(shutil.which(py) or os.path.exists(os.path.expandvars(py))) if py else True,
            'claudeFound': bool(engine_program(local, 'claude-code'))}


def save_machine_paths(ctx, values):
    """python / claudeExe into the machine settings ('' = use the default). A path is only checked for being there
    (Python may also be a program name on PATH). Returns (file, error text or '')."""
    dst = machine_file(ctx)
    d, err = read_machine(dst)
    if err:
        return dst, err
    for k, what in (('python', 'Python'), ('claudeExe', 'Claude Code')):
        if k in values:
            v = clean_text(values.get(k))
            if v and not (os.path.exists(os.path.expandvars(v)) or (k == 'python' and shutil.which(v))):
                return dst, '%s 的位置找不到：%s' % (what, v)
            d[k] = v
    try:
        write_machine(dst, d)
    except OSError as ex:
        return dst, '写不进机器设置：%s' % ex
    return dst, ''


def provider_setup(ctx, name):
    """Ask where one provider's key is (never the key) and its few settings; write them into the machine settings
    (save_provider: the page's form writes the same way)."""
    cat = provider_catalog()
    if not name:
        name = ask('哪个服务商（%s；也可以起一个新名字，接自己的网关）' % '、'.join(cat)) or ''
    if not name or not re.match(r'^[A-Za-z0-9_-]+$', name):
        say('名字只能用英文字母、数字、_、-。')
        return 2
    if not sys.stdin.isatty():
        say('这一步要人答：在终端里运行 prk provider setup %s（或者在页面的「设置」里填）。' % name)
        return 2
    form = provider_form(ctx, name)
    rule('设置服务商：%s %s' % (name, (cat.get(name) or {}).get('name', '')))
    if form['docs']:
        say('官方说明：%s（核对于 %s）' % (form['docs'], form['checked'] or '?'))
    if form['note']:
        say(form['note'])
    say('这里只问 key 放在哪，不问 key 本身。直接回车 = 用括号里的。')
    vals = {}
    if not form['kind']:
        vals['kind'] = ask('接口类型：compatible（Anthropic 兼容接口或网关）/ anthropic / bedrock / vertex / foundry', 'compatible') or 'compatible'
        form = provider_form(ctx, name, vals['kind'])
    for f in form['fields']:
        vals[f['key']] = ask(f['label'], f['value']) or ''
    if form['engine'] != 'claude-code':
        say()
        say('这一家的审查员是 %s，不是 Claude Code。它只读地跑（报告由工具包写），但它没法像 Claude Code 那样用规则挡住'
            '"不许读"的文件夹（机器设置和项目设置的 neverRead、key 所在的文件夹），只能在提示里告诉它别读。' % form['engineName'])
        vals['promptOnly'] = yes('可以接受"只在提示里说"吗（不接受的话，有不许读的文件夹时它不会跑）', default=False)
        if not form['program']:
            say('这台电脑上没找到 %s。装好以后放在 PATH 上，或者在机器设置里写 %sExe。' % (form['engineName'], form['engine']))
    how = ask('key 从哪来：1 = 一个只放 key 的文本文件，2 = 一个环境变量，回车 = %s' % ('不变' if form['key'] else '先不设'), '')
    if how == '1':
        p = ask('那个文本文件的路径', form['keyFile']) or ''
        if p:
            vals.update(key='file', keyFile=p)
    elif how == '2':
        v = ask('环境变量的名字', form['keyEnv']) or ''
        if v:
            vals.update(key='env', keyEnv=v)
    m = ask('默认用哪个模型（回车 = %s）' % (form['modelDefault'] or 'Claude Code 自己的默认'), form['model']) or ''
    if m:
        if not MODEL_ID.match(m):
            say('模型 id 写得不对，没记。')
        else:
            vals['model'] = m
    dst, err = save_provider(ctx, name, vals)
    if err:
        say(err)
        return 2
    say('写好了：%s（key 本身没有写进去）' % mask_home(dst))
    if yes('以后就用 %s 吗' % name, default=True):
        set_provider(ctx, name)
        say('记住了。')
    return 0


def groups_of(proj):
    return proj.get('reviewGroups') or proj.get('personaGroups') or []


def group_kind(g):
    return g.get('kind') or g.get('walk') or 'persona'


# ---------- commands ----------

def cmd_kinds(ctx):
    if want_json(ctx):
        out_json([{k: v for k, v in kd.items() if k != 'splitScope'} for kd in load_kinds()])
        return 0
    rule('审查种类（kinds\\kinds.json）')
    for k in load_kinds():
        tag = {'prepare': '准备环节', 'extend': '后续环节'}.get(k.get('role'), '审查')
        say('%-12s %s  〔%s〕' % (k['id'], k['name'], tag))
        say('             %s' % k.get('what', ''))
        if k.get('needs'):
            say('             要项目设置里有：%s' % '、'.join(k['needs']))
    return 0


def cmd_presets(ctx):
    ps = load_presets()
    if want_json(ctx):
        out_json({'presets': ps})
        return 0
    rule('预设（一类游戏一份现成的画像对照；项目设置里写 "presets": ["id"]）')
    if not ps:
        say('还没有。')
    for p in ps:
        say('%-12s %s' % (p['id'], p.get('name', '')))
        say('             适合：%s' % p.get('fits', ''))
    return 0


def cmd_personas(ctx):
    word = ctx['args'].get('find') or ''
    ps = [p for p in load_personas() if word in p[1]]
    if want_json(ctx):
        out_json([{'number': n, 'name': title, 'class': c, 'file': f} for n, title, c, f in ps])
        return 0
    rule('画像（%d 个%s）' % (len(ps), '，名字里有「%s」' % word if word else ''))
    last = None
    for n, title, _cls, f in ps:
        if f != last:
            say('〔%s〕' % f)
            last = f
        say('%4d  %s' % (n, title))
    say()
    say('每个画像怎么玩、盯着什么：打开上面的文件，找 "## 编号"。每个画像适用什么样的作品：method\\画像_索引.md。')
    say('这一类游戏该派哪些：prk suggest <游戏类型>。')
    return 0


def cmd_suggest(ctx):
    """Which personas for which kind of game: the table at the end of method\\画像_索引.md."""
    word = ctx['args'].get('word') or ''
    rows = []
    p = os.path.join(KIT, 'method', '画像_索引.md')
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            on = False
            for line in f:
                if line.startswith('## '):
                    on = '按游戏类型' in line
                elif on and line.startswith('| **'):
                    cells = [c.strip() for c in line.strip().strip('|').split('|')]
                    if len(cells) >= 3:
                        rows.append((cells[0].strip('*'), cells[1], cells[2]))
    if not rows:
        say('没找到「按游戏类型怎么挑画像」的表（method\\画像_索引.md）。')
        return 1
    hit = [r for r in rows if word in r[0]] if word else []
    if want_json(ctx):
        out_json([{'type': r[0], 'must': r[1], 'may': r[2]} for r in (hit or rows)])
        return 0
    if not word or not hit:
        rule('有这些游戏类型（prk suggest <类型里的几个字>）')
        for r in rows:
            say('  ' + r[0])
        if word:
            say()
            say('没有名字里带「%s」的类型。' % word)
        return 0
    for name, must, may in hit + [r for r in rows if r[0].startswith('任何作品') and r not in hit]:
        rule(name)
        say('一定要派：%s' % must)
        say('可以派　：%s' % may)
    say()
    say('一组不超过四个画像；这张表是用来挑的，不是一次全上。32 以后的画像先看它的「适用」（prk personas --find 名字）。')
    say('挑好以后写进项目设置的 reviewGroups（画像写"编号 名字"）。')
    return 0


def cmd_groups(ctx):
    proj, path = ctx['proj'], ctx['path']
    kinds = {k['id']: k for k in load_kinds()}
    default = proj.get('defaultGroups') or []
    if want_json(ctx):
        out_json({'project': path, 'name': proj.get('name'), 'defaultGroups': default,
                  'groups': [{'id': g['id'], 'name': g.get('name', ''), 'kind': group_kind(g), 'personas': g.get('personas') or [],
                              'default': g['id'] in default} for g in groups_of(proj)],
                  'splits': [{'id': s.get('id'), 'name': s.get('name'), 'items': s.get('characters') or []} for s in proj.get('characterSplits') or []]})
        return 0
    rule('审查组：%s' % (proj.get('name') or path))
    for g in groups_of(proj):
        k = group_kind(g)
        mark = '*' if g['id'] in default else ' '
        say('%s %-3s %s  〔%s〕' % (mark, g['id'], g.get('name', ''), kinds.get(k, {}).get('name', k + '？')))
        if g.get('personas'):
            say('       画像：%s' % '；'.join(g['personas']))
    say()
    say('带 * 的是默认会派的（defaultGroups，顺序：%s）。' % '、'.join(default))
    splits = proj.get('characterSplits') or []
    if splits:
        say('按份拆分（characterSplits）：%s' % '；'.join('%s = %s' % (s.get('name', s['id']), '、'.join(s.get('characters') or [])) for s in splits))
    return 0


def check_data(ctx):
    """(problems, notes) of the project file: what cmd_check prints, as data (the page and the guide use it too)."""
    proj, path = ctx['proj'], ctx['path']
    problems, notes = [], []
    if proj.get('language', 'zh') not in LANGUAGES:
        problems.append('language 只能是 zh 或 en。')

    def need(field, kind='any'):
        problem = path_problem(field, projfile.get_field(proj, field), kind, required=True)
        if problem:
            problems.append(problem)

    for f in ('projectRoot', 'modSource'):
        need(f, 'dir')
    need('reviewOutDir', 'out')
    for f in ('rulesFile', 'modReadme', 'characterDir', 'behaviourDir', 'loreBible', 'personaOverlay'):
        v = proj.get(f)
        if v and '*' not in v and not os.path.exists(v):
            problems.append('%s 指的地方不存在：%s' % (f, v))
        elif not v:
            notes.append('没写 %s（可以不写）' % f)
    tables = proj.get('staticTables')
    if tables is None or 'text' in tables:
        for f in ('csv.zh', 'csv.en'):
            need(f, 'file')
    if tables and 'images' in tables:
        img_dirs = projfile.get_field(proj, 'static.images.dirs') or []
        if not img_dirs:
            problems.append('staticTables 里有 images，但没写 static.images.dirs（玩家要点、要拖的东西的图在哪）')
        for d in img_dirs:
            if not os.path.isdir(d):
                problems.append('static.images.dirs 指的文件夹不存在：%s' % d)
    for t in tables or []:
        if isinstance(t, dict) and not os.path.exists(t.get('script', '')):
            problems.append('staticTables 里表 %s 的脚本不存在：%s' % (t.get('id', '?'), t.get('script')))
    if not proj.get('playLoop'):
        notes.append('没写 playLoop：审查员会自己从说明和代码里理出一个回合的界面顺序')

    known = {p['id']: p for p in load_presets()}
    for pid in proj.get('presets') or []:
        if pid not in known:
            problems.append('presets 里的「%s」不是工具包里的预设（有：%s）' % (pid, '、'.join(known) or '一个都没有'))
        elif not known[pid]['overlayExists']:
            problems.append('预设「%s」缺画像对照文件' % pid)

    kinds = {k['id']: k for k in load_kinds()}
    numbers = {p[0] for p in load_personas()}
    gids = set()
    for g in groups_of(proj):
        gid = g.get('id', '?')
        gids.add(gid)
        k = group_kind(g)
        if k not in kinds:
            problems.append('组 %s：审查种类 %s 没登记（kinds\\kinds.json）' % (gid, k))
            continue
        if kinds[k].get('role') == 'prepare':
            problems.append('组 %s：%s 是准备环节，不能当审查组的 kind' % (gid, k))
        for n in kinds[k].get('needs') or []:
            if not proj.get(n):
                problems.append('组 %s：%s 要项目设置里有 %s' % (gid, kinds[k]['name'], n))
        for p in g.get('personas') or []:
            m = re.match(r'\s*(\d+)\b', p)
            if m and int(m.group(1)) not in numbers:
                problems.append('组 %s：画像「%s」的编号在画像库里没有' % (gid, p))
    if not groups_of(proj):
        problems.append('没有审查组（reviewGroups）')
    for gid in proj.get('defaultGroups') or []:
        if gid not in gids:
            problems.append('defaultGroups 里的 %s 不在 reviewGroups 里' % gid)
    for s in proj.get('characterSplits') or []:
        if not re.match(r'^[A-Za-z0-9_-]+$', str(s.get('id', ''))):
            problems.append('characterSplits 的 id「%s」只能用英文字母、数字、_、-' % s.get('id'))
    return problems, notes


def local_info(ctx):
    """What this computer has for running things. Says whether a key is configured (for the provider in use), never
    where it is or what it is."""
    lf = local_file(ctx['args'], ctx['state'])
    local = read_json(lf) if lf and os.path.exists(lf) else {}
    exe = local.get('claudeExe') or ''
    proj = ctx.get('proj') or {}
    pv = current_provider(ctx)[0]
    d = load_providers(ctx).get(pv) or {}
    pay = pay_of(ctx)[0]
    exe = os.path.expandvars(str(exe))
    return {'file': lf or None, 'python': local.get('python') or proj.get('python') or sys.executable,
            'claude': (exe if os.path.exists(exe) else None) if exe else shutil.which('claude'),
            'apiKey': d.get('key') or ('signin' if d.get('keyReady') else None),
            'provider': pv, 'providerName': d.get('name', pv), 'providerReady': bool(d.get('configured')),
            'pay': pay or None, 'providerSignin': bool(d.get('signin')), 'program': bool(d.get('program')),
            'engine': d.get('engine') or 'claude-code', 'powershell': powershell()}


def cmd_check(ctx):
    proj, path = ctx['proj'], ctx['path']
    problems, notes = check_data(ctx)
    if want_json(ctx):
        out_json({'project': path, 'name': proj.get('name'), 'ok': not problems, 'problems': problems, 'notes': notes,
                  'groups': len(groups_of(proj)), 'defaultGroups': proj.get('defaultGroups') or [], 'splits': len(proj.get('characterSplits') or []),
                  'local': local_info(ctx), **output_metadata(proj)})
        return 1 if problems else 0
    rule('项目设置：%s' % rel(path))
    say('名字：%s　审查组 %d 个，默认派 %d 个，拆分 %d 份' % (proj.get('name', ''), len(groups_of(proj)),
        len(proj.get('defaultGroups') or []), len(proj.get('characterSplits') or [])))
    for p in problems:
        say('  ✗ %s' % p)
    for n in notes:
        say('  · %s' % n)
    if not problems:
        say('  ✓ 没有发现问题')

    lf = local_file(ctx['args'], ctx['state'])
    rule('机器设置：%s' % (lf or '（没有，全用默认）'))
    local = read_json(lf) if lf and os.path.exists(lf) else {}
    py = local.get('python') or proj.get('python') or sys.executable
    say('  Python：%s%s' % (py, '' if shutil.which(py) or os.path.exists(py) else '  ✗ 找不到'))
    exe = local.get('claudeExe') or ''
    if exe:
        say('  Claude Code：%s%s' % (exe, '' if os.path.exists(exe) else '  ✗ 不存在'))
    else:
        say('  Claude Code：PATH 上的 claude%s' % ('' if shutil.which('claude') else '  ✗ 找不到（API 模式要它；订阅模式不用）'))
    if local.get('apiKeyFile'):
        say('  API key：在文件里（%s）%s' % (local['apiKeyFile'], '' if os.path.exists(local['apiKeyFile']) else '  ✗ 文件不存在'))
    elif local.get('apiKeyEnv'):
        say('  API key：环境变量 %s%s' % (local['apiKeyEnv'], '' if os.environ.get(local['apiKeyEnv']) else '  ✗ 现在是空的'))
    else:
        say('  API key：没设（只用会员额度的话不用设）')
    pay = pay_of(ctx)[0]
    say('  怎么付：%s' % (PAY_LONG[pay] if pay else '还没选（prk pay sub 或 prk pay api）'))
    if pay_problem(ctx, pay):
        say('  ✗ ' + pay_problem(ctx, pay).replace('\n', '\n    '))
    say('  PowerShell：%s' % (powershell() or '✗ 找不到（正式检查和安装要它）'))
    return 1 if problems else 0


def python_for(ctx):
    lf = local_file(ctx['args'], ctx['state'])
    local = read_json(lf) if lf and os.path.exists(lf) else {}
    return local.get('python') or ctx['proj'].get('python') or sys.executable


def cmd_static(ctx):
    proj, path = ctx['proj'], ctx['path']
    out = ctx['args'].get('out') or os.path.join(proj.get('staticOutDir') or os.path.join(proj.get('reviewOutDir') or '.', '_static'))
    cmd = [python_for(ctx), '-I', os.path.join(KIT, 'static', 'run_all.py'), '--project', path]
    local = local_file(ctx['args'], ctx['state'])
    if local:
        cmd += ['--local', local]
    cmd.append(out)
    rule('静态表')
    r = subprocess.run(cmd)
    summary = os.path.join(out, '_summary.md')
    if os.path.exists(summary):
        say()
        with open(summary, encoding='utf-8') as f:
            for line in f:
                if line.startswith('|') or line.startswith('**'):
                    say(line.rstrip())
        say()
        say('表在：%s' % out)
    return r.returncode


def powershell():
    return shutil.which('powershell') or shutil.which('pwsh')


def api_args(ctx, extra, pay=None):
    """The command line of player_review_api.ps1. pay: 'sub' adds -Subscription (every task runs on the reviewer
    program's own login); not given = --pay / the remembered choice (plan and fake never ask)."""
    a = ctx['args']
    ps = powershell()
    if not ps:
        say('找不到 PowerShell：API 模式的脚本是 PowerShell 写的。Windows 自带；别的系统装 pwsh。')
        return None
    cmd = [ps, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(KIT, 'api', 'player_review_api.ps1'),
           '-ProjectFile', ctx['path']]
    lf = local_file(a, ctx['state'])
    if lf:
        cmd += ['-LocalFile', lf]
    if a.get('groups'):
        cmd += ['-Groups', a['groups']]
    if a.get('split'):
        cmd += ['-SplitByCharacters']
    if a.get('parallel'):
        cmd += ['-Parallel', '-MaxParallel', str(a['parallel'])]
    if a.get('no_map'):
        cmd += ['-NoMap']
    if a.get('map_dir'):
        cmd += ['-MapDir', a['map_dir']]
    if a.get('no_merge'):
        cmd += ['-NoMerge']
    if a.get('kind'):
        cmd += ['-Kind', a['kind']]
    for key, flag in (('scope', '-Scope'), ('out', '-OutDir'), ('max_turns', '-MaxTurns')):
        if a.get(key):
            cmd += [flag, str(a[key])]
    if '-PrepareOnly' in extra:
        return cmd + extra
    if (pay or pay_of(ctx)[0]) == 'sub':
        cmd += ['-Subscription']
    if a.get('runner') and '-Runner' not in extra:     # --runner: another runner (the fake one for tests)
        cmd += ['-Runner', a['runner']]
    return cmd + runner_target(ctx) + extra


def run_api(ctx, extra, quiet=False, pay=None):
    cmd = api_args(ctx, extra, pay)
    if not cmd:
        return 2, ''
    if quiet:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        return r.returncode, (r.stdout or '') + (r.stderr or '')
    return subprocess.run(cmd).returncode, ''


def parse_plan(text):
    d = {'groups': [], 'summary': '', 'outDir': '', 'warnings': [], 'tasks': re.findall(r'^\s+\[([^\]]+)\] ', text, re.M)}
    for line in text.splitlines():
        if line.startswith('Groups:'):
            d['groups'] = [x.strip() for x in line[len('Groups:'):].split(' | ') if x.strip()]
        elif line.startswith('Tasks :'):
            d['summary'] = line[len('Tasks :'):].strip()
        elif line.startswith('Out folder'):
            path = line.split(':', 1)[1].strip()
            suffix = ' (task_<name>.md, log_<name>.txt)'
            d['outDir'] = path[:-len(suffix)] if path.endswith(suffix) else path
        elif 'WARNING' in line or line.startswith('警告') or 'rror' in line or 'Exception' in line:
            d['warnings'].append(line.strip())
    return d


def show_plan(text):
    d = parse_plan(text)
    if d['groups']:
        say('审查组：' + '\n        '.join(d['groups']))
    if d['summary']:
        say('任务　：' + d['summary'])
    if d['outDir']:
        say('文件夹：' + d['outDir'])
    for w in d['warnings']:
        say('  ! ' + w)
    if d['tasks']:
        say('一共 %d 个任务：%s' % (len(d['tasks']), '、'.join(d['tasks'])))
    return len(d['tasks'])


def preview_dir(ctx):
    """Dry runs write their task files here (not into the project's review folder), emptied each time."""
    if ctx['args'].get('out'):
        return []
    d = os.path.join(STATE_DIR, 'plan_preview')
    shutil.rmtree(d, ignore_errors=True)
    return ['-OutDir', d]


EST_KINDS = ('审查', '作品地图', '合并', '内容提案')     # the ledger's kinds of task a check is made of (not the guide, not fixes)


def estimate(ctx, tasks, model=None):
    """How much these tasks (names as a dry run lists them: map, A, A_part1, merge_A, merge, G1, expand) may use,
    from the cost ledger: per task the average of earlier tasks of the same kind on the same model (all kinds
    together when there are none of that kind), added up. Nothing is made up: no earlier task on this model = no
    number. Returns {model, tasks, basedOn, usd (Claude Code's own figure), priced, currency (the price table's),
    tokens, text: {sub, api} (one sentence each)}."""
    cl = ledger_mod()
    m = current_model(ctx)[0] if model is None else model
    try:
        rows = cl.read_ledger(ledger_file(ctx))
    except (OSError, ValueError):
        rows = []
    rows = [r for r in rows if (r.get('模型') or '') == (m or '(cli default)') and r.get('类别') in EST_KINDS]
    kinds = [cl.task_kind(t) for t in tasks]

    def number(v):
        try:
            return float(v) if v not in (None, '') else None
        except (TypeError, ValueError):
            return None

    def total(value):
        out = 0.0
        for k in kinds:
            vals = [x for x in (value(r) for r in rows if r.get('类别') == k) if x is not None] or \
                   [x for x in (value(r) for r in rows) if x is not None]
            if not vals:
                return None
            out += sum(vals) / len(vals)
        return out

    def tokens(r):
        vals = [number(r.get(k)) for k in ('输入token', '输出token', '缓存写token', '缓存读token')]
        return sum(v for v in vals if v is not None) if any(v is not None for v in vals) else None

    cur = ''
    with_price = [r.get('币种') or 'USD' for r in rows if number(r.get('按价目表')) is not None]
    if with_price:
        cur = max(set(with_price), key=with_price.count)
    est = {'model': m or '', 'tasks': len(tasks), 'basedOn': len(rows), 'usd': total(lambda r: number(r.get('CLI估的USD'))),
           'tokens': total(tokens), 'currency': cur,
           'priced': total(lambda r: number(r.get('按价目表')) if (r.get('币种') or 'USD') == cur else None) if cur else None}
    name = '「%s」' % m if m else '默认型号'
    based = '照以前用这个型号的 %d 个任务平均算，这次 %d 个任务' % (len(rows), len(tasks))
    if est['usd'] is None and est['priced'] is None:
        api = '以前没用%s跑过检查，估不了。第一次建议只派一组，跑完在「花了多少钱」里看一个任务花了多少。' % name
    else:
        bits = []
        if est['priced'] is not None:
            bits.append('照价目表大概 %.2f %s' % (est['priced'], cur))
        if est['usd'] is not None:
            bits.append('大概 %.2f 美元' % est['usd'] + ('（Claude Code 照官方价估的，用别家的 AI 时不是账单）'
                                                       if current_provider(ctx)[0] != 'anthropic' and est['priced'] is None else ''))
        api = '，'.join(bits) + '（%s；实际可能更多）。' % based
    sub = ('以前没用%s跑过检查，估不了会用掉多少额度。' % name if est['tokens'] is None else
           '大概用掉 %s token 的会员额度（%s）。额度还剩多少，这里看不到。' % (wan(est['tokens']), based))
    est['text'] = {'api': api, 'sub': sub}
    return est


def task_label(proj, name):
    """One task of a check (map, A, A_part1, merge_A, merge, G1, expand) in plain words."""
    groups = OrderedDict((str(g.get('id')), g.get('name') or g.get('id')) for g in groups_of(proj))
    splits = {str(s.get('id')): s.get('name') or s.get('id') for s in proj.get('characterSplits') or []}
    if name == 'map':
        return '先把游戏整理成几张表'
    if name == 'merge':
        return '把报告汇总成一份'
    if name == 'expand':
        return '写加内容的建议'
    if name.startswith('merge_'):
        return '把「%s」的几份汇总' % groups.get(name[6:], name[6:])
    if name in groups:
        return '「%s」' % groups[name]
    for gid in sorted(groups, key=len, reverse=True):
        if name.startswith(gid + '_') and name[len(gid) + 1:] in splits:
            return '「%s」· %s' % (groups[gid], splits[name[len(gid) + 1:]])
    if re.match(r'^G\d+$', name):
        return '只派的这几类玩家'
    return name


def run_cannot(ctx, pay, what='run'):
    """Why a check (what: run / quick / expand) cannot be started from the page right now ('' when it can)."""
    if not powershell():
        return '找不到 PowerShell（Windows 自带；别的系统装 pwsh）。'
    if not (ctx.get('proj') or {}).get('reviewOutDir'):
        return '游戏的设置里没写 reviewOutDir（报告写到哪个文件夹）。'
    if pay not in PAYS:
        return '还没选用什么付。'
    problem = pay_problem(ctx, pay)
    if problem:
        return problem
    if what == 'expand' and not merged_report(ctx):
        return '还没有汇总好的报告，没法写加内容的建议。'
    if ctx['args'].get('runner'):         # a runner of one's own (the fake one, for tests) needs no program and no key
        return ''
    pv = current_provider(ctx)[0]
    d = load_providers(ctx).get(pv) or {}
    if not d.get('program'):
        return '这台电脑上没找到 %s：先装好、登录一次。装在不常见的地方的话，在「设置 → 这台电脑」里写上它在哪。' % ENGINE_NAMES.get(d.get('engine'), 'Claude Code')
    if pay == 'api' and not d.get('keyReady'):
        return '还没告诉它「%s」的钥匙（key）放在哪：在「设置 → 用哪家的 AI」里填。' % d.get('name', pv)
    return ''


def cmd_plan(ctx):
    pay = pay_of(ctx)[0]
    problem = pay_problem(ctx, pay)
    if want_json(ctx):
        if problem:
            out_json({'ok': False, 'pay': pay or None, 'error': problem})
            return 2
        code, text = run_api(ctx, ['-DryRun'] + preview_dir(ctx), quiet=True)
        d = parse_plan(text)
        d['ok'] = code == 0 and bool(d['tasks'])
        d['pay'] = pay or None
        if d['ok']:
            d['estimate'] = estimate(ctx, d['tasks'])
        else:
            d['error'] = text.strip()[-600:]
        out_json(d)
        return 0 if d['ok'] else 1
    rule('演习（不调 API、不花钱）')
    if problem:
        say(problem)
        return 2
    code, text = run_api(ctx, ['-DryRun'] + preview_dir(ctx), quiet=True)
    n = show_plan(text)
    if code != 0 and not n:
        say(text.strip()[-600:])
    else:
        say()
        if pay:
            say(pay_line(ctx, pay))
        else:
            say('用什么付：还没选。正式跑时要说：--pay sub（%s）或 --pay api（%s），或者先 prk pay。' % (PAY_NAMES['sub'], PAY_NAMES['api']))
        if pay == 'sub':
            say('每个任务是一次没有界面的运行，用的是这台电脑上登录的账号的额度。组越多用得越多：第一次先只跑一组，看用了多少。')
        else:
            say('每个任务是一次没有界面的 Claude Code 运行，按 token 收钱。没量过的项目：先只跑一组，看花费表，再乘组数估全部，往高里估。')
        if n:
            say('大概花多少：%s' % estimate(ctx, parse_plan(text)['tasks'])['text'][pay or 'api'])
        say('打开上面文件夹里的 task_*.md，就是每个审查员拿到的全部内容。')
    return code


def cmd_fake(ctx):
    rule('假 runner（不花钱，数字是假的）')
    code, _ = run_api(ctx, ['-Runner', os.path.join(KIT, 'api', 'fake_runner.ps1')])
    return code


def cmd_run(ctx):
    pay = need_pay(ctx)
    if not pay:
        return 2
    problem = pay_problem(ctx, pay)
    if problem:
        say(problem)
        return 2
    rule('正式检查（%s）' % ('用会员额度' if pay == 'sub' else '按次付费，花钱'))
    code, text = run_api(ctx, ['-DryRun'] + preview_dir(ctx), quiet=True, pay=pay)
    n = show_plan(text)
    if code != 0 or not n:
        say(text.strip()[-600:])
        return code or 1
    say()
    if pay == 'sub':
        say('这 %d 个任务会真的跑，用会员额度。停掉只停排队，已经开跑的会跑完。' % n)
    else:
        say('这 %d 个任务会真的调 API，按 token 收钱。停掉只停排队，已经开跑的会跑完。' % n)
    say(pay_line(ctx, pay) + ' 要换：prk pay，或这一次加 --pay sub|api。')
    say('服务商：%s；模型：%s（%s）。要换：prk provider <名字>、prk model <id>，或这一次加 --provider / --model。' % (
        current_provider(ctx)[0], current_model(ctx)[0] or '没指定', current_model(ctx)[1]))
    say('大概花多少：%s' % estimate(ctx, parse_plan(text)['tasks'])['text'][pay])
    if not ctx['args'].get('yes'):
        if not sys.stdin.isatty():
            say('不是在终端里：要正式跑，加 --yes。')
            return 2
        if not yes('现在开跑吗'):
            say('没有跑。')
            return 0
    code, _ = run_api(ctx, [], pay=pay)
    say()
    done = ctx['args'].get('out') or (review_dirs(ctx['proj']) or [None])[0]
    if done and os.path.isdir(done):
        ctx['args']['dir'] = done
        cmd_feedback(ctx)
        say()
        say('花费表、每份报告、任务和日志都在：%s' % done)
    return code


def quick_groups(who):
    """prk quick's players ("15 + 18": persona numbers, or names) as the one free-text group the scripts take.
    Returns (group text, the players in words, error text or '')."""
    who = re.sub(r'["\r\n\t]', ' ', who or '').strip().lstrip('-–— ').strip()[:300]   # a leading - would read as a switch
    if not who:
        return '', '', '写玩家类型的编号，用 + 隔开（例：15 + 18），也可以直接写名字。'
    if re.match(r'^[\d\s+,，、]+$', who):
        nums = [int(x) for x in re.findall(r'\d+', who)]
        if not nums:
            return '', '', '至少写一个玩家类型的编号（例：15 + 18）。'
        names = {n: title for n, title, _c, _f in load_personas()}
        missing = [n for n in nums if n not in names]
        if missing:
            return '', '', '画像库里没有这些编号：%s' % '、'.join(str(n) for n in missing)
        who = ' + '.join('%d %s' % (n, names[n]) for n in nums)
    return who.replace(',', '，'), who, ''     # an ASCII comma would be read as a list of group ids


def cmd_quick(ctx):
    """One reviewer, a few personas, no map, no merge: the fastest way to hear one kind of player."""
    a = ctx['args']
    if not (a.get('word') or '').strip():
        say('用法：prk quick "15 + 18"  （画像编号，用 + 隔开；也可以直接写名字。--kind 走法 id，不写 = persona）')
        say('画像有哪些：prk personas；这类游戏该派谁：prk suggest <游戏类型>。')
        return 2
    groups, who, err = quick_groups(a.get('word'))
    if err or not groups or ',' in groups:
        say(err or '快速检查只能派一组玩家。')
        return 2
    a['groups'] = groups
    a['no_merge'] = True
    a.setdefault('no_map', True)
    a.pop('split', None)
    say('只问这几类玩家：%s（走法：%s；一个任务，不建地图、不合并）' % (who, a.get('kind') or 'persona'))
    return cmd_run(ctx)


def cmd_prepare(ctx):
    a, proj = ctx['args'], ctx['proj']

    def error(message, code=2):
        out_json({'ok': False, 'error': message, **output_metadata(proj)}) if want_json(ctx) else say(message)
        return code

    if proj.get('language', 'zh') not in LANGUAGES:
        return error('language 只能是 zh 或 en。')
    if not powershell():
        return error('找不到 PowerShell。')
    if 'who' in a:
        if a.get('groups') or a.get('split') or a.get('map_dir'):
            return error('--who 只派一个任务，不能和 --groups、--split 或 --map-dir 一起用。')
        group, _who, problem = quick_groups(a['who'])
        if problem:
            return error(problem)
        a.update(groups=group, no_map=True, no_merge=True)
    elif a.get('kind'):
        return error('--kind 要和 --who 一起用。')
    base = proj.get('reviewOutDir')
    for field, kind in [('projectRoot', 'dir'), ('modSource', 'dir'), ('reviewOutDir', 'out')]:
        problem = path_problem(field, proj.get(field), kind, required=True)
        if problem:
            return error(problem)
    if a.get('out'):
        return error('prepare 把任务写进项目的 reviewOutDir。请去掉 --out。')
    folder, output = None, ''
    try:
        os.makedirs(base, exist_ok=True)
        stamp = time.strftime('%Y%m%d_%H%M%S')
        suffix = 1
        while True:
            folder = os.path.join(base, stamp if suffix == 1 else '%s_%d' % (stamp, suffix))
            try:
                os.mkdir(folder)
                break
            except FileExistsError:
                suffix += 1
        code, output = run_api(ctx, ['-PrepareOnly', '-OutDir', folder], quiet=True)
        placeholder = next((line for line in output.splitlines()
                            if line.startswith('Unfilled task placeholder ')), '')
        if code == 1 and placeholder:
            return error(placeholder, 1)
        data = read_json(os.path.join(folder, '_prepared.json'))
    except (OSError, ValueError) as exc:
        if folder:
            try:
                os.rmdir(folder)
            except OSError:
                pass
        return error(output.strip()[-1500:] or str(exc))
    if want_json(ctx):
        out_json(dict(data, **output_metadata(proj, folder)))
    else:
        say('已准备 %d 个任务，分 %d 个阶段。清单在 %s' % (data['count'], len(data['stages']), folder))
        if not data['static']['ok']:
            say('静态表没跑全，任务文件已写好。')
            say(output.strip()[-1500:])
    return 0 if data['ok'] else 1


def review_dirs(proj):
    base = proj.get('reviewOutDir')
    if not base or not os.path.isdir(base):
        return []
    ds = [os.path.join(base, d) for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and not d.startswith('_')]
    return sorted(ds, key=os.path.getmtime, reverse=True)


def cost_name(proj):
    return names(proj, 'cost')[0]


def check_round(proj, selected=None, sample=True):
    """Resolve one round without promoting an older round when its page is regenerated."""
    base = proj.get('reviewOutDir')
    demo = proj.get('sampleRound') if sample else None
    if selected == '':
        return None, False
    if selected is None:
        def started(path):
            m = re.fullmatch(r'(\d{8}_\d{6})(?:_(\d+))?', os.path.basename(path))
            if m:
                try:
                    return time.mktime(time.strptime(m[1], '%Y%m%d_%H%M%S')), int(m[2] or 1)
                except (ValueError, OverflowError):
                    pass
            return os.path.getmtime(path), 0

        folder = max(review_dirs(proj), key=started, default=None) or demo
    elif demo and selected == '__sample__':
        folder = demo
    else:
        named = os.path.join(base, selected) if base else selected
        folder = named if os.path.isdir(named) else selected
        if demo and not os.path.isdir(folder) and selected == os.path.basename(os.path.normpath(demo)):
            folder = demo
    if not folder or not os.path.isdir(folder):
        return None, False
    folder = os.path.realpath(folder)
    return folder, bool(demo and same_path(folder, demo))


def same_path(a, b):
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def round_member(folder, path):
    """Only actual files under this round may be read or linked from its generated page."""
    folder, real = (os.path.normcase(os.path.realpath(p)) for p in (folder, path))
    try:
        return folder != real and os.path.commonpath([folder, real]) == folder
    except ValueError:
        return False


def prepared_tasks(folder, never=()):
    path = os.path.join(folder, '_prepared.json')
    if not os.path.isfile(path) or not round_member(folder, path) or protected_path(path, never):
        return None
    return [task for stage in read_json(path)['stages'] for task in stage['tasks']]


def output_written(folder, path):
    return round_member(folder, path) and os.path.isfile(path) and os.path.getsize(path) > 0


def task_written(proj, folder, task, never=()):
    path = task['writes']
    if task['kind'] == 'map' or not round_member(folder, path):
        candidates = [path]
    else:
        candidates = [os.path.join(os.path.dirname(path), n) for n in report_aliases(proj, os.path.basename(path))]
    return next((p for p in candidates if not protected_path(p, never) and output_written(folder, p)), None)


def round_reports(proj, folder, never=()):
    """Reports to check, including intermediate merges and excluding auxiliary Markdown files."""
    tasks = prepared_tasks(folder, never)
    candidates = (existing_reports(folder, proj, lambda p: protected_path(p, never)) if tasks is None else
                  [task_written(proj, folder, t, never) for t in tasks if t['kind'] != 'map'])
    return list(dict.fromkeys(p for p in candidates if p and not protected_path(p, never) and output_written(folder, p)))


def cmd_reports(ctx):
    proj = ctx['proj']
    ds = review_dirs(proj)
    if want_json(ctx):
        rows = []
        for d in ds[:30]:
            merged, cost = (named_path(proj, d, k) for k in ('merged', 'cost'))
            rows.append({'dir': d, 'reports': [os.path.basename(p) for p in existing_reports(d, proj)],
                         'merged': merged if os.path.isfile(merged) else None,
                         'cost': cost if os.path.isfile(cost) else None,
                         'map': os.path.isdir(os.path.join(d, '_map')), **output_metadata(proj, d)})
        out_json({'reviewOutDir': proj.get('reviewOutDir'), 'reviews': rows})
        return 0
    rule('最近的审查（%s）' % (proj.get('reviewOutDir') or '没写 reviewOutDir'))
    if not ds:
        say('还没有。')
        return 0
    for d in ds[:12]:
        files = os.listdir(d)
        reports = [f for f in files if f.endswith('.md') and f != 'review.md' and not f.startswith(('_', 'task_'))]
        bits = ['%d 份报告' % len(reports)]
        if os.path.isfile(named_path(proj, d, 'merged')):
            bits.append('有合并报告')
        if os.path.isfile(named_path(proj, d, 'cost')):
            bits.append('有花费表')
        if os.path.isdir(os.path.join(d, '_map')):
            bits.append('有地图')
        say('%s   %s' % (os.path.basename(d), '，'.join(bits)))
    say()
    say('文件夹：%s' % (proj.get('reviewOutDir')))
    return 0


def md_sections(text, word):
    """Every section whose heading has `word` in it: (heading, body up to the next heading of the same or a higher level)."""
    lines = text.splitlines()
    english = {heading.casefold() for heading in SECTIONS.get(word, ())}
    out, i, fence = [], 0, False
    while i < len(lines):
        if lines[i].lstrip().startswith('```'):
            fence = not fence
        m = None if fence else re.match(r'^(#{1,6})\s+(.*)$', lines[i])
        if m and (word in m[2] or m[2].strip().casefold() in english):
            level, j, f2 = len(m.group(1)), i + 1, False
            while j < len(lines):
                if lines[j].lstrip().startswith('```'):
                    f2 = not f2
                n = None if f2 else re.match(r'^(#{1,6})\s', lines[j])
                if n and len(n.group(1)) <= level:
                    break
                j += 1
            out.append((m.group(2).strip(), '\n'.join(lines[i + 1:j]).strip()))
            i = j
            continue
        i += 1
    return out


def parse_feedback(body):
    """Players and what they say, from the Markdown of a feedback section: "### player" blocks with "- kind：text" lines, or table rows."""
    players, cur = [], None
    for line in body.splitlines():
        s = line.strip()
        m = re.match(r'^#{2,6}\s+(.*)$', s)
        if m:
            cur = {'player': m.group(1).strip(), 'says': []}
            players.append(cur)
            continue
        m = re.match(r'^[-*]\s+\**([^：:*]{1,40})\**[：:]\**\s*(.+)$', s)
        if m and cur is not None:
            cur['says'].append({'kind': m.group(1).strip(), 'text': m.group(2).strip(), 'refs': re.findall(r'\b[SMLDW]\d+\b', m.group(2))})
            continue
        if s.startswith('|') and not re.match(r'^[\s|:\-]+$', s):
            cells = [c.strip() for c in s.strip('|').split('|')]
            if len(cells) >= 2 and cells[0].casefold() not in ('玩家类型', '玩家类型（画像）', '画像', '玩家', 'player type', 'player type (persona)', 'persona', 'player'):
                players.append({'player': cells[0], 'says': [{'kind': '', 'text': cells[1], 'refs': re.findall(r'\b[SMLDW]\d+\b', ' '.join(cells[1:]))}]})
    return [x for x in players if x['says']]


def collect_feedback(ctx, *, with_sources=False, never=None):
    """The newest round (or the one asked for): its player feedback, its entries, where the files are."""
    proj, a = ctx['proj'], ctx['args']
    if never is None:
        never = tuple(proj.get('neverRead') or ()) + tuple(machine_never_read(ctx))
    src, folder, merged = [], None, False
    if a.get('from'):
        if not protected_path(a['from'], never) and os.path.isfile(a['from']):
            src, folder, merged = [a['from']], os.path.dirname(os.path.abspath(a['from'])), is_merged(os.path.basename(a['from']), proj)
    else:
        dirs = [a['dir']] if a.get('dir') else review_dirs(proj)
        for d in dirs:
            if protected_path(d, never) or not os.path.isdir(d):
                continue
            combined = named_path(proj, d, 'merged')
            if output_written(d, combined) and not protected_path(combined, never):
                src, folder, merged = [combined], d, True
                break
            files = [p for p in round_reports(proj, d, never) if not is_merged(os.path.basename(p), proj)]
            if files:
                src, folder = files, d
                break
    if not src:
        return None
    data = {'project': proj.get('name'), 'dir': folder, 'reports': src, 'merged': merged, 'counts': {k: 0 for k in 'SMLDW'},
            'entries': [], 'feedback': [], 'feedbackMarkdown': '', 'lastRound': '', 'conclusion': '',
            **output_metadata(proj, folder)}
    parts = []
    for rp in src:
        with open(rp, encoding='utf-8-sig', errors='replace') as f:
            text = f.read()
        name = os.path.basename(rp)
        bodies = entry_bodies(text)
        for m in re.finditer(r'(?m)^### ([SMLDW]\d+)[ \t]+(.*)$', text):
            conf = CONFIDENCE.search(bodies.get(m[1], ''))
            data['entries'].append({'id': m.group(1), 'title': m.group(2).strip(), 'confidence': conf.group(1) if conf else '', 'report': name})
            data['counts'][m.group(1)[0]] += 1
        fb = [body for head, body in md_sections(text, '玩家反馈') if body]
        if fb:
            parts.append(('' if len(src) == 1 else '〔%s〕\n' % name) + '\n\n'.join(fb))
            for body in fb:
                players = parse_feedback(body)
                if with_sources:
                    for player in players:
                        player['report'] = name
                data['feedback'] += players
        for head, body in md_sections(text, '上一轮反馈的去向')[:1]:
            data['lastRound'] = body
        for head, body in md_sections(text, '结论')[:1]:
            data['conclusion'] = data['conclusion'] or body
    data['feedbackMarkdown'] = '\n\n'.join(parts)
    return data


def feedback_text(d):
    """The same text for the terminal and for the saved file (Markdown, readable as plain text)."""
    c = d['counts']
    if d.get('language') == 'en':
        source = 'Merged report' if d['merged'] else '%d reviewer reports (may contain duplicates)' % len(d['reports'])
        lines = ['# Player feedback · %s' % (d['project'] or ''), '', 'From: ' + source, 'Folder: ' + d['dir'],
                 'Severe %d · Medium %d · Minor %d · Decisions %d · Wanted but missing %d' % tuple(c[k] for k in 'SMLDW'), '']
        sections = [('Conclusion', d['conclusion']),
                    ('Player feedback', d['feedbackMarkdown'] or 'No player feedback in these reports.'),
                    ('Follow-up on last round', d['lastRound'])]
        for heading, body in sections:
            if body:
                lines += ['## ' + heading, '', body, '']
        if d['entries']:
            lines += ['## Findings', '']
            for entry in d['entries']:
                source = '' if d['merged'] else '  (%s)' % entry['report']
                lines.append('- %s  %s  %s%s' % (entry['id'], entry['title'], entry['confidence'], source))
            lines.append('')
        lines += ['Full reports:'] + ['  %s' % r for r in d['reports']]
        return '\n'.join(lines)
    L = ['# 玩家反馈 · %s' % (d['project'] or ''), '',
         '来自：%s' % ('合并报告' if d['merged'] else '%d 份审查员的报告（还没合并，可能有重复）' % len(d['reports'])),
         '文件夹：%s' % d['dir'],
         '一共：严重 %d、中 %d、轻 %d、要定 %d、想要但没有的 %d' % (c['S'], c['M'], c['L'], c['D'], c['W']), '']
    if d['conclusion']:
        L += ['## 结论', '', d['conclusion'], '']
    L += ['## 玩家怎么说', '']
    L += [d['feedbackMarkdown'] if d['feedbackMarkdown'] else '（这一轮的报告里没有「玩家反馈」一节：是旧格式的报告，或者审查员没写。条目在下面。）', '']
    if d['lastRound']:
        L += ['## 上一轮反馈的去向', '', d['lastRound'], '']
    if d['entries']:
        L += ['## 条目（详细的在完整报告里，按编号找）', '']
        L += ['- %s  %s  %s%s' % (e['id'], e['title'], e['confidence'], '' if d['merged'] else '  〔%s〕' % e['report']) for e in d['entries']]
        L.append('')
    L += ['完整报告：'] + ['  %s' % r for r in d['reports']]
    return '\n'.join(L)


def cmd_feedback(ctx):
    a = ctx['args']
    d = collect_feedback(ctx)
    if d is None:
        if want_json(ctx):
            out_json({'ok': False, 'error': 'no report found'})
        else:
            say('没找到报告（先跑一轮审查；或者 --from 指一份报告，或在命令后面写文件夹）。')
        return 1
    if want_json(ctx):
        d['ok'] = True
        out_json(d)
        return 0
    if a.get('full'):
        for rp in d['reports']:
            rule(rp)
            with open(rp, encoding='utf-8-sig', errors='replace') as f:
                say(f.read().rstrip())
        return 0
    text = feedback_text(d)
    say()
    say(text)
    if a.get('save'):
        out = a['save']
        if os.path.isdir(out):
            out = os.path.join(out, 'player-feedback.md' if d.get('language') == 'en' else '玩家反馈.md')
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text + '\n')
        say()
        say('另存了一份：%s' % os.path.abspath(out))
    say()
    say('接下来：prk decide 记下你对每条的决定；prk cite 核一遍出处；prk feedback --full 看整份报告。')
    return 0


def cmd_cost(ctx):
    proj = ctx['proj']
    d = ctx['args'].get('dir')
    if not d:
        with_cost = [x for x in review_dirs(proj) if os.path.exists(named_path(proj, x, 'cost'))]
        if not with_cost:
            say('没找到花费表（只有 API 模式跑过才有）。')
            return 1
        d = with_cost[0]
    p = named_path(proj, d, 'cost')
    if not os.path.exists(p):
        say('这里没有花费表：%s' % p)
        return 1
    rule('花费表：%s' % d)
    with open(p, encoding='utf-8') as f:
        say(f.read().rstrip())
    return 0


def ledger_mod():
    sys.path.insert(0, os.path.join(KIT, 'api'))   # -I drops the script folder from the path
    import cost_ledger
    return cost_ledger


def ledger_file(ctx):
    """The cost ledger: in the project's review folder; without a project, in the kit's state folder (guide questions only)."""
    if ctx.get('proj') and ctx['proj'].get('reviewOutDir'):
        return ledger_mod().ledger_path(ctx['proj'])
    return os.path.join(STATE_DIR, ledger_mod().LEDGER_NAME)


def remember_ledger(ctx):
    if not (ctx.get('proj') or {}).get('reviewOutDir'):
        return
    path = os.path.realpath(ledger_file(ctx))
    key = hashlib.sha256(os.fsencode(os.path.normcase(path))).hexdigest()
    record = os.path.join(STATE_DIR, 'ledgers', key + '.json')
    try:
        if not os.path.isfile(record):
            atomic_json(record, path)
    except OSError:
        pass  # The registry is only for finding other projects' ledgers.


def budget_of(ctx):
    """The monthly budget in US dollars (state file: budget), or None."""
    try:
        b = float(ctx['state'].get('budget'))
    except (TypeError, ValueError):
        return None
    return b if b > 0 else None


def set_budget(ctx, value):
    """Remember the monthly budget ('' / 0 = none). It is only shown (the page's small bar, prk costs); it stops nothing.
    Returns an error text or ''."""
    v = str('' if value is None else value).strip().lstrip('$').strip()
    st = ctx['state']
    if v.lower() in ('', '0', 'none', '不设'):
        st.pop('budget', None)
    else:
        try:
            b = float(v)
        except ValueError:
            return '每个月最多花多少：写一个数（美元），例如 20；不设就写 0。'
        if not 0 < b < 1e6:
            return '每个月最多花多少：写一个大于 0 的数（美元）。'
        st['budget'] = round(b, 2)
    save_state(st)
    return ''


def month_use(ctx):
    """This month's use across every ledger the kit knows (each known project's, and the one for guide questions
    asked without a project), with the budget. See cost_ledger.month_usage."""
    import datetime
    cl = ledger_mod()
    paths = [os.path.join(STATE_DIR, cl.LEDGER_NAME)]
    known_folders = set()
    for p in find_projects(ctx['state']) + ([ctx['path']] if ctx.get('path') else []):
        try:
            proj, _ = projfile.load_project(p)
        except (SystemExit, OSError, ValueError):
            continue
        if proj.get('reviewOutDir'):
            paths.append(cl.ledger_path(proj))
            known_folders.add(os.path.normcase(os.path.realpath(proj['reviewOutDir'])))
    registry = os.path.join(STATE_DIR, 'ledgers')
    if os.path.isdir(registry):
        for name in os.listdir(registry):
            if name.endswith('.json'):
                try:
                    path = read_json(os.path.join(registry, name))
                    if (isinstance(path, str) and os.path.isabs(path)
                            and os.path.normcase(os.path.dirname(path)) not in known_folders):
                        paths.append(path)
                except (OSError, ValueError):
                    continue
    seen, rows = set(), []
    for p in paths:
        k = os.path.normcase(os.path.realpath(p))
        if k not in seen:
            seen.add(k)
            try:
                rows += cl.read_ledger(p)
            except (OSError, ValueError):
                pass
    u = cl.month_usage(rows, datetime.date.today().strftime('%Y-%m'))
    u['budget'] = budget_of(ctx)
    return u


def wan(n):
    """A token count the way people say it: 3.5 万 rather than 35000."""
    return ('%.1f 万' % (n / 10000.0)).replace('.0 万', ' 万') if n >= 10000 else str(int(n))


def month_line(u):
    s = '这个月（%s）：按次付费 $%.2f' % (u['month'], u['usd'])
    if u.get('budget'):
        s += ' / 预算 $%.2f（用了 %d%%）' % (u['budget'], round(u['usd'] * 100 / u['budget']))
    if u.get('other'):
        s += '，另有 ' + '、'.join('%.2f %s' % (v, k) for k, v in u['other'].items())
    if u.get('subTasks'):
        s += '；会员额度：用了约 %s token（还剩多少看不到，这里只记这个工具自己用了多少）' % wan(u['subTokens'])
    return s + '。'


def cmd_costs(ctx):
    """prk costs             the cost ledger: one row per task, every round (this month first, then totals, then the latest tasks)
       prk costs --rebuild   read every round folder again (also brings in rounds from before the ledger existed)
       prk costs --budget N  at most N US dollars a month (paid by use); only shown, never stops a run; 0 = none"""
    cl = ledger_mod()
    path = ledger_file(ctx)
    if ctx['args'].get('budget') is not None:
        err = set_budget(ctx, ctx['args']['budget'])
        if err:
            out_json({'ok': False, 'error': err}) if want_json(ctx) else say(err)
            return 2
    if ctx['args'].get('rebuild'):
        base = (ctx.get('proj') or {}).get('reviewOutDir')
        if not base or not os.path.isdir(base):
            say('这个项目还没有审查的文件夹，没有可以重记的。')
            return 1
        folders = [os.path.join(base, d) for d in sorted(os.listdir(base)) if os.path.isdir(os.path.join(base, d))]
        rows = []
        for d in folders:
            rows += cl.rows_for_round(d, read_local(ctx).get('prices'))
        cl.update(path, rows, [os.path.basename(d) for d in folders], lang=language(ctx.get('proj')))
    month = month_use(ctx)
    rows = cl.read_ledger(path)
    s = cl.summarize(rows)
    if want_json(ctx):
        out_json({'ok': True, 'file': path, 'month': month, 'summary': s, 'rows': rows,
                  **output_metadata(ctx.get('proj'))})
        return 0
    say(month_line(month))
    rule('花费总账：每个任务一行')
    say('文件：%s' % mask_home(path))
    if not rows:
        say('还没有记录。跑过真的任务（审查、内容提案、问向导）以后这里才有；假 runner 不记。')
        say('以前跑过、但总账里没有的轮次：prk costs --rebuild。')
        return 0
    say('一共 %d 个任务，失败 %d 个。Claude Code 估的花费 %.2f 美元%s。' % (
        s['tasks'], s['failed'], s['usd'], '；订阅那边折算 %.2f 美元（不另收钱）' % s['usdSubscription'] if s['usdSubscription'] else ''))
    if s.get('priced'):
        say('按价目表算：%s。' % '，'.join('%.2f %s' % (v, k) for k, v in s['priced'].items()))
    say('（"Claude Code 估的"是照 Anthropic 的价目算的：用官方 API 时就是账单；接别家的模型时不是，看"按价目表"。价目表写在机器设置的 prices。）')
    for title, key in (('按服务商', 'byProvider'), ('按模型', 'byModel'), ('按任务的类别', 'byKind'), ('按谁付的', 'byPaid'), ('按天（最近 7 天）', 'byDay'), ('按轮次（最近 8 轮）', 'byRound')):
        say()
        say('%s：' % title)
        for b in s[key][:7 if key == 'byDay' else 8 if key == 'byRound' else 20]:
            say('  %-28s %3d 个任务  %8.2f 美元（估）%s  %5d 步%s' % (b['name'], b['tasks'], b['usd'],
                ''.join('  %.2f %s' % (v, k) for k, v in (b.get('priced') or {}).items()), b['turns'], '  失败 %d' % b['failed'] if b['failed'] else ''))
    say()
    say('最近的任务：')
    for r in rows[-12:]:
        say('  %s  %-16s %-8s %-10s %-20s %7s 美元%s  %s' % (r['开始时间'][:16], r['轮次'][:16], r['类别'], (r.get('提供方') or '')[:10], r['模型'][:20],
            r.get('CLI估的USD') or '-', '（价目表 %s %s）' % (r['按价目表'], r['币种']) if r.get('按价目表') else '', r['结果']))
    say()
    say('这张表可以直接用表格软件打开。数是从每个任务的日志里读的，没有的就空着。')
    return 0


def cmd_cite(ctx):
    proj = ctx['proj']
    d = ctx['args'].get('dir')
    if not d:
        ds = review_dirs(proj)
        if not ds:
            say('还没有审查的文件夹。')
            return 1
        d = ds[0]
    rule('引文核验：%s' % d)
    out = os.path.join(d, '_citations.md')
    r = subprocess.run(cite_cmd(ctx, d), capture_output=True)
    if not cite_written(r, out):
        say((r.stderr + r.stdout).decode('utf-8', 'replace').strip() or '这次没有写出引文核验表。')
        return r.returncode or 1
    with open(out, encoding='utf-8') as f:
        say(f.read().rstrip())
    return 0


def cite_written(result, path):
    return (result.returncode == 0 and os.path.isfile(path)
            and b'citations-written' in result.stdout.splitlines())


def cite_cmd(ctx, d, *, out=None, reports=None):
    """The citation check of one round folder (free, a few seconds): writes _citations.md into it."""
    cmd = [python_for(ctx), '-I', os.path.join(KIT, 'static', 'check_citations.py'), '--project', ctx['path']]
    machine = machine_never_read(ctx)
    for path in machine:
        cmd += ['--never', path]
    if reports is None:
        never = tuple(ctx['proj'].get('neverRead') or ()) + tuple(machine)
        reports = round_reports(ctx['proj'], d, never)
    return cmd + ['--out', out or os.path.join(d, '_citations.md')] + (reports if reports is not None else [d])


def merged_report(ctx):
    """The merged report to work from: --from, or the newest review folder that has one."""
    proj = ctx['proj']
    p = ctx['args'].get('from')
    if p:
        return p if os.path.exists(p) else None
    for d in review_dirs(proj):
        path = named_path(proj, d, 'merged')
        if os.path.isfile(path):
            return path
    return None


DECISIONS = ['修', '放进待做', '是设计', '不是问题', '误报']
DECISIONS_EN = ['fix', 'later', 'by-design', 'not-an-issue', 'false-positive']
DECISION_HEAD = ['日期', '合并报告', '编号', '把握', '核对结论', '决定', '一句原因']
DECISION_HEAD_EN = ['Date', 'Merged report', 'ID', 'Confidence', 'Verification', 'Decision', 'Reason']


def decision_word(value, lang='zh'):
    value = value.strip().casefold()
    for zh, en in zip(DECISIONS, DECISIONS_EN):
        if value in (zh, en):
            return en if lang == 'en' else zh
    return ''


def write_decisions(out, rows, lang=None):
    """Append rows to the decision record (the ledger of the loop: the next round starts from it)."""
    import csv
    lang = lang or ('en' if os.path.basename(out) == 'decisions.csv' else 'zh')
    new = not os.path.exists(out) or not os.path.getsize(out)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, 'a', encoding='utf-8-sig' if new else 'utf-8', newline='') as f:
        w = csv.writer(f)
        if new:
            w.writerow(DECISION_HEAD_EN if lang == 'en' else DECISION_HEAD)
        w.writerows([*row[:5], decision_word(row[5], lang) or row[5], *row[6:]] for row in rows)


def read_decisions(path):
    """Rows of a decision record as dicts (empty when there is none)."""
    import csv
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    base = os.path.dirname(os.path.abspath(path))
    out = []
    for r in rows[1:]:
        if not r:
            continue
        d = dict(zip(DECISION_HEAD, r + [''] * (len(DECISION_HEAD) - len(r))))
        d['决定'] = decision_word(d['决定']) or d['决定']
        rp = d['合并报告'].strip()
        if rp and not os.path.isabs(rp):    # written by hand relative to the record's own folder (the review folder)
            d['合并报告'] = os.path.normpath(os.path.join(base, rp))
        out.append(d)
    return out


def report_identity(proj, path):
    folder, name = os.path.split(os.path.abspath(path))
    return os.path.normcase(os.path.join(folder, report_aliases(proj, name)[0]))


def decisions_by_entry(proj, sample=False):
    return {(report_identity(proj, row['合并报告']), row['编号']): row
            for row in read_decisions(decisions_file(proj, sample)) if row['合并报告']}


def decision_entries(reports):
    """Entries in report order, with the details shared by the offline page and CLI."""
    entries = []
    for report in reports:
        with open(report, encoding='utf-8-sig', errors='replace') as f:
            text = f.read()
        bodies = entry_bodies(text)
        for m in re.finditer(r'(?m)^### ([SMLDW]\d+)[ \t]+(.*)$', text):
            ident, title = m.groups()
            body = bodies.get(ident, '')
            conf = CONFIDENCE.search(body)
            check = CHECK.search(body)
            entries.append({'id': ident, 'title': title.strip(), 'report': os.path.abspath(report), 'body': body,
                            'confidence': conf[1] if conf else '', 'check': check[1].strip()[:60] if check else ''})
    return entries


def record_decisions(proj, sample, choices):
    """Write validated owner choices from either CLI input path and sync the existing fix list."""
    import datetime
    day = datetime.date.today().isoformat()
    path = decisions_file(proj, sample)
    lang = language(proj)
    choices = [(e, decision_word(d, lang), why) for e, d, why in choices]
    rows = [[day, e['report'], e['id'], e['confidence'], e['check'], decision, why] for e, decision, why in choices]
    result = {'ok': True, 'recorded': [{'id': e['id'], 'decision': decision, 'why': why}
                                      for e, decision, why in choices], 'fixAdded': [], 'file': path}
    if not rows:
        return result
    key = hashlib.sha256(os.fsencode(os.path.normcase(os.path.realpath(path)))).hexdigest()
    lock = os.path.join(STATE_DIR, 'decisions', key)
    with ledger_mod().ledger_lock(lock):
        write_decisions(path, rows, lang)
        for e, decision, why in choices:
            try:
                got = fix_sync(proj, sample, e['report'], e['id'], decision, e['title'], e['body'], why)
                if got['added']:
                    result['fixAdded'].append(got['fix'])
            except OSError as exc:
                result['ok'] = False
                result.setdefault('fixErrors', []).append('%s 的决定已记，待修清单没写成：%s' % (e['id'], exc))
    return result


def parse_decisions(text, entries):
    by_id = {}
    for entry in entries:
        by_id.setdefault(entry['id'], []).append(entry)
    choices, seen = [], set()
    for line in text.split(';'):
        ident, separator, value = line.strip().partition('=')
        ident = ident.strip().upper()
        if not separator or not ident:
            raise ValueError('决定格式应为 编号=决定：%s' % (line.strip() or '（空）'))
        if ident not in by_id:
            raise ValueError('这一轮的报告里没有 %s。' % ident)
        if len(by_id[ident]) > 1:
            raise ValueError('多份报告都有 %s，请用 --from 指定一份报告。' % ident)
        if ident in seen:
            raise ValueError('这一批里的 %s 出现了两次。' % ident)
        copied = re.fullmatch(r'\s*(.*?)\s*[（(](?:原因[：:]|reason:)\s*(.*)[）)]\s*', value, re.I)
        parts = list(copied.groups()) if copied else re.split(r'[：:]', value, maxsplit=1)
        decision = decision_word(parts[0])
        if not decision:
            raise ValueError('%s 的决定「%s」不认识。可用：%s' % (ident, decision, '、'.join(DECISIONS + DECISIONS_EN)))
        why = parts[1].replace('\r', ' ').replace('\n', ' ').strip() if len(parts) > 1 else ''
        choices.append((by_id[ident][0], decision, why))
        seen.add(ident)
    return choices


def cmd_decide(ctx):
    proj, a = ctx['proj'], ctx['args']
    batch = 'set' in a
    use_json = batch and want_json(ctx)

    def error(message, code=2):
        out_json({'ok': False, 'error': message}) if use_json else say(message)
        return code

    if a.get('round') == '':
        return error('--round 后面要写检查轮次。')
    sample = False
    machine = tuple(machine_never_read(ctx))
    never = tuple(proj.get('neverRead') or ()) + machine
    if a.get('from'):
        report = os.path.abspath(a['from'])
        folder, sample = check_round(proj, a.get('round') or os.path.dirname(report))
        if folder and a.get('round') and os.path.basename(a['from']) == a['from']:
            report = os.path.join(folder, a['from'])
        if not folder or not same_path(folder, os.path.dirname(report)) or not output_written(folder, report):
            return error('找不到这份报告，或它不在指定的检查轮次里：%s' % report, 2 if batch else 1)
        if protected_path(report, machine if sample else never):
            return error('这一份报告在不许读的路径里。')
        reports = [report]
    elif batch or a.get('round'):
        folder, sample = check_round(proj, a.get('round'))
        if not folder:
            return error('找不到要记决定的检查轮次。', 2 if a.get('round') else 1)
        data = collect_feedback(dict(ctx, args={'dir': folder}), never=machine if sample else never)
        reports = data['reports'] if data else []
    else:
        report = merged_report(ctx)
        if not report:
            return error('没找到合并报告（--from 指一份，或者先跑一轮审查）。', 1)
        reports = [report]
    entries = decision_entries(reports)
    if batch:
        try:
            choices = parse_decisions(a['set'], entries)
        except ValueError as exc:
            return error(str(exc))
        try:
            result = record_decisions(proj, sample, choices)
        except OSError as exc:
            return error('没能记下决定：%s' % exc, 1)
        if use_json:
            out_json(dict(result, **output_metadata(proj, folder)))
        else:
            say('记下了 %d 条决定：%s' % (len(choices), result['file']))
            for problem in result.get('fixErrors', []):
                say(problem)
        return 0 if result['ok'] else 1

    only = [x.strip().upper() for x in (a.get('items') or '').split(',') if x.strip()]
    if only:
        entries = [e for e in entries if e['id'] in only]
    if not entries:
        return error('报告里没找到条目（### S1 / M1 / L1 / D1 / W1 这样的标题）。', 1)
    out = decisions_file(proj, sample)
    rule('记下决定：%s' % '、'.join(reports))
    say('一条一条问。1 修　2 放进待做　3 是设计　4 不是问题　5 误报　回车 = 这条先不定　q = 停')
    say('写到：%s（下一轮审查从它开始：说了修的会回头核，说了是设计的不再报）' % out)
    choices = []
    for e in entries:
        say()
        say('%s  %s  %s' % (e['id'], e['title'], e['confidence']))
        a = ask('  决定')
        if a is None or a.lower() == 'q':
            break
        if a not in ('1', '2', '3', '4', '5'):
            continue
        why = ask('  一句原因（可以不写）', '') or ''
        choices.append((e, DECISIONS[int(a) - 1], why))
    if not choices:
        say('没有记下任何决定。')
        return 0
    result = record_decisions(proj, sample, choices)
    say()
    say('记下了 %d 条：%s' % (len(choices), '、'.join('%s %s' % (e['id'], d) for e, d, _ in choices)))
    for problem in result.get('fixErrors', []):
        say(problem)
    put = result['fixAdded']
    todo = [e['id'] for e, d, _ in choices if d == '修']
    if todo:
        say('说了修的：%s。改完以后再跑一轮，审查员会回头核这几条。' % '、'.join(todo))
        say('放进了待修清单%s：prk fix 看怎么交给 AI 去修。' % ('（%s）' % '、'.join(put) if put else ''))
    wants = [ident for ident in todo if ident.startswith('W')]
    if wants:
        say('其中是「想要但没有的」：%s。要 AI 先写内容提案和草稿：prk expand --items %s' % ('、'.join(wants), ','.join(wants)))
    return 0 if result['ok'] else 1


def cmd_expand(ctx):
    rp = merged_report(ctx)
    if not rp:
        say('没找到合并报告（--from 指一份，或者先跑一轮审查）。')
        return 1
    ps = powershell()
    if not ps:
        say('找不到 PowerShell：这一步的脚本是 PowerShell 写的。')
        return 2
    pay = need_pay(ctx)
    if not pay:
        return 2
    problem = pay_problem(ctx, pay)
    if problem:
        say(problem)
        return 2
    a = ctx['args']
    rule('内容拓展（可选；%s；不改作品）' % ('用会员额度' if pay == 'sub' else '花钱'))
    say('依据：%s' % rp)
    say('做哪几条：%s' % (a.get('items') or '全部「想要但没有的」'))
    say('会跑一个任务：读合并报告和作品，写一份内容拓展提案（要加什么、怎么接上现有的、照作品格式的草稿、自查）。作品一个字不动。')
    say(pay_line(ctx, pay))
    if not a.get('yes'):
        if not sys.stdin.isatty():
            say('不是在终端里：要正式跑，加 --yes。')
            return 2
        if not yes('现在跑吗'):
            say('没有跑。')
            return 0
    attempt = run_id()
    folder = os.path.dirname(os.path.abspath(rp))
    log = os.path.join(folder, '_运行记录.txt')
    proposal = expand_output(ctx, rp, attempt)
    try:
        with open(log, 'ab') as f:
            offset = f.tell()
            result = subprocess.run(expand_cmd(ctx, rp, pay, attempt), stdout=f, stderr=subprocess.STDOUT)
    except OSError as e:
        say('写建议没开始：%s' % e)
        return 1
    lines = expand_run_lines(log, offset)
    say('\n'.join(lines))
    if expand_ok(lines, attempt, result.returncode, proposal):
        say('这次的内容提案：%s' % proposal)
        return 0
    say(api_text('expandFailed'))
    return result.returncode or 1


def expand_output(ctx, rp, attempt=None):
    latest = os.path.abspath(ctx['args'].get('out') or os.path.join(
        os.path.dirname(rp), names(ctx['proj'], 'expand')[0]))
    stem, ext = os.path.splitext(latest)
    return '%s_%s%s' % (stem, attempt, ext) if attempt else latest


def file_version(path):
    try:
        s = os.stat(path)
        return (s.st_mtime_ns, s.st_size) if os.path.isfile(path) else None
    except OSError:
        return None


def expand_run_lines(log, offset):
    try:
        with open(log, 'rb') as f:
            f.seek(offset)
            data = f.read()
    except OSError:
        return []
    for encoding in ('utf-8', 'oem', 'mbcs', 'latin-1'):
        try:
            return data.decode(encoding).splitlines()
        except (UnicodeDecodeError, LookupError):
            continue


def expand_ok(lines, attempt, returncode, proposal, before=None):
    if returncode != 0:
        return False
    task_log = 'log_expand_%s.txt' % attempt
    fresh = file_version(proposal)
    return (fresh is not None and fresh[1] > 0 and fresh != tuple(before or ())
            and any(re.match(r'^Result : ok(?:;|\s*$)', line)
                    and os.path.basename(line.rpartition('; log ')[2].strip()) == task_log for line in lines))


def expand_cmd(ctx, rp, pay, attempt):
    """The command line of expand_api.ps1 for the merged report rp (prk expand, and the page's「让 AI 写建议」)."""
    a = ctx['args']
    cmd = [powershell(), '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(KIT, 'api', 'expand_api.ps1'),
           '-ProjectFile', ctx['path'], '-From', rp, '-RunId', attempt]
    lf = local_file(a, ctx['state'])
    if lf:
        cmd += ['-LocalFile', lf]
    for key, flag in (('items', '-Items'), ('max_turns', '-MaxTurns'), ('out', '-OutFile'), ('map_dir', '-MapDir'), ('runner', '-Runner')):
        if a.get(key):
            cmd += [flag, str(a[key])]
    if pay == 'sub':
        cmd += ['-Subscription']
    return cmd + runner_target(ctx)


def entry_bodies(text):
    """{entry id: its full text} of one report: from its "### M1 title" line up to the next heading of level 1-3."""
    out = {}
    for m in re.finditer(r'(?m)^### ((?:S|M|L|D|W)\d+)\s+(.*)$', text):
        end = re.search(r'(?m)^#{1,3} ', text[m.end():])
        out[m.group(1)] = text[m.end(): m.end() + end.start() if end else len(text)].strip()
    return out


# ---------- the fix list (待修清单) ----------
# One Markdown file hands what the owner decided to fix over to an AI, and back. The person reads the titles; an AI
# reads the details and the instructions at the top (taken from api\fix_template.md, the same text the kit's own AI
# gets). Two ways to hand an item over:
#   - copy one short sentence into the AI window the person already uses ("read <list>, fix F3"): the details stay in
#     the file, so nothing long is pasted and nothing is paid twice;
#   - let the kit send an AI itself (prk fix F3, or the page). It spends quota or money, runs only when the owner says
#     yes to that one item, and backs up the files the item cites first, so it can be undone.
# Either AI ticks the item ([x]) and fills in「修完填这里」. A decision 修 puts an entry on the list (once per round,
# report and entry); another decision takes it off again unless it is fixed already. Numbers F1, F2 ... are never reused.

FIX_NAME = '待修清单.md'
FIX_FIELDS = ('改了', '自己核过', '要进游戏看的', '没把握的', '顺手看到的')
FIX_FIELDS_EN = ('Changed', 'Verified', 'Needs an in-game check', 'Uncertainties', 'Other observations')
FIX_FIELD_KEYS = dict(zip(FIX_FIELDS_EN, FIX_FIELDS))
FIX_SEV_EN = dict(zip('SMLDW', ('Severe', 'Medium', 'Minor', 'Needs your decision', 'Wanted but missing')))
FIX_META = {'来自': 'from', '有多要紧': 'severity', '负责人说': 'why',
            'From': 'from', 'Severity': 'severity', 'Owner reason': 'why'}
FIX_NUMBER = r'(?:用过的最大编号|Highest assigned ID)[：:]\s*'
FIX_SECTION = re.compile(r'^##\s*(?:要修的|Items to fix)')
FIX_FILL_HEADING = re.compile(r'^#{4,6}\s*(?:修完填这里|Fill in after fixing)')
FIX_SEV = {'S': '严重', 'M': '一般', 'L': '小问题', 'D': '要你拿主意', 'W': '玩家想要的'}
FIX_HEAD = re.compile(r'^###\s*\[([ xX]?)\]\s*(F\d+)\b\s*(.*)$')
FIX_DONE = '修完填这里'
CITE = re.compile(r'`([^`\n]+?):(\d+)(?:-\d+)?`')


def fix_file(proj, sample=False):
    """Where the fix list is. A sample round (hand-written) never writes into the real one (as decisions_file)."""
    if sample:
        name = 'sample_fix-list.md' if language(proj) == 'en' else 'sample_' + FIX_NAME
        return os.path.join(STATE_DIR, name)
    return named_path(proj, proj.get('reviewOutDir') or '.', 'fixList')


def fix_template_text():
    with open(os.path.join(KIT, 'api', 'fix_template.md'), encoding='utf-8-sig') as f:
        return f.read()


def fix_header(proj, path):
    """A new list's top: what it is, and the instructions for any AI (the <规矩>, <背景笔记> and <交回来> parts of
    api\\fix_template.md as plain text)."""
    if language(proj) == 'en':
        blocked = ', '.join(proj.get('neverRead') or []) or '(none)'
        return ['# Fix list', '',
                'Each title identifies an owner-approved item. The details and instructions below are for the AI doing the fix.',
                'When an item is fixed, change [ ] to [x] and fill in its “Fill in after fixing” section.',
                'IDs are never reused. Highest assigned ID: F0', '',
                '## Instructions for AI', '',
                '- Fix only the items named by the owner. Make the smallest change that addresses each item.',
                '- Read and follow the project rules, including projectRules, rulesFile and CLAUDE.md if present.',
                '- Never read, modify, list or search these paths: ' + blocked,
                '- Verify the quoted source first. If it has changed, stop and record that the source has changed.',
                '- Check the affected steps in the code. Record any in-game check the owner needs to run.',
                '- Describe only changes and checks you performed. Use the five fields under “Fill in after fixing”.',
                '- Read the background notes before working. Add a short note if it will help the next person.', '',
                '## Background notes', '', 'Notes from previous fixes. Use one line per note.', '',
                '## Items to fix', '']
    tpl = fix_template_text()
    fill = {'NEVERREAD': '、'.join(proj.get('neverRead') or []) or '（没有）', 'LIST': path, 'RETURN_NOTE': ''}

    def part(tag):
        m = re.search(r'<%s>\s*\n(.*?)\n\s*</%s>' % (tag, tag), tpl, re.S)
        text = m.group(1).strip() if m else ''
        for k, v in fill.items():
            text = text.replace('{{%s}}' % k, v)
        return text
    return ['# 待修清单', '',
            '给人看：每条的标题。给 AI 看：每条下面的细节和最上面的说明。',
            '修完一条：把标题里的 [ ] 改成 [x]，在这一条的「修完填这里」写上改了什么。',
            '编号一直往上加，不重复用。用过的最大编号：F0', '',
            '## 给 AI 的说明', '',
            '下面是%s决定要修的问题，每条一个编号（F 开头）。会有人告诉你修哪一条。' % (proj.get('ownerName') or '负责人'), '',
            part('规矩'), '', part('背景笔记'), '', part('交回来'), '',
            '## 背景笔记', '',
            '（做过的人留下的话：哪些地方连着、哪里容易改坏。一句一行。）', '',
            '## 要修的', '']


def _fix_lines(path):
    with open(path, encoding='utf-8-sig', errors='replace') as f:
        return f.read().splitlines()


def _fix_write(path, lines):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    text = '\n'.join(lines).rstrip('\n') + '\n'
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    try:
        os.replace(tmp, path)
    except OSError:                      # some setups (sandboxes, synced folders) refuse the rename: write in place
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        try:
            os.remove(tmp)
        except OSError:
            pass


def _fix_blocks(lines):
    """[(start, end)] of every item: its "### [ ] F3" line up to the next heading of level 1-3 (code fences skipped)."""
    out, fence, cur = [], False, None
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith('```'):
            fence = not fence
            continue
        if fence or not (re.match(r'^#{1,3}\s', ln) or FIX_HEAD.match(ln)):
            continue
        if cur is not None:
            out.append((cur, i))
            cur = None
        if FIX_HEAD.match(ln):
            cur = i
    if cur is not None:
        out.append((cur, len(lines)))
    return out


def _fix_item(block):
    """One item as data. Tolerant: whatever a person or an AI wrote, the heading decides; fields may be empty or
    run over several lines."""
    m = FIX_HEAD.match(block[0])
    it = OrderedDict([('id', m.group(2).upper()), ('done', m.group(1) in ('x', 'X')), ('title', m.group(3).strip()),
                      ('severity', ''), ('why', ''), ('from', ''), ('round', ''), ('report', ''), ('entry', ''),
                      ('body', ''), ('filled', OrderedDict()), ('filledText', ''), ('hasFill', False)])
    k = next((j for j, ln in enumerate(block) if FIX_FILL_HEADING.match(ln)), len(block))
    head, tail = block[1:k], block[k + 1:]
    j = 0
    while j < len(head):
        mm = re.match(r'^\s*[-*]\s*([^：:]+)[：:]\s*(.*)$', head[j])
        if mm and mm[1] in FIX_META:
            key = FIX_META[mm[1]]
            it[key] = it[key] or mm.group(2).strip()
        elif head[j].strip():
            break
        j += 1
    it['body'] = '\n'.join(head[j:]).strip()
    src = re.findall(r'`([^`]+)`', it['from'])
    if len(src) >= 2:
        it['round'], it['report'] = src[0], src[1]
    e = re.search(r'(?:里的|, item)\s*([SMLDW]\d+)\b', it['from'])
    it['entry'] = e.group(1) if e else ''
    cur = None
    for ln in tail:
        mm = re.match(r'^\s*[-*]\s*(%s)[：:]\s*(.*)$' % '|'.join(FIX_FIELDS + FIX_FIELDS_EN), ln)
        if mm:
            cur = FIX_FIELD_KEYS.get(mm[1], mm[1])
            it['filled'][cur] = '\n'.join(x for x in (it['filled'].get(cur, ''), mm.group(2).strip()) if x)
        elif cur and ln.strip():
            it['filled'][cur] = '\n'.join(x for x in (it['filled'].get(cur, ''), ln.strip()) if x)
    it['filledText'] = '\n'.join(tail).strip()
    it['hasFill'] = any(it['filled'].values())
    return it


def read_fixes(path):
    """{file, exists, items, maxNo}: the list as data (see _fix_item). maxNo = the highest number ever used."""
    out = {'file': path, 'exists': os.path.isfile(path), 'items': [], 'maxNo': 0}
    if not out['exists']:
        return out
    lines = _fix_lines(path)
    out['items'] = [_fix_item(lines[s:e]) for s, e in _fix_blocks(lines)]
    m = re.search(FIX_NUMBER + r'F?(\d+)', '\n'.join(lines))
    out['maxNo'] = max([int(m.group(1)) if m else 0] + [int(it['id'][1:]) for it in out['items']])
    return out


def _fix_edit(path, fid, change):
    """change(block lines) -> new block lines, for item fid. False when the list has no such item."""
    if not os.path.isfile(path):
        return False
    lines = _fix_lines(path)
    for s, e in _fix_blocks(lines):
        if FIX_HEAD.match(lines[s]).group(2).upper() == fid.upper():
            lines[s:e] = change(lines[s:e])
            _fix_write(path, lines)
            return True
    return False


def _fix_key(report, entry_id):
    return os.path.basename(os.path.dirname(os.path.abspath(report))), os.path.basename(report), entry_id


def same_fix_entry(proj, item, key):
    round_id, report, entry_id = key
    return (item['round'] == round_id and item['entry'] == entry_id
            and item['report'] in report_aliases(proj, report))


def fix_add(proj, sample, report, entry_id, title, body, why=''):
    """Put one entry of a report on the list, once. Returns (item id, True when it was added now)."""
    path = fix_file(proj, sample)
    data = read_fixes(path)
    rnd, rep, _e = _fix_key(report, entry_id)
    for it in data['items']:
        if same_fix_entry(proj, it, (rnd, rep, entry_id)):
            return it['id'], False
    lines = _fix_lines(path) if data['exists'] else fix_header(proj, path)
    no = data['maxNo'] + 1
    en = language(proj) == 'en'
    why = ' '.join(why.split())
    block = ['### [ ] F%d %s' % (no, ' '.join(title.split()))]
    if en:
        block += ['- From: round `%s`, report `%s`, item %s' % (rnd, rep, entry_id),
                  '- Severity: ' + FIX_SEV_EN.get(entry_id[0], ''),
                  '- Owner reason: ' + (why or 'None provided')]
    else:
        block += ['- 来自：`%s` 这次检查的 `%s` 里的 %s' % (rnd, rep, entry_id),
                  '- 有多要紧：' + FIX_SEV.get(entry_id[0], ''),
                  '- 负责人说：' + (why or '没写')]
    empty = '(The report has no details for this item.)' if en else '（报告里这一条没有写详细）'
    block += [''] + (body.strip() or empty).split('\n') + ['', *fix_fill_lines(en), '']
    at, sec, fence = len(lines), None, False       # at the end of「要修的」
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith('```'):
            fence = not fence
        elif not fence and FIX_SECTION.match(ln):
            sec = i
        elif not fence and sec is not None and re.match(r'^#{1,2}\s', ln):
            at = i
            break
    if sec is None:
        lines += ['', '## Items to fix' if en else '## 要修的', '']
        at = len(lines)
    lines[at:at] = ([''] if at and lines[at - 1].strip() else []) + block
    text = re.sub('(' + FIX_NUMBER + r')F?\d+', lambda m: m.group(1) + 'F%d' % no, '\n'.join(lines), count=1)
    _fix_write(path, text.split('\n'))
    return 'F%d' % no, True


def fix_remove(proj, sample, report, entry_id):
    """Take an entry off the list (its decision is not 修 any more), only while it is not fixed. Returns the ids."""
    path = fix_file(proj, sample)
    if not os.path.isfile(path):
        return []
    key, lines, gone = _fix_key(report, entry_id), _fix_lines(path), []
    for s, e in reversed(_fix_blocks(lines)):
        it = _fix_item(lines[s:e])
        if same_fix_entry(proj, it, key) and not it['done']:
            del lines[s:e]
            gone.append(it['id'])
    if gone:
        _fix_write(path, lines)
    return gone


def fix_sync(proj, sample, report, entry_id, decision, title='', body='', why=''):
    """After a decision (page or prk decide): 修 = on the list; anything else = off it, unless fixed already."""
    if decision_word(decision) == '修':
        fid, added = fix_add(proj, sample, report, entry_id, title, body, why)
        return {'fix': fid, 'added': added, 'removed': []}
    return {'fix': None, 'added': False, 'removed': fix_remove(proj, sample, report, entry_id)}


def fix_mark(path, fid, done):
    """Tick ([x]) or untick ([ ]) an item by hand. False when there is no such item."""
    def change(block):
        m = FIX_HEAD.match(block[0])
        block[0] = '### [%s] %s %s' % ('x' if done else ' ', m.group(2).upper(), m.group(3).strip())
        return block
    return _fix_edit(path, fid, change)


def fix_fill_lines(en):
    if en:
        return ['#### Fill in after fixing'] + ['- %s:' % field for field in FIX_FIELDS_EN]
    return ['#### ' + FIX_DONE] + ['- %s：' % field for field in FIX_FIELDS]


def fix_reset(path, fid):
    """Not fixed again, with「修完填这里」empty (after an undo: what it said was put back)."""
    def change(block):
        m = FIX_HEAD.match(block[0])
        k = next((j for j, ln in enumerate(block) if FIX_FILL_HEADING.match(ln)), None)
        keep = block[1:k] if k is not None else block[1:] + ['']
        en = 'Fill in after fixing' in block[k] if k is not None else os.path.basename(path).endswith('fix-list.md')
        return ['### [ ] %s %s' % (m.group(2).upper(), m.group(3).strip())] + keep + fix_fill_lines(en) + ['']
    return _fix_edit(path, fid, change)


def fix_prompt(path, ids, lang='zh'):
    """The short sentence to hand to an AI the person already uses. The details stay in the file."""
    if not ids:
        return ''
    if lang == 'en':
        return ('Read %s and follow its instructions to fix only %s. After each fix, tick its checkbox '
                'and fill in the completion section.') % (path, ', '.join(ids))
    if len(ids) == 1:
        return '请读 %s，照里面「给 AI 的说明」修 %s，只修这一条。修完在文件里打勾、填好「修完填这里」。' % (path, ids[0])
    return '请读 %s，照里面「给 AI 的说明」修 %s，一条一条修。每修完一条，在文件里给它打勾、填好「修完填这里」。' % (
        path, '、'.join(ids))


def fix_backups(proj, fid):
    """Backups made before the kit's AI changed files for this item, newest first: [(folder, manifest)]."""
    out = {}
    for name in names(proj, 'beforeFix'):
        base = os.path.join(proj.get('reviewOutDir') or '.', name)
        if not os.path.isdir(base):
            continue
        for d in os.listdir(base):
            if d.upper().startswith(fid.upper() + '_') and d not in out:
                try:
                    with open(os.path.join(base, d, 'manifest.json'), encoding='utf-8') as f:
                        out[d] = (os.path.join(base, d), json.load(f))
                except (OSError, ValueError):
                    pass
    return [out[d] for d in sorted(out, reverse=True)]


def fix_list(proj, sample=False):
    """The list for the page and prk fix --json: items, how many are left, the sentences to copy."""
    d = read_fixes(fix_file(proj, sample))
    for it in d['items']:
        it['copy'] = fix_prompt(d['file'], [it['id']], language(proj))
        bk = [] if sample else fix_backups(proj, it['id'])
        it['canUndo'] = bool(bk) and not bk[0][1].get('undone')
    todo = [it['id'] for it in d['items'] if not it['done']]
    d.update({'sample': sample, 'todo': len(todo), 'fixed': len(d['items']) - len(todo),
              'copyAll': fix_prompt(d['file'], todo, language(proj))})
    return d


def _finder(ctx):
    import check_citations          # static\ is on the path: the same way the citation check finds a cited file
    return check_citations.make_finder(ctx['proj'], ctx['path'], never_read=machine_never_read(ctx))


def protected_path(path, never):
    p = os.path.normcase(os.path.realpath(path))
    for root in never:
        r = os.path.normcase(os.path.realpath(root))
        if p == r or p.startswith(r.rstrip('\\/') + os.sep):
            return True
    return False


def fix_cited(ctx, it):
    """The files an item cites (`path:line`): (found, not found)."""
    find = _finder(ctx)
    rdir = os.path.join(ctx['proj'].get('reviewOutDir') or '.', it.get('round') or '')
    found, missing = [], []
    for m in CITE.finditer(it.get('body') or ''):
        p = find(m.group(1).strip(), rdir)
        if p and os.path.abspath(p) not in found:
            found.append(os.path.abspath(p))
        elif not p and m.group(1).strip() not in missing:
            missing.append(m.group(1).strip())
    return found, missing


def fix_cannot(ctx, pay):
    """Why the kit cannot send an AI to change files right now ('' when it can)."""
    if not powershell():
        return '找不到 PowerShell（Windows 自带；别的系统装 pwsh）。'
    if not ctx['proj'].get('reviewOutDir'):
        return '游戏的设置里没写 reviewOutDir（报告和待修清单放在哪个文件夹）。'
    problem = pay_problem(ctx, pay)
    if problem:
        return problem
    pv = current_provider(ctx)[0]
    d = load_providers(ctx).get(pv) or {}
    engine = d.get('engine') or 'claude-code'
    if engine != 'claude-code':
        return ('现在选的 AI 是「%s」，它用 %s 干活。在这个工具包里它只读、不改文件，所以不能直接修。\n'
                '要直接修：换成用 Claude Code 的服务商（例如 prk provider anthropic，或这一次加 --provider anthropic）。\n'
                '或者用「复制给 AI」，把一句话交给你自己的 AI 窗口去修。') % (d.get('name', pv), ENGINE_NAMES.get(engine, engine))
    return ''


def sign_in_problem(text):
    """A refused sign-in in the CLI's own words, said plainly; '' when the text is not about that."""
    t = text or ''
    if re.search(r'claude auth login|setup-token|reached its time limit|OAuth token has expired|Please run /login', t, re.I):
        return '会员额度的登录过期了：在终端里运行 claude auth login，登录好以后再试一次。'
    if re.search(r'Invalid API key|invalid x-api-key|authentication_error', t, re.I):
        return 'API key 不对或者过期了：换一个新的 key 放进原来那个文件（工具包不读也不显示 key 本身），或者改用会员额度。'
    if re.search(r'Failed to authenticate', t, re.I):
        return '登录没通过：用会员额度的话在终端里运行 claude auth login；按次付费的话检查 key 还能不能用。'
    return ''


def runner_error(err, provider):
    """The runner's English error, said plainly (the guide and fix use it)."""
    err = re.split(r' At [A-Za-z]:\\| \+ CategoryInfo| 所在位置 ', re.sub(r'\s+', ' ', err or '').strip())[0][:300]
    if sign_in_problem(err):
        return sign_in_problem(err)
    if 'Claude Code not found' in err or 'claudeExe' in err:
        return '这台电脑上没找到 Claude Code。先装好；装在不常见的地方时，运行 prk local 写上它在哪。'
    if 'No API key' in err or 'apiKeyFile' in err:
        return '还没写 API key 放在哪：运行 prk provider setup %s（只问 key 放在哪个文件或环境变量，不问 key 本身）。或者改用会员额度。' % provider
    if 'no sign-in of its own' in err:
        return '这家 AI 只能按次付费，用不了会员额度：换回 anthropic，或者改成按次付费。'
    return mask_home(err)


def fix_run(ctx, fid, pay, expected_item=None):
    """Send an AI to fix one item of the (real) list: back up the files it cites, write the task (api\\fix_template.md),
    run it with edits allowed, read the list again, record the cost. The caller has asked the owner first.
    Returns {ok, id, error, log, tail, backup, files, missing, filled, cost, seconds}."""
    proj = ctx['proj']
    path = fix_file(proj)
    fid = fid.upper()
    out = {'ok': False, 'id': fid, 'file': path}
    it = next((x for x in read_fixes(path)['items'] if x['id'] == fid), None)
    if expected_item is not None and it != expected_item:
        return dict(out, changed=['id', 'report', 'title'], error='待修条目变了，请重新确认。')
    if not it:
        out['error'] = '待修清单里没有 %s。' % fid
        return out
    if it['done']:
        out['error'] = '%s 已经打勾了。要再修一次，先放回去：prk fix %s --reopen（页面上是「放回去」）。' % (fid, fid)
        return out
    out['error'] = fix_cannot(ctx, pay)
    if out['error']:
        return out
    root = proj.get('projectRoot') or os.path.dirname(ctx['path'])
    base = proj['reviewOutDir']
    stamp = run_id()
    files, missing = fix_cited(ctx, it)
    machine_never = machine_never_read(ctx)
    never = list(proj.get('neverRead') or []) + machine_never
    bdir = os.path.join(named_path(proj, base, 'beforeFix', write=True), '%s_%s' % (fid, stamp))
    os.makedirs(bdir)
    saved = OrderedDict()
    for p in files:                                   # 1. a copy of every cited file, kept by its place in the project
        if protected_path(p, never):
            missing.append(p)
            continue
        try:
            r = os.path.relpath(p, root)
        except ValueError:
            r = '..'
        if r.startswith('..') or os.path.isabs(r):
            r = os.path.join('_外面', re.sub(r'^([A-Za-z]):', r'\1', p).lstrip('\\/'))
        dst = os.path.join(bdir, 'files', r)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)
        saved[p] = dst
    atomic_json(os.path.join(bdir, 'manifest.json'),
                {'item': fid, 'title': it['title'], 'time': stamp, 'files': saved, 'notFound': missing})
    work = named_path(proj, base, 'fixDir', write=True)                  # 2. the task, from the same template the list's instructions come from
    os.makedirs(work, exist_ok=True)
    task = os.path.join(work, 'task_fix_%s_%s.md' % (fid, stamp))
    log = os.path.join(work, 'log_fix_%s_%s.txt' % (fid, stamp))
    body = '\n'.join(['- 来自：' + it['from'], '- 有多要紧：' + it['severity'], '- 负责人说：' + (it['why'] or '没写'), '', it['body']])
    note = '改之前，工具包已经把这一条出处里的文件备份了一份。你要是改了别的文件，一定写进「改了」：撤回时靠它说清楚哪些没有备份。'
    tpl = fix_template_text()
    for k, v in (('NEVERREAD', '、'.join(proj.get('neverRead') or []) or '（没有）'), ('LIST', path), ('ITEM', '%s %s' % (fid, it['title'])),
                 ('RETURN_NOTE', note), ('ITEM_BODY', body)):        # the item's own text last: nothing in it is a placeholder
        tpl = tpl.replace('{{%s}}' % k, v)
    tpl = delivery_task(proj, tpl)
    if language(proj) == 'en':
        tpl = tpl.replace('# Delivery language: English\n\n', '# Delivery language: English\n\n'
                          'Keep the fix list’s existing checkbox and completion heading for this item. '
                          'Write the completion details in English, using the English fix fields in the format guide.\n\n', 1)
    problem = task_placeholder(task, tpl)
    if problem:
        return {'ok': False, 'error': problem}
    with open(task, 'w', encoding='utf-8', newline='\n') as f:
        f.write(tpl)
    a = ctx['args']                                   # 3. run it: the project's folder, edits allowed this once
    cmd = [powershell(), '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', a.get('runner') or os.path.join(KIT, 'api', 'run_api_task.ps1'),
           '-TaskFile', task, '-LogFile', log, '-WorkDir', root]
    if proj.get('readOnlyPaths'):
        cmd += ['-ReadOnly', ';'.join(proj['readOnlyPaths'])]
    cmd += ['-AllowEdits']
    if never:
        cmd += ['-NeverRead', ';'.join(never)]
    lf = local_file(a, ctx['state'])
    if lf:
        cmd += ['-LocalFile', lf]
    if a.get('max_turns'):
        cmd += ['-MaxTurns', str(a['max_turns'])]
    cmd += ['-Json'] + (['-Subscription'] if pay == 'sub' else []) + runner_target(ctx)
    t0, err = time.time(), ''
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=3600)
        err = r.stderr or ('' if r.returncode == 0 else r.stdout)
    except subprocess.TimeoutExpired:
        err = '等了一个小时还没修完，停了。'
    try:                                              # 4. one row in the cost ledger (category 修)
        row = ledger_mod().parse_log(log, read_local(ctx).get('prices'))
        if row:
            row['轮次'] = '修'
            ledger_mod().update(ledger_file(ctx), [row], lang=language(proj))
            out['cost'] = row.get('CLI估的USD') or None
    except (OSError, ValueError):
        pass
    now = next((x for x in read_fixes(path)['items'] if x['id'] == fid), None)   # 5. ticked = done
    out.update({'log': log, 'task': task, 'backup': bdir, 'files': list(saved), 'missing': missing, 'seconds': round(time.time() - t0, 1)})
    if now and now['done']:
        out.update({'ok': True, 'error': '', 'filled': now['filled']})
        return out
    tail = []
    if os.path.exists(log):
        with open(log, encoding='utf-8-sig', errors='replace') as f:
            tail = [ln for ln in f.read().splitlines() if ln.strip()][-8:]
    out['tail'] = mask_home('\n'.join(ln[:400] for ln in tail))
    why = runner_error(err, current_provider(ctx)[0]) if err.strip() else ''
    out['error'] = ('AI 没修完：清单里的 %s 还没打勾。%s文件可能已经改了一部分：要改回去，prk fix %s --undo（页面上是「撤回」）。' % (
        fid, (why + ' ') if why else '看日志的最后几行。', fid))
    return out


def _named_files(ctx, text, rdir):
    """Files named in backticks in a text (「改了」), found like cited files; ones not found stay as written."""
    find, out = _finder(ctx), []
    for m in re.finditer(r'`([^`\n]+?)(?::\d+(?:-\d+)?)?`', text or ''):
        raw = m.group(1).strip()
        if re.search(r'[\\/]|\.\w{1,6}$', raw):
            p = find(raw, rdir)
            out.append(os.path.abspath(p) if p else raw)
    return out


def fix_undo(ctx, fid):
    """Put back the files from the newest backup of this item, and the item back to not fixed. Files the AI says it
    changed that were not backed up are named (they cannot be put back from here)."""
    proj = ctx['proj']
    path, fid = fix_file(proj), fid.upper()
    out = {'ok': False, 'id': fid, 'restored': [], 'failed': [], 'noBackup': []}
    it = next((x for x in read_fixes(path)['items'] if x['id'] == fid), None)
    if not it:
        out['error'] = '待修清单里没有 %s。' % fid
        return out
    pending = []                          # every attempt since the last undo: back to before the first of them
    for folder, man in fix_backups(proj, fid):
        if man.get('undone'):
            break
        pending.append((folder, man))
    if not pending:
        out['error'] = ('%s 没有能撤回的备份：不是这个工具派 AI 改的（你自己的 AI 窗口改的，用你们自己的版本管理改回去），'
                        '或者已经撤回过了。只想把它放回「还没修的」：prk fix %s --reopen（页面上是「放回去」）。' % (fid, fid))
        return out
    files = OrderedDict()
    for _folder, man in pending:          # newest first: the oldest copy of each file wins
        files.update(man.get('files') or {})
    folder, newest = pending[0]
    manifest = os.path.join(folder, 'manifest.json')
    results = newest.setdefault('restore', {})
    never = list(proj.get('neverRead') or []) + machine_never_read(ctx)
    for orig, bak in files.items():
        if results.get(orig) == {'backup': bak, 'restored': True}:
            continue
        try:
            if protected_path(orig, never) or protected_path(bak, never):
                raise OSError('属于不许碰的路径')
            if os.path.normcase(os.path.basename(bak)) == 'manifest.json' and any(
                    os.path.normcase(os.path.abspath(bak)) == os.path.normcase(os.path.join(d, 'manifest.json')) for d, _ in pending):
                raise OSError('旧备份的原文件与备份清单重名，原副本已被覆盖')
            shutil.copy2(bak, orig)
            out['restored'].append(orig)
            results[orig] = {'backup': bak, 'restored': True}
        except OSError as e:
            reason = str(e.strerror or e)
            results[orig] = {'backup': bak, 'restored': False, 'error': reason}
            out['failed'].append('%s（%s）' % (orig, reason))
    saved = {os.path.normcase(os.path.abspath(p)) for p in files}
    rdir = os.path.join(proj.get('reviewOutDir') or '.', it.get('round') or '')
    out['noBackup'] = [p for p in _named_files(ctx, it['filled'].get('改了', ''), rdir)
                       if not (os.path.isabs(p) and os.path.normcase(p) in saved)]
    out['backup'] = pending[-1][0]
    atomic_json(manifest, newest)
    if out['failed']:
        out['error'] = '有 %d 个文件没改回去：%s' % (len(out['failed']), '；'.join(out['failed']))
        return out
    if not fix_reset(path, fid):
        out['error'] = '文件已改回去，但待修清单里没有 %s 了。' % fid
        return out
    # The newest manifest is the checkpoint for every attempt restored together.
    newest['undone'] = time.strftime('%Y%m%d_%H%M%S')
    atomic_json(manifest, newest)
    out['ok'] = True
    return out


def cmd_fix(ctx):
    """prk fix               the fix list: not fixed yet, fixed (and the sentence to hand to your own AI)
       prk fix F3            send an AI to fix F3 (changes the game's files; quota or money; asks first, --yes when not in a terminal)
       prk fix F3 --undo     put back the files from the copy made before, and F3 back to not fixed
       prk fix F3 --done     mark F3 fixed by hand          prk fix F3 --reopen   take the tick off again"""
    a, proj = ctx['args'], ctx['proj']
    path = fix_file(proj)
    fid = (a.get('word') or '').strip().upper()

    def tell(r):
        out_json(dict(r, **output_metadata(proj))) if want_json(ctx) else say(r.get('error') or r.get('message') or '')
        return 0 if r.get('ok') else 1
    if fid and not re.match(r'^F\d+$', fid):
        return tell({'ok': False, 'error': '编号写成 F 加数字，例如 prk fix F3。'}) and 2
    if not fid:
        d = fix_list(proj)
        if want_json(ctx):
            out_json(dict(d, ok=True, **output_metadata(proj)))
            return 0
        rule('待修清单')
        say('文件：%s' % mask_home(path))
        if not d['items']:
            say('还是空的。在页面「要处理的问题」里点「要修」，或者在 prk decide 里选 1（修），那一条就会放进来。')
            return 0
        todo, done = [x for x in d['items'] if not x['done']], [x for x in d['items'] if x['done']]
        say()
        say('还没修的（%d 条）：' % len(todo))
        for x in todo:
            say('  %-4s [%s] %s%s' % (x['id'], x['severity'] or '?', x['title'], '  （AI 改过一次，可以撤回）' if x['canUndo'] else ''))
        if not todo:
            say('  没有了。')
        say()
        say('修好了，等下次检查确认（%d 条）：' % len(done))
        for x in done:
            say('  %-4s %s%s' % (x['id'], x['title'], '  （可以撤回）' if x['canUndo'] else ''))
            for k in FIX_FIELDS:
                if x['filled'].get(k):
                    say('        %s：%s' % (k, x['filled'][k].replace('\n', '\n          ')))
        if todo:
            say()
            say('交给你自己正在用的 AI：把下面这句话发给它（细节它自己去文件里读）')
            say('  ' + d['copyAll'])
            say()
            say('让这个工具派 AI 去修一条：prk fix %s（会用掉额度或花钱，先问你；改之前先备份，可以撤回）' % todo[0]['id'])
        f1 = d['items'][0]['id']
        say('手动标：prk fix %s --done（修好了）/ --reopen（放回去）。撤回 AI 改的：prk fix %s --undo。' % (f1, f1))
        return 0
    if a.get('done') or a.get('reopen'):
        ok = fix_mark(path, fid, bool(a.get('done')))
        return tell({'ok': ok, 'id': fid, 'message': '%s %s。' % (fid, '标成修好了' if a.get('done') else '放回了还没修的'),
                     'error': '' if ok else '待修清单里没有 %s（prk fix 看有哪些）。' % fid})
    if a.get('undo'):
        r = fix_undo(ctx, fid)
        if r['ok'] and not want_json(ctx):
            say('改回去了 %d 个文件，%s 放回了还没修的。' % (len(r['restored']), fid))
            for p in r['restored']:
                say('  ' + mask_home(p))
            if r['noBackup']:
                say('这些文件没有备份，没法撤回（AI 说它改过）：')
                for p in r['noBackup']:
                    say('  ' + mask_home(p))
            return 0
        return tell(r)
    it = next((x for x in fix_list(proj)['items'] if x['id'] == fid), None)
    if not it or it['done']:
        return tell({'ok': False, 'error': ('待修清单里没有 %s（prk fix 看有哪些）。' % fid) if not it else
                     '%s 已经打勾了。要再修一次，先 prk fix %s --reopen。' % (fid, fid)})
    pay = need_pay(ctx)
    if not pay:
        return 2
    err = fix_cannot(ctx, pay)
    if err:
        return tell({'ok': False, 'error': err}) and 2
    if not want_json(ctx):
        files, _missing = fix_cited(ctx, it)
        rule('让 AI 直接修 %s' % fid)
        say(it['title'])
        say('会做的事：')
        say('  1. 先把这一条提到的文件备份一份：%s。' % ('、'.join(os.path.basename(p) for p in files) or '这一条没写出处，没有要备份的'))
        say('  2. 派一个 AI 去改游戏的文件，只修这一条。改完它在清单里打勾，写上改了什么。')
        say('  3. 改坏了：prk fix %s --undo，照备份改回去。' % fid)
        say(pay_line(ctx, pay))
        say('服务商：%s；模型：%s。' % (current_provider(ctx)[0], current_model(ctx)[0] or '默认'))
        say('效果不保证和你自己直接用 AI 一样：它没有你们聊过的上下文，只看这份清单和游戏自己的规矩。')
    if not a.get('yes'):
        if not sys.stdin.isatty():
            return tell({'ok': False, 'error': '不是在终端里：要真的派 AI 去改，加 --yes。'}) and 2
        if not yes('现在派 AI 去修吗'):
            say('没有派。')
            return 0
    if not want_json(ctx):
        say('AI 在修，一般要几分钟……')
    r = fix_run(ctx, fid, pay)
    if want_json(ctx):
        out_json(r)
        return 0 if r['ok'] else 1
    if r['ok']:
        say('修好了：清单里的 %s 打勾了。' % fid)
        for k in FIX_FIELDS:
            if r['filled'].get(k):
                say('  %s：%s' % (k, r['filled'][k].replace('\n', '\n    ')))
        say('改之前的备份：%s。改坏了：prk fix %s --undo。' % (mask_home(r['backup']), fid))
    else:
        say(r['error'])
        if r.get('tail'):
            say('日志的最后几行（%s）：' % mask_home(r.get('log')))
            say('  ' + r['tail'].replace('\n', '\n  '))
    if r.get('cost'):
        say('这一次：%s 美元（Claude Code 自己算的%s）。' % (r['cost'], '；用会员额度时只是折算，不另收钱' if pay == 'sub' else ''))
    return 0 if r['ok'] else 1


def cmd_ask(ctx):
    rule('让你自己的 AI 从玩家视角审查')
    say('1. 在项目里打开你的 AI 助手。第一次对它说：「读工具包里的 AGENTS.md，帮我装好。」')
    say('2. 对它说：「从玩家视角审查一下。」只看一处时，把范围也告诉它。')
    say('3. 它会用 prk prepare 准备任务，做完后用 prk page 核对出处、生成离线报告页面。')
    say('4. 在页面上点选决定，再点「复制给 AI」，贴回对话。改完以后可以请它再审一轮。')
    say('对话里审查用的是这场会话的额度。')
    return 0


def cmd_install(ctx):
    ps = powershell()
    if not ps:
        say('找不到 PowerShell。手动装：把 agent\\player-bug-reviewer.md 和 skill\\player-review\\ 复制进项目的 .claude\\agents 和 .claude\\skills，'
            '把里面的 {{KIT}}、{{PROJECT_FILE}}、{{OWNER}} 换成工具包路径、项目设置路径、负责人的称呼。')
        return 2
    return subprocess.run([ps, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(KIT, 'install.ps1'),
                           '-ProjectFile', ctx['path']]).returncode


# What a new project file starts from (prk new asks these one by one; the page's「新加一个游戏」shows them as a form):
# (field, question, default, what it is: 'dir' / 'file' = a path that must be there, 'out' = a folder a run makes, '' = words)
NEW_PROJECT_QUESTIONS = [
    ('name', '作品的名字', '', ''),
    ('ownerName', '报告里怎么称呼拿主意的人', '负责人', ''),
    ('projectRoot', '项目文件夹（审查员在这里干活）', '', 'dir'),
    ('modSource', '作品的源码和数据在哪个文件夹', '', 'dir'),
    ('modReadme', '给审查员读的说明文档（一个文件）', '', 'file'),
    ('characterDir', '角色 / 关卡 / 任务的数据在哪个文件夹', '', 'dir'),
    ('behaviourDir', '它们的行为代码在哪个文件夹', '', 'dir'),
    ('rulesFile', '项目自己的规矩（一个文件，没有就空着）', '', 'file'),
    ('loreBible', '设定集（一个文件，没有就空着）', '', 'file'),
    ('reviewOutDir', '审查报告写到哪个文件夹（还没有的话，第一次检查时会建）', '', 'out'),
    ('playUnit', '玩家的一个回合叫什么（天、关、章……）', '天', ''),
    ('csvZh', '中文文本表（每行 键,文字 的 csv；没有就空着）', '', 'file'),
    ('csvEn', '英文文本表（没有就空着）', '', 'file'),
    ('playLoop', '一个回合里玩家按顺序看到哪些界面（用 > 隔开，例：早上的消息>开门>客人>关门；不知道就空着）', '', ''),
]
PROJECT_LANGUAGE_QUESTION = ('language', '报告和页面用什么语言（zh 中文 / en English）', 'zh', '')
NEW_PROJECT_REQUIRED = ('id', 'projectRoot', 'modSource', 'reviewOutDir')


def new_project_fields():
    examples = {'name': '我的游戏', 'projectRoot': '.', 'modSource': 'game', 'modReadme': 'game/README.md',
                'characterDir': 'game/data/characters', 'behaviourDir': 'game/src', 'rulesFile': 'RULES.md',
                'loreBible': 'game/world.md', 'reviewOutDir': 'review_out', 'csvZh': 'game/text/zh.csv',
                'csvEn': 'game/text/en.csv', 'playLoop': '开门>客人>关门'}
    paths = {'dir': '填写已有的文件夹。可以写绝对路径，或相对于设置文件的路径。',
             'file': '可留空。填写时用已有文件的路径，相对于设置文件，或用绝对路径。',
             'out': '可以填写尚未创建的文件夹。相对路径以设置文件所在文件夹为准。'}
    fields = [{'key': 'id', 'label': '给它起个英文名字（字母、数字、- 和 _），当设置文件的名字用',
               'required': True, 'help': '不能用 _ 开头。这个名字会用作项目设置的文件名。', 'example': 'my-game'}]
    for key, label, default, kind in NEW_PROJECT_QUESTIONS + [PROJECT_LANGUAGE_QUESTION]:
        fields.append({'key': key, 'label': label, 'required': key in NEW_PROJECT_REQUIRED,
                       'help': paths.get(kind, '留空时用「%s」。' % default if default else '可以留空。'),
                       'example': examples.get(key, default)})
    fields += [{'key': 'isMod', 'label': '这是模组（依附在别的游戏上）', 'required': False,
                'help': '填 true 或 false，留空时按独立作品设置。', 'example': False},
               {'key': 'folder', 'label': '这份设置文件放在哪个文件夹', 'required': False,
                'help': '填写已有的文件夹，留空时写到工具包的 projects 文件夹。', 'example': 'projects'}]
    next(field for field in fields if field['key'] == 'language')['default'] = 'zh'
    return fields


def new_project(values, folder='', strict=False):
    """Write a new project file from the answers (NEW_PROJECT_QUESTIONS by field, plus id and isMod), starting from
    projects\\_template.json. folder: where the file goes ('' = the kit's projects folder). Paths are only checked for
    being there in the CLI. Strict mode checks required inputs and path types and returns errors by form field."""
    pid = clean_text(values.get('id'), 80)
    if not pid or not re.match(r'^[A-Za-z0-9_-]+$', pid) or pid.startswith('_'):
        error = '名字（id）只能用英文字母、数字、- 和 _，不能用 _ 开头。'
        return '', error, {'id': error} if strict else []
    folder = os.path.abspath(os.path.expandvars(clean_text(folder) or os.path.join(KIT, 'projects')))
    if not os.path.isdir(folder):
        error = '放设置文件的文件夹找不到：%s' % mask_home(folder)
        return '', error, {'folder': error} if strict else []
    dst = os.path.join(folder, pid + '.json')
    if os.path.exists(dst):
        error = '已经有了：%s' % mask_home(dst)
        return dst, error, {'id': error} if strict else []
    got = {k: clean_text(values.get(k, default)) for k, _t, default, _w in NEW_PROJECT_QUESTIONS}
    got['language'] = clean_text(values.get('language')) or 'zh'
    if got['language'] not in LANGUAGES:
        error = 'language 只能是 zh 或 en。'
        return '', error, {'language': error} if strict else []
    missing = []
    errors = {}
    for key, text, _d, what in NEW_PROJECT_QUESTIONS:
        p = os.path.expandvars(got[key])
        resolved = os.path.abspath(os.path.join(folder, p)) if p else ''
        if strict and what in ('dir', 'file', 'out'):
            label = text.split('（')[0]
            problem = path_problem(label, resolved, what, key in NEW_PROJECT_REQUIRED)
            if problem:
                errors[key] = mask_home(problem)
        elif got[key] and what in ('dir', 'file') and not os.path.exists(resolved):
            missing.append('%s：%s' % (text.split('（')[0], mask_home(got[key])))
    if errors:
        return '', '请检查标出的输入框。', errors
    d = read_json(os.path.join(KIT, 'projects', '_template.json'))
    d['id'] = pid
    d['language'] = got['language']
    for key, _t, _d, _w in NEW_PROJECT_QUESTIONS:
        if key not in ('csvZh', 'csvEn', 'playLoop'):
            d[key] = got[key]
    d['csv'] = OrderedDict([('zh', got['csvZh']), ('en', got['csvEn'])])
    if not (got['csvZh'] and got['csvEn']):
        d['staticTables'] = []
    loop = values.get('playLoop')
    d['playLoop'] = [clean_text(x, 100) for x in (loop if isinstance(loop, list) else got['playLoop'].split('>')) if clean_text(x, 100)]
    if d.get('projectRoot') and d.get('modSource'):
        d['readOnlyPaths'] = [d['modSource']]
    if d.get('reviewOutDir'):
        d['staticOutDir'] = os.path.join(d['reviewOutDir'], '_static')
    if not values.get('isMod'):
        d['reviewGroups'] = [g for g in d['reviewGroups'] if g.get('kind') not in ('modsurface', 'interaction')]
    try:
        with open(dst, 'x' if strict else 'w', encoding='utf-8', newline='\n') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
    except FileExistsError:
        error = '已经有了：%s' % mask_home(dst)
        return dst, error, {'id': error} if strict else []
    return dst, '', missing


def cmd_new(ctx):
    a = ctx['args']
    if a.get('fields') or 'from_json' in a:
        if a.get('fields') and 'from_json' in a:
            data = {'ok': False, 'errors': [{'key': 'from-json', 'message': '--fields 和 --from-json 不能一起用。'}]}
        elif a.get('fields'):
            data = {'ok': True, 'fields': new_project_fields()}
        else:
            data = new_from_json(a['from_json'], ctx)
        if want_json(ctx):
            out_json(data)
        elif data.get('fields'):
            for field in data['fields']:
                say('%s%s  %s' % (field['key'], '（必填）' if field['required'] else '', field['label']))
        elif data['ok']:
            say('写好了：%s' % data['file'])
        else:
            for issue in data['errors']:
                say('%s  %s' % (issue['key'], issue['message']))
        return 0 if data['ok'] else 2
    rule('新建项目设置')
    say('问几件最要紧的，别的字段留在文件里，之后照说明补。路径可以写绝对路径。直接回车 = 先空着。（页面上是「新加一个游戏」，问的一样）')
    pid = ctx['args'].get('id') or ask('项目 id（英文字母、数字、-、_）')
    if not pid or not re.match(r'^[A-Za-z0-9_-]+$', pid) or pid.startswith('_'):
        say('id 不对，没有建。')
        return 1
    if os.path.exists(os.path.join(KIT, 'projects', pid + '.json')):
        say('已经有了：%s' % os.path.join(KIT, 'projects', pid + '.json'))
        return 1
    vals = {'id': pid}
    for key, text, default, _w in NEW_PROJECT_QUESTIONS + [PROJECT_LANGUAGE_QUESTION]:
        v = ask(text, default)
        if v is None:
            say('没有建。')
            return 1
        vals[key] = v
    vals['isMod'] = yes('这个作品是模组吗（依附在别的游戏上）')
    dst, err, missing = new_project(vals)
    if err:
        say(err)
        return 1
    if not (vals.get('csvZh') and vals.get('csvEn')):
        say('  没有两个文本表：先不跑自带的文字检查（staticTables 留空）。')
    for m in missing:
        say('  这个现在找不到（文件照样写了，之后改）：%s' % m)
    say()
    say('写好了：%s' % dst)
    say('接下来：打开它，照每个 _说明 把剩下的补上（projectRules、审查组、要不要按份拆分）；')
    say('然后  python -I prk.py check -p "%s"  和  plan。' % dst)
    ctx['state']['project'] = dst
    save_state(ctx['state'])
    return 0


def new_from_json(path, ctx):
    try:
        values = read_json(path)
    except (ValueError, OSError) as exc:
        return {'ok': False, 'errors': [{'key': 'from-json', 'message': '读不了 JSON 回答文件：%s' % exc}]}
    if not isinstance(values, dict):
        return {'ok': False, 'errors': [{'key': 'from-json', 'message': '请用一个 JSON 对象填写每个字段。'}]}
    errors = []
    for field in new_project_fields():
        key = field['key']
        value = values.get(key)
        if value is None or isinstance(value, str) and not value.strip():
            if field['required']:
                errors.append({'key': key, 'message': '请填写%s。' % field['label']})
        elif key == 'isMod':
            if not isinstance(value, bool):
                errors.append({'key': key, 'message': '请填写 true 或 false。'})
        elif not isinstance(value, str) and not (key == 'playLoop' and isinstance(value, list)
                                                 and all(isinstance(step, str) for step in value)):
            errors.append({'key': key, 'message': '请填写文字。'})
    if errors:
        return {'ok': False, 'errors': errors}
    try:
        dst, error, by_field = new_project(values, values.get('folder') or '', strict=True)
    except (OSError, ValueError) as exc:
        return {'ok': False, 'errors': [{'key': 'folder', 'message': '写不了项目设置：%s' % exc}]}
    if error:
        return {'ok': False, 'errors': [{'key': key, 'message': message} for key, message in by_field.items()]}
    ctx['state']['project'] = dst
    save_state(ctx['state'])
    return {'ok': True, 'file': dst}


def cmd_local(ctx):
    rule('机器设置')
    say('这台电脑上的东西：不属于项目，也别发给别人。这里只问 key 放在哪，不问 key 本身。直接回车 = 用括号里的。')
    dst = ctx['args'].get('local') or os.path.join(KIT, 'local.json')
    old = read_json(dst) if os.path.exists(dst) else read_json(os.path.join(KIT, 'local.example.json'))
    d = OrderedDict((k, v) for k, v in old.items())
    v = ask('写到哪个文件', dst)
    if v is None:
        return 1
    dst = v
    for key, text, default in (
            ('python', '跑静态表的 Python', old.get('python') or sys.executable),
            ('claudeExe', 'Claude Code 的可执行文件，或装它的文件夹（回车 = 用 PATH 上的 claude）', old.get('claudeExe') or ''),
            ('defaultModel', 'API 模式默认用的模型 id（回车 = Claude Code 自己的默认）', old.get('defaultModel') or '')):
        v = ask(text, default)
        if v is None:
            return 1
        d[key] = v
    how = ask('API key 从哪来：1 = 一个只放 key 的文本文件，2 = 一个环境变量，回车 = 先不设（只用订阅模式）', '')
    if how == '1':
        d['apiKeyFile'] = ask('那个文本文件的路径', old.get('apiKeyFile') or '') or ''
        d['apiKeyEnv'] = ''
    elif how == '2':
        d['apiKeyEnv'] = ask('环境变量的名字', old.get('apiKeyEnv') or 'ANTHROPIC_API_KEY') or ''
        d['apiKeyFile'] = ''
    nr = ask('整台电脑上都不许审查员读的文件夹（用 ; 隔开）', ';'.join(old.get('neverRead') or []))
    d['neverRead'] = [x.strip() for x in (nr or '').split(';') if x.strip()]
    with open(dst, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    say('写好了：%s' % dst)
    if os.path.abspath(dst) != os.path.abspath(os.path.join(KIT, 'local.json')):
        ctx['state']['local'] = dst
        save_state(ctx['state'])
        say('记住了这个位置（以后不用每次写 --local）。')
    return 0


# ---------- what to do next, the guide, the page ----------

def decisions_file(proj, sample=False):
    """Where decisions go. A sample round (hand-written, to show the page) never writes into the real record:
    the real record is handed to the next round's reviewers."""
    if sample:
        return os.path.join(STATE_DIR, 'sample_decisions.csv')
    return named_path(proj, proj.get('reviewOutDir') or '.', 'decisions')


def latest_round(ctx):
    """collect_feedback of the newest real round, or None."""
    if not ctx.get('proj'):
        return None
    keep = {k: ctx['args'].pop(k, None) for k in ('dir', 'from')}
    try:
        return collect_feedback(ctx)
    finally:
        ctx['args'].update({k: v for k, v in keep.items() if v is not None})


def next_steps(ctx, conversation=False):
    """What to do now, worked out from the files alone (no AI, no cost). Each step: title, detail, cmd (a terminal
    command for the terminal and for an AI, or ''), view (where the page does it: run, settings, entries, fixes,
    files, cite, expand, newgame, cli, guide), costs (True when doing it spends money or quota), pay (how such a step
    pays: 'sub' / 'api', '' = not chosen yet); the expand step also has items."""
    steps = []
    pay = pay_of(ctx)[0]
    pf = ' --pay %s' % pay if pay else ''

    def add(title, detail='', cmd='', view='', costs=False):
        steps.append({'title': title, 'detail': detail, 'cmd': cmd, 'view': view, 'costs': costs, 'pay': pay if costs else ''})

    if not ctx.get('path'):
        add('先选一个游戏', '想先看看样子，选「茶摊（例子）」。要检查自己的游戏，新加一个：它会一步一步问你游戏放在哪。',
            'prk new', 'newgame')
        return steps
    proj, path = ctx['proj'], ctx['path']
    p = '-p "%s"' % path
    problems, _notes = check_data(ctx)
    if problems:
        add('游戏的设置里有 %d 个地方要改' % len(problems), '；'.join(problems[:4]) + ('……' if len(problems) > 4 else ''), 'prk check %s' % p, 'guide')
    if conversation:
        folder, _ = check_round(proj, sample=False)
        never = tuple(proj.get('neverRead') or ()) + tuple(machine_never_read(ctx))
        if folder and not protected_path(folder, never):
            prepared = prepared_tasks(folder, never)
            pending = [task for task in prepared or () if not task_written(proj, folder, task, never)]
            rid = os.path.basename(folder)
            if pending:
                add('接着做这次检查的任务', '按 _prepared.json 的阶段顺序做。还要读的任务文件：\n' +
                    '\n'.join(task['task'] for task in pending), '', 'files')
                steps[-1].update(round=rid, tasks=pending)
                return steps
            reports = round_reports(proj, folder, never)
            html = os.path.join(folder, 'review.html')
            stale = not os.path.isfile(html) or any(os.path.getmtime(r) > os.path.getmtime(html) for r in reports)
            if reports and stale and (prepared is not None or not page_module().missing_reports(
                    sys.modules[__name__], proj, folder, never)):
                add('生成给负责人看的页面', '核对出处，写出 review.md 和 review.html。',
                    'prk page %s --round "%s"' % (p, rid), 'files')
                steps[-1]['round'] = rid
                return steps
    d = latest_round(ctx)
    if conversation and d is None:
        add('开始第一次审查', '在当前对话里做。先准备静态表和任务文件，再照任务文件审查。',
            'prk prepare %s' % p, 'cli')
    background = []

    def add_background(title, detail, cmd, view, costs=False):
        if conversation:
            detail = '只有想让它在后台跑才需要。' + detail
        add(title, detail, cmd, view, costs)
        if conversation:
            step = steps.pop()
            step['optional'] = True
            background.append(step)

    info = local_info(ctx)
    problem = pay_problem(ctx, pay)
    if problem:
        add_background('现在选的这家 AI 只能按次付费', problem.replace('\n', ''), '', 'settings')
    elif info['engine'] == 'claude-code' and not info['claude']:
        add_background('这台电脑上没找到 Claude Code', '先装好、登录一次。装在不常见的地方的话，告诉工具包它在哪。',
            'prk local', 'settings')
    elif not info['program']:
        add_background('这台电脑上没找到 %s' % ENGINE_NAMES.get(info['engine'], info['engine']), '先装好、登录一次。', '', 'guide')
    elif pay != 'sub' and not info['apiKey']:
        add_background('还没告诉它钥匙（key）放在哪', '用会员额度的话不用管这一条。只问钥匙放在哪个文件里（或哪个环境变量），不问钥匙本身。',
            'prk provider setup %s' % info['provider'], 'settings')
    if not pay:
        add_background('先选怎么付', '用会员额度：用这台电脑上登录的账号，不另外花钱，但会用掉你的额度。按次付费：用钥匙（key），按用量花钱。'
            '选一次就记住，以后都用它。', '', 'settings')
    run_title = '正式检查一次（%s）' % PAY_NAMES[pay] if pay else '正式检查一次'
    if d is None:
        add_background('还没检查过：先试一下', '试一下不花钱，只告诉你会派出几个 AI。', 'prk plan %s%s' % (p, pf), 'run')
        add_background(run_title, ('用会员额度，不另外花钱，但会用掉额度。' if pay == 'sub' else '要花钱。' if pay else '') +
                       '先试一下，看清会派几个 AI 再跑。', 'prk run %s%s' % (p, pf), 'run', True)
        if not conversation:
            add('也可以在自己的 AI 对话里审查', '用这场会话的额度。让你的 AI 读 AGENTS.md，再请它从玩家视角审查一下。',
                'prk ask %s' % p, 'cli')
        return steps + background
    round_path = os.path.abspath(d['dir'])
    rid = os.path.basename(round_path)
    report_arg = ' --from "%s"' % os.path.abspath(d['reports'][0]) if d['merged'] else ''
    if not d['merged'] and len(d['reports']) > 1:
        add('上一次检查还没做完', '有 %d 份报告，但还没有汇总成一份，里面可能有重复的。' % len(d['reports']), '', 'files')
        steps[-1]['round'] = rid
    done = {key: decision_word(row['决定']) for key, row in decisions_by_entry(proj).items()}
    # Include the report because unmerged reports each have their own M1.
    keys = [(report_identity(proj, os.path.join(d['dir'], e['report'])), e['id']) for e in d['entries']]
    ids = [k[1] for k in keys]
    todo = [k for k in keys if not done.get(k)]
    unfixed = len([x for x in read_fixes(fix_file(proj))['items'] if not x['done']])

    def add_fix():
        if unfixed:
            add('待修清单里有 %d 条还没修' % unfixed, '复制一句话交给你自己的 AI 去修；或者让这个工具派 AI 去修（会用额度或花钱，改之前先备份）。',
                'prk fix %s' % p, 'fixes')
    if not ids:
        add('上一次检查的报告里没认出问题', '可能是旧版的报告。可以直接打开报告看。', '', 'files')
        steps[-1]['round'] = rid
        add_fix()
    elif todo:
        if d['merged']:
            add('有 %d 个问题等你处理（一共 %d 个）' % (len(todo), len(ids)), '先看看玩家说了什么，再一条一条告诉它：要修、以后再说、本来就这样、不是问题，还是 AI 看错了。',
                'prk decide %s%s' % (p, report_arg), 'entries')
        else:
            add('查看上一次检查的报告', '这一轮还没有合并报告。', '', 'files')
        steps[-1]['round'] = rid
        add('想放心的话，先核对一下出处', '查一查报告里说的那几行，游戏里是不是真有。不花钱。对不上的先别信。', 'prk cite "%s" %s' % (round_path, p), 'cite')
        steps[-1]['round'] = rid
        add_fix()
    else:
        add_fix()
        fix = [k[1] for k in keys if done.get(k) == '修']
        wants = [i for i in fix if i.upper().startswith('W')]
        if wants and d['merged']:
            add('可以让 AI 写一份加内容的建议', '针对玩家想要的：%s。它只写建议，不改你的游戏。' % '、'.join(wants),
                'prk expand %s%s --items %s%s' % (p, report_arg, ','.join(wants), pf), 'expand', True)
            steps[-1].update(items=','.join(wants), round=rid, report=os.path.abspath(d['reports'][0]))
        if conversation:
            add('改好以后再审一轮', '在当前对话里准备一轮，先核上一轮说要修的条目。',
                'prk prepare %s' % p, 'cli')
        elif fix:
            add('都处理完了，要修的有 %d 个' % len(fix), '%s。改好以后再检查一次，AI 会先看这几个修好了没有。' % '、'.join(fix),
                'prk run %s%s' % (p, pf), 'run', True)
        else:
            add('都处理完了，没有要修的', '游戏改过以后再检查一次。', 'prk plan %s%s' % (p, pf), 'run')
    return steps + background


PROJECT_TOKEN = '<项目设置>'


def mask_home(text):
    """The user's home folder holds the account name: show it as %USERPROFILE% wherever a path is displayed or sent."""
    home = os.path.expanduser('~')
    if not text or not home or len(home) < 4:
        return text
    return re.sub(re.escape(home), lambda m: '%USERPROFILE%', str(text), flags=re.I)


def scrub(ctx, text):
    """Before anything goes to a model: the project file's path becomes a token, the home folder a variable."""
    text = str(text or '')
    if ctx.get('path'):
        for p in {ctx['path'], ctx['path'].replace('\\', '\\\\'), ctx['path'].replace('\\', '/')}:
            text = re.sub(re.escape(p), lambda m: PROJECT_TOKEN, text, flags=re.I)
    return mask_home(text)


def guide_state(ctx):
    """What the guide is told about where the user is: as little as it needs to say what comes next.
    Numbers and yes/no only. No project name, no paths, no titles or text from the reports, nothing about the key."""
    info = local_info(ctx)
    pay, gpay, separate = pay_state(ctx['state'])
    st = {'project': None,
          'thisComputer': {'claudeCode': bool(info['claude']), 'apiKeyConfigured': bool(info['apiKey']),
                           'powershell': bool(info['powershell']), 'machineSettingsFile': bool(info['file']),
                           'pay': pay or None, 'guidePay': gpay or None, 'providerCanUseSignin': info['providerSignin']},
          'next': [{'title': scrub(ctx, s['title']), 'cmd': scrub(ctx, s['cmd']), 'costs': s['costs'], 'pay': s['pay']} for s in next_steps(ctx)]}
    if ctx.get('path'):
        proj = ctx['proj']
        problems, _notes = check_data(ctx)
        st['project'] = {'chosen': True, 'file': PROJECT_TOKEN, 'problemsInSettings': len(problems),
                         'groups': [{'id': g.get('id'), 'kind': group_kind(g), 'personas': len(g.get('personas') or [])} for g in groups_of(proj)],
                         'defaultGroups': proj.get('defaultGroups') or [], 'splits': len(proj.get('characterSplits') or [])}
        d = latest_round(ctx)
        if d:
            st['latestRound'] = {'merged': d['merged'], 'reports': len(d['reports']), 'counts': d['counts'], 'entries': len(d['entries']),
                                 'hasPlayerFeedback': bool(d['feedback'] or d['feedbackMarkdown'])}
    return st


def ask_guide(ctx, question, mode, history=None, state=None):
    """One question to the guide: a headless Claude Code that only reads the kit's documents and answers.
    mode: 'sub' = the Claude Code login on this computer (plan quota); 'api' = the key of the machine settings (money).
    Returns {ok, answer, cost, turns, seconds, error, log}."""
    ps = powershell()
    if not ps:
        return {'ok': False, 'error': '找不到 PowerShell（Windows 自带；别的系统装 pwsh）。'}
    a = ctx['args']
    gdir = os.path.join(KIT, '.guide')   # inside the kit: the guide is given this path relative to the kit, so no account name in it
    os.makedirs(gdir, exist_ok=True)
    stamp = run_id()
    task, log = os.path.join(gdir, 'task_guide_%s.md' % stamp), os.path.join(gdir, 'log_guide_%s.txt' % stamp)
    never = list((ctx.get('proj') or {}).get('neverRead') or [])   # enforced by the runner as deny rules; never written into the task
    hist = '\n\n'.join('使用者：%s\n向导：%s' % (scrub(ctx, h.get('q', '')), scrub(ctx, h.get('a', ''))) for h in (history or [])[-3:]) or '（这是第一句）'
    with open(os.path.join(KIT, 'api', 'guide_template.md'), encoding='utf-8') as f:
        text = f.read()
    for k, v in (('KIT', '.'), ('TOKEN', PROJECT_TOKEN),
                 ('STATE', json.dumps(state or guide_state(ctx), ensure_ascii=False, indent=1)), ('HISTORY', hist), ('QUESTION', scrub(ctx, question.strip()))):
        text = text.replace('{{%s}}' % k, v)
    text = delivery_task(ctx.get('proj'), text, format_guide='docs/report-format.md')
    if language(ctx.get('proj')) == 'en':
        text = text.replace('- 用中文，直接答。', '- Answer directly in English.')
    problem = task_placeholder(task, text)
    if problem:
        return {'ok': False, 'error': problem}
    with open(task, 'x', encoding='utf-8', newline='\n') as f:
        f.write(text)
    runner = a.get('runner') or os.path.join(KIT, 'api', 'run_api_task.ps1')
    cmd = [ps, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', runner, '-TaskFile', task, '-LogFile', log, '-WorkDir', KIT,
           '-Json', '-MaxTurns', '15', '-Answer', '-Tools', 'Read;Grep;Glob']
    if mode == 'sub':
        cmd.append('-Subscription')
    if never:
        cmd += ['-NeverRead', ';'.join(never)]
    lf = local_file(a, ctx['state'])
    if lf:
        cmd += ['-LocalFile', lf]
    provider = current_provider(ctx)[0]
    if mode == 'sub' and not can_sign_in(ctx, provider):
        # the checks use a provider that can only be paid by key: the guide asks Claude Code on its own login (as it
        # always did), with the model remembered for anthropic, if any
        provider = 'anthropic'
        cmd += ['-Provider', provider]
        if remembered_models(ctx['state']).get('anthropic'):
            cmd += ['-Model', str(remembered_models(ctx['state'])['anthropic'])]
    else:
        cmd += runner_target(ctx)
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)
    except subprocess.TimeoutExpired:
        return {'ok': False, 'error': '等了 15 分钟没有回话，停了。', 'log': mask_home(log)}
    res = None
    logtext = ''
    if os.path.exists(log):
        with open(log, encoding='utf-8-sig', errors='replace') as f:
            logtext = f.read()
            for line in reversed(logtext.splitlines()):
                if line.lstrip().startswith('{') and '"type"' in line and '"result"' in line:
                    try:
                        res = json.loads(line)
                    except ValueError:
                        res = None
                    break
    try:                                   # every question is a task too: one row in the ledger
        row = ledger_mod().parse_log(log, read_local(ctx).get('prices'))
        if row:
            row['轮次'] = '向导'
            ledger_mod().update(ledger_file(ctx), [row], lang=language(ctx.get('proj')))
    except (OSError, ValueError):
        pass
    out = {'ok': False, 'log': mask_home(log), 'seconds': round(time.time() - t0, 1), 'mode': mode, 'pay': mode, 'provider': provider}
    if not res:
        out['error'] = '没有拿到回答。' + (sign_in_problem(logtext[-3000:]) or runner_error(r.stderr or r.stdout or '', provider) or '看日志。')
        return out
    answer = res.get('result') or ''
    if ctx.get('path'):                    # the guide writes the token; the real path is put back here, on this computer
        answer = answer.replace('"%s"' % PROJECT_TOKEN, '"%s"' % ctx['path']).replace(PROJECT_TOKEN, '"%s"' % ctx['path'])
    out.update({'answer': answer, 'cost': res.get('total_cost_usd'), 'turns': res.get('num_turns')})
    if res.get('is_error') or not out['answer']:
        out['error'] = sign_in_problem(out['answer']) or '向导那边出错了（%s）。%s' % (res.get('subtype') or '?', out['answer'][:300])
        return out
    out['ok'] = True
    return out


def cmd_guide(ctx):
    """prk guide            what to do next, worked out from the files (free)
       prk guide "问题"     ask the AI guide (--mode sub | api; asks first, --yes skips the question)"""
    a = ctx['args']
    q = (a.get('word') or '').strip()
    steps = next_steps(ctx, conversation=not q)
    if not q:
        if want_json(ctx):
            out_json({'ok': True, 'next': steps, **output_metadata(ctx.get('proj'), check_round(ctx.get('proj') or {}, sample=False)[0])})
            return 0
        rule('现在该做什么（照文件算出来的，没问 AI，不花钱）')
        for i, s in enumerate(steps, 1):
            tags = ('  〔可选〕' if s.get('optional') else '') + ('  〔花钱〕' if s['costs'] else '')
            say('%d. %s%s' % (i, s['title'], tags))
            if s['detail']:
                say('   %s' % s['detail'])
            if s['cmd']:
                say('   命令：%s' % s['cmd'])
        say()
        say('还不清楚：prk guide "你的问题"（用 prk pay 记住的付法；只这一次：--pay sub = 会员额度，--pay api = 按次付费）。页面版：prk ui。')
        return 0
    mode = need_pay(ctx, guide=True)
    if not mode:
        return 2
    if not a.get('yes'):
        if not sys.stdin.isatty():
            msg = '问向导会用%s：不在终端里时要带 --yes。' % ('会员额度' if mode == 'sub' else '钱（按次付费）')
            out_json({'ok': False, 'error': msg}) if want_json(ctx) else say(msg)
            return 2
        if not yes('这一问会用%s，问吗' % ('一点会员额度' if mode == 'sub' else '钱（按次付费，通常几美分到几毛）'), default=True):
            return 0
    if not want_json(ctx):
        say('在问向导（%s），一般要半分钟到两分钟……' % PAY_NAMES[mode])
    r = ask_guide(ctx, q, mode)
    if want_json(ctx):
        out_json(dict(r, **output_metadata(ctx.get('proj'))))
        return 0 if r['ok'] else 1
    if not r['ok']:
        say(r.get('error') or '没有拿到回答。')
        return 1
    rule('向导')
    say(r['answer'].strip())
    say()
    cost = r.get('cost')
    say('（%s%s；%s 秒%s）' % (PAY_NAMES[mode], '，%s 的登录' % r['provider'] if mode == 'sub' and r.get('provider') else '', r.get('seconds'),
                           '' if cost is None else '；这一问 %.4f 美元%s' % (cost, '（用会员额度时这个数只是折算，不另收钱）' if mode == 'sub' else '')))
    return 0


def cmd_pay(ctx):
    """prk pay                    how the checks (run / quick / expand) and the guide are paid now
       prk pay sub | api          remember it for both (sub = the login on this computer, api = a key)
       prk pay guide sub | api    the guide on its own
       prk pay guide same         the guide like the checks again"""
    words = (ctx['args'].get('word') or '').split()
    err = ''
    if words[:1] == ['guide']:
        err = set_pay(ctx, guide=words[1] if len(words) > 1 else '') if len(words) == 2 else '用法：prk pay guide sub|api|same'
    elif len(words) == 1:
        err = set_pay(ctx, pay=words[0])
    elif words:
        err = '用法：prk pay = 看现在怎么付；prk pay sub|api = 换并记住；prk pay guide sub|api|same = 问 AI 单独设 / 跟检查一样'
    if err:
        out_json({'ok': False, 'error': err}) if want_json(ctx) else say(err)
        return 2
    pay, gpay, separate = pay_state(ctx['state'])
    pv = current_provider(ctx)[0]
    d = load_providers(ctx).get(pv) or {}
    problem = pay_problem(ctx, pay, pv)
    if want_json(ctx):
        out_json({'ok': True, 'pay': pay or None, 'guidePay': gpay or None, 'payGuideSeparate': separate,
                  'provider': pv, 'providerSignin': bool(d.get('signin')), 'signinProviders': signin_providers(ctx),
                  'problem': problem or None})
        return 0
    rule('怎么付')
    say('检查（run、quick、expand）：%s' % (PAY_LONG[pay] if pay else '还没选'))
    say('问 AI（guide）　　　　　　：%s' % ((PAY_LONG[gpay] + '（单独设的）') if separate else ('跟检查一样' if pay else '还没选')))
    say()
    if d.get('signin'):
        say('现在用的 AI：%s。它两种都能用：会员额度用的是这台电脑上 %s 登录的账号。' % (d.get('name', pv), d.get('signinWith')))
    else:
        say('现在用的 AI：%s。它只能按次付费。能用会员额度的：%s。' % (d.get('name', pv), '、'.join(signin_providers(ctx))))
    if problem:
        say()
        say(problem)
    say()
    say('改：prk pay sub（会员额度）/ prk pay api（按次付费）。问 AI 单独设：prk pay guide sub|api；跟检查一样：prk pay guide same。')
    say('只这一次：run、quick、expand、guide 后面加 --pay sub 或 --pay api。')
    return 0


def cmd_ui(ctx):
    """The page: the same things as the menu, in a browser window. Reads the files; the only thing it writes is the decision record."""
    sys.path.insert(0, os.path.join(KIT, 'ui'))   # the page and its service live in ui\\ (-I drops script folders from the path)
    import server as prk_ui
    a = ctx['args']
    return prk_ui.serve(sys.modules[__name__], ctx, port=int(a.get('port') or 0), open_browser=not a.get('no_open'), keep=bool(a.get('keep')))


def page_module():
    sys.path.insert(0, os.path.join(KIT, 'ui'))   # -I drops script folders from the path
    import static_page
    return static_page


def cmd_page(ctx):
    return page_module().generate(sys.modules[__name__], ctx)


COMMANDS = OrderedDict([
    ('ui', cmd_ui), ('guide', cmd_guide), ('pay', cmd_pay), ('model', cmd_model), ('provider', cmd_provider),
    ('check', cmd_check), ('kinds', cmd_kinds), ('presets', cmd_presets), ('personas', cmd_personas), ('suggest', cmd_suggest), ('groups', cmd_groups), ('static', cmd_static),
    ('plan', cmd_plan), ('prepare', cmd_prepare), ('fake', cmd_fake), ('run', cmd_run), ('quick', cmd_quick), ('feedback', cmd_feedback), ('cost', cmd_cost), ('costs', cmd_costs), ('cite', cmd_cite), ('page', cmd_page), ('decide', cmd_decide), ('fix', cmd_fix), ('expand', cmd_expand), ('reports', cmd_reports), ('ask', cmd_ask),
    ('new', cmd_new), ('local', cmd_local), ('install', cmd_install),
])
NO_PROJECT = ('pay', 'model', 'provider', 'costs', 'kinds', 'presets', 'personas', 'suggest', 'new', 'local', 'ui', 'guide')


# ---------- interactive menu ----------

def choose_project(ctx):
    items = find_projects(ctx['state'])
    p = pick('选项目', items + ['（输入一个项目设置的路径）', '（新建一份）'],
             show=lambda x: project_title(x) if os.path.exists(str(x)) else x)
    if p is None:
        return
    if p == '（新建一份）':
        cmd_new(ctx)
        p = ctx['state'].get('project')
    elif p == '（输入一个项目设置的路径）':
        p = ask('路径')
    if p and os.path.exists(p):
        set_project(ctx, p)
    elif p:
        say('找不到：%s' % p)


def set_project(ctx, path):
    proj, path = projfile.load_project(path)
    ctx['proj'], ctx['path'] = proj, path
    st = ctx['state']
    st['project'] = path
    recent = [path] + [x for x in st.get('recent', []) if x != path]
    remember_ledger(ctx)
    for old in recent[8:]:
        if os.path.isfile(old):
            try:
                old_proj, _ = projfile.load_project(old)
                remember_ledger(dict(ctx, proj=old_proj))
            except (OSError, ValueError, SystemExit):
                continue
    st['recent'] = recent[:8]
    save_state(st)


def menu_review(ctx):
    proj = ctx['proj']
    cmd_groups(ctx)
    a = ctx['args']
    g = ask('派哪几组（组 id 用逗号隔开；回车 = 默认那几组）', '')
    if g is None:
        return
    a['groups'] = g
    a['split'] = bool(proj.get('characterSplits')) and yes('每组按份拆开吗（每个审查员只看一份，走得深；任务数 = 组数 × 份数）')
    a['no_map'] = not yes('先建作品地图吗（多一个任务；派两组以上建议建）', default=True)
    n = ask('同时最多跑几个（API 模式用）', '7')
    a['parallel'] = int(n) if n and n.isdigit() else 7
    while True:
        pay = pay_of(ctx)[0]
        how = pick('怎么跑', ['演习：看看会有哪些任务（不花钱）', '对话：告诉我在 Claude Code 里怎么说（用会员额度）', '假 runner 走一遍（不花钱）',
                              '正式跑（%s）' % (PAY_NAMES[pay] if pay else '先问用会员额度还是按次付费')])
        if how is None:
            return
        if how.startswith('演习'):
            cmd_plan(ctx)
        elif how.startswith('对话'):
            cmd_ask(ctx)
        elif how.startswith('假'):
            cmd_fake(ctx)
        else:
            cmd_run(ctx)
            return


def menu(ctx):
    while True:
        refresh_state(ctx)          # another window (the page, another prk) may have changed the choices
        rule('玩家视角审查')
        say('让 AI 假装成不同的玩家去玩你的游戏，告诉你他们会碰到什么问题、想要什么。')
        say('现在看的游戏：%s' % (project_title(ctx['path']).split('  [')[0] if ctx.get('path') else '还没选（先按 13）'))
        say()
        say('  对你的 AI 说「从玩家视角审查一下」。它用 prk prepare 准备任务，')
        say('  做完用 prk page 生成离线页面。第一次用请它先读 AGENTS.md。')
        say()
        say('  最常用的')
        say(' 14  不知道下一步？问一下')
        say()
        say('  一步一步来')
        say(' 13  换一个游戏 / 加一个新游戏')
        say('  2  看看设置对不对')
        say('  3  自动查一遍文字（不花钱）')
        say('  4  在后台跑一轮审查')
        say('  5  在后台只派一类玩家')
        say('  6  看玩家说了什么')
        say('  7  一条一条处理问题')
        say('  8  让 AI 写加内容的建议（要花钱）')
        say()
        say('  别的')
        say('  1  打开页面（可选的本机服务）')
        say('  9  看有哪些玩家类型、检查方法')
        say(' 10  看以前的检查、花了多少钱')
        say(' 11  设置这台电脑（钥匙放在哪）')
        say(' 12  把指路牌和审查员装到项目的 .claude（可选）')
        pay = pay_of(ctx)[0]
        say(' 15  换 AI 和付钱的方式（现在：%s；%s / %s）' % (PAY_NAMES[pay] if pay else '还没选怎么付', current_provider(ctx)[0],
                                                     current_model(ctx)[0] or '默认型号'))
        say('  0  退出')
        a = ask('输一个数字')
        if a is None or a == '0':
            return 0
        if a == '13':
            choose_project(ctx)
            continue
        if a == '11':
            cmd_local(ctx)
            continue
        if a == '1':
            say('关掉页面的窗口，过一会儿就回到这里（或者按 Ctrl+C）。')
            try:
                cmd_ui(ctx)
            except KeyboardInterrupt:
                pass
            continue
        if a == '15':
            ctx['args'].pop('word', None)
            cmd_pay(ctx)
            w = ask('改怎么付吗（sub = 会员额度，api = 按次付费；guide sub / guide api = 问 AI 单独设，guide same = 跟检查一样；回车 = 不改）', '') or ''
            if w:
                ctx['args']['word'] = w
                cmd_pay(ctx)
                ctx['args'].pop('word', None)
            cmd_provider(ctx)
            pv = ask('换服务商吗（写名字；setup 名字 = 设 key 放在哪；回车 = 不换）', '') or ''
            if pv:
                ctx['args']['word'] = pv
                cmd_provider(ctx)
                ctx['args'].pop('word', None)
            cmd_model(ctx)
            m = ask('换成哪个（写 id；default = 忘掉记住的；回车 = 不换）', '') or ''
            if m:
                ctx['args']['word'] = m
                cmd_model(ctx)
                ctx['args'].pop('word', None)
            continue
        if a == '14':
            ctx['args'].pop('word', None)
            cmd_guide(ctx)
            q = ask('想问 AI 就写问题（回车 = 不问）', '') or ''
            if q:
                ctx['args']['word'] = q
                cmd_guide(ctx)
                ctx['args'].pop('word', None)
            continue
        if a == '9' and not ctx.get('path'):
            cmd_kinds(ctx)
            cmd_personas(ctx)
            continue
        if a in ('2', '3', '4', '5', '6', '7', '8', '9', '10', '12') and not ctx.get('path'):
            say('先按 13 选一个游戏（或按 1 在页面上选）。')
            continue
        try:
            if a == '2':
                cmd_check(ctx)
            elif a == '3':
                cmd_static(ctx)
            elif a == '4':
                menu_review(ctx)
            elif a == '5':
                who = ask('哪几类玩家（画像编号，用 + 隔开，例 15 + 18；不知道编号先看 9）')
                if who:
                    kind = ask('走法 id（回车 = persona 画像走查；想要的选项 = wants；全部见 9）', '') or ''
                    ctx['args'].update({'word': who, 'kind': kind})
                    cmd_quick(ctx)
                    ctx['args'].pop('kind', None)
            elif a == '6':
                ctx['args'].pop('dir', None)
                save = ask('也存成文件吗（写文件路径或文件夹；回车 = 只显示）', '') or ''
                if save:
                    ctx['args']['save'] = save
                cmd_feedback(ctx)
                ctx['args'].pop('save', None)
                if yes('看整份报告吗'):
                    ctx['args']['full'] = True
                    cmd_feedback(ctx)
                    ctx['args'].pop('full', None)
            elif a == '7':
                cmd_decide(ctx)
            elif a == '8':
                ctx['args']['items'] = ask('做哪几条（例：W1,W3；回车 = 全部「想要但没有的」）', '') or ''
                cmd_expand(ctx)
            elif a == '9':
                cmd_kinds(ctx)
                cmd_groups(ctx)
                if yes('也列出全部画像吗'):
                    cmd_personas(ctx)
                w = ask('看哪一类游戏该派谁（写类型里的几个字，例 RPG；回车 = 不看）', '') or ''
                if w:
                    ctx['args']['word'] = w
                    cmd_suggest(ctx)
            elif a == '10':
                cmd_reports(ctx)
                if yes('看最近一次的花费表吗'):
                    cmd_cost(ctx)
                if yes('看花费总账吗（每个任务一行，所有轮次）'):
                    cmd_costs(ctx)
                if yes('对最近一次做引文核验吗（查报告里的出处对不对，不花钱）'):
                    cmd_cite(ctx)
            elif a == '12':
                if yes('会覆盖项目 .claude 里的审查员和技能，装吗'):
                    cmd_install(ctx)
            else:
                say('输 0 到 15 里的一个数字。')
        except SystemExit as e:        # a script below stopped with a message
            if e.code not in (0, None):
                say(str(e.code))


# ---------- entry ----------

def parse(argv):
    args = {}
    rest = []
    flags = {'--split': 'split', '--no-map': 'no_map', '--no-merge': 'no_merge', '--yes': 'yes', '--json': 'json', '--full': 'full',
             '--no-open': 'no_open', '--rebuild': 'rebuild', '--keep': 'keep', '--log': 'log',
             '--undo': 'undo', '--done': 'done', '--reopen': 'reopen', '--fields': 'fields', '--open': 'open'}
    values = {'-p': 'project', '--project': 'project', '--local': 'local', '--groups': 'groups', '--parallel': 'parallel',
              '--map-dir': 'map_dir', '--scope': 'scope', '--from': 'from', '--items': 'items', '--out': 'out', '--model': 'model', '--max-turns': 'max_turns', '--find': 'find', '--save': 'save', '--kind': 'kind',
              '--mode': 'mode', '--pay': 'pay', '--port': 'port', '--runner': 'runner', '--provider': 'provider', '--budget': 'budget',
              '--who': 'who', '--round': 'round', '--set': 'set', '--from-json': 'from_json'}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in flags:
            args[flags[a]] = True
        elif a in values:
            if i + 1 >= len(argv) or argv[i + 1] in flags or argv[i + 1] in values:
                raise ValueError('%s 后面要跟一个值' % a)
            args[values[a]] = argv[i + 1]
            i += 1
        elif a in ('-h', '--help', 'help'):
            args['help'] = True
        else:
            rest.append(a)
        i += 1
    return args, rest


def main():
    select_state_dir()
    if '--log' in sys.argv:       # started by the .exe without a console: what it says goes to a file
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            log = os.path.join(STATE_DIR, 'ui.log')
            if os.path.exists(log) and os.path.getsize(log) > 200000:
                os.remove(log)
            # appended, not overwritten: a second start must not wipe what the running service writes
            sys.stdout = sys.stderr = open(log, 'a', encoding='utf-8', buffering=1)
            print('---- %s' % __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        except OSError:
            pass
    for s in (sys.stdout, sys.stderr):
        if s is not None and hasattr(s, 'isatty') and not s.isatty() and hasattr(s, 'reconfigure'):
            s.reconfigure(encoding='utf-8')
    if not sys.stdin.isatty():
        sys.stdin.reconfigure(encoding='utf-8-sig')   # answers piped in from a file or another program
    # the PowerShell scripts fall back to this when the machine settings name no Python: "python" on PATH can be
    # a stub that runs nothing, and then the static tables are silently skipped
    os.environ.setdefault('PLAYER_REVIEW_PYTHON', sys.executable)
    try:
        args, rest = parse(sys.argv[1:])
    except ValueError as exc:
        if '--json' in sys.argv[1:]:
            out_json({'ok': False, 'error': str(exc)})
        else:
            say(str(exc))
        return 2
    if args.get('help'):
        say(__doc__.strip())
        return 0
    state = load_state()
    if args.get('local') and os.path.exists(args['local']) and os.path.abspath(args['local']) != state.get('local'):
        state['local'] = os.path.abspath(args['local'])     # given once, used from then on (the menu and the page too)
        save_state(state)
    ctx = {'args': args, 'state': state, 'proj': None, 'path': None}
    command = rest[0] if rest else None
    if command and command not in COMMANDS:
        say('不认识的命令：%s' % command)
        say(__doc__.strip())
        return 2
    structured = command in ('prepare', 'page') or (command == 'decide' and 'set' in args) or (
        command == 'new' and ('from_json' in args or args.get('fields')))

    def usage_error(message):
        out_json({'ok': False, 'error': message}) if structured and want_json(ctx) else say(message)
        return 2

    if structured and len(rest) > 1:
        return usage_error('不认识的参数：%s' % ' '.join(rest[1:]))
    for k, ok in (('pay', PAYS), ('mode', PAYS)):      # --pay sub|api (the guide's older --mode too): only these two
        if args.get(k) is not None and norm_pay(args[k]) not in ok:
            say('--%s 只能是 sub（会员额度：用这台电脑上登录的账号）或 api（按次付费：用钥匙 key）。' % k)
            return 2
    if command == 'new' and len(rest) > 1:
        args['id'] = rest[1]
    if command in ('suggest', 'quick', 'guide', 'model', 'provider', 'pay', 'fix') and len(rest) > 1:
        args['word'] = ' '.join(rest[1:])
    if command in ('cost', 'cite', 'feedback') and len(rest) > 1:
        args['dir'] = rest[1]

    path = args.get('project')
    if not path and (command not in NO_PROJECT or command in ('ui', 'guide', 'costs')):   # these two work without a project, better with one
        if state.get('project') and os.path.exists(state['project']):
            path = state['project']
        else:
            found = find_projects(state)
            mine = [p for p in found if os.path.dirname(os.path.abspath(p)) == os.path.join(KIT, 'projects')]
            if len(mine) == 1:
                path = mine[0]
            if not path and command == 'ui':      # the page opens on something: the last one used, else the first it knows
                recent = [x for x in state.get('recent', []) if os.path.exists(x)]
                path = (recent or found or [None])[0]
    if path:
        if not os.path.exists(path):
            return usage_error('找不到项目设置：%s' % path)
        # the menu and the page remember the project (it shows up in their project list); single commands leave the choice alone
        try:
            set_project(ctx, path) if command in (None, 'ui') else ctx.update(zip(('proj', 'path'), projfile.load_project(path)))
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            if not structured and command != 'guide':
                raise
            return usage_error('读不了项目设置：%s' % exc)
        if command in ('run', 'quick', 'expand', 'fix') or (command == 'guide' and args.get('word')):
            remember_ledger(ctx)

    if not command:
        return menu(ctx)
    if command not in NO_PROJECT and not ctx['path']:
        return usage_error('要先说用哪个项目：-p <项目设置.json>（或者不带命令进菜单选一次，它会记住）。')
    return COMMANDS[command](ctx) or 0


if __name__ == '__main__':
    sys.exit(main())
