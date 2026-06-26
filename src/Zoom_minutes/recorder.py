# ========================================================
# recorder.py
# 【目的】
#   sounddevice を使ってシステム音声またはマイクを録音し
#   WAV ファイルに保存する。
#
# 【依存ライブラリ（任意）】
#   pip install sounddevice numpy
#   ※ インストールしなくてもアプリは起動するが録音機能は無効になる
# ========================================================

import threading
import wave
import os
import datetime
import time

try:
    import sounddevice as sd
    import numpy as np
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


def is_available() -> bool:
    """sounddevice と numpy が両方インストールされていれば True"""
    return _AVAILABLE


def list_devices() -> list[dict]:
    """
    入力可能なオーディオデバイス一覧を返す。

    Returns
    -------
    list of dict with keys:
        index       int   - sounddevice のデバイスインデックス
        name        str   - デバイス名
        channels    int   - 最大入力チャンネル数
        is_loopback bool  - システム音声（ループバック）の可能性が高いか
    """
    if not _AVAILABLE:
        return []

    result = []
    for i, d in enumerate(sd.query_devices()):
        if int(d["max_input_channels"]) < 1:
            continue
        name: str = d["name"]
        is_loopback = any(kw in name.lower() for kw in [
            "loopback", "stereo mix", "ステレオ ミキサー", "ステレオミキサー",
            "what u hear", "vb-audio", "blackhole", "soundflower", "virtual",
        ])
        result.append({
            "index":       i,
            "name":        name,
            "channels":    int(d["max_input_channels"]),
            "is_loopback": is_loopback,
        })
    return result


class AudioRecorder:
    """
    指定したデバイスで音声を録音して WAV ファイルに保存する。

    使い方
    ------
    rec = AudioRecorder()
    rec.start(device_index=0)
    ...
    path = rec.stop(save_dir="/path/to/dir")
    """

    SAMPLE_RATE = 44100

    def __init__(self) -> None:
        self._frames: list = []
        self._recording = False
        self._stream = None
        self._lock = threading.Lock()
        self._peak = 0.0
        self._channels = 1

    # ─────────────────────────────────────────────────────────
    # 公開メソッド
    # ─────────────────────────────────────────────────────────

    def start(self, device_index: int) -> None:
        """
        録音を開始する。別スレッドで非同期に動作する。

        Parameters
        ----------
        device_index : int
            list_devices() で得たデバイスの index 値
        """
        if not _AVAILABLE:
            raise RuntimeError(
                "録音機能を使うには sounddevice と numpy が必要です。\n"
                "コマンドプロンプトで以下を実行してください:\n\n"
                "  pip install sounddevice numpy\n\n"
                "実行後にアプリを再起動してください。"
            )

        info = sd.query_devices(device_index)
        self._channels = min(int(info["max_input_channels"]), 2)
        self._frames = []
        self._recording = True
        self._peak = 0.0

        def _callback(indata, frames, time, status):
            if self._recording:
                with self._lock:
                    self._frames.append(indata.copy())
                peak = float(np.max(np.abs(indata)))
                # 緩やかに減衰するピーク値
                self._peak = self._peak * 0.88 + peak * 0.12

        self._stream = sd.InputStream(
            device=device_index,
            channels=self._channels,
            samplerate=self.SAMPLE_RATE,
            dtype="int16",
            blocksize=2048,
            callback=_callback,
        )
        self._stream.start()

    def stop(self, save_dir: str) -> str:
        """
        録音を停止して WAV ファイルを保存し、そのパスを返す。

        Parameters
        ----------
        save_dir : str
            WAV ファイルを保存するディレクトリ

        Returns
        -------
        str
            保存した WAV ファイルの絶対パス
        """
        self._recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if not self._frames:
                raise ValueError("録音データがありません。マイクや設定を確認してください。")
            audio = np.concatenate(self._frames, axis=0)

        os.makedirs(save_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(save_dir, f"recording_{ts}.wav")

        with wave.open(path, "wb") as wf:
            wf.setnchannels(self._channels)
            wf.setsampwidth(2)          # int16 = 2 bytes/sample
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(audio.tobytes())

        return path

    # ─────────────────────────────────────────────────────────
    # プロパティ
    # ─────────────────────────────────────────────────────────

    @property
    def is_recording(self) -> bool:
        return self._recording

    def get_peak(self) -> float:
        """現在の音量を 0.0〜1.0 で返す（VU メーター用）"""
        return min(self._peak / 32767.0, 1.0)


# ──────────────────────────────────────────────────────────────────────────────
# 録画（画面キャプチャ＋音声）
# ──────────────────────────────────────────────────────────────────────────────

def is_video_available() -> bool:
    """mss と opencv-python が両方インストールされていれば True"""
    if not _AVAILABLE:
        return False
    try:
        import mss   # noqa: F401
        import cv2   # noqa: F401
        return True
    except ImportError:
        return False


def list_monitors() -> list[dict]:
    """
    利用可能なモニター一覧を返す（mss 未インストール時は空リスト）。

    Returns
    -------
    list of dict with keys:
        index  int  - mss のモニターインデックス（1 始まり）
        label  str  - 表示名
        region dict - mss に渡す座標辞書
    """
    try:
        import mss as _mss
        with _mss.mss() as sct:
            result = []
            for i, m in enumerate(sct.monitors[1:], start=1):
                result.append({
                    "index":  i,
                    "label":  f"モニター {i}（{m['width']}×{m['height']}）",
                    "region": dict(m),
                })
            return result
    except Exception:
        return []


class VideoRecorder:
    """
    画面キャプチャ（mss）＋音声録音（sounddevice）を組み合わせて
    動画ファイルを生成する。

    【必要なライブラリ】
        pip install mss opencv-python sounddevice numpy

    【出力ファイル】
        ffmpeg が使える場合: 音声付き MP4 1 ファイル
        ffmpeg がない場合:   映像のみ MP4 + 音声 WAV の 2 ファイル
                            （WAV のパスが返され、文字起こしに使われる）

    使い方
    ------
    rec = VideoRecorder()
    rec.start(device_index=0, monitor_index=1)
    ...
    path = rec.stop(save_dir="/path/to/dir")
    """

    SAMPLE_RATE = 44100
    FPS = 10  # スクリーンキャプチャのフレームレート（高いほど CPU 負荷が上がる）

    def __init__(self) -> None:
        self._recording = False
        self._lock = threading.Lock()
        self._audio_frames: list = []
        self._peak = 0.0
        self._channels = 1
        self._audio_stream = None
        self._video_thread: threading.Thread | None = None
        self._monitor: dict | None = None
        self._tmp_video_path: str | None = None  # 一時的な映像のみファイル
        self.extra_video_path: str | None = None  # ffmpeg 未使用時の映像ファイルパス

    # ─────────────────────────────────────────────────────────
    # 公開メソッド
    # ─────────────────────────────────────────────────────────

    def start(self, device_index: int, monitor_index: int = 1) -> None:
        """
        録画を開始する。

        Parameters
        ----------
        device_index  : int  list_devices() で得たデバイスの index
        monitor_index : int  list_monitors() で得たモニターの index（1 始まり）
        """
        if not _AVAILABLE:
            raise RuntimeError(
                "録音機能を使うには sounddevice と numpy が必要です。\n"
                "  pip install sounddevice numpy\n"
                "実行後にアプリを再起動してください。"
            )
        try:
            import mss   # noqa: F401
            import cv2   # noqa: F401
        except ImportError:
            raise RuntimeError(
                "録画機能を使うには mss と opencv-python が必要です。\n"
                "  pip install mss opencv-python\n"
                "実行後にアプリを再起動してください。"
            )

        import mss as _mss
        import tempfile

        with _mss.mss() as sct:
            monitors = sct.monitors
            idx = monitor_index if monitor_index < len(monitors) else 1
            self._monitor = dict(monitors[idx])

        # 一時ファイル（映像のみ）
        tmp_fd, self._tmp_video_path = tempfile.mkstemp(suffix=".mp4", prefix="rec_video_")
        os.close(tmp_fd)

        info = sd.query_devices(device_index)
        self._channels = min(int(info["max_input_channels"]), 2)
        self._audio_frames = []
        self._recording = True
        self._peak = 0.0
        self.extra_video_path = None

        def _audio_cb(indata, frames, t, status):
            if self._recording:
                with self._lock:
                    self._audio_frames.append(indata.copy())
                peak = float(np.max(np.abs(indata)))
                self._peak = self._peak * 0.88 + peak * 0.12

        self._audio_stream = sd.InputStream(
            device=device_index,
            channels=self._channels,
            samplerate=self.SAMPLE_RATE,
            dtype="int16",
            blocksize=2048,
            callback=_audio_cb,
        )
        self._audio_stream.start()

        self._video_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._video_thread.start()

    def stop(self, save_dir: str) -> str:
        """
        録画を停止してファイルを保存し、文字起こし用ファイルのパスを返す。

        Returns
        -------
        str
            文字起こしに渡すファイルのパス
            ffmpeg で合成できた場合: 音声付き MP4
            ffmpeg がない場合:       WAV（映像のみ MP4 は extra_video_path に格納）
        """
        self._recording = False
        if self._audio_stream:
            self._audio_stream.stop()
            self._audio_stream.close()
            self._audio_stream = None
        if self._video_thread:
            self._video_thread.join(timeout=5.0)
            self._video_thread = None

        with self._lock:
            audio_frames = list(self._audio_frames)

        if not audio_frames:
            raise ValueError("音声データがありません。デバイス設定を確認してください。")

        os.makedirs(save_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # ── 音声 WAV 保存 ──
        wav_path = os.path.join(save_dir, f"recording_{ts}.wav")
        audio = np.concatenate(audio_frames, axis=0)
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(self._channels)
            wf.setsampwidth(2)
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(audio.tobytes())

        # ── ffmpeg で音声付き MP4 にマージ ──
        if self._tmp_video_path and os.path.exists(self._tmp_video_path):
            final_mp4 = os.path.join(save_dir, f"recording_{ts}.mp4")
            if self._merge_ffmpeg(self._tmp_video_path, wav_path, final_mp4):
                os.remove(self._tmp_video_path)
                os.remove(wav_path)
                self._tmp_video_path = None
                return final_mp4

            # ffmpeg がない場合: 映像のみ MP4 を保存、WAV を文字起こし用に返す
            video_only = os.path.join(save_dir, f"recording_{ts}_video.mp4")
            os.replace(self._tmp_video_path, video_only)
            self.extra_video_path = video_only
            self._tmp_video_path = None

        return wav_path

    # ─────────────────────────────────────────────────────────
    # 内部メソッド
    # ─────────────────────────────────────────────────────────

    def _capture_loop(self) -> None:
        """別スレッドで実行: 画面をキャプチャして一時ファイルに書き込む"""
        import mss
        import cv2

        interval = 1.0 / self.FPS
        writer = None
        try:
            with mss.mss() as sct:
                while self._recording:
                    t0 = time.perf_counter()

                    img = sct.grab(self._monitor)
                    frame = np.array(img)[:, :, :3]  # BGRA → BGR

                    if writer is None:
                        h, w = frame.shape[:2]
                        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                        writer = cv2.VideoWriter(
                            self._tmp_video_path, fourcc, self.FPS, (w, h))

                    writer.write(frame)

                    elapsed = time.perf_counter() - t0
                    wait = interval - elapsed
                    if wait > 0:
                        time.sleep(wait)
        finally:
            if writer:
                writer.release()

    @staticmethod
    def _merge_ffmpeg(video: str, audio: str, output: str) -> bool:
        """ffmpeg で映像＋音声を MP4 に合成する。ffmpeg がなければ False を返す。"""
        import subprocess
        try:
            r = subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", video,
                    "-i", audio,
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-shortest",
                    output,
                ],
                capture_output=True,
                timeout=600,
            )
            return r.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    # ─────────────────────────────────────────────────────────
    # プロパティ
    # ─────────────────────────────────────────────────────────

    @property
    def is_recording(self) -> bool:
        return self._recording

    def get_peak(self) -> float:
        """現在の音量を 0.0〜1.0 で返す（VU メーター用）"""
        return min(self._peak / 32767.0, 1.0)
