# BMI判定(例外処理あり版)
# ユーザーから正しい値を得てBMIを計算
while True:
    try:
        # 入力
        weight = float(input("体重(kg)は ? "))
        height = float(input("身長(cm)は ? "))
        # BMIの計算
        height = height / 100 # m に直す
        bmi = weight / (height * height)
        break
    except Exception as e:
        print("入力ミスがあります。再度入力してください。")
# bmiの値から結果を判定
result = ""
if bmi < 18.5:
    result = "痩せ型"
elif bmi < 25:
    result = "標準体重"
elif bmi < 30:
    result = "肥満(軽)"
else:
    result = "肥満(重)"
# 結果を表示
print("BMI :", bmi)
print("判定:", result)
