from flask import Flask, request
app = Flask(__name__)

# ルートURLにアクセスした時の処理
@app.route("/")
def show_form():
    # フォームを表示 --- (*1)
    return """
    <form action="/calc">
      <input type="text" name="v1" value="5">＋
      <input type="text" name="v2" value="10">
      <input type="submit" value="計算">
    </form>
  """

# /calcにアクセスした時の処理 --- (*2)
@app.route("/calc")
def calc():
    # パラメータを取得 --- (*3)
    v1 = int(request.args.get("v1"))
    v2 = int(request.args.get("v2"))
    # 足し算をして結果を表示 --- (*4)
    answer = v1 + v2
    return f"<h1>{v1} + {v2} = {answer}</h1>"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888, debug=True) # サーバを起動
