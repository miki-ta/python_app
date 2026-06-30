import json, os
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, BatchNormalization, Dropout, Input
from keras.utils import to_categorical
from keras.callbacks import TensorBoard

# ワインデータ(JSON)を読み --- (*1)
with open("wine-data.json", "r", encoding="utf-8") as fp:
   data_train, label_train_n, data_test, label_test_n = json.load(fp)

# ラベルを低品質(0)/普通(1)/高品質(2)に変換する --- (*2)
def convert_three_label(labels):
   new_label = [0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2]
   return [new_label[label] for label in labels]
label_train_n = convert_three_label(label_train_n)
label_test_n = convert_three_label(label_test_n)
# ラベルをone-hotベクトルに変換 --- (*3)
label_train = to_categorical(label_train_n, 3)
label_test = to_categorical(label_test_n, 3)
# ログディレクトリを作成
logs_dir = os.path.join(os.path.dirname(__file__), "logs_wine")
os.makedirs(logs_dir, exist_ok=True)

# 必要な要素のみ取り出す関数 --- (*4)
def pickup_cols(data):
   return [c[0:4] + c[5:7] + c[8:11] for c in data] # 4と7の要素は使わない
data_train = np.array(pickup_cols(data_train))  # 必要な要素のみを取り出す
data_test = np.array(pickup_cols(data_test))
# MLPのモデルを構築 --- (*5)
model = Sequential(
   [
       Input(shape=(9,)),  # 入力データを指定
       Dense(128, activation="relu"),  # 全結合NN層
       BatchNormalization(),  # バッチ正規化
       Dropout(0.4),  # ドロップアウト
       Dense(64, activation="relu"),
       Dense(3, activation="softmax"),
   ]
)
model.compile(optimizer="sgd", loss="categorical_crossentropy", metrics=["accuracy"])
# モデルの学習 --- (*6)
history = model.fit(
   data_train,  # 学習用データ
   label_train,  # 学習用ラベル
   epochs=66,  # 学習回数
   batch_size=64,  # バッチサイズ
   validation_split=0.2,
   callbacks=[TensorBoard(log_dir=logs_dir)],  # TensorBoard用のログ
)
# テストデータでの評価 --- (*7)
loss, accuracy = model.evaluate(data_test, label_test)
print(f"精度(accuracy): {accuracy}")
print(f"損失(loss): {loss}")
