# 正規表現モジュールを取り込む
import re

# 単語の一覧
words = [
    "orange", "october", "octpus", 
    "order","banana", "baby", "busy"
]

# 正規表現のパターンに一致するものを画面に出力
pattern = r"oc.*"
print("ocで始まるパターン=", pattern)
for word in words:
    if re.match(pattern, word):
        print("-", word)

pattern = r"b.*y"
print("bで始まりyで終わるパターン=", pattern)
for word in words:
    if re.match(pattern, word):
        print("-", word)


