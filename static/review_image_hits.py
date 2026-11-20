"""图片点得到的面积（只读，只用标准库）。

为什么要有它：审查员读代码、读数据、读文本，但**不看图**。一件东西的图要是大半是透明的，而游戏按"点在不透明的
像素上才算点中"来判定，玩家就很难点中它、拿不起来、拖不到该放的地方。这件事代码里没有一行写着，读代码走不到。
这张表把每张图"有多大一块点得到"量出来，交给审查员去接上玩家的结果。

量什么：项目设置 static.images.dirs 里的每张 PNG：宽高、不透明的像素占整张图的百分之几、不透明部分的外框。
不量什么：游戏到底按什么判定点中（像素 / 整格 / 整个矩形 / 碰撞框），这要审查员回代码和设计里查。

项目设置：
  "static": { "images": {
      "dirs": [ "game\\images" ],     必写。玩家要点、要拖的东西的图在哪（可以写几个）
      "cellSize": 16,                  可选。格子边长（像素）：表里多一列"占几格"
      "minOpaque": 50,                 可选。点得到的不到百分之几算可疑（默认 50）
      "alphaAbove": 0,                 可选。透明度大于多少算点得到（0–254，默认 0）
      "skip": "^ui[\\\\/]bg_",         可选。相对路径对上这个正则的不量
      "maxPixels": 4194304             可选。比这个大的图不量（背景、整张地图；纯 Python 解码慢）
  } }

用法：python -I review_image_hits.py [--project 项目设置.json] [输出.md]
"""
import math
import os
import re
import struct
import sys
import zlib
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)   # -I drops the script folder from the path
sys.dont_write_bytecode = True
from projfile import load_project, machine_never_read, md_cell, need_path, never_read_guard, walk_files  # noqa: E402

CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


class Skip(Exception):
    pass


def unfilter(raw, h, stride, bpp):
    """PNG scanline filters, one row at a time."""
    prev = bytearray(stride)
    pos = 0
    for _y in range(h):
        if pos + 1 + stride > len(raw):
            raise Skip('数据不完整')
        ft = raw[pos]
        line = bytearray(raw[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        if ft == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 255
        elif ft == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif ft == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif ft == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        elif ft != 0:
            raise Skip('不认识的行滤波 %d' % ft)
        yield line
        prev = line


def unpack_bits(line, depth, w):
    """Samples of a row whose bit depth is 1, 2 or 4."""
    out = bytearray(w)
    mask = (1 << depth) - 1
    per = 8 // depth
    for x in range(w):
        byte = line[x // per]
        shift = 8 - depth * (x % per + 1)
        out[x] = (byte >> shift) & mask
    return out


def measure(path, alpha_above, max_pixels):
    """Returns (w, h, opaque pixel count, bbox or None). Raises Skip with the reason."""
    with open(path, 'rb') as f:
        data = f.read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise Skip('不是 PNG')
    pos, idat, trns, hdr = 8, [], None, None
    while pos + 8 <= len(data):
        ln, typ = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b'IHDR':
            hdr = struct.unpack('>IIBBBBB', body[:13])
        elif typ == b'tRNS':
            trns = body
        elif typ == b'IDAT':
            idat.append(body)
        elif typ == b'IEND':
            break
    if not hdr:
        raise Skip('没有文件头')
    w, h, depth, ctype, _comp, _flt, interlace = hdr
    if ctype not in CHANNELS or w == 0 or h == 0:
        raise Skip('不认识的颜色类型')
    # no alpha anywhere: every pixel is hit
    if (ctype in (0, 2) and trns is None) or (ctype == 3 and (trns is None or min(trns or b'\xff') == 255)):
        return w, h, w * h, (0, 0, w - 1, h - 1)
    if interlace:
        raise Skip('隔行存的 PNG，没量')
    if w * h > max_pixels:
        raise Skip('太大（%d×%d），没量' % (w, h))
    bits = CHANNELS[ctype] * depth
    stride = (w * bits + 7) // 8
    bpp = max(1, bits // 8)
    try:
        raw = zlib.decompress(b''.join(idat))
    except zlib.error:
        raise Skip('解不开')

    th = bytes(1 if v > alpha_above else 0 for v in range(256))
    pal = None
    if ctype == 3:
        pal = bytes(trns) + b'\xff' * (256 - len(trns))
    key = None
    if ctype == 0 and trns:
        key = struct.unpack('>H', trns[:2])[0]
    if ctype == 2 and trns:
        key = struct.unpack('>HHH', trns[:6])

    count, x0, x1, y0, y1 = 0, w, -1, h, -1
    for y, line in enumerate(unfilter(raw, h, stride, bpp)):
        if ctype == 6:
            if depth == 8:
                alpha = bytes(line[3::4])
            else:
                alpha = bytes((hi or (1 if lo else 0)) for hi, lo in zip(line[6::8], line[7::8]))
        elif ctype == 4:
            if depth == 8:
                alpha = bytes(line[1::2])
            else:
                alpha = bytes((hi or (1 if lo else 0)) for hi, lo in zip(line[2::4], line[3::4]))
        elif ctype == 3:
            idx = bytes(line[:w]) if depth == 8 else bytes(unpack_bits(line, depth, w))
            alpha = idx.translate(pal)
        elif ctype == 0:
            if depth == 16:
                alpha = bytes(0 if (hi << 8 | lo) == key else 255 for hi, lo in zip(line[0::2], line[1::2]))
            else:
                samples = line[:w] if depth == 8 else unpack_bits(line, depth, w)
                alpha = bytes(0 if v == key else 255 for v in samples)
        else:  # ctype 2 with a colour key
            if depth == 8:
                alpha = bytes(0 if (r, g, b) == key else 255 for r, g, b in zip(line[0::3], line[1::3], line[2::3]))
            else:
                alpha = bytes(0 if (line[i] << 8 | line[i + 1], line[i + 2] << 8 | line[i + 3], line[i + 4] << 8 | line[i + 5]) == key
                              else 255 for i in range(0, w * 6, 6))
        mask = alpha.translate(th)
        n = mask.count(1)
        if n:
            count += n
            y0, y1 = min(y0, y), y
            x0 = min(x0, mask.find(1))
            x1 = max(x1, mask.rfind(1))
    return w, h, count, ((x0, y0, x1, y1) if count else None)


def main():
    args = sys.argv[1:]
    project, out_path = None, None
    i = 0
    while i < len(args):
        if args[i] == '--project':
            project = args[i + 1]; i += 2
        elif args[i] in ('--only', '--prefix'):
            i += 2
        else:
            out_path = args[i]; i += 1
    proj, project = load_project(project)
    is_blocked = never_read_guard(proj, project, machine_never_read())
    cfg = (proj.get('static') or {}).get('images') or {}
    dirs = cfg.get('dirs') or []
    if not dirs:
        sys.exit('项目设置没写 static.images.dirs（玩家要点、要拖的东西的图在哪）；这张表没生成。')
    dirs = [d for d in dirs if not is_blocked(d)]
    if not dirs:
        sys.exit('图片目录都在禁读范围内，这张表没生成。')
    for d in dirs:
        need_path(d, '项目设置的 static.images.dirs')
    cell = cfg.get('cellSize')
    min_opaque = float(cfg.get('minOpaque', 50))
    alpha_above = int(cfg.get('alphaAbove', 0))
    max_pixels = int(cfg.get('maxPixels', 4194304))
    skip = re.compile(cfg['skip']) if cfg.get('skip') else None
    root = proj.get('projectRoot') or os.path.dirname(project)

    rows, unmeasured, skipped = [], [], 0
    other_exts = ('.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tga', '.dds', '.psd', '.svg')
    for d in dirs:
        for full in walk_files(d, (), is_blocked, skip_dirs=()):
            rel = os.path.relpath(full, d)
            shown = os.path.relpath(full, root) if os.path.commonpath([os.path.abspath(root), os.path.abspath(full)]) == os.path.abspath(root) else full
            low = full.lower()
            if skip and skip.search(rel):
                skipped += 1
                continue
            if low.endswith(other_exts):
                unmeasured.append((shown, '只量 PNG'))
                continue
            if not low.endswith('.png'):
                continue
            try:
                w, h, count, box = measure(full, alpha_above, max_pixels)
            except Skip as e:
                unmeasured.append((shown, str(e)))
                continue
            except (OSError, struct.error, IndexError) as e:
                unmeasured.append((shown, '读不了：%s' % type(e).__name__))
                continue
            rows.append((100.0 * count / (w * h), shown, w, h, count, box))
    rows.sort(key=lambda r: (r[0], r[1]))
    suspects = [r for r in rows if r[0] < min_opaque]

    def cells(w, h):
        return '%d×%d' % (math.ceil(w / cell), math.ceil(h / cell)) if cell else ''

    def line(r):
        pct, shown, w, h, count, box = r
        box_s = '全透明' if not box else '%d×%d，从 (%d,%d) 起' % (box[2] - box[0] + 1, box[3] - box[1] + 1, box[0], box[1])
        cols = ['`%s`' % md_cell(shown), '%d×%d' % (w, h)]
        if cell:
            cols.append(cells(w, h))
        cols += ['%.1f%%（%d 个像素）' % (pct, count), box_s]
        return '| ' + ' | '.join(cols) + ' |'

    head = '| 图片 | 宽×高 |' + (' 占几格 |' if cell else '') + ' 点得到的 | 不透明部分的外框 |'
    sep = '|---|---|' + ('---|' if cell else '') + '---|---|'
    out = ['# 图片点得到的面积（静态表）', '',
           '生成：%s；项目：%s' % (datetime.now().strftime('%Y-%m-%d %H:%M'), proj.get('name', '')), '',
           '量的是：%s 里的 PNG。透明度大于 %d 的像素算"点得到"；点得到的不到 %g%% 的列进第一节。' % (
               '、'.join('`%s`' % d for d in dirs), alpha_above, min_opaque), '',
           '**这张表只量了图，没看游戏怎么判定点中。** 审查员不看图，所以这里替你量了；剩下三件事要你回代码、数据、设计里查：', '',
           '1. 这张图是玩家要点、要拿、要拖的吗？只是给人看的（提示图标、装饰），点不中不算问题。',
           '2. 游戏按什么判定点中：按像素的透明度、按整格 / 整个矩形、还是按另外写的碰撞框？按整格和矩形的，面积小不算问题。',
           '3. 按像素判定的：玩家点不中会怎样。一直走到底：拿不起来 → 放不到该放的地方 → 哪一步做不了、哪条线走不下去、东西会不会过了时候就没了。',
           '', '## 一、可疑：点得到的不到 %g%%（%d 张）' % (min_opaque, len(suspects)), '']
    if suspects:
        out += [head, sep] + [line(r) for r in suspects]
    else:
        out.append('（没有）')
    out += ['', '## 二、全部图片（%d 张，从点得到的最少的排起）' % len(rows), '']
    if rows:
        out += [head, sep] + [line(r) for r in rows]
    else:
        out.append('（这几个文件夹里没有 PNG）')
    out += ['', '## 三、没量的（%d 张）' % len(unmeasured), '']
    if unmeasured:
        out += ['| 图片 | 为什么 |', '|---|---|'] + ['| `%s` | %s |' % (md_cell(p), md_cell(why)) for p, why in sorted(unmeasured)]
        out += ['', '没量的不等于没问题：要紧的东西在这里的，写进报告的「这次没走到的」。']
    else:
        out.append('（没有）')
    if skipped:
        out += ['', '照 `static.images.skip` 跳过了 %d 张。' % skipped]

    out_path = out_path or os.path.join(proj.get('staticOutDir') or '.', '_image_hits.md')
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    print('wrote %s (%d 张图；点得到的不到 %g%% 的 %d 张；没量的 %d 张)' % (out_path, len(rows), min_opaque, len(suspects), len(unmeasured)))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    main()
