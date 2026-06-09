#BMI=体重（Kg）÷｛身長（ｍ）×身長（ｍ）｝
#BMI判定プログラム
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

#BMIの計算
height = height/100 #mに直す
bmi = weight/(height*height)
#BMIの値に応じて結果を分岐
result = ""   #これは 空文字列（何も入っていない文字列）を変数に代入 しています。
advice = ""   #これは 空文字列（何も入っていない文字列）を変数に代入 しています。
if bmi<18.5:
    result = "やせ型"
    advice = "やせ型です。栄養バランスの良い食事と適度な筋力トレーニングで体重を増やしましょう。"
elif bmi < 25:
    result = "標準型"
    advice = "標準型です。現在の生活習慣を続けつつ、運動とバランスの良い食事で体調管理を続けましょう。"
elif bmi < 30:
    result = "肥満（軽）型"
    advice = "肥満（軽）型です。有酸素運動を増やし、脂肪の多い食事を控えて少しずつ体重を落としましょう。"
else:
    result = "肥満（重）型"
    advice = "肥満（重）型です。医師や栄養士に相談し、適切な食事管理と運動習慣を取り入れて健康改善を目指しましょう。"
#結果を表示
print("BMI:" ,bmi)
print("判定：" ,result)
print("アドバイス：" ,advice)