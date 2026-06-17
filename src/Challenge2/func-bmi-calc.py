# 【実践1】実用的な例：BMI計算機
def calculate_bmi(height, weight):
    """
    身長(m)と体重(kg)を受け取ってBMIを計算する
    戻り値: BMIの値
    """
    bmi = weight / (height ** 2)
    return bmi

def judge_bmi(bmi):
    """BMIの値を判定する"""
    if bmi < 18.5:
        return "低体重"
    elif bmi < 25:
        return "標準体重"
    elif bmi < 30:
        return "肥満（1度）"
    else:
        return "肥満（2度以上）"

# 使用例
height = 1.70
weight = 65

bmi = calculate_bmi(height, weight)
judgment = judge_bmi(bmi)

print(f"身長: {height}m")
print(f"体重: {weight}kg")
print(f"BMI: {bmi:.1f}")
print(f"判定: {judgment}")

print("\n--- 別の人 ---")
height2 = 1.60
weight2 = 50
bmi2 = calculate_bmi(height2, weight2)
print(f"身長: {height2}m, 体重: {weight2}kg")
print(f"BMI: {bmi2:.1f}, 判定: {judge_bmi(bmi2)}")
