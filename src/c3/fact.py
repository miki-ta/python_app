# 階乗を求める
def fact(n):
    if n == 0: # 引数が0なら1を返す
        return 1
    else: # それ以外の場合、fact()を再帰的に呼び出す
        return n * fact(n-1)

print(fact(3))
print(fact(5))

