# 画面に線をたくさん描画する

# グラフィックライブラリを取り込む
from tkinter import *
# 画面の初期化
w = Canvas(Tk(), width=400, height=300)
w.pack()

# 線をたくさん引く
for i in range(100):
    y = i * 3
    if i % 2 == 0:
        c = "#ff0000" # red
    else:
        c = "#0000FF" # blue
    w.create_line(0, 0, 400, y, fill=c)

mainloop()
