# ========================================================
# summarizer.py
# 【目的】
#   Anthropic の Claude API を使って、会議の文字起こし
#   テキストから整形された議事録 (Markdown) を生成する。
# ========================================================

import anthropic


def create_minutes(
    transcript: str,
    api_key: str,
    meeting_title: str = "",
    meeting_date: str = "",
) -> str:
    """
    文字起こしテキストから議事録を生成して返す。

    Parameters
    ----------
    transcript : str
        Whisper で生成した文字起こしテキスト
    api_key : str
        Anthropic API キー
    meeting_title : str
        会議名（省略可）
    meeting_date : str
        会議日時（省略可）

    Returns
    -------
    str
        Markdown 形式の議事録テキスト
    """
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""あなたは優秀な秘書です。以下の Zoom 会議の文字起こしテキストをもとに、
読みやすい日本語の議事録を Markdown 形式で作成してください。

【会議名】{meeting_title or "（不明）"}
【日時】{meeting_date or "（不明）"}

---
## 出力フォーマット (このまま使うこと)

# 議事録

## 会議概要
- **会議名**: （会議名）
- **日時**: （日時）
- **参加者**: （文字起こしから判断できる場合のみ記載、不明なら「不明」）

## 議題・アジェンダ
（話し合われたトピックを箇条書きで）

## 議論の要点
（各トピックの議論内容を簡潔にまとめる）

## 決定事項
（会議で決まったことを箇条書きで）

## アクションアイテム
| No. | 担当者 | タスク内容 | 期限 |
|-----|--------|-----------|------|
| 1   |        |           |      |

## 次回会議
- **日時**: （言及があれば記載、なければ「未定」）
- **議題**: （言及があれば記載）

---
【文字起こしテキスト】
{transcript}
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text
