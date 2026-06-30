# for 構文で else を記述する場合
# 食材の一覧
foodstuff = ["Banana", "Mango", "Fish", "Carrot", "cabbage"]

# マンゴーがないか確認する
for food in foodstuff:
    if food == "Mango":
        print("マンゴーが入っています")
        break
else:
    print("ありません")

