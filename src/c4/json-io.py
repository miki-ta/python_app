import json

# 辞書型のデータを定義
data = {
    "page": 3,  # 数値
    "index": ["jas", 1, 19],  # リスト型
    "contents": "be quick to listen, slow to speak, slow to anger", # 文字列
    "has_next": True, # 真偽型
}

# ファイルへ書き込む
filename = "test.json"
with open(filename, "w") as fp:
    json.dump(data, fp)

# ファイルから読み込む
with open(filename, "r") as fp:
    r = json.load(fp)
    print("page=", r["page"])
    print("index=", r["index"])
    print("contents=", r["contents"])
    print("has_next=", r["has_next"])
