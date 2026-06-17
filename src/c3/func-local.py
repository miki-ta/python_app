
# 関数の外側でvalueに100を代入
value = 100

def changeValue():
    # 関数の内側でvalueを変更
    value = 20

changeValue()
print("value=",value) # <--- はたしてこの値は？
