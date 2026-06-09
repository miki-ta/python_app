# 時給計算プログラム

# 時給の入力 --- (*1)
while True:
    user = input("時給はいくらですか？(1100円以上を入力してください) ")
    try:
        jikyu = int(user)
        if jikyu >= 1100:
            break
        elif jikyu > 0:
            print("時給は1100円以上で入力してください。")
        else:
            print("正しい時給を入力してください。1100円以上の整数を入力してください。")
    except ValueError:
        print("数値を入力してください。")

# 時間の入力
while True:
    user = input("何時間働きましたか？ ")
    try:
        jikan = int(user)
        if jikan > 0:
            break
        elif jikan == 0:
            print("0より大きい値を入力してください。")
        else:
            print("正しい時間を入力してください。0以上の整数を入力してください。")
    except ValueError:
        print("数値を入力してください。")

# 平日／土日祝日の入力
while True:
    user = input("0=平日、1=土日祝日 を入力してください: ")
    try:
        shuku = int(user)
        if shuku == 0:
            break
        elif shuku == 1:
            break
        else:
            print("0 または 1 を入力してください。")
    except ValueError:
        print("数値を入力してください。")

# 計算 --- (*2)
if shuku == 0:
    kyuryou = jikyu * jikan
elif shuku == 1:
    kyuryou = int(jikyu * 1.25 * jikan)
else:
    # ここには本来到達しません。
    # 入力ループで 0 または 1 以外は受け付けないため、
    # もし何らかの理由で異常な値が入った場合の安全策です。
    print("エラー：平日/土日祝日の入力が正しくありません。")
    kyuryou = int(0)

# 結果を表示 --- (*3)
fmt = """
時給{0}円で、{1}時間働いたので...
給料は、{2}円です。
"""
desc = fmt.format(jikyu, jikan, kyuryou)
print(desc)

