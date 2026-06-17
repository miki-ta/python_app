import TkEasyGUI as eg

# 画面レイアウトを定義 --- (*1)
layout = [
    [eg.Text("興味のあるジャンルを選んでください。")], # 一行目に配置するパーツ
    [eg.Button("人間関係"), eg.Button("お金"), eg.Button("健康")], # 二行目
]
# ウィンドウを作成 --- (*2)
window = eg.Window("役立つ格言", layout)
# イベントループ --- (*3)
while window.is_alive():
    # イベントを繰り返し取得 --- (*4)
    event, value = window.read()
    # 押したボタンのラベルがeventに入るので分岐 --- (*5)
    if event == "人間関係":
        eg.popup_ok("受けるより与える方が幸福である")
    elif event == "お金":
        eg.popup_ok("お金は身の守りになるが知識や知恵は人の命を保たせる")
    elif event == "健康":
        eg.popup_ok("喜びにあふれた心は良い薬になる")


