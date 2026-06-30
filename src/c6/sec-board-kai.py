"""
秘密のメッセージボード「sec-board.py」の改良版です。
以下の機能を追加しています。
- 新規ユーザを追加する仕組み
- 定期的に古いセッションデータを削除する仕組み
"""

import os
import html
import datetime
import hashlib
import json
from flask import Flask, request, make_response
from flask.views import View
from cksession import CookieSession  # 自作のセッションモジュール

class CookieSessionKai(CookieSession):
    """ セッション管理を行うクラス - 古いファイルを自動削除する機能付き """
    def __save_to_file(self):
        """ セッションデータをファイルに書き出す """
        # 古いセッションがあればここで削除する
        now = datetime.datetime.now().timestamp()
        expired = now - 60 * 60 * 24 * 7  # 1週間前を期限とする
        for fname in os.listdir(self.SESSION_DIR):
            # ファイルの更新日時を得る
            path = self.SESSION_DIR + "/" + fname
            mtime = os.path.getmtime(path)
            if mtime < expired:
                os.remove(path)
        # セッションデータを保存
        path = self.SESSION_DIR + "/" + self.sid
        # JSON形式に変換して保存
        a_json = json.dumps(self.values)
        with open(path, "w", encoding="utf-8") as f:
            f.write(a_json)

    def save(self, response):
        """ クッキーにセッションIDを設定 """
        response.set_cookie(self.SESSION_ID, self.sid)
        self.__save_to_file()


class SecBoardKai(View):
    """ 秘密のメッセージボードを実現するクラス """
    # ユーザー名とパスワードを記録するファイル
    USER_FILE = "sec-board-user-data.json"
    PASSWORD_SALT = "salt#xEiFiZJV3RIz0tMk#"
    # 管理者ユーザーとパスワード
    ADMIN_USER = {"taro": "aaa", "jiro": "bbb"}
    # 秘密のメッセージを記述したファイル
    FILE_MSG = "sec-board-message-data.txt"
    # このビューで許可するHTTPメソッド
    methods = ["GET", "POST"]

    def __init__(self):
        # セッションを開始
        self.session = CookieSessionKai(request)
        if not os.path.exists(self.USER_FILE):
            for user, pw in self.ADMIN_USER.items():
                self.__user_add(user, pw)

    def dispatch_request(self):
        """ リクエストを処理する """
        # request.path からメソッド名を取得
        method_name = request.path.replace("/", "")
        # 指定されたメソッド名に対応するメソッドを取得し実行
        method = getattr(self, method_name, None)
        return method() if method else self.login()

    def make_html(self, title, body):  # --- (*4)
        """レスポンスを作成する"""
        response = make_response(f"""
            <!DOCTYPE html><meta charset="utf-8"><html>
            <head><title>{title}</title></head><style>
            h1 {{ background-color: #eef; padding: 0.5em; }}
            .err {{ color: red; }}
            form {{
                padding: 1em;
                border: 1px solid #ccc;
                background-color: #f8f8f8;
            }}
            </style><body><h1>{title}</h1>{body}</body>
            </html>""")
        self.session.save(response)  # セッションを保存
        return response

    def make_error(self, msg):
        """エラーを表示"""
        return self.make_html(
            "エラー", 
            f"""
            <div class="err">{msg}<div>
            <hr>
            <div><a href="/">トップへ</a></div>
            """)

    def login(self):
        """ログイン画面を表示する"""
        # もし既にログインしていたらメッセージボードを表示
        if self.is_login():
            return self.sec()
        return self.make_html(
            "ログイン",
            """
            <form method="POST" action="/try_login">
            ユーザー名: <input type="text" name="user" size="8"><br>
            パスワード: <input type="password" name="pw" size="8">
            <input type="submit" value="ログイン"></form>
            """)

    def load_userinfo(self):
        userinfo = {}
        if os.path.exists(self.USER_FILE):
            with open(self.USER_FILE, "r") as f:
                userinfo = json.load(f)
        return userinfo

    def try_login(self):
        """ ログイン可能か検証する """
        # フォームデータからログイン情報を得る
        user = request.form.get("user", "")
        pw = request.form.get("pw", "")
        pw2 = self.PASSWORD_SALT + pw
        hash = hashlib.sha256(pw2.encode("utf-8")).hexdigest()
        # ログインできるか調べる
        userinfo= self.load_userinfo()
        if (user not in userinfo) or (userinfo[user] != hash):
            return self.make_error("ユーザ名かパスワードが違います")
        # ログイン成功を明示
        now = datetime.datetime.now()
        self.session["login"] = now.timestamp()
        self.session["user"] = user # ユーザー名をセッションに保存
        return self.make_html("ログイン成功", """
        <a href="/sec">会員専用ボードを見る</a>
        """)

    def sec(self):
        """秘密のメッセージを表示する"""
        if not self.is_login():
            return self.make_error("ログインが必要です")
        # 秘密のメッセージを読み込む
        msg = "(ここに秘密のメッセージを書いてください)"  # 初期値
        if os.path.exists(self.FILE_MSG):
            with open(self.FILE_MSG, "r", encoding="utf-8") as f:
                msg = f.read()
        msg = html.escape(msg)
        return self.make_html(
            "秘密のメッセージ",
            f"""
            <form method="POST" action="/sec_edit">
            <textarea name="msg" cols="70" rows="5">{msg}</textarea>
            <br><input type="submit" value="変更"></form>
            <hr><a href="/user_add">→新規ユーザを追加</a>
            <hr><a href="/logout">→ログアウト</a>""",
        )

    def sec_edit(self):
        """秘密のメッセージを編集する"""  # --- (*10)
        if not self.is_login():
            return self.make_error("ログインが必要です")
        # 秘密のメッセージを保存して変更した旨を表示
        with open(self.FILE_MSG, "w", encoding="utf-8") as f:
            f.write(request.form.get("msg", ""))
        return self.make_html("変更", "<a href='/sec'>変更完了</a>")

    def is_login(self):
        """ ログインしているか判定する """
        if "login" in self.session:
            if self.session['login'] > 0:
                return True
        return False

    def logout(self):
        """ログアウトする"""
        self.session["login"] = 0
        return self.make_html("ログアウト", "<a href='/'>完了</a>")

    def user_add(self):
        """新規ユーザー登録画面を表示する"""
        if not self.is_login():
            return self.make_error("ログインが必要です")
        return self.make_html(
            "新規ユーザー登録",
            """
            <h3>新規ユーザー作成</h3>
            <form method="POST" action="/try_user_add">
            ユーザー名: <input type="text" name="user" size="8"><br>
            パスワード: <input type="password" name="pw" size="8">
            <input type="submit" value="新規作成">
            </form>
            """,
        )

    def try_user_add(self):
        """新規ユーザー登録を行う"""
        if not self.is_login():
            return self.make_error("ログインが必要です")
        user = request.form.get("user", "")
        pw = request.form.get("pw", "")
        ok, err_response = self.__user_add(user, pw)
        if not ok:
            return err_response
        return self.make_html(
            "新規ユーザーを追加しました",
            """
            <a href="/sec">秘密のメッセージを見る</a>
            """,
        )

    def __user_add(self, user, pw):
        """ユーザーを追加する"""
        # 既にユーザーが存在するか調べる
        userinfo = self.load_userinfo()
        if user in userinfo:
            return False, self.make_error("ユーザーが既に存在します")
        pw2 = self.PASSWORD_SALT + pw
        hash = hashlib.sha256(pw2.encode("utf-8")).hexdigest()
        userinfo[user] = hash
        with open(self.USER_FILE, "w") as f:
            json.dump(userinfo, f)
        return True, None


# Flaskのオブジェクトを作成する
app = Flask(__name__)
# URLとメソッドを結びつける
board = SecBoardKai.as_view('board')
urls = [
    "/",
    "/login",
    "/try_login",
    "/logout",
    "/sec",
    "/sec_edit",
    "/user_add",
    "/try_user_add",
]
for path in urls:
    app.add_url_rule(path, view_func=board)

if __name__ == "__main__":
    app.run(debug=True, port=8080)




