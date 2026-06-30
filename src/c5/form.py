from flask import Flask
app = Flask(__name__)
# ルートURLにアクセスした時の処理
@app.route("/")
def show_form():
  # フォームを表示 --- (*1)
  return """
    <form>
      <input type="text" name="body" value="">
      <input type="hidden" name="mode" value="read">
      <input type="submit" value="発言">
    </form>
  """
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888, debug=True) # Flaskサーバを起動
