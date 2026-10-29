# 学生成绩管理系统 1.3
# 相比 1.2，只做了四件事：
#   1) 修掉只能在 Python 3.12+ 上运行的 f-string 写法
#   2) 补上「修改 / 查询 / 统计」
#   3) 分数和姓名的校验补全
#   4) 把 global 从 2 处减到 1 处
# 数据仍然只在内存里，关掉程序就没了 —— 这是 1.4 要解决的。

import unicodedata

students = []
next_id = 1001
PASS_LINE = 60


def width(text):
    """中文在终端里占 2 格。按显示宽度算，表格才不会歪。"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in str(text))


def pad(text, size):
    text = str(text)
    return text + " " * max(0, size - width(text))


def get_int(prompt, low=None, high=None):
    """读一个整数；可以顺便限定范围。非数字不会崩，只会重问。"""
    while True:
        try:
            num = int(input(prompt))
        except ValueError:
            print("你输入的并非整数，请重新输入")
            continue
        if low is not None and num < low:
            print(f"不能小于 {low}，请重新输入")
            continue
        if high is not None and num > high:
            print(f"不能大于 {high}，请重新输入")
            continue
        return num


def get_name():
    while True:
        name = input("请输入学生的名字:").strip()
        if name:
            return name
        print("名字不能为空")


def find_student(student_id):
    """按学号找人：找到返回那个字典，找不到返回 None。"""
    for s in students:
        if s["id"] == student_id:
            return s
    return None


def add_student():
    global next_id
    name = get_name()
    score = get_int("请输入学生的分数:", 0, 100)
    students.append({"id": next_id, "name": name, "score": score})
    print(f"该学生的学号为:{next_id}")
    next_id += 1


def print_list(records):
    """把一批学生打印成表格。数据从参数来，所以查询结果也能用它。"""
    if not records:
        print("没有学生成绩可被找到")
        return
    print(pad("学号", 8) + pad("姓名", 14) + pad("成绩", 8) + "状态")
    print("-" * 36)
    for s in records:
        status = "及格" if s["score"] >= PASS_LINE else "不及格"
        print(pad(s["id"], 8) + pad(s["name"], 14) + pad(s["score"], 8) + status)


def show_students():
    print_list(students)


def search_student():
    keyword = input("输入学号或姓名关键字:").strip()
    if not keyword:
        print("关键字不能为空")
        return
    result = [
        s for s in students
        if keyword in s["name"] or keyword == str(s["id"])
    ]
    print_list(result)


def update_student():
    student_id = get_int("请输入要修改的学生学号:")
    target = find_student(student_id)
    if target is None:
        print("未找到该学号学生")
        return

    print(f"当前：{target['name']}  成绩 {target['score']}")
    new_name = input("新名字（直接回车表示不改）:").strip()
    raw_score = input("新成绩（直接回车表示不改）:").strip()

    # 先把两个输入都校验完，再动数据。
    # 如果边改边校验，姓名改了、分数非法，就会留下改了一半的记录。
    new_score = None
    if raw_score:
        try:
            new_score = int(raw_score)
        except ValueError:
            print("成绩必须是整数，本次修改取消")
            return
        if not 0 <= new_score <= 100:
            print("成绩必须在 0~100 之间，本次修改取消")
            return

    if not new_name and new_score is None:
        print("没有做任何修改")
        return

    if new_name:
        target["name"] = new_name
    if new_score is not None:
        target["score"] = new_score
    print("修改成功")


def delete_student():
    student_id = get_int("请输入你要删除的学生学号:")
    target = find_student(student_id)
    if target is None:
        print("未找到该学号学生")
        return

    answer = input(f"确认删除 {target['name']}（学号 {target['id']}）吗？(y/N):")
    if answer.strip().lower() != "y":
        print("已取消")
        return

    # 先找到「那个对象」，再删它。不是边遍历边删。
    # 原地 remove 还有一个好处：不需要 global students。
    students.remove(target)
    print("已删除")


def show_stats():
    if not students:
        print("系统中暂无学生成绩")
        return
    scores = [s["score"] for s in students]
    passed = [x for x in scores if x >= PASS_LINE]
    best = max(students, key=lambda s: s["score"])
    print(f"人数：{len(students)}")
    print(f"平均分：{sum(scores) / len(scores):.1f}")
    print(f"最高分：{max(scores)}    最低分：{min(scores)}")
    print(f"及格率：{len(passed) / len(scores) * 100:.1f}%")
    print(f"最高分学生：{best['name']}（{best['score']}）")


MENU = """
1. 添加学生成绩
2. 删除学生成绩
3. 查看学生成绩
4. 查询学生
5. 修改学生成绩
6. 成绩统计
0. 退出
"""

# 把「数字 → 函数」存成表，主循环就不用一长串 if/elif。
# 这张表就是以后 GUI 里「按钮 → 槽函数」的同一件事。
ACTIONS = {
    1: add_student,
    2: delete_student,
    3: show_students,
    4: search_student,
    5: update_student,
    6: show_stats,
}


def main():
    while True:
        print(MENU)
        try:
            choice = get_int("请输入你的操作指令:", 0, 6)
            if choice == 0:
                print("再见")
                return
            ACTIONS[choice]()
        except (KeyboardInterrupt, EOFError):
            print("\n已退出")
            return


if __name__ == "__main__":
    main()
