"""业务层（Service）。

规则：所有“会改变数据”的操作都必须经过这里。
界面层（cli.py / gui.py）只能调用方法，不许自己改列表。

写操作统一走 _commit()：
    构造“新的完整列表” -> 先落盘 -> 成功后再替换内存
好处：磁盘和内存永远一致；写盘失败时内存不会莫名其妙变脏。
"""

from __future__ import annotations

from models import Student, normalize_name, normalize_scores
from storage import JsonRepository


class NotFoundError(LookupError):
    """按学号找不到人。"""


class StudentService:
    def __init__(self, repo: JsonRepository) -> None:
        self._repo = repo
        document = repo.load()
        self._students: list[Student] = [
            Student.from_dict(raw) for raw in document["students"]
        ]
        # 学号序号单独存：删掉 S002 之后，新同学依然拿 S003，不会“复活”旧学号。
        stored = document.get("next_seq")
        self._next_seq = int(stored) if stored else self._max_seq() + 1

    # ---------------- 读 ----------------
    def all(self) -> list[Student]:
        return list(self._students)  # 返回副本：外面 append 也污染不了内部状态

    def get(self, sid: str) -> Student:
        _, student = self._locate(sid)
        return student

    def search(self, keyword: str) -> list[Student]:
        key = keyword.strip().lower()
        if not key:
            return self.all()
        return [
            s for s in self._students
            if key in s.sid.lower() or key in s.name.lower()
        ]

    def stats(self) -> dict[str, object]:
        students = self._students
        if not students:
            return {"count": 0}

        subject_avg: dict[str, float] = {}
        for subject in sorted({k for s in students for k in s.scores}):
            values = [s.scores[subject] for s in students if subject in s.scores]
            subject_avg[subject] = round(sum(values) / len(values), 2)

        passing = [s for s in students if s.is_passing()]
        best = max(students, key=lambda s: s.average())
        return {
            "count": len(students),
            "avg": round(sum(s.average() for s in students) / len(students), 2),
            "pass_rate": round(len(passing) / len(students) * 100, 1),
            "subject_avg": subject_avg,
            "best": (best.sid, best.name, best.average()),
        }

    # ---------------- 写 ----------------
    def add(self, name: str, scores: dict[str, object]) -> Student:
        # 不盲信磁盘上的计数器：万一有人手改过文件，也要保证学号不撞车
        seq = max(self._next_seq, self._max_seq() + 1)
        student = Student(
            sid=f"S{seq:03d}",
            name=normalize_name(name),
            scores=normalize_scores(scores),
        )
        self._commit([*self._students, student], next_seq=seq + 1)
        return student

    def update(
        self,
        sid: str,
        *,
        name: str | None = None,
        scores: dict[str, object] | None = None,
    ) -> Student:
        index, old = self._locate(sid)

        merged = dict(old.scores)          # 注意：复制，不要直接改 old.scores
        if scores:
            merged.update(scores)          # 只覆盖传进来的科目，其余保留
        updated = Student(
            sid=old.sid,
            name=normalize_name(name if name is not None else old.name),
            scores=normalize_scores(merged),
        )

        new_list = list(self._students)
        new_list[index] = updated
        self._commit(new_list)             # 校验通过、落盘成功，才真正生效
        return updated

    def remove(self, sid: str) -> Student:
        _, target = self._locate(sid)
        # 正确姿势：重建一个新列表。绝不在遍历 _students 的同时删元素。
        # 用 target.sid 而不是原始 sid：调用方可能传了带空格的 " S001 "。
        self._commit([s for s in self._students if s.sid != target.sid])
        return target

    # ---------------- 内部工具 ----------------
    def _locate(self, sid: str) -> tuple[int, Student]:
        for index, student in enumerate(self._students):
            if student.sid == sid.strip():
                return index, student
        raise NotFoundError(f"学号 {sid} 不存在")

    def _max_seq(self) -> int:
        """现有学号里最大的数字部分，S001 -> 1。"""
        used = [
            int(s.sid[1:])
            for s in self._students
            if s.sid.startswith("S") and s.sid[1:].isdigit()
        ]
        return max(used, default=0)

    def _commit(self, students: list[Student], *, next_seq: int | None = None) -> None:
        seq = self._next_seq if next_seq is None else next_seq
        payload = {"next_seq": seq, "students": [s.to_dict() for s in students]}
        self._repo.save(payload)   # 1. 先落盘
        self._students = students  # 2. 再提交内存
        self._next_seq = seq
