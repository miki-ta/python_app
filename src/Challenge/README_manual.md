# コールセンター運用マニュアル生成ツール

使い方の例:

JSONファイルからMarkdownを生成して表示:

```bash
python manual_builder.py -i manual_sample.json
```

CSVを使う場合はヘッダに `category,title,description` を含めてください。

出力をファイルに保存する例:

```bash
python manual_builder.py -i manual_sample.json -o manual.md
```

引数を指定しないと対話モードになります。

GUIで操作する方法:

1. ターミナルで `src` フォルダに移動して実行する方法:

```bash
cd src
python manual_gui.py
```

2. 用意したバッチファイルで実行する方法（Windows）:

```bash
src\run_manual_gui.bat
```

GUIの機能:
- JSON/CSVファイルの読み込み
- 項目の追加・編集・削除・並べ替え
- カテゴリごとにMarkdownで保存

CSVのサンプルは `src/manual_sample.csv` を参照してください。
