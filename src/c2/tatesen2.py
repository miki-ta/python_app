# 赤と青の線を交互に100本引く

# グラフィックライブラリを取り込む
from tkinter import *
# 画面の初期化
w = Canvas(Tk(), width=900, height=400)
w.pack()

# 線の色を交互にたくさん引く ---- (*1)
for i in range(100):
    x = i * 9 
    if i % 2 == 0:
        c = "#ff0000"
    else:
        c = "#0000FF"
    w.create_line(x, 0, x, 400, fill=c)

mainloop()

