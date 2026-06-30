color = "green"
# if文で処理を分岐する
if color == "red":
    print("赤です。車を止めてください。")
elif color == "blue" or color == "green":
    print("青です。車を進めてください。")
elif color == "yellow":
    print("黄色です。注意して車を止めてください。")
else:
    print("その他の色です。色を確認し直しましょう。")
