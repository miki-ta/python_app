# for 構文をフラグで分岐する場合
# 食材の一覧
foodstuff = ["Banana", "Mango", "Fish", "Carrot", "cabbage"]

# マンゴーがないか確認する
flag_found = False
for food in foodstuff:
    if food == "Mango":
        flag_found = True
        break

if flag_found:
    print("マンゴーが入ってます")
else:
    print("ありません。")


