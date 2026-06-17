# 辞書型で動物:最高時速を表したもの
animal_dict = {
    "ライオン": 58,
    "チーター": 110,
    "シマウマ": 60,
    "トナカイ": 80
}

# 時速で並び替えて表示
li = sorted(
    animal_dict.items(), 
    key=lambda x: x[1],
    reverse=True)
for name,speed in li:
    print(name, speed)

