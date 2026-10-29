"""M01 验收：输入契约。

只验行为：非法输入必须被拦下，最终存进去的必须是合法值。
提示语怎么写不管，但数据不能脏。
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import ScriptTest  # noqa: E402


class M01InputContract(ScriptTest):
    def test_01_添加成功并显示学号(self):
        out = self.run_script("1", "张三", "90", "3")
        self.assertIn("该学生的学号为:1001", out)
        self.assert_row(out, 1001, "张三", 90)

    def test_02_空名字被拦下(self):
        out = self.run_script("1", "", "   ", "张三", "90", "3")
        self.assert_row(out, 1001, "张三", 90)

    def test_03_分数越界被拦下(self):
        for bad in ("120", "-1", "101"):
            with self.subTest(bad=bad):
                self.data_file.unlink(missing_ok=True)
                out = self.run_script("1", "张三", bad, "90", "3")
                self.assert_row(out, 1001, "张三", 90)
                self.assertNotRegex(out, rf"张三\s+{re.escape(bad)}\b")

    def test_04_分数不是整数(self):
        out = self.run_script("1", "张三", "abc", "90", "3")
        self.assert_row(out, 1001, "张三", 90)

    def test_05_乱敲菜单不会崩(self):
        out = self.run_script("9", "abc", "3")
        self.assertIn("没有学生成绩", out)
