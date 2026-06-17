# ダイアログを表示するために必要なモジュール --- (*1)
import TkEasyGUI as eg   # as についてはChapter4-1を参照

# ダイアログを表示 --- (*2)
ans = eg.popup_yes_no("ラーメンは好きですか？")
if ans == "Yes":
    # OKボタンがあるだけのダイアログを表示 --- (*3)
    eg.popup_ok("同意 - 僕も好きです。")
else:
    eg.popup_ok("本当？ - まさか、ラーメンが嫌いだなんて!")
