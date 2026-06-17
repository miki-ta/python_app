import os
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Input, Dense, Conv2D, MaxPooling2D, Flatten
from keras.optimizers import Adam
from keras.datasets import cifar10
from keras.callbacks import TensorBoard

# データセット「CIFAR-10」を読み込む --- (*1)
(train_images, train_labels), (test_images, test_labels) = cifar10.load_data()
# 学習用のデータのshapeを表示
print("学習用データのshape:", train_images.shape, train_labels.shape)

# 画像データを0.0-1.0の範囲に正規化 --- (*2)
train_images = train_images.astype("float32") / 255.0
# ラベルをone-hotエンコード --- (*3)
train_labels = to_categorical(train_labels, 10)

# KerasでCNNモデルを定義 --- (*4)
model = Sequential(
   [
       Input(shape=(32, 32, 3)),
       Conv2D(32, (3, 3), activation="relu"),
       MaxPooling2D((2, 2)),
       Conv2D(64, (3, 3), activation="relu"),
       MaxPooling2D((2, 2)),
       Flatten(),
       Dense(128, activation="relu"),
       Dense(10, activation="softmax"),
   ]
)
# モデルをコンパイル --- (*5)
model.compile(optimizer=Adam(), loss="categorical_crossentropy", metrics=["accuracy"])
# TensorBoardのログディレクトリを設定 --- (*6)
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)
# モデルを学習 --- (*7)
model.fit(
   train_images, # 学習したいデータ
   train_labels, # 答えとなるラベルデータ
   epochs=12, # 学習回数
   batch_size=64, # 一度に学習するデータ数
   validation_split=0.1, # 10%のデータを検証用に使う
   callbacks=[tensorboard_callback], # TensorBoardのログを出力
)

# 学習済みモデルを保存 --- (*8)
model.save("cifar10_model.keras")
print("ok")
