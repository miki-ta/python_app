import datetime
# 2028年ロサンゼルスオリンピックの日付
t1 = datetime.date(2028, 7, 14)
# 日数差を計算
t2 = datetime.date.today()
diff = t1 - t2
# 結果を表示
print("今日:", t2.strftime("%Y/%m/%d"))
print("あと", diff.days, "日")

