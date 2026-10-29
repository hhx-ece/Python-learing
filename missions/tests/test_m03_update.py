"""M03 验收：修改。

重点不是"能改"，而是"改一半失败"时数据不能脏。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import ScriptTest  # noqa: E402


class M03Update(ScriptTest):
    def test_01_只改分数名字不动(self):
        out = self.run_script("1", "张三", "90", "5", "1001", "", "95", "3")
        self.assert_row(out, 1001, "张三", 95)

    def test_02_只改名字分数不动(self):
        out = self.run_script("1", "张三", "90", "5", "1001", "张三丰", "", "3")
        self.assert_row(out, 1001, "张三丰", 90)

    def test_03_非法分数整次取消(self):
        out = self.run_script("1", "张三", "90", "5", "1001", "", "120", "3")
        self.assert_row(out, 1001, "张三", 90)

    def test_04_全回车等于没改(self):
        out = self.run_script("1", "张三", "90", "5", "1001", "", "")
        self.assertIn("没有做任何修改", out)

    def test_05_学号不存在(self):
        out = self.run_script("1", "张三", "90", "5", "9999", "", "")
        self.assertIn("未找到该学号学生", out)
