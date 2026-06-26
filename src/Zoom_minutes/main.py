# ========================================================
# main.py  ―  Zoom 議事録 自動作成・共有ツール
# ========================================================
# 【使い方】
#   1. .env ファイルに API キーとメール設定を記入する (.env.example 参照)
#   2. python run_zoom_minutes.py でウィンドウを起動
#   3. タブを順番に操作する (録音 → ① → ② → ③ → ④)
#
# 【必要なライブラリ】
#   pip install openai anthropic python-dotenv sounddevice numpy
# ========================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import tempfile
import datetime
import webbrowser

from dotenv import load_dotenv

from .transcriber import transcribe
from .summarizer import create_minutes
from .mailer import send_email
from .recorder import (
    AudioRecorder, VideoRecorder,
    is_available as recorder_available, is_video_available,
    list_devices as list_audio_devices, list_monitors,
)

load_dotenv()

_OPENAI_URL       = "https://platform.openai.com/api-keys"
_ANTHROPIC_URL    = "https://console.anthropic.com/"
_GMAIL_APP_PW_URL = "https://myaccount.google.com/apppasswords"

# タブインデックス定数（録音タブが 0 番目に追加されたため）
_TAB_REC   = 0
_TAB_SETUP = 1
_TAB_TRANS = 2
_TAB_MIN   = 3
_TAB_MAIL  = 4


class ZoomMinutesApp:

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Zoom 議事録 自動作成ツール")
        self.root.geometry("1020x820")
        self.root.resizable(True, True)

        today = datetime.date.today().strftime("%Y年%m月%d日")

        # ── 文字起こし・議事録関連 ──
        self.recording_path    = tk.StringVar()
        self.openai_api_key    = tk.StringVar(value=os.getenv("OPENAI_API_KEY", ""))
        self.anthropic_api_key = tk.StringVar(value=os.getenv("ANTHROPIC_API_KEY", ""))
        self.meeting_title     = tk.StringVar()
        self.meeting_date      = tk.StringVar(value=today)

        # ── メール関連 ──
        self.smtp_server     = tk.StringVar(value=os.getenv("SMTP_SERVER", "smtp.gmail.com"))
        self.smtp_port       = tk.IntVar(value=int(os.getenv("SMTP_PORT", "465")))
        self.sender_email    = tk.StringVar(value=os.getenv("SENDER_EMAIL", ""))
        self.sender_password = tk.StringVar(value=os.getenv("SENDER_PASSWORD", ""))
        self.recipients      = tk.StringVar(value=os.getenv("RECIPIENTS", ""))
        self.email_subject   = tk.StringVar()
        self.attach_md       = tk.BooleanVar(value=True)

        # ── パスワード表示切り替え用参照 ──
        self._openai_entry    : ttk.Entry | None = None
        self._anthropic_entry : ttk.Entry | None = None
        self._gmail_pw_entry  : ttk.Entry | None = None

        # ── SMTP 詳細折りたたみ用 ──
        self._smtp_detail_frame : ttk.LabelFrame | None = None
        self._smtp_toggle_btn   : ttk.Button | None = None

        # ── 録音・録画関連 ──
        self._recorder        : AudioRecorder | VideoRecorder | None = None
        self._rec_save_dir    = tk.StringVar(
            value=os.path.join(os.path.expanduser("~"), "Documents"))
        self._rec_timer_var   = tk.StringVar(value="00:00")
        self._rec_seconds     = 0
        self._rec_device_idx  : int | None = None
        self._rec_devices     : list[dict] = []
        self._meter_canvas    : tk.Canvas | None = None
        self._meter_bar       = None
        self._rec_btn         : tk.Button | None = None
        self._rec_mode        = tk.StringVar(value="audio")  # "audio" or "video"
        self._rec_monitor_idx = tk.IntVar(value=1)
        self._rec_monitors    : list[dict] = []
        self._monitor_frame   : ttk.Frame | None = None
        self._monitor_combo   : ttk.Combobox | None = None

        self._build_ui()

    # ─────────────────────────────────────────────────────────
    # UI 構築
    # ─────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # ── ステータスバー (最下部) ──
        self.status_var = tk.StringVar(
            value="準備完了  |  「🎙 録音」タブで録音するか、「① ファイル選択」タブで録音済みファイルを選んでください")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var,
            relief="sunken", anchor="w", padding=(8, 3))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # ── プログレスバー ──
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(side=tk.BOTTOM, fill=tk.X)

        # ── タブ ──
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        tab_rec   = ttk.Frame(self.notebook)
        tab_setup = ttk.Frame(self.notebook)
        tab_trans = ttk.Frame(self.notebook)
        tab_min   = ttk.Frame(self.notebook)
        tab_mail  = ttk.Frame(self.notebook)

        self.notebook.add(tab_rec,   text="🎙 録音")
        self.notebook.add(tab_setup, text="① ファイル選択・設定")
        self.notebook.add(tab_trans, text="② 文字起こし結果")
        self.notebook.add(tab_min,   text="③ 議事録")
        self.notebook.add(tab_mail,  text="④ メール送信")

        self._build_tab_rec(tab_rec)
        self._build_tab1(tab_setup)
        self._build_tab2(tab_trans)
        self._build_tab3(tab_min)
        self._build_tab4(tab_mail)

    # ══════════════════════════════════════════════════════════
    # 🎙 録音タブ
    # ══════════════════════════════════════════════════════════

    def _build_tab_rec(self, parent: ttk.Frame) -> None:
        pad = {"padx": 14, "pady": 7}

        # ── sounddevice が未インストールの場合 ──
        if not recorder_available():
            warn = ttk.LabelFrame(parent, text="録音機能を有効にするには追加ライブラリが必要です", padding=16)
            warn.pack(fill=tk.X, **pad)
            ttk.Label(
                warn,
                text="録音機能を使うには sounddevice と numpy をインストールする必要があります。\n"
                     "コマンドプロンプトを開いて以下のコマンドを実行してください：",
                foreground="#b05000",
                font=("Yu Gothic UI", 10),
            ).pack(anchor="w")

            cmd_frame = tk.Frame(warn, bg="#1e2233", padx=12, pady=10)
            cmd_frame.pack(fill=tk.X, pady=(10, 0))
            tk.Label(
                cmd_frame,
                text="pip install sounddevice numpy",
                bg="#1e2233", fg="#c3e88d",
                font=("Consolas", 12),
            ).pack(anchor="w")

            ttk.Label(
                warn,
                text="実行後にアプリを再起動すると録音機能が使えるようになります。",
                foreground="#555",
                font=("Yu Gothic UI", 9),
            ).pack(anchor="w", pady=(10, 0))
            return

        # ── 説明 ──────────────────────────────────────────
        tip = ttk.LabelFrame(parent, text="このタブでできること", padding=10)
        tip.pack(fill=tk.X, **pad)
        ttk.Label(
            tip,
            text="Zoom や Google Meet の会議を PC 上で直接録音・録画できます。\n"
                 "完了すると自動的に ① タブへ移動して文字起こしを開始できます。\n"
                 "すでに録音ファイルがある場合は ① タブで直接ファイルを選んでください。",
            foreground="#444",
            font=("Yu Gothic UI", 9),
            justify="left",
        ).pack(anchor="w")

        # ── 録音・録画モード切り替え ──────────────────────
        mode_frame = ttk.LabelFrame(parent, text="録音・録画モードを選ぶ", padding=10)
        mode_frame.pack(fill=tk.X, **pad)

        ttk.Radiobutton(
            mode_frame,
            text="🎙  音声のみ録音する（WAV ファイル）  ←  文字起こしだけしたい場合",
            variable=self._rec_mode, value="audio",
            command=self._on_rec_mode_changed,
        ).pack(anchor="w", pady=2)

        ttk.Radiobutton(
            mode_frame,
            text="🎬  画面も録画する（MP4 動画）  ←  映像も保存したい場合",
            variable=self._rec_mode, value="video",
            command=self._on_rec_mode_changed,
        ).pack(anchor="w", pady=2)

        # モニター選択（録画モード時のみ表示）
        self._monitor_frame = ttk.Frame(mode_frame)
        mon_inner = ttk.Frame(self._monitor_frame)
        mon_inner.pack(fill=tk.X)
        ttk.Label(mon_inner, text="録画するモニター:").pack(side=tk.LEFT)
        self._monitor_combo = ttk.Combobox(mon_inner, width=42, state="readonly")
        self._monitor_combo.pack(side=tk.LEFT, padx=8)
        self._monitor_combo.bind("<<ComboboxSelected>>", self._on_monitor_selected)
        ttk.Button(mon_inner, text="🔄 一覧を更新",
                   command=self._refresh_monitors).pack(side=tk.LEFT)

        if not is_video_available():
            ttk.Label(
                mode_frame,
                text="⚠  「画面も録画」を使うには追加ライブラリが必要です:\n"
                     "    pip install mss opencv-python  を実行してアプリを再起動してください。",
                foreground="#b05000",
                font=("Yu Gothic UI", 9),
                justify="left",
            ).pack(anchor="w", pady=(8, 0))

        # ── 手順ガイド ────────────────────────────────────
        guide = ttk.LabelFrame(parent, text="録音・録画の手順", padding=10)
        guide.pack(fill=tk.X, **pad)

        steps = [
            ("1", "Zoom または Google Meet でミーティングを開始する\n（ブラウザや Zoom アプリを先に起動してください）"),
            ("2", "上の「モード」を選び、「録音デバイス」を選ぶ\n（音声のみ: ステレオ ミキサー推奨 / 録画: モニターも選んでください）"),
            ("3", "「● 録音を開始する」または「● 録画を開始する」ボタンを押す"),
            ("4", "ミーティングが終わったら「■ 停止する」ボタンを押す"),
            ("5", "自動的に ① タブへ移動します。文字起こしを開始してください。"),
        ]
        for num, desc in steps:
            row = ttk.Frame(guide)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=num,
                     bg="#2a7ae4", fg="white",
                     font=("Yu Gothic UI", 9, "bold"),
                     width=2, relief="flat").pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(row, text=desc, justify="left",
                      font=("Yu Gothic UI", 9)).pack(side=tk.LEFT, anchor="w")

        # ── デバイス選択 ──────────────────────────────────
        dev_frame = ttk.LabelFrame(parent, text="録音デバイスを選ぶ", padding=12)
        dev_frame.pack(fill=tk.X, **pad)

        ttk.Label(
            dev_frame,
            text="どのデバイスを使うか選んでください。よくわからない場合は「🔊 ステレオ ミキサー」を選んでください。",
            foreground="#444", font=("Yu Gothic UI", 9),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        ttk.Label(dev_frame, text="デバイス:").grid(row=1, column=0, sticky="w")

        self._device_combo = ttk.Combobox(dev_frame, width=52, state="readonly")
        self._device_combo.grid(row=1, column=1, padx=6, sticky="w")
        self._device_combo.bind("<<ComboboxSelected>>", self._on_device_selected)

        ttk.Button(dev_frame, text="🔄 一覧を更新",
                   command=self._refresh_devices).grid(row=1, column=2)

        self._device_hint = ttk.Label(
            dev_frame, text="", foreground="#666", font=("Yu Gothic UI", 8))
        self._device_hint.grid(row=2, column=1, sticky="w", pady=(4, 0))

        # デバイス一覧を初期ロード
        self._refresh_devices()

        # ── 録音コントロール ──────────────────────────────
        ctrl_frame = ttk.LabelFrame(parent, text="録音コントロール", padding=12)
        ctrl_frame.pack(fill=tk.X, **pad)

        # タイマー
        timer_row = ttk.Frame(ctrl_frame)
        timer_row.pack(fill=tk.X)
        ttk.Label(timer_row, text="録音時間:", font=("Yu Gothic UI", 10)).pack(side=tk.LEFT)
        ttk.Label(timer_row, textvariable=self._rec_timer_var,
                  font=("Yu Gothic UI", 14, "bold"), foreground="#2a7ae4").pack(
            side=tk.LEFT, padx=8)

        # 音量メーター
        meter_label = ttk.Frame(ctrl_frame)
        meter_label.pack(fill=tk.X, pady=(8, 2))
        ttk.Label(meter_label, text="音量レベル:",
                  font=("Yu Gothic UI", 9)).pack(side=tk.LEFT)
        ttk.Label(meter_label,
                  text="（録音中に動きます）",
                  foreground="#888", font=("Yu Gothic UI", 8)).pack(side=tk.LEFT, padx=4)

        self._meter_canvas = tk.Canvas(
            ctrl_frame, height=22, bg="#222222",
            relief="flat", highlightthickness=0)
        self._meter_canvas.pack(fill=tk.X, pady=(0, 10))
        self._meter_bar = self._meter_canvas.create_rectangle(
            0, 2, 0, 20, fill="#27ae60", outline="")

        # 録音ボタン
        self._rec_btn = tk.Button(
            ctrl_frame,
            text="●  録音を開始する",
            command=self._toggle_recording,
            bg="#e74c3c", fg="white",
            font=("Yu Gothic UI", 13, "bold"),
            relief="flat",
            padx=28, pady=12,
            cursor="hand2",
            activebackground="#c0392b",
        )
        self._rec_btn.pack(anchor="w")

        self._rec_status_var = tk.StringVar(value="")
        ttk.Label(ctrl_frame, textvariable=self._rec_status_var,
                  foreground="#27ae60",
                  font=("Yu Gothic UI", 9, "bold")).pack(anchor="w", pady=(6, 0))

        # ── 保存先 ────────────────────────────────────────
        save_frame = ttk.LabelFrame(parent, text="録音ファイルの保存先フォルダ", padding=12)
        save_frame.pack(fill=tk.X, **pad)
        save_frame.columnconfigure(1, weight=1)

        ttk.Label(save_frame, text="保存先:").grid(row=0, column=0, sticky="w")
        ttk.Entry(save_frame, textvariable=self._rec_save_dir,
                  width=54).grid(row=0, column=1, padx=6, sticky="ew")
        ttk.Button(save_frame, text="📁  フォルダを選ぶ",
                   command=self._browse_save_dir).grid(row=0, column=2)
        ttk.Label(save_frame,
                  text="※ 録音が完了すると「recording_日時.wav」という名前でここに保存されます",
                  foreground="#888", font=("Yu Gothic UI", 8)).grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

    # ── タブ① ────────────────────────────────────────────────

    def _build_tab1(self, parent: ttk.Frame) -> None:
        pad = {"padx": 14, "pady": 6}

        # ── 使い方ガイド ──────────────────────────────────
        guide = ttk.LabelFrame(parent, text="このツールの使い方（4ステップで完了します）", padding=10)
        guide.pack(fill=tk.X, padx=14, pady=(12, 6))

        steps = [
            ("①", "ファイル選択・設定",  "録音ファイルを選んでAPIキーを入力"),
            ("②", "文字起こし確認",      "AIが音声をテキストに変換"),
            ("③", "議事録の確認・編集",  "AIが自動で議事録を作成"),
            ("④", "メール送信",          "チームへ議事録を共有"),
        ]
        for col, (num, title, desc) in enumerate(steps):
            f = ttk.Frame(guide)
            f.grid(row=0, column=col * 2, padx=10, pady=4, sticky="n")
            ttk.Label(f, text=f"{num} {title}",
                      font=("Yu Gothic UI", 10, "bold")).pack()
            ttk.Label(f, text=desc, foreground="#666666",
                      font=("Yu Gothic UI", 8)).pack()
            if col < 3:
                ttk.Label(guide, text="→",
                          font=("Yu Gothic UI", 18), foreground="#aaaaaa").grid(
                    row=0, column=col * 2 + 1)

        # ── STEP 1: ファイル選択 ──────────────────────────
        file_frame = ttk.LabelFrame(parent, text="STEP 1  録音ファイルを選ぶ", padding=12)
        file_frame.pack(fill=tk.X, **pad)
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(
            file_frame,
            text="Zoom で録音した音声・動画ファイルを指定してください（対応形式: MP4 / M4A / WAV / MP3）\n"
                 "「🎙 録音」タブで録音した場合は自動的にここに入力されます。",
            foreground="#444444",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        ttk.Label(file_frame, text="選択中のファイル:").grid(row=1, column=0, sticky="w")
        ttk.Entry(file_frame, textvariable=self.recording_path,
                  width=58, state="readonly").grid(row=1, column=1, padx=6, sticky="ew")
        ttk.Button(file_frame, text="📂  ファイルを選ぶ",
                   command=self._browse_file).grid(row=1, column=2)

        ttk.Label(
            file_frame,
            text="※ 25MB を超えるファイルは自動で分割されます（別途 pydub + ffmpeg のインストールが必要）",
            foreground="#888888", font=("Yu Gothic UI", 8),
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(4, 0))

        # ── STEP 2: 会議情報 ──────────────────────────────
        info_frame = ttk.LabelFrame(parent, text="STEP 2  会議情報を入力する（省略可）", padding=12)
        info_frame.pack(fill=tk.X, **pad)

        ttk.Label(info_frame, text="会議名:").grid(row=0, column=0, sticky="w")
        ttk.Entry(info_frame, textvariable=self.meeting_title, width=46).grid(
            row=0, column=1, padx=6, sticky="w")
        ttk.Label(info_frame,
                  text="← 議事録のタイトルになります（ファイル選択時に自動入力・省略可）",
                  foreground="#888888", font=("Yu Gothic UI", 8)).grid(
            row=0, column=2, sticky="w")

        ttk.Label(info_frame, text="日時:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(info_frame, textvariable=self.meeting_date, width=28).grid(
            row=1, column=1, padx=6, sticky="w", pady=(8, 0))
        ttk.Label(info_frame,
                  text="← 議事録に記載される日時（例: 2025年6月26日）",
                  foreground="#888888", font=("Yu Gothic UI", 8)).grid(
            row=1, column=2, sticky="w", pady=(8, 0))

        # ── STEP 3: API キー ──────────────────────────────
        api_frame = ttk.LabelFrame(parent, text="STEP 3  API キーを設定する", padding=12)
        api_frame.pack(fill=tk.X, **pad)

        ttk.Label(
            api_frame,
            text="「API キー」とは？\n"
                 "  AI サービス（OpenAI・Anthropic）を使うために必要な認証コード（パスワードのようなもの）です。\n"
                 "  各サービスのウェブサイトで登録してキーを取得し、下の欄に貼り付けてください。\n"
                 "  取得済みの場合は .env ファイルに保存しておくと次回から自動入力されます。",
            foreground="#555555",
            font=("Yu Gothic UI", 9),
            justify="left",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        ttk.Label(api_frame,
                  text="OpenAI APIキー\n（音声の文字起こし用）",
                  justify="left").grid(row=1, column=0, sticky="w", padx=(0, 8))
        self._openai_entry = ttk.Entry(
            api_frame, textvariable=self.openai_api_key, width=50, show="*")
        self._openai_entry.grid(row=1, column=1, padx=6, sticky="w")
        ttk.Button(api_frame, text="表示 / 非表示",
                   command=self._toggle_openai_key).grid(row=1, column=2)

        openai_link = ttk.Label(
            api_frame,
            text="▶ キーの取得はこちら（platform.openai.com/api-keys）",
            foreground="#0066cc", cursor="hand2",
            font=("Yu Gothic UI", 8, "underline"),
        )
        openai_link.grid(row=2, column=1, sticky="w", pady=(2, 10))
        openai_link.bind("<Button-1>", lambda e: webbrowser.open(_OPENAI_URL))

        ttk.Label(api_frame,
                  text="Anthropic APIキー\n（議事録の自動生成用）",
                  justify="left").grid(row=3, column=0, sticky="w", padx=(0, 8))
        self._anthropic_entry = ttk.Entry(
            api_frame, textvariable=self.anthropic_api_key, width=50, show="*")
        self._anthropic_entry.grid(row=3, column=1, padx=6, sticky="w")
        ttk.Button(api_frame, text="表示 / 非表示",
                   command=self._toggle_anthropic_key).grid(row=3, column=2)

        anthr_link = ttk.Label(
            api_frame,
            text="▶ キーの取得はこちら（console.anthropic.com）",
            foreground="#0066cc", cursor="hand2",
            font=("Yu Gothic UI", 8, "underline"),
        )
        anthr_link.grid(row=4, column=1, sticky="w", pady=(2, 4))
        anthr_link.bind("<Button-1>", lambda e: webbrowser.open(_ANTHROPIC_URL))

        ttk.Label(
            api_frame,
            text="⚠  API キーは他人に教えないでください。パスワードと同じく厳重に管理してください。",
            foreground="#b05000",
            font=("Yu Gothic UI", 8),
        ).grid(row=5, column=0, columnspan=3, sticky="w", pady=(6, 0))

        # ── スタートボタン ────────────────────────────────
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=14, pady=(10, 8))

        ttk.Label(
            action_frame,
            text="STEP 1〜3 の入力が終わったら、下のボタンを押してください。\n"
                 "音声ファイルの長さによっては数分かかります。完了するまで画面を閉じないでください。",
            foreground="#444444",
            font=("Yu Gothic UI", 9),
            justify="left",
        ).pack(anchor="w")

        start_btn = tk.Button(
            action_frame,
            text="▶  文字起こしを開始する",
            command=self._start_transcription,
            bg="#2a7ae4", fg="white",
            font=("Yu Gothic UI", 12, "bold"),
            relief="flat",
            padx=24, pady=10,
            cursor="hand2",
        )
        start_btn.pack(anchor="w", pady=(8, 0))

    # ── タブ② ────────────────────────────────────────────────

    def _build_tab2(self, parent: ttk.Frame) -> None:
        tip_frame = ttk.LabelFrame(parent, text="このタブでできること", padding=8)
        tip_frame.pack(fill=tk.X, padx=12, pady=(10, 4))
        ttk.Label(
            tip_frame,
            text="AI が音声・動画ファイルを聞き取り、日本語テキストに変換しました。\n"
                 "聞き取り間違いや固有名詞の誤りがあれば、テキストを直接クリックして修正できます。\n"
                 "修正が終わったら「議事録を自動生成する」ボタンを押して次に進んでください。",
            foreground="#444444",
            font=("Yu Gothic UI", 9),
            justify="left",
        ).pack(anchor="w")

        ttk.Label(parent,
                  text="文字起こし結果（クリックして直接編集できます）:",
                  font=("Yu Gothic UI", 9)).pack(anchor="w", padx=12, pady=(6, 2))
        self.transcript_text = scrolledtext.ScrolledText(
            parent, wrap=tk.WORD, font=("Yu Gothic UI", 10))
        self.transcript_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=12, pady=8)
        ttk.Button(btn_frame, text="💾  テキストをファイルに保存 (.txt)",
                   command=self._save_transcript).pack(side=tk.LEFT, padx=4)

        next_btn = tk.Button(
            btn_frame,
            text="▶  議事録を自動生成する（次へ）",
            command=self._generate_minutes,
            bg="#2a7ae4", fg="white",
            font=("Yu Gothic UI", 10, "bold"),
            relief="flat",
            padx=16, pady=7,
            cursor="hand2",
        )
        next_btn.pack(side=tk.LEFT, padx=10)
        ttk.Label(btn_frame,
                  text="← テキストの確認・修正が終わったらこちらを押してください",
                  foreground="#777777", font=("Yu Gothic UI", 8)).pack(
            side=tk.LEFT, pady=4)

    # ── タブ③ ────────────────────────────────────────────────

    def _build_tab3(self, parent: ttk.Frame) -> None:
        tip_frame = ttk.LabelFrame(parent, text="このタブでできること", padding=8)
        tip_frame.pack(fill=tk.X, padx=12, pady=(10, 4))
        ttk.Label(
            tip_frame,
            text="AI が文字起こしをもとに会議の議事録を自動作成しました。\n"
                 "内容を確認・修正してから、「保存」またはそのまま「メール送信画面へ」進んでください。\n"
                 "※ テキストは Markdown 形式で書かれていますが、メール送信時は見やすい形式に自動変換されます。",
            foreground="#444444",
            font=("Yu Gothic UI", 9),
            justify="left",
        ).pack(anchor="w")

        ttk.Label(parent,
                  text="議事録（クリックして直接編集できます）:",
                  font=("Yu Gothic UI", 9)).pack(anchor="w", padx=12, pady=(6, 2))
        self.minutes_text = scrolledtext.ScrolledText(
            parent, wrap=tk.WORD, font=("Yu Gothic UI", 10))
        self.minutes_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=12, pady=8)
        ttk.Button(btn_frame, text="💾  議事録をファイルに保存 (.md)",
                   command=self._save_minutes).pack(side=tk.LEFT, padx=4)

        next_btn = tk.Button(
            btn_frame,
            text="▶  メール送信画面へ（次へ）",
            command=lambda: self.notebook.select(_TAB_MAIL),
            bg="#2a7ae4", fg="white",
            font=("Yu Gothic UI", 10, "bold"),
            relief="flat",
            padx=16, pady=7,
            cursor="hand2",
        )
        next_btn.pack(side=tk.LEFT, padx=10)

    # ── タブ④ ────────────────────────────────────────────────

    def _build_tab4(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=1)

        pad = {"padx": 14, "pady": 6}

        basic = ttk.LabelFrame(container, text="メール送信の基本設定", padding=12)
        basic.grid(row=0, column=0, sticky="ew", **pad)
        basic.columnconfigure(1, weight=1)

        ttk.Label(basic, text="自分のメールアドレス\n（送信元）:", justify="left").grid(
            row=0, column=0, sticky="w", pady=5)
        ttk.Entry(basic, textvariable=self.sender_email, width=42).grid(
            row=0, column=1, padx=6, sticky="ew")
        ttk.Label(basic, text="例: yourname@gmail.com",
                  foreground="#888888", font=("Yu Gothic UI", 8)).grid(
            row=0, column=2, sticky="w", padx=(0, 4))

        ttk.Label(basic, text="Gmail アプリパスワード:", justify="left").grid(
            row=1, column=0, sticky="w", pady=5)
        pw_inner = ttk.Frame(basic)
        pw_inner.grid(row=1, column=1, padx=6, sticky="w")
        self._gmail_pw_entry = ttk.Entry(
            pw_inner, textvariable=self.sender_password, width=24, show="*")
        self._gmail_pw_entry.pack(side=tk.LEFT)
        ttk.Button(pw_inner, text="表示 / 非表示",
                   command=self._toggle_gmail_pw).pack(side=tk.LEFT, padx=6)

        pw_note = ttk.Frame(basic)
        pw_note.grid(row=2, column=0, columnspan=3, sticky="w", pady=(0, 8))
        ttk.Label(
            pw_note,
            text="⚠ Gmail アプリパスワードとは？\n"
                 "  通常のログインパスワードとは別に発行する 16 文字の専用コードです。\n"
                 "  Google アカウント → セキュリティ → 2段階認証を有効化 → アプリパスワード の順に設定してください。",
            foreground="#b05000",
            font=("Yu Gothic UI", 8),
            justify="left",
        ).pack(side=tk.LEFT)
        gmail_link = ttk.Label(
            pw_note,
            text="▶ 設定ページを開く",
            foreground="#0066cc", cursor="hand2",
            font=("Yu Gothic UI", 8, "underline"),
        )
        gmail_link.pack(side=tk.LEFT, padx=10)
        gmail_link.bind("<Button-1>", lambda e: webbrowser.open(_GMAIL_APP_PW_URL))

        ttk.Label(basic, text="送信先メールアドレス\n（受信者）:", justify="left").grid(
            row=3, column=0, sticky="w", pady=5)
        ttk.Entry(basic, textvariable=self.recipients, width=42).grid(
            row=3, column=1, padx=6, sticky="ew")
        ttk.Label(
            basic,
            text="複数人の場合はカンマ（,）で区切る\n例: a@example.com, b@example.com",
            foreground="#888888", font=("Yu Gothic UI", 8), justify="left",
        ).grid(row=3, column=2, sticky="w", padx=(0, 4))

        ttk.Label(basic, text="件名（メールの件名）:").grid(
            row=4, column=0, sticky="w", pady=5)
        ttk.Entry(basic, textvariable=self.email_subject, width=42).grid(
            row=4, column=1, padx=6, sticky="ew")

        ttk.Checkbutton(
            basic,
            text="議事録ファイル（.md）をメールに添付する",
            variable=self.attach_md,
        ).grid(row=5, column=0, columnspan=3, sticky="w", pady=(6, 2))

        smtp_toggle_frame = ttk.Frame(container)
        smtp_toggle_frame.grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 0))

        self._smtp_toggle_btn = ttk.Button(
            smtp_toggle_frame,
            text="▶  詳細設定（SMTP サーバー）　※ Gmail 以外のサービスを使う場合のみ変更が必要です",
            command=self._toggle_smtp_detail,
        )
        self._smtp_toggle_btn.pack(side=tk.LEFT)

        self._smtp_detail_frame = ttk.LabelFrame(
            container, text="詳細設定（SMTP サーバー設定）", padding=10)
        self._smtp_detail_frame.grid(row=2, column=0, sticky="ew", padx=14, pady=(2, 2))
        self._smtp_detail_frame.grid_remove()

        ttk.Label(self._smtp_detail_frame, text="SMTP サーバー:").grid(
            row=0, column=0, sticky="w", pady=3)
        ttk.Entry(self._smtp_detail_frame, textvariable=self.smtp_server, width=28).grid(
            row=0, column=1, padx=6, sticky="w")
        ttk.Label(self._smtp_detail_frame,
                  text="Gmail の場合: smtp.gmail.com",
                  foreground="#888888", font=("Yu Gothic UI", 8)).grid(
            row=0, column=2, sticky="w")

        ttk.Label(self._smtp_detail_frame, text="SMTP ポート:").grid(
            row=1, column=0, sticky="w", pady=3)
        ttk.Entry(self._smtp_detail_frame, textvariable=self.smtp_port, width=8).grid(
            row=1, column=1, padx=6, sticky="w")
        ttk.Label(
            self._smtp_detail_frame,
            text="465: SSL（Gmail 標準）  /  587: STARTTLS",
            foreground="#888888", font=("Yu Gothic UI", 8),
        ).grid(row=1, column=2, sticky="w")

        preview_frame = ttk.LabelFrame(
            container,
            text="送信メール本文プレビュー　※ ③ 議事録タブの内容がそのまま送信されます",
            padding=6)
        preview_frame.grid(row=3, column=0, sticky="nsew", padx=14, pady=6)
        container.rowconfigure(3, weight=1)

        self.email_preview = scrolledtext.ScrolledText(
            preview_frame, wrap=tk.WORD, height=8,
            font=("Yu Gothic UI", 9), state="disabled")
        self.email_preview.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=4, column=0, sticky="ew", padx=14, pady=6)

        ttk.Button(btn_frame, text="🔄  プレビューを更新",
                   command=self._update_email_preview).pack(side=tk.LEFT, padx=4)

        send_btn = tk.Button(
            btn_frame,
            text="📧  メールを送信する",
            command=self._send_email,
            bg="#27ae60", fg="white",
            font=("Yu Gothic UI", 11, "bold"),
            relief="flat",
            padx=18, pady=8,
            cursor="hand2",
        )
        send_btn.pack(side=tk.LEFT, padx=10)

        ttk.Label(btn_frame,
                  text="← 送信前に宛先・件名を必ず確認してください",
                  foreground="#777777", font=("Yu Gothic UI", 8)).pack(
            side=tk.LEFT, pady=4)

        self.send_status_var = tk.StringVar()
        ttk.Label(container, textvariable=self.send_status_var,
                  foreground="#27ae60",
                  font=("Yu Gothic UI", 10, "bold")).grid(row=5, column=0, pady=4)

    # ─────────────────────────────────────────────────────────
    # 録音イベントハンドラ
    # ─────────────────────────────────────────────────────────

    def _on_rec_mode_changed(self) -> None:
        """録音/録画モード切り替え時にモニター選択欄を表示・非表示にする"""
        if self._monitor_frame is None:
            return
        if self._rec_mode.get() == "video":
            self._monitor_frame.pack(fill=tk.X, pady=(8, 0))
            self._refresh_monitors()
        else:
            self._monitor_frame.pack_forget()

    def _on_monitor_selected(self, event=None) -> None:
        idx = self._monitor_combo.current()
        if 0 <= idx < len(self._rec_monitors):
            self._rec_monitor_idx.set(self._rec_monitors[idx]["index"])

    def _refresh_monitors(self) -> None:
        """モニター一覧を取得してコンボボックスに反映する"""
        self._rec_monitors = list_monitors()
        if self._monitor_combo is None:
            return
        names = [m["label"] for m in self._rec_monitors]
        self._monitor_combo["values"] = names if names else ["モニターが見つかりません"]
        if names:
            self._monitor_combo.current(0)
            self._on_monitor_selected()

    def _refresh_devices(self) -> None:
        """オーディオデバイス一覧を再取得してコンボボックスに反映する"""
        self._rec_devices = list_audio_devices()
        names = []
        for d in self._rec_devices:
            icon = "🔊" if d["is_loopback"] else "🎙"
            names.append(f"{icon} {d['name']}")
        self._device_combo["values"] = names
        if names:
            self._device_combo.current(0)
            self._on_device_selected()
        else:
            self._device_hint.config(
                text="デバイスが見つかりません。マイクや設定を確認してください。")

    def _on_device_selected(self, event=None) -> None:
        idx = self._device_combo.current()
        if idx < 0 or idx >= len(self._rec_devices):
            return
        self._rec_device_idx = self._rec_devices[idx]["index"]
        d = self._rec_devices[idx]
        if d["is_loopback"]:
            self._device_hint.config(
                text="🔊 PC から出る音全体（Zoom/Meet の相手の声など）を録音します。おすすめです。")
        else:
            self._device_hint.config(
                text="🎙 マイクに入る音（自分の声）を録音します。相手の声は録音されません。")

    def _toggle_recording(self) -> None:
        if self._recorder and self._recorder.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        if self._rec_device_idx is None:
            messagebox.showwarning("警告", "録音デバイスを選択してください")
            return

        is_video = self._rec_mode.get() == "video"

        if is_video and not is_video_available():
            messagebox.showwarning(
                "録画機能が使えません",
                "画面録画には mss と opencv-python が必要です。\n\n"
                "コマンドプロンプトで以下を実行してから再起動してください:\n\n"
                "    pip install mss opencv-python",
            )
            return

        try:
            if is_video:
                self._recorder = VideoRecorder()
                self._recorder.start(self._rec_device_idx, self._rec_monitor_idx.get())
            else:
                self._recorder = AudioRecorder()
                self._recorder.start(self._rec_device_idx)
        except Exception as e:
            messagebox.showerror("エラー", f"録音/録画を開始できませんでした:\n{e}")
            self._recorder = None
            return

        action = "録画" if is_video else "録音"
        self._rec_seconds = 0
        self._rec_timer_var.set("00:00")
        self._rec_btn.config(
            text=f"■  {action}を停止する",
            bg="#555555",
            activebackground="#333333",
        )
        self._rec_status_var.set(f"● {action}中...")
        self._set_status(f"{action}中... ミーティングが終わったら「■ {action}を停止する」を押してください")

        self._tick_timer()
        self._tick_meter()

    def _stop_recording(self) -> None:
        if not self._recorder:
            return
        self._rec_btn.config(state="disabled", text="保存中...")
        threading.Thread(target=self._stop_recording_thread, daemon=True).start()

    def _stop_recording_thread(self) -> None:
        try:
            path = self._recorder.stop(save_dir=self._rec_save_dir.get())

            def _done():
                self.recording_path.set(path)
                self._rec_btn.config(
                    state="normal",
                    text="●  録音を開始する",
                    bg="#e74c3c",
                    activebackground="#c0392b",
                )
                self._rec_status_var.set(f"✅ 保存完了: {os.path.basename(path)}")

                # 録画モードで ffmpeg なしの場合: 映像が別ファイルになる
                extra = getattr(self._recorder, "extra_video_path", None)
                if extra:
                    self._set_status(f"録画完了！音声: {os.path.basename(path)}  映像: {os.path.basename(extra)}")
                    self.notebook.select(_TAB_SETUP)
                    messagebox.showinfo(
                        "録画完了",
                        f"ファイルを保存しました:\n\n"
                        f"  🎵 音声（文字起こし用）:\n    {path}\n\n"
                        f"  🎬 映像（音声なし）:\n    {extra}\n\n"
                        "💡 映像と音声を 1 つの MP4 に合成するには ffmpeg をインストールしてください。\n\n"
                        "① タブへ移動しました。文字起こしを開始してください。"
                    )
                else:
                    label = "録画" if self._rec_mode.get() == "video" else "録音"
                    self._set_status(f"{label}完了！ファイルを保存しました → {path}")
                    self.notebook.select(_TAB_SETUP)
                    messagebox.showinfo(
                        f"{label}完了",
                        f"ファイルを保存しました:\n{path}\n\n"
                        "① タブへ移動しました。\n文字起こしを開始してください。"
                    )
            self.root.after(0, _done)

        except Exception as e:
            msg = str(e)
            def _err():
                self._rec_btn.config(
                    state="normal",
                    text="●  録音を開始する",
                    bg="#e74c3c",
                    activebackground="#c0392b",
                )
                self._rec_status_var.set("❌ 保存失敗")
                messagebox.showerror("エラー", f"録音/録画ファイルの保存に失敗しました:\n{msg}")
            self.root.after(0, _err)

    def _tick_timer(self) -> None:
        """1 秒ごとに録音タイマーを更新する"""
        if self._recorder and self._recorder.is_recording:
            self._rec_seconds += 1
            m, s = divmod(self._rec_seconds, 60)
            self._rec_timer_var.set(f"{m:02d}:{s:02d}")
            self.root.after(1000, self._tick_timer)

    def _tick_meter(self) -> None:
        """100 ms ごとに VU メーターを更新する"""
        if self._recorder and self._recorder.is_recording and self._meter_canvas:
            level = self._recorder.get_peak()
            w = self._meter_canvas.winfo_width()
            bar_w = max(4, int(w * level))
            color = (
                "#27ae60" if level < 0.60 else
                "#e67e22" if level < 0.85 else
                "#e74c3c"
            )
            self._meter_canvas.coords(self._meter_bar, 0, 2, bar_w, 20)
            self._meter_canvas.itemconfig(self._meter_bar, fill=color)
            self.root.after(100, self._tick_meter)
        elif self._meter_canvas:
            # 録音終了後メーターをリセット
            self._meter_canvas.coords(self._meter_bar, 0, 2, 0, 20)

    def _browse_save_dir(self) -> None:
        d = filedialog.askdirectory(title="録音ファイルの保存先フォルダを選択")
        if d:
            self._rec_save_dir.set(d)

    # ─────────────────────────────────────────────────────────
    # 表示切り替えヘルパー
    # ─────────────────────────────────────────────────────────

    def _toggle_openai_key(self) -> None:
        if self._openai_entry:
            self._openai_entry.config(
                show="" if self._openai_entry.cget("show") == "*" else "*")

    def _toggle_anthropic_key(self) -> None:
        if self._anthropic_entry:
            self._anthropic_entry.config(
                show="" if self._anthropic_entry.cget("show") == "*" else "*")

    def _toggle_gmail_pw(self) -> None:
        if self._gmail_pw_entry:
            self._gmail_pw_entry.config(
                show="" if self._gmail_pw_entry.cget("show") == "*" else "*")

    def _toggle_smtp_detail(self) -> None:
        if self._smtp_detail_frame.winfo_viewable():
            self._smtp_detail_frame.grid_remove()
            self._smtp_toggle_btn.config(
                text="▶  詳細設定（SMTP サーバー）　※ Gmail 以外のサービスを使う場合のみ変更が必要です")
        else:
            self._smtp_detail_frame.grid()
            self._smtp_toggle_btn.config(
                text="▼  詳細設定（SMTP サーバー）　※ Gmail 以外のサービスを使う場合のみ変更が必要です")

    # ─────────────────────────────────────────────────────────
    # 文字起こし・議事録イベントハンドラ
    # ─────────────────────────────────────────────────────────

    def _browse_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Zoom 録音ファイルを選択",
            filetypes=[
                ("音声・動画ファイル", "*.mp4 *.m4a *.wav *.mp3 *.webm *.ogg"),
                ("すべてのファイル", "*.*"),
            ],
        )
        if not path:
            return
        self.recording_path.set(path)
        basename = os.path.splitext(os.path.basename(path))[0]
        if not self.meeting_title.get():
            self.meeting_title.set(basename)
        if not self.email_subject.get():
            self.email_subject.set(
                f"【議事録】{self.meeting_date.get()}　{basename}"
            )

    def _start_transcription(self) -> None:
        path = self.recording_path.get()
        api_key = self.openai_api_key.get()
        if not path:
            messagebox.showwarning("警告", "録音ファイルを選択してください")
            return
        if not api_key:
            messagebox.showwarning("警告", "OpenAI API キーを入力してください")
            return
        self._set_status("文字起こし中... しばらくお待ちください")
        self.progress.start(10)
        threading.Thread(target=self._transcribe_thread, args=(path, api_key), daemon=True).start()

    def _transcribe_thread(self, path: str, api_key: str) -> None:
        try:
            result = transcribe(path, api_key)
            def _done():
                self.transcript_text.delete("1.0", tk.END)
                self.transcript_text.insert(tk.END, result)
                self._set_status("文字起こし完了！「② 文字起こし結果」タブで内容を確認してください")
                self.notebook.select(_TAB_TRANS)
                self.progress.stop()
            self.root.after(0, _done)
        except Exception as e:
            msg = str(e)
            def _err():
                self._set_status(f"文字起こしエラー: {msg}")
                messagebox.showerror("エラー", f"文字起こしに失敗しました:\n{msg}")
                self.progress.stop()
            self.root.after(0, _err)

    def _generate_minutes(self) -> None:
        transcript = self.transcript_text.get("1.0", tk.END).strip()
        api_key = self.anthropic_api_key.get()
        title = self.meeting_title.get()
        date = self.meeting_date.get()
        if not transcript:
            messagebox.showwarning("警告", "文字起こしテキストがありません")
            return
        if not api_key:
            messagebox.showwarning("警告", "Anthropic API キーを入力してください")
            return
        self._set_status("議事録を生成中... しばらくお待ちください")
        self.progress.start(10)
        threading.Thread(
            target=self._minutes_thread, args=(transcript, api_key, title, date), daemon=True
        ).start()

    def _minutes_thread(self, transcript: str, api_key: str, title: str, date: str) -> None:
        try:
            minutes = create_minutes(transcript, api_key, title, date)
            def _done():
                self.minutes_text.delete("1.0", tk.END)
                self.minutes_text.insert(tk.END, minutes)
                self._set_status("議事録生成完了！「③ 議事録」タブで内容を確認・編集してください")
                self.notebook.select(_TAB_MIN)
                self._update_email_preview()
                self.progress.stop()
            self.root.after(0, _done)
        except Exception as e:
            msg = str(e)
            def _err():
                self._set_status(f"議事録生成エラー: {msg}")
                messagebox.showerror("エラー", f"議事録の生成に失敗しました:\n{msg}")
                self.progress.stop()
            self.root.after(0, _err)

    def _save_transcript(self) -> None:
        text = self.transcript_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "保存するテキストがありません")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("テキストファイル", "*.txt")],
            initialfile=f"文字起こし_{self.meeting_date.get()}.txt",
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("保存完了", f"保存しました:\n{path}")

    def _save_minutes(self) -> None:
        text = self.minutes_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "保存する議事録がありません")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("テキストファイル", "*.txt")],
            initialfile=f"議事録_{self.meeting_date.get()}_{self.meeting_title.get() or '会議'}.md",
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("保存完了", f"保存しました:\n{path}")

    def _update_email_preview(self) -> None:
        minutes = self.minutes_text.get("1.0", tk.END).strip()
        self.email_preview.config(state="normal")
        self.email_preview.delete("1.0", tk.END)
        self.email_preview.insert(
            tk.END, minutes or "（③ 議事録タブで議事録を生成してからここに表示されます）")
        self.email_preview.config(state="disabled")

    def _send_email(self) -> None:
        minutes = self.minutes_text.get("1.0", tk.END).strip()
        recipients_raw = self.recipients.get().strip()
        if not minutes:
            messagebox.showwarning("警告", "送信する議事録がありません\n\n③ 議事録タブで議事録を生成してください")
            return
        if not recipients_raw:
            messagebox.showwarning("警告", "送信先メールアドレスを入力してください")
            return

        recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
        confirmed = messagebox.askyesno(
            "送信確認",
            f"以下の宛先に議事録を送信します:\n\n"
            + "\n".join(f"  {r}" for r in recipients)
            + f"\n\n件名: {self.email_subject.get()}\n\n送信しますか？",
        )
        if not confirmed:
            return

        smtp_server  = self.smtp_server.get()
        smtp_port    = self.smtp_port.get()
        sender_email = self.sender_email.get()
        sender_pw    = self.sender_password.get()
        subject      = self.email_subject.get()
        attach_md    = self.attach_md.get()
        title        = self.meeting_title.get() or "会議"
        date         = self.meeting_date.get()

        self.send_status_var.set("送信中...")
        self._set_status("メール送信中...")
        self.progress.start(10)
        threading.Thread(
            target=self._send_thread,
            args=(recipients, minutes, smtp_server, smtp_port,
                  sender_email, sender_pw, subject, attach_md, title, date),
            daemon=True,
        ).start()

    def _send_thread(
        self,
        recipients: list[str],
        minutes: str,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_pw: str,
        subject: str,
        attach_md: bool,
        title: str,
        date: str,
    ) -> None:
        tmp_path = None
        try:
            if attach_md:
                fd, tmp_path = tempfile.mkstemp(
                    suffix=".md", prefix=f"minutes_{date}_{title}_")
                os.close(fd)
                with open(tmp_path, "w", encoding="utf-8") as f:
                    f.write(minutes)

            send_email(
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                sender_email=sender_email,
                sender_password=sender_pw,
                recipients=recipients,
                subject=subject,
                body=minutes,
                attachment_path=tmp_path,
            )
            def _done():
                self.send_status_var.set("✅  送信完了！")
                self._set_status("メール送信完了！")
                messagebox.showinfo("送信完了", "議事録をチームにメールで送信しました！")
                self.progress.stop()
            self.root.after(0, _done)
        except Exception as e:
            msg = str(e)
            def _err():
                self.send_status_var.set("❌  送信失敗")
                self._set_status(f"メール送信エラー: {msg}")
                messagebox.showerror("エラー", f"メール送信に失敗しました:\n{msg}")
                self.progress.stop()
            self.root.after(0, _err)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)
        self.root.update_idletasks()
