import json, os
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Input
from keras.optimizers import Adam
from keras.utils import to_categorical
from keras.callbacks import TensorBoard

# ワインデータ(JSON)を読み --- (*1)
with open("wine-data.json", "r", encoding="utf-8") as fp:
   data_train, label_train, data_test, label_test = json.load(fp)
   # データの概要を表示
   print("train:", len(data_train), "test:", len(data_test))
# ラベルをone-hotベクトルに変換 --- (*2)
label_train = to_categorical(label_train, 11) # 0から10までの11段階
label_test = to_categorical(label_test, 11)
# データをNumPy配列に変換 --- (*3)
data_train = np.array(data_train)
data_test = np.array(data_test)
# ログディレクトリを作成
logs_dir = os.path.join(os.path.dirname(__file__), "logs_wine")
os.makedirs(logs_dir, exist_ok=True)

# MLPのモデルを構築 --- (*4)
model = Sequential(
   [
       Input(shape=(11,)), # 入力データを指定
       Dense(128, activation="relu"), # 全結合NN層
       Dense(64, activation="relu"),
       Dense(11, activation="softmax"), # 出力層
   ]
)
model.compile(optimizer=Adam(), loss="categorical_crossentropy",
   metrics=["accuracy"])
# モデルの学習 --- (*5)
model.fit(
   data_train,  # 学習用データ
   label_train,  # 学習用ラベル
   epochs=50,  # 学習回数
   batch_size=32,  # バッチサイズ
   validation_split=0.2,
   callbacks=[TensorBoard(log_dir=logs_dir)]) # TensorBoardのため

# テストデータでの評価 --- (*6)
loss, accuracy = model.evaluate(data_test, label_test)
print(f"精度(accuracy): {accuracy}")
print(f"損失(loss): {loss}")
