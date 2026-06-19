# 【総合】成績管理システム - 複数の関数を組み合わせる 
def add_student(students, name, score):
    """
    学生を辞書で追加する
    """
    students[name] = score
    return students

def display_all_students(students):
    """全学生の成績を表示"""
    print("--- 成績一覧 ---")
    for name, score in students.items():
        grade = get_grade(score)
        print(f"{name}: {score}点 ({grade})")

def get_grade(score):
    """点数から成績を返す"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def get_top_student(students):
    """最高点の学生を返す"""
    if not students:
        return None
    return max(students.items(), key=lambda x: x[1])

def get_average_score(students):
    """平均点を計算する"""
    if not students:
        return 0
    scores = list(students.values())
    return sum(scores) / len(scores)

# 使用例
print("=== 成績管理システム ===\n")

students = {}
students = add_student(students, "太郎", 85)
students = add_student(students, "花子", 92)
students = add_student(students, "次郎", 78)
students = add_student(students, "美咲", 88)

display_all_students(students)

print(f"\n最高点: {get_top_student(students)[0]}さん ({get_top_student(students)[1]}点)")
print(f"平均点: {get_average_score(students):.1f}点")
