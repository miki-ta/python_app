# じゃんけんゲーム(スコア付)
import random
import math

# 手をリストで表現
hand = ["グー", "チョキ", "パー", "ゲーム終了"]

print("=== じゃんけんしましょう！ ===")
score = 0
count = 0
while True:
    # 勝率を表示
    if count > 0:
        win = math.floor(score / count * 100)
        print("+--------------------------")
        print("| スコア:", score, "/", count)
        print("| 勝率  :", win, "%")
        print("+--------------------------")
    # コンピューターの手を決定
    com = random.randint(0, 2)
    # ユーザーの手を入力してもらう
    for i,desc in enumerate(hand):
        print(i, ":", desc)
    yt = input("出す手を数値で入力: ")
    if yt == "q" or yt == "": quit()
    you = int(yt)
    if you == 3: break
    if you < 0 or you > 2:
        print("0から3の間で入力してね")
        continue
    # 手を表示
    print("---")
    print("自分:", hand[you])
    print("相手:", hand[com])
    input("---")
    # じゃんけんの勝敗を判定する
    j = (you - com + 3) % 3
    if j == 0:
        print("あいこ")
    elif j == 1:
        print("負け(ToT)")
        count += 1
    else:
        print("勝ち!!")
        score += 1
        count += 1
    input("---")


