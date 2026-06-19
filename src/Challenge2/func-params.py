# 【基本2】パラメータ付き関数 - 値を受け取る 
def greet_person(name):
    """名前を受け取って挨拶する"""
    print(f"こんにちは、{name}さん！")

greet_person("太郎")
greet_person("花子")

# 複数のパラメータ
def add_numbers(a, b):
    """2つの数字を足して表示する"""
    result = a + b
    print(f"{a} + {b} = {result}")

add_numbers(5, 3)
add_numbers(10, 20)
