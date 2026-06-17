# 国語の点数の一覧 --- (*1)
points = [80, 40, 23, 14, 29, 58]

# 30点以下のデータだけ選んで赤点リストに追加 --- (*2)
akaten = []
for p in points:
    if p < 30:
        akaten.append(p)

# 選んだデータを表示 --- (*3)
print(akaten)

