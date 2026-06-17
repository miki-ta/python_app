from keras.models import load_model
from PIL import Image
import numpy as np

# クラス名
classes = ("plane", "car", "bird", "cat", "deer",
           "dog", "frog", "horse", "ship", "truck")

def test_image(filename):
    # 自分の写真を読み込んで、RGB(32x32ピクセル)に変形 --- (*1)
    img = Image.open(filename)
    img = img.convert("RGB") # RGBモードに変換
    img = img.resize((32, 32)) # 32x32にリサイズ
    # Numpy配列に変換して正規化する --- (*2)
    img = np.array(img)
    img = img.astype("float32") / 255.0

    # 学習済みモデルを読み込む --- (*3)
    model = load_model("cifar10_model.keras")
    # 推論する --- (*4)
    pred = model.predict(np.array([img]), verbose=0)
    # 結果を表示 --- (*5)
    index = np.argmax(pred) # 最大値を取り出す
    _values = ", ".join([f"{pred[0][i]:.2f}" for i in range(10)])
    # print(f"_values = [{_values}]")
    # ベスト3と確率を表示
    best3 = np.argsort(pred[0])[::-1][:3]
    vals = ",".join([f"{classes[i]}({int(pred[0][i]*100)}%)" for i in best3])
    print(f"画像[{filename:<15}]: {classes[index]:<6} : {vals}")

if __name__ == "__main__":
    # 自分の写真を使ってテスト --- (*6)
    test_image("test_cat.png")
    test_image("test_deer.png")
    test_image("test_horse.png")

