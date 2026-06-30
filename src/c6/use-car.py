# 定義したクラスを含むモジュールを取り込む
import car

# ワゴン車を作成
car1 = car.Van("Taro")
car1.turn_left() # --- (*1) 基底クラスのメソッドが使える
car1.show_status()

# キャンピングカーを作成
car2 = car.Camper("Jiro")
car2.turn_right()
car2.show_status()
car2.make_ice()


