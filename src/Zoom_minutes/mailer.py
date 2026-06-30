# ========================================================
# mailer.py
# 【目的】
#   SMTP (SSL) を使ってチームに議事録メールを送信する。
#   Gmail を使う場合は「アプリパスワード」が必要。
#   (Google アカウント → セキュリティ → 2段階認証 → アプリパスワード)
# ========================================================

import smtplib
import os
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def _markdown_to_html(md: str) -> str:
    """Markdown テキストを簡易 HTML に変換する。"""
    lines = md.splitlines()
    html_lines = []
    in_table = False
    in_list = False
    table_header_done = False

    for line in lines:
        # テーブル行
        if line.startswith("|"):
            if not in_table:
                html_lines.append('<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse">')
                in_table = True
                table_header_done = False
            cells = [c.strip() for c in line.strip("|").split("|")]
            is_separator = all(re.fullmatch(r":?-+:?", c) for c in cells if c)
            if is_separator:
                table_header_done = True
                continue
            tag = "th" if not table_header_done else "td"
            html_lines.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
            continue
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
                table_header_done = False

        # リスト行
        if re.match(r"^[-*] ", line):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{line[2:].strip()}</li>")
            continue
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False

        # 見出し
        m = re.match(r"^(#{1,3}) (.+)", line)
        if m:
            level = len(m.group(1))
            html_lines.append(f"<h{level}>{m.group(2)}</h{level}>")
            continue

        # 区切り線
        if re.fullmatch(r"-{3,}", line.strip()):
            html_lines.append("<hr>")
            continue

        # 空行
        if not line.strip():
            html_lines.append("<br>")
            continue

        # 太字 **text**
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        html_lines.append(f"<p>{line}</p>")

    if in_list:
        html_lines.append("</ul>")
    if in_table:
        html_lines.append("</table>")

    return "\n".join(html_lines)


def send_email(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    recipients: list[str],
    subject: str,
    body: str,
    attachment_path: str = None,
) -> None:
    """
    議事録をメール送信する。本文は HTML と プレーンテキストの両方を添付。

    Parameters
    ----------
    smtp_server : str
        SMTPサーバー (例: "smtp.gmail.com")
    smtp_port : int
        SMTPポート (Gmail SSL: 465)
    sender_email : str
        送信者のメールアドレス
    sender_password : str
        送信者のパスワード (Gmailはアプリパスワード)
    recipients : list[str]
        受信者のメールアドレスリスト
    subject : str
        メールの件名
    body : str
        メール本文 (Markdown 形式の議事録テキスト)
    attachment_path : str, optional
        添付ファイルのパス (Markdown ファイルなど)
    """
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    # プレーンテキスト版
    plain_part = MIMEText(body, "plain", "utf-8")

    # HTML 版 (Markdown をシンプルな HTML に変換)
    html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.7;
         color: #222; max-width: 800px; margin: 0 auto; padding: 24px; }}
  h1 {{ color: #1a1a2e; border-bottom: 2px solid #4a90d9; padding-bottom: 8px; }}
  h2 {{ color: #2c3e50; margin-top: 28px; }}
  h3 {{ color: #34495e; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
  th {{ background: #4a90d9; color: white; padding: 8px 12px; text-align: left; }}
  td {{ padding: 8px 12px; border: 1px solid #ddd; }}
  tr:nth-child(even) {{ background: #f9f9f9; }}
  ul {{ padding-left: 22px; }}
  li {{ margin: 4px 0; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 20px 0; }}
  strong {{ color: #1a1a2e; }}
</style>
</head>
<body>
{_markdown_to_html(body)}
</body>
</html>"""
    html_part = MIMEText(html_body, "html", "utf-8")

    # alternative では最後に追加したものが優先される (HTML 優先)
    msg.attach(plain_part)
    msg.attach(html_part)

    # 添付ファイルがあれば追加
    if attachment_path and os.path.exists(attachment_path):
        outer = MIMEMultipart("mixed")
        outer["From"] = sender_email
        outer["To"] = ", ".join(recipients)
        outer["Subject"] = subject
        outer.attach(msg)

        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(attachment_path)
        part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        outer.attach(part)
        final_msg = outer
    else:
        final_msg = msg

    if smtp_port == 587:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, final_msg.as_string())
    else:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, final_msg.as_string())
