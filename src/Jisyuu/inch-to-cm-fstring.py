#f文字列を使ってインチをセンチメートルに変換
per_inch = 2.54
inch = 24
cm = inch * per_inch
#文字列で説明を加える
desk=f"{inch}インチ={cm}センチメートルです"
print(desk)