# 関数を定義
def mul_func(a, b):
    return a * b

def div_func(a, b):
    return a / b

# mul_func関数を変数に代入 --- (*1)
func = mul_func
# 代入した変数で関数を使う --- (*2)
result = func(2, 3)
print(result) # 表示結果→ 6

# div_func関数を変数に代入する場合 --- (*3)
func2 = div_func
result = func2(10, 5)
print(result) # 表示結果→ 2.0



