# コールセンター勤怠管理システム

from datetime import datetime, timedelta

# ===== 定数設定 =====
BASE_HOURLY_WAGE = 1200  # 基本時給（円）
EARLY_SHIFT_START = 9  # 早番開始時刻
EARLY_SHIFT_END = 18  # 早番終了時刻
LATE_SHIFT_START = 12  # 遅番開始時刻
LATE_SHIFT_END = 21  # 遅番終了時刻
PREMIUM_START_TIME = 20  # 割増開始時刻
PREMIUM_RATE = 1.25  # 割増率

# ===== 従業員データ =====
# 実際のデータとして30名の従業員情報
employees = [
    {"id": f"E{i+1:03d}", "name": f"従業員{i+1}", "shift": "早番" if i % 2 == 0 else "遅番"}
    for i in range(30)
]

# ===== 関数群 =====

def calculate_work_hours(shift_type):
    """
    シフト種別から勤務時間を計算
    """
    if shift_type == "早番":
        return EARLY_SHIFT_END - EARLY_SHIFT_START
    elif shift_type == "遅番":
        return LATE_SHIFT_END - LATE_SHIFT_START
    else:
        return 0

def calculate_premium_hours(shift_type):
    """
    割増対象時間を計算（遅番で20時以降）
    """
    if shift_type == "遅番":
        return LATE_SHIFT_END - PREMIUM_START_TIME
    else:
        return 0

def calculate_regular_hours(shift_type):
    """
    割増対象外の時間を計算
    """
    total_hours = calculate_work_hours(shift_type)
    premium_hours = calculate_premium_hours(shift_type)
    return total_hours - premium_hours

def calculate_daily_wage(shift_type):
    """
    1日の給料を計算
    """
    regular_hours = calculate_regular_hours(shift_type)
    premium_hours = calculate_premium_hours(shift_type)
    
    regular_pay = regular_hours * BASE_HOURLY_WAGE
    premium_pay = premium_hours * BASE_HOURLY_WAGE * PREMIUM_RATE
    
    return regular_pay + premium_pay

def display_employee_info(employee):
    """
    従業員情報を表示
    """
    shift = employee["shift"]
    wage = calculate_daily_wage(shift)
    work_hours = calculate_work_hours(shift)
    
    if shift == "遅番":
        premium_hours = calculate_premium_hours(shift)
        regular_hours = calculate_regular_hours(shift)
        print(f"{employee['id']} | {employee['name']:8} | {shift:4} | "
              f"{work_hours}時間 ({regular_hours}h + 割増{premium_hours}h) | "
              f"¥{wage:,.0f}")
    else:
        print(f"{employee['id']} | {employee['name']:8} | {shift:4} | "
              f"{work_hours}時間 | ¥{wage:,.0f}")

def display_all_employees(employees):
    """
    全従業員の勤怠情報を表示
    """
    print("=" * 80)
    print("【コールセンター勤怠管理表】")
    print("=" * 80)
    print(f"基本時給: ¥{BASE_HOURLY_WAGE:,}/時")
    print(f"割増開始: {PREMIUM_START_TIME}:00")
    print(f"割増率: {PREMIUM_RATE}倍")
    print("=" * 80)
    print(f"{'ID':6} | {'名前':10} | {'シフト':6} | {'勤務時間':20} | {'日給':10}")
    print("-" * 80)
    
    for employee in employees:
        display_employee_info(employee)

def calculate_total_payroll(employees):
    """
    全従業員の総給料を計算
    """
    total = 0
    for employee in employees:
        daily_wage = calculate_daily_wage(employee["shift"])
        total += daily_wage
    return total

def count_shift_distribution(employees):
    """
    シフト別人数をカウント
    """
    early_count = sum(1 for e in employees if e["shift"] == "早番")
    late_count = sum(1 for e in employees if e["shift"] == "遅番")
    return early_count, late_count

def display_summary(employees):
    """
    集計サマリーを表示
    """
    print("\n" + "=" * 80)
    print("【集計サマリー】")
    print("=" * 80)
    
    early_count, late_count = count_shift_distribution(employees)
    total_payroll = calculate_total_payroll(employees)
    daily_early_wage = calculate_daily_wage("早番")
    daily_late_wage = calculate_daily_wage("遅番")
    
    print(f"総従業員数: {len(employees)}名")
    print(f"  ├─ 早番: {early_count}名 (日給 ¥{daily_early_wage:,.0f}/名)")
    print(f"  └─ 遅番: {late_count}名 (日給 ¥{daily_late_wage:,.0f}/名)")
    print(f"\n1日の総給料: ¥{total_payroll:,.0f}")
    print(f"月間給料（22日稼働想定）: ¥{total_payroll * 22:,.0f}")
    print("=" * 80)

def export_to_csv(employees, filename="勤怠管理表.csv"):
    """
    CSVファイルにエクスポート
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write("従業員ID,名前,シフト,基本給,割増給,日給\n")
        
        for employee in employees:
            shift = employee["shift"]
            regular_hours = calculate_regular_hours(shift)
            premium_hours = calculate_premium_hours(shift)
            
            regular_pay = regular_hours * BASE_HOURLY_WAGE
            premium_pay = premium_hours * BASE_HOURLY_WAGE * PREMIUM_RATE
            daily_wage = regular_pay + premium_pay
            
            f.write(f"{employee['id']},{employee['name']},{shift},"
                   f"{regular_pay:.0f},{premium_pay:.0f},{daily_wage:.0f}\n")
    
    print(f"\n✓ CSVファイルに保存しました: {filename}")

# ===== メイン処理 =====
if __name__ == "__main__":
    # 全従業員情報を表示
    display_all_employees(employees)
    
    # 集計サマリーを表示
    display_summary(employees)
    
    # CSVエクスポート
    export_to_csv(employees)