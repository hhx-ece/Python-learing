"""阶段一的自测：把“我以为的逻辑”变成“机器每次都会检查的逻辑”。

运行：cd reference && python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import sys
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BASE = Path(__file__).resolve().parents[1]
TMP_DIR = BASE / ".tests-tmp"

from models import ValidationError  # noqa: E402
from service import NotFoundError, StudentService  # noqa: E402
from storage import JsonRepository, StorageError  # noqa: E402


class StudentServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        TMP_DIR.mkdir(exist_ok=True)
        self.path = TMP_DIR / f"students-{uuid.uuid4().hex}.json"
        self.repo = JsonRepository(self.path)
        self.service = StudentService(self.repo)

    def tearDown(self) -> None:
        for leftover in TMP_DIR.glob(self.path.name + "*"):
            leftover.unlink(missing_ok=True)

    def test_add_assigns_sequential_ids(self) -> None:
        a = self.service.add("张三", {"数学": 90})
        b = self.service.add("李四", {"数学": 70})
        self.assertEqual((a.sid, b.sid), ("S001", "S002"))

    def test_data_survives_restart(self) -> None:
        self.service.add("张三", {"数学": 90, "英语": 80})
        restarted = StudentService(JsonRepository(self.path))
        self.assertEqual([s.name for s in restarted.all()], ["张三"])
        self.assertEqual(restarted.get("S001").scores["英语"], 80.0)

    def test_update_only_touches_given_subject(self) -> None:
        self.service.add("张三", {"数学": 90, "英语": 80})
        updated = self.service.update("S001", scores={"英语": 95})
        self.assertEqual(updated.scores, {"数学": 90.0, "英语": 95.0})
        self.assertEqual(updated.name, "张三")

    def test_invalid_update_keeps_data_unchanged(self) -> None:
        self.service.add("张三", {"数学": 90})
        with self.assertRaises(ValidationError):
            self.service.update("S001", scores={"数学": 120})
        self.assertEqual(self.service.get("S001").scores["数学"], 90.0)
        self.assertEqual(StudentService(JsonRepository(self.path)).get("S001").scores["数学"], 90.0)

    def test_remove_middle_rebuilds_list(self) -> None:
        for name in ("A", "B", "C"):
            self.service.add(name, {"数学": 60})
        self.service.remove("S002")
        self.assertEqual([s.sid for s in self.service.all()], ["S001", "S003"])
        with self.assertRaises(NotFoundError):
            self.service.get("S002")

    def test_remove_accepts_padded_sid(self) -> None:
        self.service.add("A", {"数学": 60})
        self.service.remove("  S001  ")
        self.assertEqual(self.service.all(), [])

    def test_removed_id_is_not_reused(self) -> None:
        self.service.add("A", {"数学": 60})
        self.service.add("B", {"数学": 60})
        self.service.remove("S002")
        self.assertEqual(self.service.add("C", {"数学": 60}).sid, "S003")

    def test_all_returns_copy(self) -> None:
        self.service.add("A", {"数学": 60})
        self.service.all().append("hacked")
        self.assertEqual(len(self.service.all()), 1)

    def test_search_by_name_and_id(self) -> None:
        self.service.add("张三", {"数学": 90})
        self.service.add("张伟", {"数学": 80})
        self.service.add("李四", {"数学": 70})
        self.assertEqual(len(self.service.search("张")), 2)
        self.assertEqual(self.service.search("s002")[0].name, "张伟")

    def test_stats(self) -> None:
        self.service.add("A", {"数学": 100})
        self.service.add("B", {"数学": 50})
        info = self.service.stats()
        self.assertEqual(info["count"], 2)
        self.assertEqual(info["pass_rate"], 50.0)
        self.assertEqual(info["subject_avg"], {"数学": 75.0})

    def test_corrupt_file_is_backed_up_and_reported(self) -> None:
        self.path.write_text("{ 这不是 json", encoding="utf-8")
        with self.assertRaises(StorageError):
            StudentService(JsonRepository(self.path))
        self.assertTrue(Path(str(self.path) + ".corrupt").exists())

    def test_saved_file_is_readable_utf8_json(self) -> None:
        self.service.add("张三", {"数学": 90})
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], 1)
        self.assertIn("张三", self.path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
