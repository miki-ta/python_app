import math

# 花の単価
rose_v = 500
sun_v = 400
tulip_v = 700

# 本数入力
while True:
    try:
        rose_c = int(input("バラは何本買いますか？："))
        sun_c = int(input("ひまわりは何本買いますか？："))
        tulip_c = int(input("チューリップは何本買いますか？："))

        if rose_c < 0 or sun_c < 0 or tulip_c < 0:
            print("エラー：本数は0以上で入力してください。")
            continue

        if rose_c + sun_c + tulip_c == 0:
            print("エラー：1本以上購入してください。")
            continue

        break

    except ValueError:
        print("エラー：整数を入力してください。")

# 購入時刻入力
while True:
    try:
        jikan = int(input("購入時刻（9～22）を入力してください："))

        if jikan < 9 or jikan > 22:
            print("エラー：9～22の範囲で入力してください。")
            continue

        break

    except ValueError:
        print("エラー：整数を入力してください。")

# 合計本数
sum_c = rose_c + sun_c + tulip_c

# 合計金額
sum_v = (
    rose_v * rose_c +
    sun_v * sun_c +
    tulip_v * tulip_c
)

# 割引率
if sum_c >= 20 and jikan >= 18:
    rate = 0.85
    discount_name = "大量購入＋夜間割引"
elif sum_c >= 20:
    rate = 0.95
    discount_name = "大量購入割引"
elif jikan >= 18:
    rate = 0.90
    discount_name = "夜間割引"
else:
    rate = 1.00
    discount_name = "割引なし"

# 支払い金額
payment = sum_v * rate
discount = sum_v - payment

# 税込み金額
tax_rate = 0.10
tax = math.ceil(payment * tax_rate)
price_with_tax = int(payment) + tax

# 結果表示
print("\n===== お買い上げ明細 =====")
print(f"バラ　　　　{rose_c}本")
print(f"ひまわり　　{sun_c}本")
print(f"チューリップ{tulip_c}本")
print("--------------------")
print(f"合計本数　　{sum_c}本")
print(f"合計金額　　{sum_v:,}円")
print(f"適用割引　　{discount_name}")
print(f"割引額　　　{int(discount):,}円")
print(f"支払金額　　{int(payment):,}円")
print(f"税込金額　　{price_with_tax:,}円")