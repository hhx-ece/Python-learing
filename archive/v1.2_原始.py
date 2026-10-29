# ============================================================
# 存档：student_score_system1.2.py 的原始版本（2026-10-27 提交的内容）
# 只读，不要在这里改。历史对照用。
#
# 注意：这份原始代码里的 f"学号:{s["id"]}" 只有 Python 3.12+ 能解析，
# 旧版本会报 SyntaxError: f-string: unmatched '['。
# 主体文件里已经改成单引号了。
# ============================================================

# 学生成绩管理系统1.2
students = []
next_id = 1001


def get_int(prompt):
    while True:
        try:
            num = int(input(prompt))
            return num
        except ValueError:
            print("你输入的并非数字，请重新输入")


# 添加学生成绩，并分配学号。
def add_student():
    global next_id
    student_add = {}
    student_add["id"] = next_id
    student_add["name"] = input("请输入学生的名字:",)
    student_add["score"] = get_int("请输入学生的分数:")
    students.append(student_add)
    print(f"该学生的学号为:{next_id}")
    next_id += 1


# 打印所有学生的成绩。
def show_students():
    if not students:
        print("没有学生成绩可被找到")
    else:
        for s in students:
            print("\n=============")
            print(f"学号:{s["id"]}")
            print(f"姓名:{s["name"]}")
            print(f"成绩:{s["score"]}")
            print("=============\n")


# 删除指定的学生，并生成新字典。
def delete_student():
    global students
    found = False
    student_id = get_int("请输入你要删除的学生学号:")

    if not students:
        print("系统中暂无学生成绩")
    else:
        for s in students:
            if s["id"] == student_id:
                found = True
        if found:
            for s in students:
                if s["id"] == student_id:
                    delete_choice = input(f"是否要删除{s["name"]}(y/n):")
            if delete_choice == "y":
                students = [s for s in students if s["id"] != student_id]
            else:
                return
        else:
            print("未找到该学号学生")


# 主函数
def main():
    while True:
        print("1.添加学生成绩")
        print("2.删除学生成绩")
        print("3.查看学生成绩")
        print("4.退出")
        menu = get_int("请输入你的操作指令:")
        if menu == 1:
            add_student()
        elif menu == 2:
            delete_student()
        elif menu == 3:
            show_students()
        elif menu == 4:
            break
        else:
            print("请输入特定数字")


if __name__ == "__main__":
    main()
