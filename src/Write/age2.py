# 年齢判定プログラム
while True:
    try:
        age = int(input("年齢は？："))
        if age >= 0:
            break
    
        if age < 0:
            print("年齢は0以上を入力してください。もう一度入力してください。")
            
    except ValueError:
        print("入力が正しくありません。整数で入力してください。")

if age >= 18:
    print("成人です")
else:
    print("未成年です")
    