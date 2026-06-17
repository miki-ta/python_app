class Cat:
    # クラス変数
    nakigoe = "nya-"
    # メソッド
    def naku(self):
        print(self.nakigoe) # ← ここを変更(*1)

mike = Cat()
nora = Cat()

# 鳴き声を変更
mike.nakigoe = "myu-" # --- (*2)
mike.naku()
nora.naku()


