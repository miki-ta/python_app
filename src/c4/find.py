# テキストからキーワードを探す
key = "find"
with open("mt7_7.txt", encoding="utf-8") as tf:
    # 一行ずつファイルを読む
    for i, line in enumerate(tf):
        # 文字列 key が行に含まれるか？
        if line.find(key) >= 0:
            print(i+1, ":", line)

