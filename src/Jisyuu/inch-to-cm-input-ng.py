#入力を得てインチをセンチメートルに変換
#変換の元となる値
per_inch = 2.54
#ユーザからインチの値を入力してもらう
inch = input("インチを入力してください: ")
#計算
cm = inch* per_inch
#結果を表示
desk="{0}inch={1}cm".format(inch,cm)
print(desk)
