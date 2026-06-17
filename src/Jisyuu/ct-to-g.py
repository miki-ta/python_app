#カラットからグラムbに変換するプログラム
#変換の元になる値
per_carat = 0.2
#ユーザーからカラットの値を入力してもらう
user = input("カラットを入力してください: ")
#浮動小数点に変換する
carat = float(user)
#グラムに変換する計算
gram = carat * per_carat
#結果を表示する
desc="{0}カラット={1}グラムです。".format(carat, gram)
print(desc)

