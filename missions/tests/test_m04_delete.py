"""M04 验收：删除。

确认、取消、大写 Y、删中间一个，四种情况都要对。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import ScriptTest  # noqa: E402


class M04Delete(ScriptTest):
    def test_01_输_y_删除(self):
        out = self.run_script("1", "张三", "90", "2", "1001", "y", "3")
        self.assertIn("没有学生成绩", out)
        self.assertNotIn("张三", out)

    def test_02_输_n_取消(self):
        out = self.run_script("1", "张三", "90", "2", "1001", "n", "3")
        self.assert_row(out, 1001, "张三", 90)

    def test_03_大写_Y_也算确认(self):
        out = self.run_script("1", "张三", "90", "2", "1001", "Y", "3")
        self.assertIn("没有学生成绩", out)

    def test_04_学号不存在(self):
        out = self.run_script("1", "张三", "90", "2", "9999")
        self.assertIn("未找到该学号学生", out)

    def test_05_删中间一个其余不受影响(self):
        out = self.run_script(
            "1", "张三", "90",
            "1", "李四", "80",
            "1", "王五", "70",
            "2", "1002", "y",
            "3",
        )
        self.assert_row(out, 1001, "张三", 90)
        self.assert_row(out, 1003, "王五", 70)
        self.assertNotIn("李四", out)
