# 型ヒントを指定してリストを定義 (定義のエラーあり)
price_list: list[int] = [
    1000,
    250,
    "#",  # エラーになる
    3000]
print(price_list)
