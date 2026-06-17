# スーパーの割引計算

def calcValue(who, hour, count, value):
    '''あるスーパーの割引を計算する関数'''
    info = "割引なし"
    # 14時に商品を3つ以上で1割引
    if (hour == 14) and (count >= 3):
        value *= 0.9
        info = "1割引"
    # 15時に商品を5つ以上で2割引
    elif (hour == 15) and (count >= 5):
        value *= 0.8
        info = "2割引"
    # 結果を表示
    value = int(value)
    print("{0}さんは{1}={2}円".format(who, info, value))

# A/B/Cさん、それぞれの支払い金額を求める
calcValue("A", 15, 3, 1200)
calcValue("B", 14, 5, 2000)
calcValue("C", 15, 8, 5400)

