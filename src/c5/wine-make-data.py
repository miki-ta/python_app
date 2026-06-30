import json
import pandas as pd
from sklearn.model_selection import train_test_split

# 入力ファイルと出力ファイルの指定
INFILE = "winequality-white.csv"
OUTFILE = "wine-data.json"

# ワインデータ(CSV)を読みこむ --- (*1)
wine_data = pd.read_csv(INFILE, sep=";")
# CSVの各データを数値に変換してラベルとデータに分ける --- (*2)
labels = wine_data["quality"].values.tolist()
data = wine_data.drop("quality", axis=1).values.tolist()

# 正規化を行う - 各列の最大値と最小値を得る --- (*3)
min_a = [min([x[i] for x in data]) for i in range(11)]
max_a = [max([x[i] for x in data]) for i in range(11)]
# 0.0から1.0の間に正規化 --- (*4)
for cols in data:
    for i in range(11):
        cols[i] = (cols[i] - min_a[i]) / (max_a[i] - min_a[i])

# 学習用データとテスト用データに分けてJSONファイルに保存 --- (*5)
data_train, data_test, label_train, label_test = \
    train_test_split(data, labels, test_size=0.2)
with open(OUTFILE, "w", encoding="utf-8") as fp:
    json.dump([data_train, label_train, data_test, label_test],
              fp, indent=2)
print("saved to", OUTFILE)
