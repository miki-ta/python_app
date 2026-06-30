# ========================================================
# transcriber.py
# 【目的】
#   OpenAI の Whisper API を使って音声/動画ファイルを
#   テキストに変換（文字起こし）する。
#
# 【対応フォーマット】
#   MP4, M4A, WAV, MP3, WEBM, OGG
#   ※ ファイルサイズ上限: 25MB (Whisper API の制限)
#      それ以上の場合は split_audio() で分割してから渡す。
# ========================================================

import os
import math
import openai


def transcribe(audio_path: str, api_key: str, language: str = "ja") -> str:
    """
    音声/動画ファイルを文字起こしして文字列で返す。

    Parameters
    ----------
    audio_path : str
        Zoom 録音ファイルのパス (MP4, M4A, WAV, MP3 など)
    api_key : str
        OpenAI API キー
    language : str
        言語コード (デフォルト "ja" = 日本語)

    Returns
    -------
    str
        文字起こし結果のテキスト
    """
    client = openai.OpenAI(api_key=api_key)

    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)

    # 25MB 以下ならそのまま送信
    if file_size_mb <= 24:
        return _transcribe_single(client, audio_path, language)

    # 25MB 超の場合はチャンク分割して結合
    chunks = _split_audio(audio_path)
    results = []
    try:
        for chunk_path in chunks:
            text = _transcribe_single(client, chunk_path, language)
            results.append(text)
    finally:
        for chunk_path in chunks:
            if os.path.exists(chunk_path):
                os.remove(chunk_path)

    return "\n".join(results)


def _transcribe_single(client: openai.OpenAI, path: str, language: str) -> str:
    with open(path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language=language,
        )
    return response.text


def _split_audio(audio_path: str, chunk_minutes: int = 20) -> list[str]:
    """
    pydub を使って音声ファイルを chunk_minutes 分ずつ分割する。
    pydub が入っていない場合は ImportError を返す。
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError(
            "ファイルが 25MB を超えています。\n"
            "分割処理には pydub が必要です:\n"
            "  pip install pydub\n"
            "また ffmpeg のインストールも必要です。"
        )

    audio = AudioSegment.from_file(audio_path)
    chunk_ms = chunk_minutes * 60 * 1000
    total_chunks = math.ceil(len(audio) / chunk_ms)

    base, ext = os.path.splitext(audio_path)
    chunk_paths = []

    for i in range(total_chunks):
        start = i * chunk_ms
        end = min((i + 1) * chunk_ms, len(audio))
        chunk = audio[start:end]
        chunk_path = f"{base}_chunk{i:03d}{ext}"
        chunk.export(chunk_path, format=ext.lstrip("."))
        chunk_paths.append(chunk_path)

    return chunk_paths
