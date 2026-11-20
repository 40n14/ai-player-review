"""编译「玩家视角审查.exe」（只用标准库和 Windows 自带的 C# 编译器，不下载、不装别的）。

用法：python -I launcher\\build.py
  1. 画图标 launcher\\app.ico（和页面左上角的标一样：青到蓝的方块，中间一个白色菱形）。
  2. 用 .NET Framework 自带的 csc.exe 编译 launcher\\launcher.cs，输出到工具包根目录的「玩家视角审查.exe」。
改了 launcher.cs 或想换图标，重跑一次就行。exe 没有签名：有的杀毒软件会多问一句。
"""
import glob
import os
import struct
import subprocess
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
OUT = os.path.join(KIT, '玩家视角审查.exe')
ICO = os.path.join(HERE, 'app.ico')


def pixel(x, y, n):
    """RGBA of the logo at (x, y) in an n×n picture: a rounded square with a teal-to-blue gradient, a white diamond."""
    r = n * 0.22                                   # corner radius
    cx = min(max(x + 0.5, r), n - r)
    cy = min(max(y + 0.5, r), n - r)
    if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 > r * r:
        return (0, 0, 0, 0)
    t = (x + y) / (2.0 * (n - 1))
    a, b = (79, 209, 197), (96, 165, 250)          # the page's accent colours
    col = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    d = abs(x + 0.5 - n / 2.0) + abs(y + 0.5 - n / 2.0)
    if d < n * 0.27:
        return (255, 255, 255, 255)
    return col + (255,)


def png(n):
    raw = bytearray()
    for y in range(n):
        raw.append(0)
        for x in range(n):
            raw += bytes(pixel(x, y, n))

    def chunk(t, b):
        return struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t + b) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', n, n, 8, 6, 0, 0, 0)) + \
        chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')


def dib(n):
    """32-bit BMP entry (what older parts of Windows read best for the small sizes)."""
    head = struct.pack('<IiiHHIIiiII', 40, n, n * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    rows = bytearray()
    for y in range(n - 1, -1, -1):
        for x in range(n):
            r, g, b, a = pixel(x, y, n)
            rows += bytes((b, g, r, a))
    mask = bytes(((n + 31) // 32 * 4) * n)
    return head + bytes(rows) + mask


def write_icon():
    images = [(16, dib(16)), (32, dib(32)), (48, dib(48)), (256, png(256))]
    out = struct.pack('<HHH', 0, 1, len(images))
    offset = 6 + 16 * len(images)
    body = b''
    for n, data in images:
        out += struct.pack('<BBBBHHII', n % 256, n % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
        body += data
    with open(ICO, 'wb') as f:
        f.write(out + body)


def find_csc():
    windir = os.environ.get('WINDIR', r'C:\Windows')
    for fw in ('Framework64', 'Framework'):
        hits = sorted(glob.glob(os.path.join(windir, 'Microsoft.NET', fw, 'v4.*', 'csc.exe')))
        if hits:
            return hits[-1]
    return None


def main():
    write_icon()
    csc = find_csc()
    if not csc:
        sys.exit('没找到 Windows 自带的 C# 编译器（.NET Framework 4 的 csc.exe）。')
    cmd = [csc, '/nologo', '/target:winexe', '/codepage:65001', '/optimize+', '/platform:anycpu',
           '/r:System.Windows.Forms.dll', '/win32icon:' + ICO, '/out:' + OUT, os.path.join(HERE, 'launcher.cs')]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        sys.exit('编译没过：\n' + (r.stdout or '') + (r.stderr or ''))
    print('built: %s (%d KB)' % (OUT, os.path.getsize(OUT) // 1024))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
