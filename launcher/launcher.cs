// 「玩家视角审查.exe」：双击打开工具包的页面。
// 它只做一件事：在后台（不弹黑窗口）运行 python -I prk.py ui，页面自己会开一个窗口。
// 页面的服务开着时再双击，只会多开一个窗口；关掉所有窗口，服务过一会儿自己停。
// 要 Python 3.8 以上（找的顺序见 FindPython）。编译：python launcher\build.py（用 Windows 自带的 C# 编译器，不用装别的）。
using System;
using System.Diagnostics;
using System.IO;
using System.Text.RegularExpressions;
using System.Windows.Forms;

[assembly: System.Reflection.AssemblyTitle("玩家视角审查")]
[assembly: System.Reflection.AssemblyProduct("玩家视角审查工具包")]
[assembly: System.Reflection.AssemblyDescription("打开玩家视角审查工具包的页面")]
[assembly: System.Reflection.AssemblyVersion("1.0.0.0")]

static class Launcher
{
    const string Title = "玩家视角审查";

    [STAThread]
    static int Main(string[] args)
    {
        string dir = AppDomain.CurrentDomain.BaseDirectory;
        string prk = Path.Combine(dir, "prk.py");
        if (!File.Exists(prk))
        {
            Fail("找不到 prk.py。\n这个 exe 要放在工具包的文件夹里，和 prk.py 在一起。");
            return 2;
        }
        string[] py = FindPython();
        if (py == null)
        {
            Fail("这台电脑上没找到 Python（要 3.8 以上）。\n\n先装 Python：https://www.python.org/downloads/\n装的时候勾上「Add python.exe to PATH」，装好再双击这个 exe。");
            return 2;
        }
        string extra = "";
        foreach (string a in args) extra += " " + Quote(a);   // e.g. -p <项目设置.json>
        ProcessStartInfo psi = new ProcessStartInfo(py[0], (py[1] + " -I " + Quote(prk) + " ui --log" + extra).Trim());
        psi.UseShellExecute = false;
        psi.CreateNoWindow = true;
        psi.WorkingDirectory = dir;
        psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";
        Process p;
        try { p = Process.Start(psi); }
        catch (Exception e) { Fail("启动不了 Python（" + py[0] + "）：\n" + e.Message); return 2; }

        // The service opens its own window and keeps running. If it stops at once with an error, say what it said.
        if (p.WaitForExit(8000) && p.ExitCode != 0)
        {
            string log = Path.Combine(StateDir(), "ui.log");
            string text = "";
            try { if (File.Exists(log)) text = File.ReadAllText(log); } catch (IOException) { }
            if (text.Length > 1500) text = "……" + text.Substring(text.Length - 1500);
            Fail("页面没打开（退出码 " + p.ExitCode + "）。\n\n" + text + "\n\n在终端里运行 prk ui 能看到完整的说明。");
            return 1;
        }
        return 0;
    }

    static string StateDir()
    {
        string la = Environment.GetEnvironmentVariable("LOCALAPPDATA");
        return Path.Combine(string.IsNullOrEmpty(la) ? Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) : la, "PlayerReviewKit");
    }

    // { program, arguments in front of the script }. Order: PLAYER_REVIEW_PYTHON, the "py" launcher (Python 3),
    // python.exe on PATH (not the Microsoft Store placeholder, which runs nothing), the usual install folders.
    static string[] FindPython()
    {
        string env = Environment.GetEnvironmentVariable("PLAYER_REVIEW_PYTHON");
        if (!string.IsNullOrEmpty(env) && File.Exists(env)) return new string[] { env, "" };
        string win = Environment.GetEnvironmentVariable("WINDIR") ?? @"C:\Windows";
        string launcher = OnPath("py.exe");
        if (launcher == null && File.Exists(Path.Combine(win, "py.exe"))) launcher = Path.Combine(win, "py.exe");
        if (launcher != null) return new string[] { launcher, "-3" };
        string onPath = OnPath("python.exe");
        if (onPath != null) return new string[] { onPath, "" };
        string best = null;
        foreach (string root in new string[] {
            Path.Combine(Environment.GetEnvironmentVariable("LOCALAPPDATA") ?? "", @"Programs\Python"),
            Environment.GetEnvironmentVariable("ProgramFiles") ?? "", Environment.GetEnvironmentVariable("ProgramFiles(x86)") ?? "" })
        {
            if (root == "" || !Directory.Exists(root)) continue;
            string[] dirs;
            try { dirs = Directory.GetDirectories(root, "Python3*"); } catch (Exception) { continue; }
            Array.Sort(dirs);
            foreach (string d in dirs)
            {
                string exe = Path.Combine(d, "python.exe");
                if (File.Exists(exe)) best = exe;   // the last one sorted is the newest
            }
        }
        return best == null ? null : new string[] { best, "" };
    }

    static string OnPath(string name)
    {
        string path = Environment.GetEnvironmentVariable("PATH") ?? "";
        foreach (string d in path.Split(';'))
        {
            if (d.Trim() == "" || d.IndexOf("WindowsApps", StringComparison.OrdinalIgnoreCase) >= 0) continue;
            try
            {
                string f = Path.Combine(d.Trim().Trim('"'), name);
                if (File.Exists(f)) return f;
            }
            catch (ArgumentException) { }
        }
        return null;
    }

    static string Quote(string s)
    {
        if (s.Length > 0 && s.IndexOfAny(new char[] { ' ', '\t', '"' }) < 0) return s;
        return "\"" + Regex.Replace(s, @"(\\*)(""|\z)", m =>
            m.Groups[1].Value + m.Groups[1].Value + (m.Groups[2].Length > 0 ? "\\\"" : "")) + "\"";
    }

    static void Fail(string text)
    {
        MessageBox.Show(text, Title, MessageBoxButtons.OK, MessageBoxIcon.Warning);
    }
}
