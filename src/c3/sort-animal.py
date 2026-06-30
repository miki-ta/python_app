# (動物,最高時速)のリスト（各要素はタプルで作成）
animal_list = [
    ("ライオン", 58),
    ("チーター", 110),
    ("シマウマ", 60),
    ("トナカイ", 80),
]

# 足の速い順に並び替える
faster_list = sorted(
    animal_list, 
    key = lambda ani : ani[1], 
    reverse = True)

# 結果を表示
for i in faster_list: print(i)

