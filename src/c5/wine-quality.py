import pandas as pd
import matplotlib.pyplot as plt
# データの読み込み
data = pd.read_csv("winequality-white.csv", delimiter=";")
# ラベルごとの個数を数える
print(data["quality"].value_counts())
plt.figure(figsize=(10, 3))
plt.hist(data["quality"], bins=11, range=(0, 10))
plt.xlabel("Quality")
plt.ylabel("Count")
plt.grid(True)
plt.xticks(range(11))
plt.show()
