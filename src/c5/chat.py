import os, time, json
from flask import Flask, request, redirect
from markupsafe import Markup

# チャットログの保存ファイル
SAVE_FILE = os.path.join(os.path.dirname(__file__), "chat_log.json")

# Flaskのオブジェクトを作成 --- (*1)
app = Flask(__name__)

# ルートにアクセスした時--- (*2)
@app.route("/")
def index():
    # チャットログを読んでHTMLを生成 --- (*3)
    logs = ""
    for c in reversed(read_chat_log()):
        name, body = Markup(c["name"]), Markup(c["body"]) # エスケープ処理
        logs += f"<div class='box'><span class='name'>{name}</span>: "
        logs += f"{body} <span class='date'>({c['date']})</span></div>"
    # CSSの定義 --- (*4)
    css = """
        h1 { background-color: #eef; color: black; padding: 1em; }
        .blue { background-color: #eef; }
        .box { border-bottom:1px solid gray; padding: 1em; margin: 1em; }
        .name { font-weight: bold; color: blue; background-color: #ff3; }
        .date { font-size:0.8em; color: gray; } """
    # フォームの定義 --- (*5)
    form = """
        <form action="/write">
            名前: <input type="text" name="name" value="" size="8">
            内容: <input type="text" name="body" value="" size="30">
            <input type="submit" value="発言">
        </form> """
    # HTMLにチャットログ埋め込んで表示 --- (*6)
    return f"""
        <html><meta charset="UTF-8"><style>{css}</style><body>
            <h1>チャット</h1>
            <div class="box blue">{form}</div>
            <div>{logs}</div>
        </body></html>
    """

# /write にアクセスした時の処理 --- (*7)
@app.route("/write")
def write():
    # パラメータを取得 --- (*8)
    name = request.args.get("name")
    body = request.args.get("body")
    # パラメータを検証 ---- (*9)
    if name is None or name == "" or body == "":
        return redirect("/")
    # チャットログに追記してファイルに書き込む --- (*10)
    try:
        chats = read_chat_log()
        chats.append({"name": name, "body": body,
                "date": time.strftime("%Y-%m-%d %H:%M:%S")})
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(chats, f) # JSON形式で保存
    except Exception as e:
        print("ログファイルに書き込めません", e)
    # トップにリダイレクトする --- (*11)
    return redirect("/")

# チャットログをファイルから読む --- (*12)
def read_chat_log():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("ログファイルが読めません", e)
        return []

if __name__ == "__main__":
    # Flaskサーバを起動 --- (*13)
    app.run(host="127.0.0.1", port=8888, debug=True)
