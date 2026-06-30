# 素数を返すイテレータ
def genPrime(maxnum):
    num = 2
    while (num <= maxnum):
        is_prime = True
        for i in range(2, num):
            if (num % i) == 0: # 素数ではない
                is_prime = False
                break
        if (is_prime): yield num
        num += 1

# イテレータを得る
it = genPrime(50)
# 画面に出力
for i in it:
    print(i, end=",")

