# ===== 給与計算プログラム =====

print("=== 給与計算プログラム ===")

# --------------------
# 時給
# --------------------
while True:
    jikyu = int(input("時給を入力してください（1100円以上）："))
    if jikyu >= 1100:
        break
    else:
        print("エラー：時給は1100円以上で入力してください。")

# --------------------
# 1日の労働時間
# --------------------
while True:
    jikan = float(input("1日の労働時間を入力してください："))
    if jikan > 0:
        break
    else:
        print("エラー：0時間より大きい値を入力してください。")

# --------------------
# 勤務日数
# --------------------
while True:
    days = int(input("今月の勤務日数を入力してください："))
    if days > 0:
        break
    else:
        print("エラー：1日以上入力してください。")

# --------------------
# 今月の残業時間
# --------------------
while True:
    overtime_hours = float(input("今月の残業時間を入力してください："))
    if overtime_hours >= 0:
        break
    else:
        print("エラー：0時間以上入力してください。")

# --------------------
# 今月の深夜勤務時間
# --------------------
while True:
    shinya = float(input("今月の深夜勤務時間を入力してください："))
    if shinya >= 0:
        break
    else:
        print("エラー：0時間以上入力してください。")

# --------------------
# 休日出勤日数
# --------------------
while True:
    holiday_days = int(input("今月の休日出勤日数を入力してください："))
    if holiday_days >= 0:
        break
    else:
        print("エラー：0日以上入力してください。")

# --------------------
# 扶養家族人数
# --------------------
while True:
    kazoku = int(input("扶養家族人数を入力してください："))
    if kazoku >= 0:
        break
    else:
        print("エラー：0人以上入力してください。")

# --------------------
# 有給休暇取得日数
# --------------------
while True:
    paid_leave = int(input("有給休暇取得日数を入力してください："))
    if paid_leave >= 0:
        break
    else:
        print("エラー：0日以上入力してください。")

# --------------------
# 交通費
# --------------------
while True:
    tsukinhi = int(input("交通費を入力してください（円）："))
    if tsukinhi >= 0:
        break
    else:
        print("エラー：0円以上入力してください。")

# --------------------
# ボーナス
# --------------------
while True:
    bonus = int(input("ボーナスを入力してください（円）："))
    if bonus >= 0:
        break
    else:
        print("エラー：0円以上入力してください。")

# ====================
# 給与計算
# ====================

# 基本給
monthly_pay = jikyu * jikan * days

# 残業代（25%増し）
overtime_pay = jikyu * 1.25 * overtime_hours

# 深夜手当（25%増し）
shinya_teate = jikyu * 0.25 * shinya

# 休日出勤手当（35%増し）
holiday_teate = jikyu * jikan * 0.35 * holiday_days

# 家族手当
kazoku_teate = kazoku * 5000

# 有給休暇支給額
paid_pay = jikyu * 8 * paid_leave

# 総支給額
gross_pay = (
    monthly_pay
    + overtime_pay
    + shinya_teate
    + holiday_teate
    + kazoku_teate
    + paid_pay
    + tsukinhi
    + bonus
)

# 所得税の累進課税（例）
# 〜200,000円:5%, 200,000〜400,000円:10%, 400,000〜600,000円:15%, 600,000〜800,000円:20%, 800,000円〜:25%
remaining = gross_pay
tax = 0
brackets = [200000, 200000, 200000, 200000]
rates = [0.05, 0.10, 0.15, 0.20, 0.25]
for amount, rate in zip(brackets, rates):
    taxable = min(remaining, amount)
    tax += taxable * rate
    remaining -= taxable
    if remaining <= 0:
        break
if remaining > 0:
    tax += remaining * rates[-1]

# 社会保険料の累進課税（例）
# 〜250,000円:10%, 250,000〜500,000円:12%, 500,000円〜:15%
remaining = gross_pay
insurance = 0
brackets = [250000, 250000]
rates = [0.10, 0.12, 0.15]
for amount, rate in zip(brackets, rates):
    taxable = min(remaining, amount)
    insurance += taxable * rate
    remaining -= taxable
    if remaining <= 0:
        break
if remaining > 0:
    insurance += remaining * rates[-1]

# 手取り額
net_pay = gross_pay - tax - insurance

# ====================
# 結果表示
# ====================

print("\n===== 給与明細 =====")

print("時給：{:,.0f}円".format(jikyu))
print("勤務日数：{}日".format(days))
print("1日の労働時間：{}時間".format(jikan))
print("残業時間：{}時間".format(overtime_hours))

print("--------------------")

print("基本給：{:,.0f}円".format(monthly_pay))
print("残業代：{:,.0f}円".format(overtime_pay))
print("深夜手当：{:,.0f}円".format(shinya_teate))
print("休日出勤手当：{:,.0f}円".format(holiday_teate))
print("家族手当：{:,.0f}円".format(kazoku_teate))
print("有給休暇支給額：{:,.0f}円".format(paid_pay))
print("交通費：{:,.0f}円".format(tsukinhi))
print("ボーナス：{:,.0f}円".format(bonus))

print("--------------------")

print("総支給額：{:,.0f}円".format(gross_pay))
print("所得税：{:,.0f}円".format(tax))
print("社会保険料：{:,.0f}円".format(insurance))

print("--------------------")

print("手取り額：{:,.0f}円".format(net_pay))