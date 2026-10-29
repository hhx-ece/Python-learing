"""黑盒运行器 + 测试基类。

它把学生系统当成一个"命令行程序"来跑：
    喂一串输入 → 收回它 print 出来的文字
所以不管你内部怎么改（拆函数、换数据结构、加类），只要"用户看到的行为"对，测试就过。
这正是一个产品该被验收的方式。

不要改这个文件。
"""

from __future__ import annotations

import builtins
import io
import os
import re
import runpy
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SCRIPT = PROJECT_DIR / "student_score_system.py"
DATA_NAME = "students.json"


def script_path() -> Path:
    """默认用项目根目录的 student_score_system.py；可用环境变量换路径。"""
    override = os.environ.get("STUDENT_SCRIPT")
    return Path(override) if override else DEFAULT_SCRIPT


def run(inputs, script=None) -> str:
    """跑一遍脚本，返回它 print 出来的内容（不含 input 的提示文字）。"""
    path = Path(script) if script else script_path()
    feed = [str(x) for x in inputs] + ["0"]   # 末尾补一个"退出"
    buf = io.StringIO()

    def fake_input(prompt=""):
        if not feed:
            raise AssertionError(
                "脚本还在等输入，但测试的数据用完了。\n"
                "两个常见原因：① 退出键不是 0（任务书要求菜单 0 = 退出）；"
                "② 某个循环没有退出路径。"
            )
        return feed.pop(0)

    original = builtins.input
    builtins.input = fake_input
    try:
        with redirect_stdout(buf):
            runpy.run_path(str(path), run_name="__main__")
    except SystemExit:
        pass
    finally:
        builtins.input = original
    return buf.getvalue()


class ScriptTest(unittest.TestCase):
    """跑脚本的测试基类：每道题开始前清空数据文件，结束后再清一次。"""

    def setUp(self) -> None:
        self.script = script_path()
        if not self.script.exists():
            self.fail(
                f"找不到 {self.script}\n"
                f"把你的 student_score_system.py 放到 {PROJECT_DIR} 下，"
                "或设置环境变量 STUDENT_SCRIPT 指向它。"
            )
        self.data_file = self.script.parent / DATA_NAME
        self.data_file.unlink(missing_ok=True)

    def tearDown(self) -> None:
        self.data_file.unlink(missing_ok=True)

    def run_script(self, *inputs) -> str:
        return run(list(inputs), script=self.script)

    def assert_row(self, out: str, sid, name: str, score) -> None:
        """断言输出里有「学号 姓名 成绩」这一行（列之间至少一个空白）。"""
        pattern = rf"{re.escape(str(sid))}\s+{re.escape(name)}\s+{re.escape(str(score))}"
        self.assertRegex(out, pattern, f"输出里没有找到这一行：{sid} {name} {score}")
