#花屋の支払金額を求める
#値段
rose_v = 500
sunflower_v = 400
tulip_v = 700
#個数
rose_c = 18
sunflower_c = 8-2
tulip_c = 21-5
#割引率
rate = 0.9
#計算
sum_v = (rose_v*rose_c) + (sunflower_v*sunflower_c) + (tulip_v*tulip_c)
payment = sum_v * rate
#結果を表示
print("買い物の合計は", sum_v, "円です。")
print("割引してもらうと", payment, "円です。")
