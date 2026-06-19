# 【基本3】戻り値を返す関数 - 計算結果を返す 
def add_numbers(a, b):
    """2つの数を足した結果を返す"""
    return a + b

result = add_numbers(5, 3)
print(f"5 + 3 = {result}")

# 戻り値を直接表示
print(f"10 + 20 = {add_numbers(10, 20)}")

# 複数の計算関数
def multiply(a, b):
    """掛け算の結果を返す"""
    return a * b

def divide(a, b):
    """割り算の結果を返す"""
    if b == 0:
        return "ゼロでは割れません"
    return a / b

print(f"4 × 6 = {multiply(4, 6)}")
print(f"15 ÷ 3 = {divide(15, 3)}")
print(f"10 ÷ 0 = {divide(10, 0)}")
