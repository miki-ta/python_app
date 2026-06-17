#時給計算プログラム
#時給の入力
user=input("時給を入力してください:")
jikyu=int(user)

#勤務時間の入力
user=input("勤務時間を入力してください:")
jikan=int(user)

#給与の計算
kyuryou=jikyu*jikan

#給与の表示
fmt=""""
給与は{0}円で,{1}時間働きました。
給料は{2}円です。
"""
desc=fmt.format(jikyu,jikan,kyuryou)
print(desc)
