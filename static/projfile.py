"""读项目设置和机器设置的公用函数（静态脚本都用它；只用标准库）。

项目设置（projects\\<id>.json）：路径可以写绝对路径，也可以写相对路径 = 相对于项目设置文件所在的文件夹。
机器设置（local.json）：这台电脑上的东西（Python、Claude Code、API key 在哪、哪些文件夹不许读）。
  找的顺序：环境变量 PLAYER_REVIEW_LOCAL 指的文件 → 工具包根目录的 local.json → 没有（都用默认值）。
"""
import json
import os
import re
import sys
from collections import OrderedDict

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'out', 'release', 'bin', 'obj', 'tests', '.git', '.vs', 'node_modules', '__pycache__'}
LITERAL = re.compile(r'"((?:[^"\\]|\\.)*)"')

# Fields of a project file that hold a path (README「项目设置」lists the same). Globs (*) are resolved too.
PATH_FIELDS = ['projectRoot', 'rulesFile', 'modSource', 'modReadme', 'characterIndex', 'characterDir', 'behaviourDir',
               'frameworkDir', 'testsDir', 'testRunner', 'testLogs', 'notesDir', 'loreBible', 'characterNotes',
               'changeReports', 'reviewOutDir', 'staticOutDir', 'personaOverlay', 'apiRunner', 'sampleRound']
PATH_LIST_FIELDS = ['previousReviews', 'readOnlyPaths', 'neverRead']


def default_project():
    """没写 --project：用工具包 projects\\ 里唯一的一份项目设置（*.json，不算 _ 开头的模板）。不止一份就要写 --project。"""
    d = os.path.join(KIT, 'projects')
    files = sorted(f for f in os.listdir(d) if f.endswith('.json') and not f.startswith('_')) if os.path.isdir(d) else []
    if len(files) != 1:
        sys.stderr.write('没写 --project，工具包 projects 文件夹里有 %d 份项目设置（%s）：用 --project 指一份。\n'
                         % (len(files), '、'.join(files) or '没有'))
        sys.exit(2)
    return os.path.join(d, files[0])


def _abs(base, p):
    if not p or not isinstance(p, str):
        return p
    p = os.path.expandvars(p)
    return p if os.path.isabs(p) else os.path.normpath(os.path.join(base, p))


def load_project(path=None):
    """Returns (proj, path). Every path field is absolute afterwards."""
    path = os.path.abspath(path or default_project())
    if not os.path.exists(path):
        sys.stderr.write('找不到项目设置：%s\n' % path)
        sys.exit(2)
    with open(path, encoding='utf-8-sig') as f:
        proj = json.load(f)
    proj.setdefault('language', 'zh')
    base = os.path.dirname(path)
    for k in PATH_FIELDS:
        if proj.get(k):
            proj[k] = _abs(base, proj[k])
    for k in PATH_LIST_FIELDS:
        if proj.get(k):
            proj[k] = [_abs(base, x) for x in proj[k]]
    if isinstance(proj.get('csv'), dict):
        for k in list(proj['csv']):
            if not k.startswith('_'):
                proj['csv'][k] = _abs(base, proj['csv'][k])
    for c in (proj.get('static') or {}).get('claims') or []:
        if c.get('file'):
            c['file'] = _abs(base, c['file'])
    img = (proj.get('static') or {}).get('images')
    if isinstance(img, dict) and img.get('dirs'):
        img['dirs'] = [_abs(base, x) for x in img['dirs']]
    for t in proj.get('staticTables') or []:
        if isinstance(t, dict) and t.get('script'):
            t['script'] = _abs(base, t['script'])
    inter = proj.get('interaction')
    if isinstance(inter, dict):
        for k in ('vanillaSource', 'modCode', 'textureDir'):
            if inter.get(k):
                inter[k] = _abs(base, inter[k])
        for d in inter.get('dataItems') or []:
            if d.get('file'):
                d['file'] = _abs(base, d['file'])
    return proj, path


def local_settings_path(path=None):
    return path or os.environ.get('PLAYER_REVIEW_LOCAL') or os.path.join(KIT, 'local.json')


def load_local(path=None):
    """Machine settings, or {} when there is no file. Never holds a key, only where the key is."""
    p = local_settings_path(path)
    if not os.path.exists(p):
        return {}
    with open(p, encoding='utf-8-sig') as f:
        return json.load(f)


def machine_never_read(path=None):
    path = os.path.abspath(local_settings_path(path))
    return [_abs(os.path.dirname(path), p) for p in load_local(path).get('neverRead') or () if p]


def path_key(path):
    return os.path.normcase(os.path.abspath(path)).casefold()


def inside(path, root):
    try:
        return os.path.commonpath([path, root]) == root
    except ValueError:  # different drive
        return False


def never_read_guard(proj, project, extra=()):
    base = os.path.dirname(os.path.abspath(project)) if project else os.getcwd()
    protected = set()
    for paths, relative_to in ((proj.get('neverRead'), base), (extra, os.getcwd())):
        for path in paths or ():
            if path:
                full = _abs(relative_to, path)
                protected.update((path_key(full), path_key(os.path.realpath(full))))

    def blocked(path):
        key = path_key(path)
        return any(inside(key, root) for root in protected)

    def is_blocked(path):
        return blocked(path) or bool(protected and blocked(os.path.realpath(path)))

    return is_blocked


# ---------- reading files ----------

def strip_jsonc(text):
    """Remove // and /* */ comments and trailing commas, but never inside strings (strings can hold "//")."""
    out = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == '\\' and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
        elif c == '/' and text.startswith('//', i):
            j = text.find('\n', i)
            i = n if j < 0 else j          # keep the newline
            continue
        elif c == '/' and text.startswith('/*', i):
            j = text.find('*/', i + 2)
            end = n if j < 0 else j + 2
            out.append('\n' * text.count('\n', i, end))
            i = end
            continue
        elif c in ']}':
            k = len(out) - 1               # drop a trailing comma before ] or }
            while k >= 0 and out[k] in ' \t\r\n':
                k -= 1
            if k >= 0 and out[k] == ',':
                out[k] = ' '
        out.append(c)
        i += 1
    return ''.join(out)


def load_jsonc(path):
    with open(path, encoding='utf-8-sig') as f:
        raw = f.read()
    return json.loads(strip_jsonc(raw), object_pairs_hook=OrderedDict), raw


def need_path(path, what):
    """A required input. A wrong path must stop the run with a clear message, not give an empty table that
    reads like "no problems"."""
    if not path or not os.path.exists(path):
        sys.exit('找不到%s：%s。项目设置里的路径写错了，或者文件挪走了；这张表没生成。' % (what, path or '（没写）'))
    return path


def get_field(proj, dotted):
    cur = proj
    for part in dotted.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def need_project_paths(proj, which):
    """which: dotted field names (csv.zh, modSource ...). Stops at the first missing one."""
    for name in which:
        need_path(get_field(proj, name), '项目设置的 %s' % name)


def walk_files(root, exts, is_blocked=None, skip_dirs=SKIP_DIRS):
    is_blocked = is_blocked or (lambda _path: False)
    if is_blocked(root):
        return
    real_root = path_key(os.path.realpath(root))

    def allowed(path):
        return not is_blocked(path) and inside(path_key(os.path.realpath(path)), real_root)

    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in skip_dirs and allowed(os.path.join(dirpath, d))]
        for name in sorted(files):
            path = os.path.join(dirpath, name)
            if (not exts or name.lower().endswith(exts)) and allowed(path):
                yield path


def md_cell(s):
    return str(s).replace('|', '\\|').replace('\n', ' ')
