# 30名のクラスメイトの点数データ
# 形式: [英語, 数学, 国語, 理科, 社会]
scores = [
    [85, 92, 78, 88, 80],      # 出席番号1
    [92, 88, 85, 91, 89],      # 出席番号2
    [78, 75, 81, 82, 79],      # 出席番号3
    [88, 95, 92, 93, 91],      # 出席番号4
    [81, 83, 79, 80, 77],      # 出席番号5
    [95, 90, 88, 92, 94],      # 出席番号6
    [73, 74, 76, 71, 75],      # 出席番号7
    [89, 87, 91, 85, 88],      # 出席番号8
    [82, 86, 84, 83, 85],      # 出席番号9
    [90, 91, 93, 89, 92],      # 出席番号10
    [79, 80, 77, 78, 76],      # 出席番号11
    [91, 93, 89, 94, 90],      # 出席番号12
    [84, 82, 86, 81, 83],      # 出席番号13
    [87, 88, 85, 86, 87],      # 出席番号14
    [76, 77, 74, 75, 72],      # 出席番号15
    [93, 95, 91, 96, 93],      # 出席番号16
    [80, 79, 82, 81, 78],      # 出席番号17
    [88, 85, 90, 87, 89],      # 出席番号18
    [85, 84, 87, 86, 85],      # 出席番号19
    [92, 91, 94, 93, 95],      # 出席番号20
    [77, 78, 75, 76, 74],      # 出席番号21
    [89, 90, 87, 91, 88],      # 出席番号22
    [83, 81, 85, 82, 84],      # 出席番号23
    [86, 87, 88, 85, 86],      # 出席番号24
    [75, 76, 73, 74, 71],      # 出席番号25
    [94, 96, 92, 95, 94],      # 出席番号26
    [81, 83, 80, 82, 79],      # 出席番号27
    [90, 88, 92, 89, 91],      # 出席番号28
    [84, 85, 86, 83, 87],      # 出席番号29
    [88, 91, 89, 90, 89],      # 出席番号30
]

# 全員の全科目の平均点を計算
total_sum = 0
total_count = 0

for student_scores in scores:
    for score in student_scores:
        total_sum += score
        total_count += 1

overall_average = total_sum / total_count

# 各科目ごとの平均点を計算
subjects = ["英語", "数学", "国語", "理科", "社会"]
subject_averages = []

for subject_idx in range(len(subjects)):
    subject_sum = sum(scores[student_idx][subject_idx] for student_idx in range(len(scores)))
    subject_average = subject_sum / len(scores)
    subject_averages.append(subject_average)

# 結果表示
print("=" * 60)
print("クラスの成績表")
print("=" * 60)

# 各生徒の成績と平均点を表示
print(f"\n{'出席番号':^6} | {'英語':^4} {'数学':^4} {'国語':^4} {'理科':^4} {'社会':^4} | {'平均':^6}")
print("-" * 60)

for i, student_scores in enumerate(scores, 1):
    student_average = sum(student_scores) / len(student_scores)
    scores_str = " ".join(f"{score:3d}" for score in student_scores)
    print(f"{i:^6} | {scores_str} | {student_average:6.2f}")

# 全員の平均点と科目ごとの平均点を表示
print("-" * 60)
print(f"{'全員平均':^6} | {' ' * 20} | {overall_average:6.2f}")
print("-" * 60)

# 科目ごとの平均点を表示
print(f"\n{'科目別平均点':^60}")
print("-" * 60)
for subject, avg in zip(subjects, subject_averages):
    print(f"{subject:^10}: {avg:6.2f}")
print("=" * 60)
