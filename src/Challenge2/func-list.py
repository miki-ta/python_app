# 【実践2】デフォルト引数とリスト処理
def print_info(name, age, city="東京"):
    """名前と年齢、そして都市を表示（都市はデフォルト値付き）"""
    print(f"{name}さんは{age}歳で、{city}に住んでいます。")

print_info("太郎", 25)
print_info("花子", 30, "大阪")
print_info("次郎", 28, "京都")

print("\n--- リストの合計を求める関数 ---")

def calculate_sum(numbers):
    """リストの合計を返す"""
    total = 0
    for num in numbers:
        total += num
    return total

def calculate_average(numbers):
    """リストの平均を返す"""
    if len(numbers) == 0:
        return 0
    return calculate_sum(numbers) / len(numbers)

scores = [85, 90, 78, 92, 88]
print(f"点数: {scores}")
print(f"合計: {calculate_sum(scores)}")
print(f"平均: {calculate_average(scores):.1f}")
