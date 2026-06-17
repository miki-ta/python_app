from flask import Flask, request, make_response
from cksession import CookieSession  # 自作のセッションモジュール

# Flaskのオブジェクトを作成する
app = Flask(__name__)

@app.route("/")
def index():
    # セッションを開始する --- (*1)
    session = CookieSession(request)
    # セッションから訪問カウントを取得
    visit_count = session["visit_count"] if "visit_count" in session else 0
    # 訪問カウントを整数型に変換して1を加算 --- (*2)
    try:
        visit_count = int(visit_count) + 1
    except ValueError:
        visit_count = 1  # エラーなら1にする
    # レスポンスを作成
    response = make_response(f"<h1>訪問回数={visit_count}回</h1>")
    # 訪問カウントをセッションに保存 --- (*3)
    session["visit_count"] = visit_count
    session.save(response)
    return response

if __name__ == "__main__":
    app.run(debug=True, port=8080)
