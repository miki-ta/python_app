# 年齢判定プログラム 繰り返し文法
while True:
    try:
        age = int(input("年齢は？："))
        break
    except ValueError:
        print("入力が正しくありません。")
if age >= 18:
    print("成人です")
else:
    print("未成年です")
    