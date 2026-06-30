from PIL import Image, ImageOps
import TkEasyGUI as eg

# 画面レイアウトを定義 --- (*1)
layout = [
    [eg.Button("画像ファイルを選択")],  # 1行目
    [eg.Image(key="image1"), eg.Image(key="image2")],  # 2行目
]
# ウィンドウを作成してイベントループを開始 --- (*2)
window = eg.Window("画像ネガポジ反転ツール", layout)
while window.is_alive():
    # イベントを取得して処理 --- (*3)
    event, value = window.read()
    if event == "画像ファイルを選択": # ボタンをクリックした時
        # ファイル選択ダイアログを表示 --- (*4)
        image_file = eg.popup_get_file(title="画像ファイルを選択")
        # 画像ファイルを読み込む --- (*5)
        try:
            img = Image.open(image_file)
        except Exception as e:
            eg.popup_ok(f"画像ファイルを読み込めません\n{e}")
            continue
        # 画像をネガポジ反転して保存 --- (*6)
        inverted_img = ImageOps.invert(img.convert("RGB"))
        out_file = image_file + "-inverted.png"
        inverted_img.save(out_file)
        # 画像を左右に表示する --- (*7)
        window["image1"].update(data=img)
        window["image2"].update(data=inverted_img)
        eg.popup_ok(f"ネガポジ反転した画像を保存しました\n{out_file}")
