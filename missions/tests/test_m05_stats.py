"""M05 验收：统计。

输出格式必须和任务书一致，否则测试读不出来。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import ScriptTest  # noqa: E402


class M05Stats(ScriptTest):
    def test_01_两个学生的统计(self):
        out = self.run_script("1", "甲", "90", "1", "乙", "55", "6")
        self.assertIn("人数:2", out)
        self.assertIn("平均分:72.5", out)
        self.assertIn("及格率:50.0%", out)
        self.assertIn("最高分:90", out)
        self.assertIn("最低分:55", out)

    def test_02_空库有提示(self):
        out = self.run_script("6")
        self.assertIn("系统中暂无学生成绩", out)

    def test_03_全及格(self):
        out = self.run_script("1", "甲", "60", "1", "乙", "80", "6")
        self.assertIn("及格率:100.0%", out)

    def test_04_平均分只保留一位小数(self):
        out = self.run_script("1", "甲", "90", "1", "乙", "80", "1", "丙", "70", "6")
        self.assertIn("平均分:80.0", out)
