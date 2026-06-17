from keras.utils import to_categorical
from keras.models import load_model
from keras.datasets import cifar10

# データセット「CIFAR-10」を読み込む --- (*1)
(train_images, train_labels), (test_images, test_labels) = cifar10.load_data()
# 画像データを0.0-1.0の範囲に正規化 --- (*2)
test_images = test_images.astype("float32") / 255.0
# ラベルをone-hotエンコード --- (*3)
test_labels = to_categorical(test_labels, 10)

# 学習済みモデルを読み込む --- (*4)
model = load_model("cifar10_model.keras")
# モデルをテストデータで評価 --- (*5)
loss, accuracy = model.evaluate(test_images, test_labels, verbose=0)
# 結果を表示 --- (*6)
print(f"精度(accuracy): {accuracy:.4f}")
print(f"損失(loss): {loss:.4f}")
