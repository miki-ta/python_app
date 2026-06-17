from flask import Flask

# Flaskのオブジェクトを作成 --- (*1)
app = Flask(__name__)

# ルートURLにアクセスした時の処理 --- (*2)
@app.route("/")
def index():
    return "Hello, World!"

if __name__ == "__main__":
    # Flaskサーバを起動 --- (*3)
    app.run(host="0.0.0.0", port=8888, debug=True)
