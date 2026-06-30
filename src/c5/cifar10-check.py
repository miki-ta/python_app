import numpy as np
from keras.datasets import cifar10
from PIL import Image

# データセット「CIFAR-10」を読み込む
(train_images, train_labels), (test_images, test_labels) = cifar10.load_data()
# クラス名
classes = ("plane", "car", "bird", "cat", "deer",
           "dog", "frog", "horse", "ship", "truck")

# データセットから一つだけ取り出す
image = train_images[1]
label = train_labels[1][0]

# NumPy配列をPIL画像に変換してPNG形式で保存
image_pil = Image.fromarray(image)
image_pil.save("cifar10_sample.png")

# 画像の概要を表示
print("ラベル:", classes[label])
print("画像サイズ:", image_pil.size)
print("画像モード:", image_pil.mode)
print("shape:", image.shape)
print("data:", image)
