# カラットからグラムに変換する
# 変換の元になる値
per_ct = 0.2
# ユーザーから入力を得る
user = input("何カラットですか？")
# 浮動小数点数に変換する
ct = float(user)
# 計算する
g = ct * per_ct
# 結果を表示
desc = "{0}カラット = {1}グラム".format(ct, g)
print(desc)

