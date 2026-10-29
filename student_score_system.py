# 学生成绩管理系统 —— 项目主体（唯一要改的文件）
# 任务书：missions/README.md    验收：cd missions; python -m unittest discover -s tests -v

# 学生成绩管理系统1.2
students = []
next_id = 1001


def get_int(prompt,low = None,high = None):
    while True:
        try:
            num = int(input(prompt))
        except ValueError:
            print("你输入的并非数字，请重新输入")
            continue
        if low is not None and num < low:
            print(f"输入的数字不能小于{low}")
            continue
        if high is not None and num > high:
            print(f"输入的数字不能大于{high}")
            continue
        return num

def get_name(prompt):
    while True:
        name = input(prompt)
        if name.strip():
            return name.strip()
        print("名字不能为空")


# 添加学生成绩，并分配学号。
def add_student():
    global next_id
    student_add = {}
    student_add["id"] = next_id
    student_add["name"] = get_name("请输入学生的名字:")
    student_add["score"] = get_int("请输入学生的分数:",0,100)
    students.append(student_add)
    print(f"该学生的学号为:{next_id}")
    next_id += 1

def find_student(student_id):
    for s in students:
        if s["id"] == student_id:
            return s
    return None


# 打印所有学生的成绩。
def show_students():
    if not students:
        print("没有学生成绩可被找到")
    else:
        print_list(students)

def print_list(records):
    print("学号  名字  分数")
    for s in records:
        print(f"{s['id']}  {s['name']}  {s['score']}")

def search_student():
    while True:
        key = input("请输入学号或姓名")
        if key.strip():
            records = [s for s in students if key.strip() in s["name"] or key.strip() == str(s["id"])]
            if records:
                print_list(records)
                return
            print("没有找到符合条件的学生")
            return
        print("输入不能为空")

# 删除指定的学生，并生成新字典。
def delete_student():
    student_id = get_int("请输入你要删除的学生学号:",1000,9999)
    target = find_student(student_id)
    if not target:
        print("未找到该学号学生")
        return
    
    answer = input(f"是否删除学生{target['name']}(学号为{target['id']})(y/N)")
    if answer.strip().lower() != "y":
        print("已取消")
        return

    students.remove(target)
    print("已删除")


# 主函数
def main():
    while True:
        print("1.添加学生成绩")
        print("2.删除学生成绩")
        print("3.查看学生成绩")
        print("4.查询学生成绩")
        print("5.修改学生成绩")
        print("6.统计学生成绩")
        print("0.退出")
        menu = get_int("请输入你的操作指令:",0,6)
        if menu == 1:
            add_student()
        elif menu == 2:
            delete_student()
        elif menu == 3:
            show_students()
        elif menu == 4:
            search_student()
        elif menu == 5:
            print("该功能正在开发中")
            continue
        elif menu == 6:
            print("该功能正在开发中")
            continue
        if menu == 0:
            break


if __name__ == "__main__":
    main()
