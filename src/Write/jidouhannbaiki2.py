#自動販売機のプログラム
#投入金額の確認
money = int(input("投入金額はいくらですか？："))
#itemの確認
print("0:コーラ(150円)")
print("1:お茶(120円)")
print("2:水(100円)")
#購入商品の確認
item = input("購入商品は？：")
#購入できるかの確認
if item == "0":
    name = "コーラ"
    price = 150
elif item == "1":
    name = "お茶"
    price = 120
elif item == "2":
    name = "水"
    price = 100
else:
    print("商品が存在しません")
    exit()
#おつりの判定
if money >= price:
    change = money - price
    print(f"購入商品は{name}です")
    print(f"おつりは{change}円です")
else:
    shortage = price - money 
    print("投入金額が不足してます")
    print(f"あと{shortage}円必要です")

    