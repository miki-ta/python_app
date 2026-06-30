import numpy as np
import torchvision
import matplotlib.pyplot as plt

# データセット「CIFAR-10」を読み込む
trainset = torchvision.datasets.CIFAR10(
    root="./data", train=True, download=True, transform=None)
# データとラベルを取得
train_images = np.array([np.array(image[0]) for image in trainset])
train_labels = np.array([image[1] for image in trainset])

# 1つの画像を表示
plt.figure(figsize=(10, 10))
plt.imshow(train_images[1])
plt.title(f"Label: {train_labels[0]}")
plt.axis('on')  # 軸を非表示にする
plt.show()
