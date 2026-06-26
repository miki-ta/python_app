"""
create_homepage.py
-------------------
Zoom 議事録ツールの説明ページ（index.html）を生成してブラウザで開く。

使い方:
    python src/Zoom_minutes/create_homepage.py
"""

import os
import webbrowser

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "index.html")

HTML = """\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zoom 議事録 自動作成ツール｜はじめてガイド</title>
<style>
/* ── リセット & 変数 ───────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --blue:    #2a7ae4;
  --blue-lt: #e8f0fc;
  --green:   #27ae60;
  --grn-lt:  #e8f8ee;
  --orange:  #e67e22;
  --orn-lt:  #fef5eb;
  --red:     #c0392b;
  --red-lt:  #fdf2f2;
  --dark:    #1a1a2e;
  --text:    #2d2d2d;
  --muted:   #666;
  --bg:      #f7f8fc;
  --card:    #ffffff;
  --border:  #e0e4ef;
  --radius:  12px;
}

/* ── ベース ──────────────────────────────────────────────────── */
html { scroll-behavior: smooth; }
body {
  font-family: "Yu Gothic UI", "Hiragino Sans", "Meiryo", sans-serif;
  color: var(--text);
  background: var(--bg);
  line-height: 1.85;
  font-size: 15px;
}
a { color: var(--blue); }
a:hover { text-decoration: underline; }
strong { font-weight: 700; }

/* ── レイアウト ──────────────────────────────────────────────── */
.container { max-width: 860px; margin: 0 auto; padding: 0 20px; }
section { padding: 60px 0; }
section:nth-of-type(even) { background: #fff; }

/* ── ナビゲーション ──────────────────────────────────────────── */
nav {
  background: var(--dark);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0 20px;
}
nav ul {
  max-width: 860px;
  margin: 0 auto;
  display: flex;
  list-style: none;
  gap: 0;
}
nav a {
  display: block;
  color: rgba(255,255,255,.75);
  padding: 14px 16px;
  font-size: .88rem;
  text-decoration: none;
  transition: color .2s;
}
nav a:hover { color: #fff; }

/* ── ヘッダー ────────────────────────────────────────────────── */
header {
  background: linear-gradient(140deg, #1a1a2e 0%, #16213e 55%, #0f3460 100%);
  color: #fff;
  padding: 80px 20px 72px;
  text-align: center;
}
header .tagline {
  display: inline-block;
  background: rgba(255,255,255,.12);
  border: 1px solid rgba(255,255,255,.25);
  border-radius: 999px;
  padding: 5px 18px;
  font-size: .82rem;
  letter-spacing: .08em;
  margin-bottom: 22px;
}
header h1 { font-size: 2.4rem; font-weight: 900; line-height: 1.3; margin-bottom: 12px; }
header h1 em { color: #5ba3f5; font-style: normal; }
header .sub {
  font-size: 1.05rem;
  color: rgba(255,255,255,.75);
  max-width: 600px;
  margin: 0 auto 10px;
  line-height: 1.7;
}
header .note {
  font-size: .88rem;
  color: rgba(255,255,255,.5);
  margin-bottom: 32px;
}
.btn {
  display: inline-block;
  padding: 13px 30px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity .18s, transform .18s;
  text-decoration: none;
}
.btn:hover { opacity: .86; transform: translateY(-1px); text-decoration: none; }
.btn-blue  { background: var(--blue);  color: #fff; }
.btn-white { background: #fff; color: var(--dark); margin-left: 10px; }

/* ── セクションタイトル ──────────────────────────────────────── */
.sec-head { text-align: center; margin-bottom: 44px; }
.sec-head .chip {
  display: inline-block;
  background: var(--blue);
  color: #fff;
  border-radius: 4px;
  padding: 3px 12px;
  font-size: .75rem;
  font-weight: 700;
  letter-spacing: .08em;
  margin-bottom: 12px;
}
.sec-head h2 { font-size: 1.75rem; font-weight: 800; color: var(--dark); margin-bottom: 8px; }
.sec-head p  { color: var(--muted); font-size: .97rem; }

/* ── おすすめ対象 ────────────────────────────────────────────── */
.target-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
.target-card {
  background: var(--blue-lt);
  border: 1px solid #c3d9fb;
  border-radius: var(--radius);
  padding: 20px 18px;
  font-size: .93rem;
  line-height: 1.6;
}
.target-card .icon { font-size: 2rem; display: block; margin-bottom: 8px; }

/* ── ビフォー/アフター ───────────────────────────────────────── */
.ba-wrap {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 12px;
  align-items: center;
}
.ba-box {
  border-radius: var(--radius);
  padding: 22px 20px;
}
.ba-before { background: var(--red-lt); border: 1px solid #f5c0bb; }
.ba-after  { background: var(--grn-lt); border: 1px solid #a8e6c0; }
.ba-label  { font-size: .78rem; font-weight: 700; letter-spacing: .08em; margin-bottom: 10px; }
.ba-before .ba-label { color: var(--red); }
.ba-after  .ba-label { color: var(--green); }
.ba-box ul { padding-left: 20px; font-size: .93rem; line-height: 2; }
.ba-arrow  { font-size: 2.4rem; color: #aaa; text-align: center; }

/* ── フロー図 ────────────────────────────────────────────────── */
.flow-wrap {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 48px;
}
.flow-box {
  background: #fff;
  border: 2px solid var(--blue);
  border-radius: var(--radius);
  padding: 14px 20px;
  text-align: center;
  min-width: 140px;
  box-shadow: 0 2px 8px rgba(42,122,228,.1);
}
.flow-box .fn { font-size: .72rem; color: var(--blue); font-weight: 800; letter-spacing: .05em; }
.flow-box .ft { font-size: .95rem; font-weight: 700; color: var(--dark); margin: 3px 0; }
.flow-box .fs { font-size: .78rem; color: var(--muted); }
.flow-arr { font-size: 1.8rem; color: #bbb; }

/* ── ステップ ────────────────────────────────────────────────── */
.step-list { display: flex; flex-direction: column; gap: 28px; }
.step {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px 22px;
  box-shadow: 0 1px 4px rgba(0,0,0,.05);
}
.step-num {
  flex-shrink: 0;
  width: 44px; height: 44px;
  border-radius: 50%;
  background: var(--blue);
  color: #fff;
  font-size: 1.15rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}
.step-body h3 { font-size: 1.08rem; font-weight: 700; margin-bottom: 6px; color: var(--dark); }
.step-body p  { font-size: .93rem; color: #444; }
.step-body .detail {
  margin-top: 10px;
  font-size: .88rem;
  color: var(--muted);
  background: var(--bg);
  border-radius: 8px;
  padding: 10px 14px;
  line-height: 1.8;
}

/* ── 用語解説ボックス ────────────────────────────────────────── */
.term-box {
  background: var(--blue-lt);
  border: 1px solid #c3d9fb;
  border-left: 4px solid var(--blue);
  border-radius: 0 8px 8px 0;
  padding: 14px 18px;
  margin: 12px 0;
  font-size: .9rem;
}
.term-box .term-head { font-weight: 700; color: var(--blue); margin-bottom: 4px; }
.term-box p { color: #444; line-height: 1.75; }

/* ── 警告・ヒントボックス ────────────────────────────────────── */
.warn-box {
  background: var(--red-lt);
  border: 1px solid #f5c0bb;
  border-left: 4px solid var(--red);
  border-radius: 0 8px 8px 0;
  padding: 12px 16px;
  margin: 10px 0;
  font-size: .88rem;
  color: #7a1a1a;
  line-height: 1.75;
}
.hint-box {
  background: var(--grn-lt);
  border: 1px solid #a8e6c0;
  border-left: 4px solid var(--green);
  border-radius: 0 8px 8px 0;
  padding: 12px 16px;
  margin: 10px 0;
  font-size: .88rem;
  color: #0e4a25;
  line-height: 1.75;
}
.orn-box {
  background: var(--orn-lt);
  border: 1px solid #fcd7a8;
  border-left: 4px solid var(--orange);
  border-radius: 0 8px 8px 0;
  padding: 12px 16px;
  margin: 10px 0;
  font-size: .88rem;
  color: #6b3700;
  line-height: 1.75;
}

/* ── コードブロック ──────────────────────────────────────────── */
pre {
  background: #1e2233;
  color: #e8eaf6;
  border-radius: 8px;
  padding: 16px 20px;
  overflow-x: auto;
  font-family: "Consolas", "Courier New", monospace;
  font-size: .88rem;
  line-height: 1.65;
  margin: 10px 0;
}
code {
  background: #eef1ff;
  color: #2a4ab5;
  padding: 1px 6px;
  border-radius: 4px;
  font-family: "Consolas", "Courier New", monospace;
  font-size: .87rem;
}
pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
.cmt { color: #8896b3; }
.key { color: #79d7f8; }
.val { color: #c3e88d; }

/* ── チェックリスト ──────────────────────────────────────────── */
.checklist { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.checklist li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
  font-size: .93rem;
}
.checklist .cb {
  flex-shrink: 0;
  width: 22px; height: 22px;
  border: 2px solid var(--border);
  border-radius: 5px;
  margin-top: 1px;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  background: #fff;
  transition: background .15s;
}
.checklist .cb:checked { background: var(--blue); border-color: var(--blue); }
.checklist .cb:checked + span::before { content: ""; }
.checklist li span { line-height: 1.7; color: #333; }
.checklist li .sub { display: block; font-size: .82rem; color: var(--muted); margin-top: 2px; }

/* ── 番号付きサブステップ ────────────────────────────────────── */
.substep-list { list-style: none; display: flex; flex-direction: column; gap: 8px; margin-top: 10px; }
.substep-list li {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  font-size: .9rem;
  line-height: 1.7;
}
.substep-list .sn {
  flex-shrink: 0;
  width: 24px; height: 24px;
  background: var(--dark);
  color: #fff;
  border-radius: 50%;
  font-size: .75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}

/* ── FAQ ─────────────────────────────────────────────────────── */
.faq { display: flex; flex-direction: column; gap: 12px; }
.faq-item {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}
.faq-q {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  font-weight: 700;
  font-size: .95rem;
  cursor: pointer;
  user-select: none;
}
.faq-q .q-badge {
  flex-shrink: 0;
  width: 28px; height: 28px;
  background: var(--blue);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: .82rem;
  font-weight: 800;
}
.faq-q .faq-arr { margin-left: auto; color: #aaa; transition: transform .2s; }
.faq-item.open .faq-arr { transform: rotate(180deg); }
.faq-a {
  display: none;
  padding: 0 20px 18px 62px;
  font-size: .92rem;
  color: #444;
  line-height: 1.85;
}
.faq-item.open .faq-a { display: block; }

/* ── トラブル表 ──────────────────────────────────────────────── */
.trouble-table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.trouble-table th {
  background: var(--dark);
  color: #fff;
  padding: 12px 16px;
  text-align: left;
  font-weight: 700;
}
.trouble-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
  line-height: 1.75;
}
.trouble-table tr:nth-child(even) td { background: var(--bg); }
.trouble-table .prob { font-weight: 700; color: var(--red); }

/* ── フッター ────────────────────────────────────────────────── */
footer {
  background: var(--dark);
  color: rgba(255,255,255,.5);
  text-align: center;
  padding: 36px 20px;
  font-size: .84rem;
  line-height: 2;
}
footer a { color: rgba(255,255,255,.65); }
</style>
</head>
<body>

<!-- ━━━ ナビ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->
<nav>
  <ul>
    <li><a href="#about">このツールとは</a></li>
    <li><a href="#howto">使い方</a></li>
    <li><a href="#checklist">準備チェック</a></li>
    <li><a href="#setup">セットアップ</a></li>
    <li><a href="#faq">よくある質問</a></li>
    <li><a href="#trouble">困ったときは</a></li>
  </ul>
</nav>

<!-- ━━━ ヘッダー ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->
<header>
  <div class="tagline">🤖 AI が議事録を自動で作ります</div>
  <h1>Zoom 議事録<br><em>自動作成ツール</em></h1>
  <p class="sub">
    録音ファイルを選ぶだけで、AI が文字起こし・議事録作成・メール送信を<br>
    すべて自動でやってくれます。
  </p>
  <p class="note">※ プログラミングの知識は不要です。操作はすべてボタンを押すだけです。</p>
  <a class="btn btn-blue" href="#setup">セットアップを始める →</a>
  <a class="btn btn-white" href="#about">詳しく見る</a>
</header>

<!-- ━━━ このツールとは ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->
<section id="about">
  <div class="container">
    <div class="sec-head">
      <div class="chip">ABOUT</div>
      <h2>このツールとは？</h2>
      <p>会議の後に毎回やっている「あの作業」を全部自動にします</p>
    </div>

    <!-- こんな人におすすめ -->
    <h3 style="font-size:1.1rem; font-weight:700; margin-bottom:16px;">こんな方におすすめ</h3>
    <div class="target-grid" style="margin-bottom:44px;">
      <div class="target-card">
        <span class="icon">😓</span>
        会議後の議事録作成に<strong>毎回 1〜2 時間かかって</strong>いる方
      </div>
      <div class="target-card">
        <span class="icon">🎙️</span>
        Zoom を録音しているけど<strong>文字起こしが面倒</strong>な方
      </div>
      <div class="target-card">
        <span class="icon">📨</span>
        議事録を<strong>チーム全員にメールで送る</strong>のが手間な方
      </div>
      <div class="target-card">
        <span class="icon">🔰</span>
        AI ツールを使ってみたいけど<strong>難しそうで躊躇している</strong>方
      </div>
    </div>

    <!-- ビフォー/アフター -->
    <h3 style="font-size:1.1rem; font-weight:700; margin-bottom:16px;">使う前と使った後の違い</h3>
    <div class="ba-wrap">
      <div class="ba-box ba-before">
        <div class="ba-label">⏰ 今まで（手作業）</div>
        <ul>
          <li>録音を聞き返しながら<br>文字起こし（30〜60 分）</li>
          <li>内容をまとめて<br>議事録を書く（30 分）</li>
          <li>メールで全員に送る（10 分）</li>
          <li>合計 <strong>1〜2 時間</strong></li>
        </ul>
      </div>
      <div class="ba-arrow">→</div>
      <div class="ba-box ba-after">
        <div class="ba-label">✅ このツールを使うと</div>
        <ul>
          <li>録音ファイルを選ぶ（1 分）</li>
          <li>AI が自動で文字起こし（1〜3 分）</li>
          <li>AI が自動で議事録を作成（30 秒）</li>
          <li>ボタン一つでメール送信（1 分）</li>
          <li>合計 <strong>5〜10 分</strong></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<!-- ━━━ 使い方（フロー） ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->
<section id="howto">
  <div class="container">
    <div class="sec-head">
      <div class="chip">HOW TO USE</div>
      <h2>アプリのタブを順番に操作するだけ</h2>
      <p>全部で 5 つのタブがあります。「🎙 録音」タブは任意です。<br>
      すでに録音ファイルがある場合は録音タブをとばして ① タブから始めてください。</p>
    </div>

    <!-- フロー図 -->
    <div class="flow-wrap">
      <div class="flow-box" style="border-style:dashed; border-color:#9ab4dc;">
        <div class="fn" style="color:#6699cc;">🎙 録音タブ（任意）</div>
        <div class="ft">PC で録音する</div>
        <div class="fs">Zoom / Meet の<br>音声を直接録音</div>
      </div>
      <div class="flow-arr">→</div>
      <div class="flow-box">
        <div class="fn">STEP 1  ①タブ</div>
        <div class="ft">ファイルを選ぶ</div>
        <div class="fs">録音ファイルと<br>APIキーを入力</div>
      </div>
      <div class="flow-arr">→</div>
      <div class="flow-box">
        <div class="fn">STEP 2  ②タブ</div>
        <div class="ft">文字起こしを確認</div>
        <div class="fs">AIが変換した<br>テキストを確認・修正</div>
      </div>
      <div class="flow-arr">→</div>
      <div class="flow-box">
        <div class="fn">STEP 3  ③タブ</div>
        <div class="ft">議事録を確認</div>
        <div class="fs">AIが作成した<br>議事録を確認・修正</div>
      </div>
      <div class="flow-arr">→</div>
      <div class="flow-box">
        <div class="fn">STEP 4  ④タブ</div>
        <div class="ft">メールで送信</div>
        <div class="fs">チームに<br>議事録を共有</div>
      </div>
    </div>

    <!-- 各ステップ詳細 -->
    <div class="step-list">

      <div class="step" style="border-left: 4px solid #9ab4dc;">
        <div class="step-num" style="background:#6699cc; font-size:.85rem;">🎙</div>
        <div class="step-body">
          <h3>🎙 録音タブ（任意）：PC 上でそのまま録音する</h3>
          <p>Zoom や Google Meet の会議中に、このアプリで PC の音声を直接録音できます。</p>
          <ul class="substep-list" style="margin: 8px 0;">
            <li><span class="sn">1</span><span>Zoom または Google Meet でミーティングを開始する</span></li>
            <li><span class="sn">2</span><span>「録音デバイス」から「🔊 ステレオ ミキサー」を選ぶ（PC 全体の音を録音する場合）</span></li>
            <li><span class="sn">3</span><span>「● 録音を開始する」を押す</span></li>
            <li><span class="sn">4</span><span>会議が終わったら「■ 録音を停止する」を押す</span></li>
            <li><span class="sn">5</span><span>自動的に ① タブへ移動するので、そのまま文字起こしを開始する</span></li>
          </ul>
          <div class="detail">
            📌 <strong>このタブは必須ではありません。</strong>すでに Zoom アプリで録音した MP4・M4A・WAV・MP3 ファイルがある場合は、このタブをとばして ① タブへ直接進んでください。<br>
            📌 録音機能には追加ライブラリが必要です。使い方は下の「セットアップ手順 B」をご確認ください。
          </div>
        </div>
      </div>

      <div class="step">
        <div class="step-num">1</div>
        <div class="step-body">
          <h3>① タブ：録音ファイルを選んで、APIキーを入力する</h3>
          <p>このタブには 3 つのサブステップがあります。上から順番に入力してください。</p>
          <ul class="substep-list" style="margin: 8px 0;">
            <li><span class="sn">1</span><span>「📂 ファイルを選ぶ」を押して録音ファイルを選ぶ<br>
            <small style="color:#888;">「🎙 録音」タブで録音した場合はすでに自動入力されています。</small></span></li>
            <li><span class="sn">2</span><span>会議名と日時を確認する（省略可・ファイル選択時に自動入力されます）</span></li>
            <li><span class="sn">3</span><span>OpenAI と Anthropic の API キーを入力する</span></li>
          </ul>
          <p>入力が終わったら「▶ 文字起こしを開始する」を押してください。</p>
          <div class="detail">
            📌 API キーとは何か → <a href="#apikey">こちらをご確認ください</a><br>
            ⏱ 処理には音声の長さに応じて <strong>1〜5 分</strong>かかります。完了するまで画面を閉じないでください。
          </div>
        </div>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <div class="step-body">
          <h3>② タブ：文字起こしの内容を確認・修正する</h3>
          <p>AI が音声をテキストに変換した結果が表示されます。<br>
          内容を確認して、間違いがあれば直接クリックして修正できます。</p>
          <div class="detail">
            📌 <strong>人名や専門用語の間違いが多い箇所</strong>は、ここで修正してから次へ進むと議事録の精度が上がります。<br>
            📌 問題なければそのまま「▶ 議事録を自動生成する」を押してください。
          </div>
        </div>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <div class="step-body">
          <h3>③ タブ：AI が作成した議事録を確認・編集する</h3>
          <p>Claude（AI）が文字起こしをもとに、議事録を自動で作成します。<br>
          「議題・決定事項・アクションアイテム・次回会議日程」などが含まれます。</p>
          <div class="detail">
            📌 内容はクリックして自由に編集できます。<br>
            📌 「💾 議事録をファイルに保存」で手元に保存することもできます。<br>
            📌 メールで送らない場合はここで作業完了です。
          </div>
        </div>
      </div>
      <div class="step">
        <div class="step-num">4</div>
        <div class="step-body">
          <h3>④ タブ：チームへメールで議事録を送る</h3>
          <p>送信先のメールアドレスを入力して「📧 メールを送信する」を押すと、<br>
          議事録が HTML メール（見やすい形式）で自動送信されます。</p>
          <div class="detail">
            📌 <strong>送信前に宛先・件名を必ず確認してください。</strong><br>
            📌 複数人に送る場合は、メールアドレスをカンマ（,）で区切って入力します。<br>
            　　例: <code>tanaka@example.com, suzuki@example.com</code>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ━━━ 準備チェックリスト ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->
<section id="checklist">
  <div class="container">
    <div class="sec-head">
      <div class="chip">CHECKLIST</div>
      <h2>セットアップ前の準備チェック</h2>
      <p>はじめる前に以下をすべて確認してください。チェックを入れながら進めましょう。</p>
    </div>

    <ul class="checklist">
      <li>
        <input type="checkbox" class="cb" id="c1">
        <span>
          <strong>Python がインストールされている</strong>
          <span class="sub">
            コマンドプロンプトで <code>python --version</code> と入力して「Python 3.x.x」と表示されれば OK。<br>
            表示されない場合は <a href="https://www.python.org/downloads/" target="_blank">python.org</a> からインストールしてください（バージョン 3.10 以上）。
          </span>
        </span>
      </li>
      <li>
        <input type="checkbox" class="cb" id="c2">
        <span>
          <strong>OpenAI のアカウントを作って API キーを取得している</strong>
          <span class="sub">
            → <a href="https://platform.openai.com/api-keys" target="_blank">platform.openai.com/api-keys</a> で取得できます。<br>
            「sk-」で始まる長い文字列がキーです。コピーしてメモ帳などに保存しておきましょう。
          </span>
        </span>
      </li>
      <li>
        <input type="checkbox" class="cb" id="c3">
        <span>
          <strong>Anthropic のアカウントを作って API キーを取得している</strong>
          <span class="sub">
            → <a href="https://console.anthropic.com/" target="_blank">console.anthropic.com</a> で取得できます。<br>
            「sk-ant-」で始まる長い文字列がキーです。
          </span>
        </span>
      </li>
      <li>
        <input type="checkbox" class="cb" id="c4">
        <span>
          <strong>Gmail アプリパスワードを発行している（メール送信を使う場合のみ）</strong>
          <span class="sub">
            → 取得方法は <a href="#gmail-pw">こちら</a> で詳しく説明しています。<br>
            メール送信を使わない場合は不要です。
          </span>
        </span>
      </li>
      <li>
        <input type="checkbox" class="cb" id="c5">
        <span>
          <strong>Zoom で録音したファイル（MP4・M4A・WAV・MP3 のいずれか）が手元にある</strong>
          <span class="sub">
            Zoom アプリでローカル録音すると「Documents/Zoom」などのフォルダに保存されます。
          </span>
        </span>
      </li>
    </ul>

    <div class="hint-box" style="margin-top:20px;">
      ✅ 上記がすべてチェックできたら、下の「セットアップ手順」に進んでください！
    </div>
  </div>
</section>

<!-- ━━━ セットアップ手順 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->
<section id="setup">
  <div class="container">
    <div class="sec-head">
      <div class="chip">SETUP</div>
      <h2>セットアップ手順</h2>
      <p>初回のみ必要な作業です。順番に実施してください。</p>
    </div>

    <div class="step-list">

      <!-- STEP A -->
      <div class="step">
        <div class="step-num" style="background:#555;">A</div>
        <div class="step-body">
          <h3>コマンドプロンプト（ターミナル）を開く</h3>
          <p>以下の手順でコマンドプロンプトを開きます。</p>
          <ul class="substep-list">
            <li><span class="sn">1</span><span>Windows キー + R を押す</span></li>
            <li><span class="sn">2</span><span>「cmd」と入力して Enter を押す</span></li>
            <li><span class="sn">3</span><span>黒い画面（コマンドプロンプト）が開けば OK</span></li>
          </ul>
          <div class="hint-box" style="margin-top:10px;">
            💡 Mac の方は「アプリケーション → ユーティリティ → ターミナル」を開いてください。
          </div>
        </div>
      </div>

      <!-- STEP B -->
      <div class="step">
        <div class="step-num" style="background:#555;">B</div>
        <div class="step-body">
          <h3>必要なライブラリをインストールする</h3>
          <p>コマンドプロンプトに以下を<strong>そのままコピー&amp;ペースト</strong>して Enter を押してください。</p>
          <pre>pip install openai anthropic python-dotenv</pre>
          <div class="detail">
            「ライブラリ」とは、このツールが動くために必要な追加プログラムのことです。<br>
            インストールには 1〜2 分かかります。画面に文字がたくさん流れますが、最後に
            「Successfully installed」と表示されれば完了です。
          </div>
          <div class="hint-box" style="margin-top:8px;">
            💡 <strong>「🎙 録音」タブでアプリ内から直接録音したい場合は、追加で以下も実行してください。</strong><br>
            <pre style="margin:8px 0 4px;">pip install sounddevice numpy</pre>
            インストール後にアプリを再起動すると録音機能が使えるようになります。<br>
            インストールしなくても、既存の録音ファイルを使う場合はこのステップは不要です。
          </div>
          <div class="orn-box" style="margin-top:8px;">
            ⚠ 25MB を超える録音ファイルを使いたい場合は、追加で以下も実行してください。<br>
            <code>pip install pydub</code>（別途 ffmpeg のインストールも必要です）
          </div>
        </div>
      </div>

      <!-- STEP C -->
      <div class="step">
        <div class="step-num" style="background:#555;">C</div>
        <div class="step-body">
          <h3>設定ファイル（.env）を作成する</h3>
          <p>
            API キーなどの設定を保存するファイルを作ります。
            <code>Zoom_minutes</code> フォルダの中にある <code>.env.example</code> を
            <strong>同じフォルダ内に「.env」という名前でコピー</strong>してください。
          </p>
          <ul class="substep-list" style="margin-top:12px;">
            <li><span class="sn">1</span><span><code>.env.example</code> を右クリック → コピー</span></li>
            <li><span class="sn">2</span><span>同じフォルダに貼り付け</span></li>
            <li><span class="sn">3</span><span>ファイル名を「<code>.env.example</code>」から「<code>.env</code>」に変更する</span></li>
            <li><span class="sn">4</span><span>メモ帳で開いて、API キーとメールの情報を入力して保存する</span></li>
          </ul>
          <pre><span class="cmt"># APIキー（「sk-」で始まる文字列をそのまま貼り付ける）</span>
<span class="key">OPENAI_API_KEY</span>=<span class="val">sk-ここにOpenAIのAPIキーを貼り付ける</span>
<span class="key">ANTHROPIC_API_KEY</span>=<span class="val">sk-ant-ここにAnthropicのAPIキーを貼り付ける</span>

<span class="cmt"># メール設定（メール送信を使う場合のみ入力）</span>
<span class="key">SMTP_SERVER</span>=<span class="val">smtp.gmail.com</span>
<span class="key">SMTP_PORT</span>=<span class="val">465</span>
<span class="key">SENDER_EMAIL</span>=<span class="val">あなたのアドレス@gmail.com</span>
<span class="key">SENDER_PASSWORD</span>=<span class="val">xxxx xxxx xxxx xxxx</span>
<span class="key">RECIPIENTS</span>=<span class="val">送信先@example.com</span></pre>

          <div class="term-box" style="margin-top:12px;">
            <div class="term-head">📁 .env ファイルとは？</div>
            <p>
              API キーやパスワードなどの「秘密の情報」を保存しておくファイルです。<br>
              一度入力しておくと、次回からアプリを起動したときに自動で読み込まれるので、毎回入力する手間が省けます。
            </p>
          </div>
          <div class="warn-box" style="margin-top:8px;">
            ⚠ <strong>.env ファイルは絶対に他人に見せないでください。</strong>
            API キーが漏れると、あなたのアカウントが不正利用される恐れがあります。
            Git を使っている場合は <code>.gitignore</code> に <code>.env</code> を追加してください。
          </div>
        </div>
      </div>

      <!-- STEP D -->
      <div class="step">
        <div class="step-num" style="background:#555;">D</div>
        <div class="step-body">
          <h3>アプリを起動する</h3>
          <p>コマンドプロンプトで、プロジェクトのフォルダに移動してから以下を実行します。</p>
          <pre>python src/Zoom_minutes/run_zoom_minutes.py</pre>
          <div class="hint-box" style="margin-top:8px;">
            ✅ ウィンドウ（GUI）が開けばセットアップ完了です！あとは画面の指示に従って操作するだけです。
          </div>
        </div>
      </div>
    </div>

    <!-- Gmail アプリパスワードの取得方法 -->
    <div id="gmail-pw" style="margin-top:44px;">
      <h3 style="font-size:1.2rem; font-weight:800; margin-bottom:16px;">
        📬 Gmail アプリパスワードの取得方法
      </h3>
      <div class="orn-box" style="margin-bottom:16px;">
        ⚠ 「アプリパスワード」とは、通常の Gmail ログインパスワードとは<strong>まったく別の 16 文字のコード</strong>です。<br>
        Google が「このアプリを信頼する」ために発行する専用パスワードです。
      </div>
      <div class="step-list">
        <div class="step" style="padding:16px 20px;">
          <div class="step-num" style="width:32px;height:32px;font-size:.9rem;">1</div>
          <div class="step-body">
            <h3 style="font-size:.97rem;">2 段階認証を有効にする</h3>
            <p><a href="https://myaccount.google.com/security" target="_blank">Google アカウント → セキュリティ</a> を開き、「2 段階認証プロセス」をオンにします。</p>
          </div>
        </div>
        <div class="step" style="padding:16px 20px;">
          <div class="step-num" style="width:32px;height:32px;font-size:.9rem;">2</div>
          <div class="step-body">
            <h3 style="font-size:.97rem;">アプリパスワードのページを開く</h3>
            <p>
              <a href="https://myaccount.google.com/apppasswords" target="_blank">myaccount.google.com/apppasswords</a> を開きます。<br>
              （2 段階認証を有効にしてから 5 分ほど待つと表示されます）
            </p>
          </div>
        </div>
        <div class="step" style="padding:16px 20px;">
          <div class="step-num" style="width:32px;height:32px;font-size:.9rem;">3</div>
          <div class="step-body">
            <h3 style="font-size:.97rem;">アプリパスワードを発行する</h3>
            <p>
              「アプリを選択」欄に「<strong>Zoom 議事録ツール</strong>」など好きな名前を入力して「作成」を押します。<br>
              表示された <strong>16 文字のコード</strong>（xxxx xxxx xxxx xxxx の形式）をコピーして .env の <code>SENDER_PASSWORD</code> に貼り付けます。
            </p>
            <div class="warn-box">
              ⚠ このコードは一度しか表示されません。<strong>必ずコピーして保存</strong>してください。
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- API キーとは -->
    <div id="apikey" style="margin-top:44px;">
      <h3 style="font-size:1.2rem; font-weight:800; margin-bottom:16px;">
        🔑 API キーとは何ですか？
      </h3>
      <div class="term-box">
        <div class="term-head">かんたんに説明すると…</div>
        <p>
          API キーは「<strong>AI サービスへの会員証（ID カード）</strong>」のようなものです。<br>
          このツールが OpenAI や Anthropic の AI を使うとき、「あなたの代わりに使っています」と証明するために必要です。<br>
          AI の利用料金（従量制）はあなたのアカウントに請求されます。
        </p>
      </div>
      <div style="margin-top:12px; display:grid; grid-template-columns:1fr 1fr; gap:12px;">
        <div style="background:#fff; border:1px solid var(--border); border-radius:10px; padding:18px;">
          <strong style="color:var(--blue);">OpenAI API キー</strong>
          <ul style="margin-top:8px; padding-left:18px; font-size:.9rem; line-height:1.9; color:#444;">
            <li>用途: 音声の文字起こし（Whisper）</li>
            <li>形式: <code>sk-</code> で始まる文字列</li>
            <li>取得先: <a href="https://platform.openai.com/api-keys" target="_blank">platform.openai.com</a></li>
            <li>料金目安: 1 時間の録音で約 10〜30 円</li>
          </ul>
        </div>
        <div style="background:#fff; border:1px solid var(--border); border-radius:10px; padding:18px;">
          <strong style="color:#8e44ad;">Anthropic API キー</strong>
          <ul style="margin-top:8px; padding-left:18px; font-size:.9rem; line-height:1.9; color:#444;">
            <li>用途: 議事録の自動生成（Claude）</li>
            <li>形式: <code>sk-ant-</code> で始まる文字列</li>
            <li>取得先: <a href="https://console.anthropic.com/" target="_blank">console.anthropic.com</a></li>
            <li>料金目安: 1 回の議事録生成で約 5〜20 円</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ━━━ よくある質問 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->
<section id="faq">
  <div class="container">
    <div class="sec-head">
      <div class="chip">FAQ</div>
      <h2>よくある質問</h2>
    </div>
    <div class="faq">

      <div class="faq-item">
        <div class="faq-q">
          <span class="q-badge">Q</span>
          無料で使えますか？
          <span class="faq-arr">▼</span>
        </div>
        <div class="faq-a">
          このツール自体は無料です。ただし、文字起こしに <strong>OpenAI</strong>、議事録生成に <strong>Anthropic</strong> の AI を使うため、
          それぞれのサービスの利用料金がかかります（使った分だけ請求される従量制です）。<br><br>
          目安として、1 時間の会議 1 回あたり合計 <strong>20〜100 円程度</strong>です（録音の長さや内容量による）。
          最初にカード情報を登録して、利用限度額を設定しておくと安心です。
        </div>
      </div>

      <div class="faq-item">
        <div class="faq-q">
          <span class="q-badge">Q</span>
          Python って何ですか？インストールが難しいですか？
          <span class="faq-arr">▼</span>
        </div>
        <div class="faq-a">
          Python はプログラミング言語の一つで、このツールを動かすために必要なソフトウェアです。<br>
          インストールは難しくありません。<a href="https://www.python.org/downloads/" target="_blank">python.org/downloads</a> にアクセスして
          「Download Python」ボタンを押すだけです。インストーラーが自動でセットアップしてくれます。<br><br>
          ⚠ インストール時に「<strong>Add Python to PATH</strong>」にチェックを入れることを忘れないでください。
        </div>
      </div>

      <div class="faq-item">
        <div class="faq-q">
          <span class="q-badge">Q</span>
          文字起こしの精度はどれくらいですか？
          <span class="faq-arr">▼</span>
        </div>
        <div class="faq-a">
          OpenAI の Whisper は非常に高精度な音声認識 AI です。日本語の認識精度はおおむね良好ですが、以下の場合に誤りが生じることがあります。<br><br>
          ・雑音の多い環境での録音<br>
          ・複数人が同時に話している部分<br>
          ・社内特有の用語・固有名詞（人名・プロジェクト名など）<br><br>
          ② 文字起こし結果タブで内容を確認し、重要な箇所は手動で修正してから議事録を生成することをおすすめします。
        </div>
      </div>

      <div class="faq-item">
        <div class="faq-q">
          <span class="q-badge">Q</span>
          録音データは外部に送られますか？セキュリティは大丈夫ですか？
          <span class="faq-arr">▼</span>
        </div>
        <div class="faq-a">
          録音ファイルは文字起こしのために <strong>OpenAI のサーバー</strong>に送信されます。また、文字起こしのテキストは議事録生成のために <strong>Anthropic のサーバー</strong>に送信されます。<br><br>
          いずれも信頼性の高い AI 企業ですが、<strong>機密情報を含む会議</strong>の録音を使用する際は、
          各サービスのデータポリシーを確認してください。このツール自体がデータを収集することはありません。
        </div>
      </div>

      <div class="faq-item">
        <div class="faq-q">
          <span class="q-badge">Q</span>
          .env ファイルは必ず作る必要がありますか？
          <span class="faq-arr">▼</span>
        </div>
        <div class="faq-a">
          必須ではありません。.env ファイルがなくてもアプリは起動します。その場合、アプリの「STEP 3 API キー設定」の入力欄にその都度キーを入力することで使えます。<br><br>
          ただし、.env に保存しておくと <strong>毎回入力する手間が省けて便利</strong>なため、設定することをおすすめします。
        </div>
      </div>

      <div class="faq-item">
        <div class="faq-q">
          <span class="q-badge">Q</span>
          Gmail 以外のメールサービス（Outlook など）は使えますか？
          <span class="faq-arr">▼</span>
        </div>
        <div class="faq-a">
          使えます。アプリ ④ タブの「詳細設定（SMTP サーバー）」を展開して、お使いのサービスに合わせて変更してください。<br><br>
          ・<strong>Outlook / Hotmail</strong>: サーバー <code>smtp-mail.outlook.com</code>、ポート <code>587</code><br>
          ・<strong>Yahoo メール</strong>: サーバー <code>smtp.mail.yahoo.co.jp</code>、ポート <code>465</code><br><br>
          詳しくはお使いのメールサービスの「SMTP 設定」をご確認ください。
        </div>
      </div>

      <div class="faq-item">
        <div class="faq-q">
          <span class="q-badge">Q</span>
          アプリで直接録音できますか？
          <span class="faq-arr">▼</span>
        </div>
        <div class="faq-a">
          はい、できます。「🎙 録音」タブで PC の音声をそのまま録音できます。<br><br>
          使う前に、コマンドプロンプトで以下を実行してください：<br>
          <code>pip install sounddevice numpy</code><br><br>
          インストール後にアプリを再起動すると録音機能が有効になります。インストールせずに録音タブを開くと、インストール手順が画面に表示されます。<br><br>
          💡 PC から出る音全体（相手の声も含めて）を録音するには、デバイス一覧で「🔊 ステレオ ミキサー」を選んでください。
        </div>
      </div>

    </div>
  </div>
</section>

<!-- ━━━ 困ったときは ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->
<section id="trouble">
  <div class="container">
    <div class="sec-head">
      <div class="chip">TROUBLESHOOTING</div>
      <h2>困ったときは</h2>
      <p>よくあるエラーと対処方法をまとめました</p>
    </div>

    <table class="trouble-table">
      <thead>
        <tr>
          <th style="width:35%;">こんな症状・エラーが出たら</th>
          <th>原因と対処方法</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><span class="prob">「python は認識されていません」と表示される</span></td>
          <td>
            Python がインストールされていないか、PATH が設定されていません。<br>
            <a href="https://www.python.org/downloads/" target="_blank">python.org</a> から Python をインストールし直してください。
            インストール時に「<strong>Add Python to PATH</strong>」に必ずチェックを入れてください。
          </td>
        </tr>
        <tr>
          <td><span class="prob">「ModuleNotFoundError」と表示される</span></td>
          <td>
            ライブラリがインストールされていません。<br>
            コマンドプロンプトで <code>pip install openai anthropic python-dotenv</code> を実行してください。
          </td>
        </tr>
        <tr>
          <td><span class="prob">文字起こしエラー：「Invalid API key」</span></td>
          <td>
            OpenAI の API キーが間違っています。<br>
            アプリの「STEP 3 API キー設定」の OpenAI キー欄を確認してください。
            「表示 / 非表示」ボタンで内容を確認して、<code>sk-</code> から始まるキーが正しく入力されているか確かめてください。
          </td>
        </tr>
        <tr>
          <td><span class="prob">議事録生成エラー：「Invalid API key」</span></td>
          <td>
            Anthropic の API キーが間違っています。<br>
            <code>sk-ant-</code> から始まるキーが正しく入力されているか確認してください。
          </td>
        </tr>
        <tr>
          <td><span class="prob">メール送信エラー：「Authentication failed」</span></td>
          <td>
            Gmail のアプリパスワードが間違っているか、入力されていません。<br>
            通常の Gmail ログインパスワードではなく、<a href="https://myaccount.google.com/apppasswords" target="_blank">発行したアプリパスワード</a>（16 文字のコード）を使ってください。
          </td>
        </tr>
        <tr>
          <td><span class="prob">ファイルを選んでも文字起こしが始まらない</span></td>
          <td>
            API キーが未入力の可能性があります。「STEP 3 API キーを設定する」のOpenAI キー欄が空欄でないか確認してください。
          </td>
        </tr>
        <tr>
          <td><span class="prob">録音タブを開くと「追加ライブラリが必要」と表示される</span></td>
          <td>
            sounddevice と numpy がインストールされていません。<br>
            コマンドプロンプトで <code>pip install sounddevice numpy</code> を実行してからアプリを再起動してください。
          </td>
        </tr>
        <tr>
          <td><span class="prob">「デバイスが見つかりません」と表示される</span></td>
          <td>
            録音デバイスが認識されていません。「🔄 一覧を更新」ボタンを押してみてください。<br>
            PC のステレオ ミキサーが無効になっている場合は、Windows の「サウンド設定 → 録音タブ」を右クリックして「無効なデバイスの表示」→「有効化」してください。
          </td>
        </tr>
        <tr>
          <td><span class="prob">「ファイルが 25MB を超えています」というエラー</span></td>
          <td>
            長時間の録音を使用しています。<code>pip install pydub</code> を実行し、<a href="https://ffmpeg.org/download.html" target="_blank">ffmpeg</a> もインストールしてから再度お試しください。
          </td>
        </tr>
        <tr>
          <td><span class="prob">議事録の内容が会議と全然違う</span></td>
          <td>
            文字起こしの精度が低かった可能性があります。② 文字起こし結果タブに戻って内容を修正してから、再度「▶ 議事録を自動生成する」を押してください。
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<!-- ━━━ フッター ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->
<footer>
  <div class="container">
    <p><strong style="color:rgba(255,255,255,.8);">Zoom 議事録 自動作成ツール</strong></p>
    <p>Python + OpenAI Whisper + Anthropic Claude</p>
    <p style="margin-top:8px;">
      このツールは <a href="https://openai.com" target="_blank">OpenAI</a> および
      <a href="https://anthropic.com" target="_blank">Anthropic</a> の API を使用しています。<br>
      各サービスの利用にはそれぞれへの登録と利用料金が必要です。
    </p>
  </div>
</footer>

<script>
  // ── FAQ アコーディオン ──────────────────────────────────────
  document.querySelectorAll('.faq-q').forEach(function(q) {
    q.addEventListener('click', function() {
      this.parentElement.classList.toggle('open');
    });
  });

  // ── チェックボックスで項目を打ち消し線 ──────────────────────
  document.querySelectorAll('.checklist .cb').forEach(function(cb) {
    cb.addEventListener('change', function() {
      var span = this.nextElementSibling;
      span.style.textDecoration = this.checked ? 'line-through' : '';
      span.style.opacity        = this.checked ? '0.5' : '1';
    });
  });
</script>

</body>
</html>
"""


def main() -> None:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HTML)
    print(f"HTML を生成しました: {OUTPUT_FILE}")
    webbrowser.open(f"file:///{OUTPUT_FILE.replace(os.sep, '/')}")


if __name__ == "__main__":
    main()
