#BMI×体脂肪率　結果判定プログラム
while True:
    try:
        weight = float(input("体重(kg)は？"))
    except ValueError:
        print("数値を入力してください。")
        continue
    if weight <= 0:
        print("体重は0より大きい値を入力してください。")
        continue
    if weight < 20 or weight > 300:
        print("体重が異常値です。正しい値を入力してください。")
        continue
    break

while True:
    try:
        height = float(input("身長(cm)は？"))
    except ValueError:
        print("数値を入力してください。")
        continue
    if height <= 0:
        print("身長は0より大きい値を入力してください。")
        continue
    if height < 50 or height > 250:
        print("身長が異常値です。正しい値を入力してください。")
        continue
    break

while True:
    try:
        body_fat = float(input("体脂肪率(%)は？"))
    except ValueError:
        print("数値を入力してください。")
        continue
    if body_fat < 0:
        print("体脂肪率は0以上の値を入力してください。")
        continue
    if body_fat > 70:
        print("体脂肪率が異常値です。正しい値を入力してください。")
        continue
    break

#BMIの計算
height = height/100 #mに直す
bmi = weight/(height*height)
#BMIと体脂肪率の値に応じて結果を分岐
result = ""   #これは 空文字列（何も入っていない文字列）を変数に代入 しています。
advice = ""   #これは 空文字列（何も入っていない文字列）を変数に代入 しています。
if bmi < 18.5:
    result = "やせ型"
    advice = "やせ型です。栄養バランスの良い食事と適度な筋力トレーニングで健康的に体重を増やしましょう。"
elif bmi < 25:
    result = "標準型"
    if body_fat >= 25:
        advice = "標準型ですが体脂肪率が高めです。筋力トレーニングと脂質・糖質を控えた食事で体脂肪を減らしましょう。"
    else:
        advice = "標準型です。体脂肪率も維持できるよう、運動とバランスの良い食事を続けましょう。"
elif bmi < 30:
    result = "肥満（軽）型"
    if body_fat >= 30:
        advice = "肥満（軽）型で体脂肪率も高めです。有酸素運動と食事管理で脂肪を落とし、筋肉量を増やしましょう。"
    else:
        advice = "肥満（軽）型です。脂肪の多い食事を控え、運動習慣を整えて健康的に体重を落としましょう。"
else:
    result = "肥満（重）型"
    if body_fat >= 35:
        advice = "肥満（重）型で体脂肪率も高いです。医師や栄養士に相談し、適切な食事管理と運動習慣で改善を目指しましょう。"
    else:
        advice = "肥満（重）型です。医師と相談して無理のない運動と食事管理で健康改善を進めましょう。"
#結果を表示
print("BMI:", round(bmi, 1))  #round() は数値を丸める関数です。BMIを小数第1位まで表示する という意味です。
print(f"体脂肪率: {body_fat:.1f}%") #体脂肪率を小数第1位まで表示し、最後に % を付ける という意味です。
print("判定：", result)
print("アドバイス：", advice)