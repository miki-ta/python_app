import math
# 型ヒント付きで税込み金額を計算する関数を定義
def add_tax(amount: int, tax_rate: float) -> int:
    tax: int = math.ceil(amount * tax_rate)
    return amount + tax

# 型ヒント付きで関数を呼び出す
amount: int = 10000
amount_with_tax: int = add_tax(amount, tax_rate=0.10)
print(f"税込み金額: {amount_with_tax}円")
