from flask import Flask

# Flaskのオブジェクトを作成
app = Flask(__name__)

# ルートURLにアクセスした時の処理
@app.route("/")
def index():
    return f"Hello, World! {3/0}" # ここでエラーが発生する

if __name__ == "__main__":
    # Flaskサーバを起動
    app.run(host="127.0.0.1", port=8888, debug=True)
