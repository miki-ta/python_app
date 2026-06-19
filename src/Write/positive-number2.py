#正の数、負の数、0を判定するプログラム
while True:
    try:
        num = int(input("数字を入力してください:"))
        break
    except ValueError:
        print("入力が正しくありません。もう一度入力してください。")
if num > 0:
    print("正の数です")
elif num == 0:
    print("ゼロです")
else:
    print("負の数です")  