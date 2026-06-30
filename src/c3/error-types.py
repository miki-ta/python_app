s = input("体重を入力: ")
try:
    v = 100 / float(s)
    print(v)
except ValueError as e:
    print(e)
except ZeroDivisionError as e:
    print(e)
except Exception as e:
    print("その他のエラー:", e)

