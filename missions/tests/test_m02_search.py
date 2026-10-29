"""M02 验收：查询。

学号精确匹配，姓名包含关键字即匹配；查不到要有明确提示。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import ScriptTest  # noqa: E402


class M02Search(ScriptTest):
    def test_01_按姓名片段查(self):
        out = self.run_script("1", "张三", "90", "1", "李四", "80", "4", "张")
        self.assert_row(out, 1001, "张三", 90)
        self.assertNotIn("李四", out)

    def test_02_按学号查(self):
        out = self.run_script("1", "张三", "90", "1", "李四", "80", "4", "1002")
        self.assert_row(out, 1002, "李四", 80)
        self.assertNotIn("张三", out)

    def test_03_查不到要有提示(self):
        out = self.run_script("1", "张三", "90", "4", "王")
        self.assertIn("没有找到符合条件的学生", out)

    def test_04_查询结果也带分数(self):
        out = self.run_script("1", "张三", "87", "4", "张")
        self.assert_row(out, 1001, "张三", 87)
