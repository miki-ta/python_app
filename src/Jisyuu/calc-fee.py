#ある遊園地の入場料を計算するプログラム
#人数の入力
children = int(input("子供料金（１３歳未満）人数を入力してください: "))
normal = int(input("通常料金（１３歳－６４歳）人数を入力してください: "))
elder = int(input("シニア料金（６５歳以上）人数を入力してください: "))
#集計
total_num= children + normal + elder
children_fee = children * 500
normal_fee = normal * 1000
elder_fee = elder * 700
total_fee = children_fee + normal_fee + elder_fee
#割引対象か確認
if total_num >= 10:
    print("団体割引が適用されます。")
    total_fee = total_fee * 0.8
else:
    print("団体割引は適用されません。")
#結果の表示
print("子供料金：{0}人×500＝{1}円".format(children, children_fee))
print("通常料金：{0}人×1000＝{1}円".format(normal, normal_fee))
print("シニア料金：{0}人×700＝{1}円".format(elder, elder_fee))
print("合計金額：{0}円".format(total_fee))    