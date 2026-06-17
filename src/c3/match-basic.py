color = "green"
# match文で処理を分岐する
match color:
    case "red":
        print("赤です。車を止めてください。")
    case "blue" | "green":
        print("青です。車を進めてください。")
    case "yellow":
        print("黄色です。注意して車を止めてください。")
    case _:
        print("その他の色です。色を確認し直しましょう。")
