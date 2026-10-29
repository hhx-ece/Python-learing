"""M06 验收：持久化。

三次启动：加人 → 重启还能看到 → 再启动学号不重置。
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import ScriptTest  # noqa: E402


class M06Persist(ScriptTest):
    def test_01_数据文件被创建且是合法JSON(self):
        self.run_script("1", "张三", "90")
        self.assertTrue(self.data_file.exists(), "没有生成 students.json")
        raw = self.data_file.read_text(encoding="utf-8")
        json.loads(raw)                      # 不是合法 JSON 会在这里抛异常
        self.assertIn("张三", raw, "中文被转义了，检查 ensure_ascii=False")

    def test_02_重启后数据还在(self):
        self.run_script("1", "张三", "90")
        out = self.run_script("3")           # 第二次启动，只查看
        self.assertIn("张三", out)
        self.assertIn("90", out)

    def test_03_重启后学号不重置(self):
        first = self.run_script("1", "张三", "90")
        self.assertIn("该学生的学号为:1001", first)
        second = self.run_script("1", "李四", "80")
        self.assertIn("该学生的学号为:1002", second)

    def test_04_改完注销再启动_改的东西还在(self):
        self.run_script("1", "张三", "90")
        self.run_script("5", "1001", "", "77")
        out = self.run_script("3")
        self.assertIn("77", out)
