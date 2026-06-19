#偶数、奇数判定プログラム
while True:
    try:
        num = int(input("数字を入力してください"))
        break
    except ValueError:
        print("入力が正しくありません。整数を入力してください。")

if num % 2 == 0:
    print("偶数です")
else:
    print("奇数です")
    
