"""数据模型层（Model）。

只回答两个问题：
1. 一个“学生”由哪些数据构成？
2. 什么才算合法的数据？

这一层刻意不 import json / os / input。
好处：它永远能被单独测试，也永远不会关心“数据存哪里、界面长什么样”。
"""

from __future__ import annotations

from dataclasses import dataclass, field

PASS_LINE = 60.0


class ValidationError(ValueError):
    """用户输入不合法 —— 可恢复错误：提示一下，让用户重填即可。"""


def normalize_name(name: str) -> str:
    """校验并清洗姓名；不合法就抛 ValidationError。"""
    text = (name or "").strip()
    if not text:
        raise ValidationError("姓名不能为空")
    if len(text) > 20:
        raise ValidationError("姓名最多 20 个字符")
    return text


def normalize_scores(scores: dict[str, object]) -> dict[str, float]:
    """把“用户输入的脏数据”变成“干净的成绩字典”。

    注意：函数返回一个新 dict，绝不修改传入的 scores。
    （修改别人传进来的可变对象，是后面最难查的 bug 之一。）
    """
    if not scores:
        raise ValidationError("至少录入一门成绩")

    cleaned: dict[str, float] = {}
    for subject, value in scores.items():
        subject = str(subject).strip()
        if not subject:
            raise ValidationError("科目名不能为空")
        try:
            score = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            raise ValidationError(f"{subject} 的成绩必须是数字") from None
        # 注意 NaN：0 <= nan <= 100 为 False，所以这里会正确拒绝 nan
        if not 0.0 <= score <= 100.0:
            raise ValidationError(f"{subject} 的成绩必须在 0~100 之间")
        cleaned[subject] = round(score, 1)
    return cleaned


@dataclass
class Student:
    sid: str
    name: str
    scores: dict[str, float] = field(default_factory=dict)

    def average(self) -> float:
        if not self.scores:
            return 0.0
        return round(sum(self.scores.values()) / len(self.scores), 2)

    def is_passing(self) -> bool:
        return bool(self.scores) and self.average() >= PASS_LINE

    def to_dict(self) -> dict[str, object]:
        return {"sid": self.sid, "name": self.name, "scores": dict(self.scores)}

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> "Student":
        if not isinstance(raw, dict):
            raise ValidationError("学生记录必须是一个对象")
        try:
            sid = str(raw["sid"]).strip()
            name = str(raw["name"])
        except KeyError as exc:
            raise ValidationError(f"学生记录缺少字段：{exc}") from exc
        if not sid:
            raise ValidationError("学号不能为空")
        return cls(sid=sid, name=name, scores=normalize_scores(dict(raw.get("scores") or {})))
