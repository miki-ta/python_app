# 複数テキストファイルからテキストを検索するスクリプト
import sys
import os

# 引数の数を確認 --- (*1)
# 何もキーワードがなければ使い方を表示
if len(sys.argv) <= 1:
    print("[USAGE] findtext (keyword)")
    sys.exit(0) # プログラムを終了する --- (*2)

# コマンドライン引数からキーワードを得る --- (*3)
keyword = sys.argv[1]

# カレントディレクトリ以下のファイルを全て処理する --- (*4)
for root, dirs, files in os.walk("."):
    for fi in files:
        result = []
        # テキストファイルを読む --- (*5)
        try:
            path = os.path.join(root, fi) 
            with open(path, encoding='utf-8') as f:
                for no, line in enumerate(f):
                    if line.find(keyword) >= 0:
                        line = line.strip()
                        s = "| {0:4}: {1}".format(no+1, line)
                        result.append(s)
        except:
            continue
        # resultに検索結果があれば結果を表示 --- (*6)
        if len(result) > 0:
            print("+ file: " + fi)
            for li in result:
                print(li)

