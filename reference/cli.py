"""界面层（View）：控制台版。

只做三件事：读输入、打印结果、把错误翻译成人话。
不含任何业务规则 —— 所以以后换成 GUI 时，这个文件整体被替换掉即可。
"""

from __future__ import annotations

import unicodedata

from models import ValidationError
from service import NotFoundError, StudentService

MENU = """
=== 学生成绩管理系统 v1.0 ===
 1) 查看全部     2) 搜索       3) 新增
 4) 修改         5) 删除       6) 统计
 0) 退出
"""


def pad(text: str, width: int) -> str:
    """按终端“显示宽度”补空格：中文/全角字符算 2 格。"""
    shown = sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)
    return text + " " * max(0, width - shown)


def render(students) -> None:
    if not students:
        print("（没有记录）")
        return
    print(
        pad("学号", 8) + pad("姓名", 12) + pad("平均分", 8)
        + pad("状态", 8) + "各科成绩"
    )
    print("-" * 72)
    for student in students:
        detail = "  ".join(f"{k}:{v:g}" for k, v in student.scores.items())
        status = "及格" if student.is_passing() else "不及格"
        print(
            pad(student.sid, 8) + pad(student.name, 12)
            + pad(f"{student.average():.2f}", 8) + pad(status, 8) + detail
        )


def parse_scores(text: str) -> dict[str, str]:
    """把 “数学=90,英语=80” 解析成字典；格式错误抛 ValidationError。"""
    scores: dict[str, str] = {}
    for chunk in text.replace("，", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise ValidationError(f"无法识别“{chunk}”，请用 科目=分数 的格式")
        subject, _, value = chunk.partition("=")
        scores[subject.strip()] = value.strip()
    if not scores:
        raise ValidationError("没有读到任何成绩")
    return scores


def _show_all(service: StudentService) -> None:
    render(service.all())


def _search(service: StudentService) -> None:
    render(service.search(input("学号或姓名关键字：")))


def _add(service: StudentService) -> None:
    name = input("姓名：")
    scores = parse_scores(input("成绩（如 数学=90,英语=80）："))
    student = service.add(name, scores)
    print(f"已新增 {student.sid} {student.name}")


def _update(service: StudentService) -> None:
    sid = input("要修改的学号：").strip()
    current = service.get(sid)  # 找不到会抛 NotFoundError，由外层统一提示
    print(f"当前：{current.name}  {current.scores}")

    name = input("新姓名（直接回车 = 不改）：").strip() or None
    raw = input("新成绩（如 数学=95，直接回车 = 不改）：").strip()
    scores = parse_scores(raw) if raw else None

    if name is None and scores is None:
        print("没有做任何修改")
        return
    student = service.update(sid, name=name, scores=scores)
    print(f"已更新：{student.name}，平均分 {student.average():.2f}")


def _delete(service: StudentService) -> None:
    sid = input("要删除的学号：").strip()
    target = service.get(sid)
    answer = input(f"确认删除 {target.sid} {target.name}？(y/N) ").strip().lower()
    if answer != "y":
        print("已取消")
        return
    service.remove(sid)
    print("已删除")


def _stats(service: StudentService) -> None:
    info = service.stats()
    if info["count"] == 0:
        print("（还没有数据）")
        return
    print(f"总人数：{info['count']}")
    print(f"总平均分：{info['avg']}    及格率：{info['pass_rate']}%")
    print("各科平均分：" + "  ".join(f"{k}:{v}" for k, v in info["subject_avg"].items()))
    sid, name, avg = info["best"]
    print(f"最高分：{sid} {name}  {avg}")


ACTIONS = {
    "1": _show_all,
    "2": _search,
    "3": _add,
    "4": _update,
    "5": _delete,
    "6": _stats,
}


def run(service: StudentService) -> None:
    while True:
        print(MENU)
        choice = input("请选择：").strip()
        if choice == "0":
            print("再见")
            return
        action = ACTIONS.get(choice)
        if action is None:
            print("没有这个选项，请重新选择")
            continue
        try:
            action(service)
        except (ValidationError, NotFoundError) as exc:
            print(f"[输入有误] {exc}")
        except (KeyboardInterrupt, EOFError):
            print()
            return
