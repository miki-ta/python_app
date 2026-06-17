from flask import Flask, request, make_response
# Flaskのオブジェクトを作成する
app = Flask(__name__)

@app.route('/')
def index():
    # Cookieから訪問カウントを取得 --- (*1)
    visit_count = request.cookies.get("visit_count", 0)
    # 訪問カウントを整数型に変換して1を加算 --- (*2)
    try:
        visit_count = int(visit_count) + 1
    except ValueError:
        visit_count = 1  # エラーなら1にする
    # レスポンスを作成 --- (*3)
    response = make_response(f"<h1>訪問回数={visit_count}回</h1>")
    # 訪問カウントをCookieに保存(有効期限を3日に設定) --- (*4)
    response.set_cookie('visit_count', str(visit_count), max_age=60*60*24*3)
    return response

if __name__ == '__main__':
    app.run(debug=True, port=8080)
