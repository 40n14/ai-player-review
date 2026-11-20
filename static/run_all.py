"""一条命令跑这个项目的静态表（只读，只写输出文件夹里的 .md）。

自带的表：
  text   _text_checks.md   玩家看得见的文字：漏翻、占位符、剧透、藏起来的名字、说明和设置不符、中英文意思不一样（只要两个文本表）
  images _image_hits.md    图片点得到的面积：每张图不透明的像素占百分之几（要项目设置的 static.images.dirs）
项目自己的表：项目设置的 staticTables 里可以登记自己的脚本（照这个作品的数据格式写的流程表、连续性表、交互表……）：
  { "id": "flow", "script": "tables\\flow.py", "out": "_flow_table.md", "filter": "only",
    "firstLook": [ { "head": "一、可疑处", "what": "条件、键、结局对不上" } ] }
  脚本的调用方式固定：python -I <script> --project <项目设置> [--only a,b | --prefix a_,b_] <输出.md>
  filter 写 only 或 prefix：run_all 的 --only / --prefix 传给哪一种脚本；不写就都不传。
  firstLook：这张表里先看哪几节（按 "## " 标题里的字找），写进 _summary.md。

用法：python -I run_all.py [--project 项目设置.json] [--local 机器设置.json] [--only id1,id2] [--prefix 前缀_,前缀_] [输出文件夹]
  不写输出文件夹 = 项目设置的 staticOutDir。不写 --project = 工具包 projects 文件夹里唯一的那份项目设置。
  跑哪几张：项目设置的 staticTables（自带表写 id，自己的表写上面那样的对象）；不写 = 只跑 text。
  必需的路径（text 要两个文本表；images 要 static.images.dirs；自己的表在 requires 里写字段名）缺了就报错、退出码 2，一张表都不跑
  （免得旧表或空表被当成"没有问题"）；可选的路径缺了写进 _summary.md。
"""
import os
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)   # -I drops the script folder from the path
sys.dont_write_bytecode = True
from projfile import get_field, load_project, local_settings_path, machine_never_read, never_read_guard  # noqa: E402

BUILTIN = {
    'text': {'id': 'text', 'script': os.path.join(HERE, 'review_text_checks.py'), 'out': '_text_checks.md', 'filter': 'prefix',
             'requires': ['csv.zh', 'csv.en'],
             'firstLook': [{'head': '一、可疑', 'what': '玩家看得见的文字问题，多数一眼能定'}]},
    'images': {'id': 'images', 'script': os.path.join(HERE, 'review_image_hits.py'), 'out': '_image_hits.md',
               'requires': ['static.images.dirs'],
               'firstLook': [{'head': '一、可疑', 'what': '图大半是透明的：玩家可能点不中、拿不起来（要回代码查游戏按什么判定点中）'}]},
}
OPTIONAL = ['projectRoot', 'rulesFile', 'modSource', 'modReadme', 'notesDir', 'loreBible', 'personaOverlay', 'reviewOutDir']


def main():
    args = sys.argv[1:]
    project, local, only, prefix, out_dir = None, None, None, None, None
    i = 0
    while i < len(args):
        if args[i] == '--project':
            project = args[i + 1]; i += 2
        elif args[i] == '--local':
            local = args[i + 1]; i += 2
        elif args[i] == '--only':
            only = args[i + 1]; i += 2
        elif args[i] == '--prefix':
            prefix = args[i + 1]; i += 2
        else:
            out_dir = args[i]; i += 1
    proj, project = load_project(project)
    local = os.path.abspath(local_settings_path(local))
    is_blocked = never_read_guard(proj, project, machine_never_read(local))

    wanted = proj.get('staticTables')
    if wanted is None:
        wanted = ['text']
    tables, bad = [], []
    for t in wanted:
        if isinstance(t, str):
            if t in BUILTIN:
                tables.append(BUILTIN[t])
            else:
                bad.append('%s（自带的表只有：%s；自己的表要写成 { "id", "script", "out" }）' % (t, '、'.join(BUILTIN)))
        elif isinstance(t, dict) and t.get('script') and t.get('out'):
            t.setdefault('id', os.path.splitext(os.path.basename(t['script']))[0])
            tables.append(t)
        else:
            bad.append('%r（缺 script 或 out）' % (t,))
    if bad:
        sys.stderr.write('项目设置的 staticTables 写得不对：\n  %s\n' % '\n  '.join(bad))
        sys.exit(2)

    out_dir = os.path.abspath(out_dir or proj['staticOutDir'])
    real_root = os.path.normcase(os.path.realpath(out_dir))
    outputs = [(t['id'], t['out']) for t in tables] + [('_summary.md', '_summary.md')]
    for table, name in outputs:
        real_out = os.path.normcase(os.path.realpath(os.path.join(out_dir, name)))
        try:
            inside = real_out != real_root and os.path.commonpath([real_root, real_out]) == real_root
        except ValueError:  # different drive
            inside = False
        if not inside:
            sys.exit('表 %s 的 out 配置有误，输出路径不在输出文件夹内：%s' % (table, name))

    missing = []
    for t in tables:
        if is_blocked(t['script']):
            missing.append('表 %s 的脚本在禁读范围内' % t['id'])
        elif not os.path.exists(t['script']):
            missing.append('表 %s 的脚本 = %s' % (t['id'], t['script']))
        for name in t.get('requires') or []:
            p = get_field(proj, name)
            for one in (p if isinstance(p, list) else [p]) or [None]:
                if one and is_blocked(one):
                    if t is not BUILTIN['images']:
                        missing.append('%s 在禁读范围内（表 %s 要用）' % (name, t['id']))
                elif not one or not os.path.exists(one):
                    missing.append('%s = %s（表 %s 要用）' % (name, one or '（没写）', t['id']))
    if missing:
        sys.stderr.write('项目设置里必需的路径不对，一张表都没跑（%s）：\n  %s\n' % (project, '\n  '.join(missing)))
        sys.exit(2)
    warn = []
    for name in OPTIONAL:
        p = proj.get(name)
        if p and '*' not in p and not is_blocked(p) and not os.path.exists(p):
            warn.append('`%s` = %s' % (name, p))
    for c in (proj.get('static') or {}).get('claims') or []:
        if c.get('file') and not is_blocked(c['file']) and not os.path.exists(c['file']):
            warn.append('`static.claims`「%s」的 `file` = %s' % (c.get('name', ''), c['file']))

    os.makedirs(out_dir, exist_ok=True)
    # old tables from an earlier run would be read as this run's: remove them first
    for _, name in outputs:
        p = os.path.join(out_dir, name)
        if os.path.lexists(p):
            os.remove(p)

    printed, failed = [], []
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PLAYER_REVIEW_LOCAL=local)
    # one after another on purpose (one process at a time, light on the machine)
    for t in tables:
        extra = []
        if t.get('filter') == 'only' and only:
            extra = ['--only', only]
        elif t.get('filter') == 'prefix' and prefix:
            extra = ['--prefix', prefix]
        cmd = [sys.executable, '-I', t['script'], '--project', project] + extra + [os.path.join(out_dir, t['out'])]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
        msg = (r.stdout.strip() or r.stderr.strip()).splitlines()
        line = msg[-1] if msg else ''
        if r.returncode != 0:
            failed.append(t['id'])
            line = 'FAILED: ' + (r.stderr.strip().splitlines() or ['?'])[-1]
        printed.append((t['id'], line))
        print('%s: %s' % (t['id'], line))

    # summary: the headings to read first, with their counts
    out = ['# 静态表：先看哪里', '',
           '生成：%s；项目：%s' % (datetime.now().strftime('%Y-%m-%d %H:%M'), proj.get('name', '')), '',
           '几张表都是只读文件、按字和正则找出来的线索，不是结论。审查员拿它当地图，每条都回代码和文本里核对。', '',
           '这次跑的表：%s' % '、'.join('`%s`（%s）' % (t['out'], t['id']) for t in tables), '']
    out.append('| 先看 | 是什么 | 标题（条数） |')
    out.append('|---|---|---|')
    for t in tables:
        for fl in t.get('firstLook') or []:
            p = os.path.join(out_dir, t['out'])
            title = '（没生成）'
            if os.path.exists(p):
                with open(p, encoding='utf-8') as f:
                    for ln in f:
                        if ln.startswith('## ') and fl.get('head', '') in ln:
                            title = ln[3:].strip()
                            break
            out.append('| `%s` | %s | %s |' % (t['out'], fl.get('what', ''), title.replace('|', '\\|')))
    out.append('')
    out.append('脚本输出：')
    out.append('')
    for tid, line in printed:
        out.append('- `%s`：%s' % (tid, line))
    if failed:
        out.append('')
        out.append('**没跑成**：%s。上面那一行是报错；单独跑一次那个脚本看全文。没跑成的表这次没有（旧的已经删掉）。' % '、'.join(failed))
    if warn:
        out.append('')
        out.append('**项目设置里这些可选的路径不存在**（表照跑，审查员读不到这些文件）：')
        out.append('')
        out += ['- %s' % x for x in warn]
    with open(os.path.join(out_dir, '_summary.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    print('summary: %s' % os.path.join(out_dir, '_summary.md'))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    main()
