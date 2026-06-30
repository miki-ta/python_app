import random

# 格言をリストに代入 --- (*1)
kakugen = [
    "能ある鷹は爪を隠す",
    "豚に真珠",
    "二兎を追う者は一兎をも得ず",
    "叩き続けなさい。そうすれば開かれます。"]

# ランダムに数値を一つ選ぶ --- (*2)
i = random.randint(0, len(kakugen)-1)

# 選んだ格言を表示する --- (*3)
print( kakugen[i] )

