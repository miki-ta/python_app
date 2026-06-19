# 自動販売機のプログラム

#投入金額
money = int(input("投入金額を入力して下さい。："))

#商品選択
print("0:コーラ(150円)")
print("1:お茶(120円)")
print("2:水(100円)")

item = input("商品を選んで下さい。：")

#商品と値段の決定
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
    print("商品が存在しません。")
    exit()
    
#購入判定
if money >= price:
    change = money - price
    print(f"{name}を購入しました。")
    print(f"おつりは{change}円です。")
else:
    shortage = price - money
    print("お金が足りません。")
    print(f"あと{shortage}円必要です。")
    

