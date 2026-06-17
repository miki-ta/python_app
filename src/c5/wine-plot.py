import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# データの読み込み
data = pd.read_csv("winequality-white.csv", delimiter=";")
# ワインの成分と品質の相関をグラフに表示
plt.figure(figsize=(12, 6))
sns.heatmap(data.corr(), annot=True, cmap='coolwarm')
plt.xticks(rotation=20)
plt.show()
