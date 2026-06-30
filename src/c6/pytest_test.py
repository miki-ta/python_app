# 引数に指定したリストを合計する関数
def sum_list(values):
    total = 0
    for v in values:
        total += v
    return total

# 関数sum_list()をテストする関数
def test_sum_list():
    assert sum_list([1, 2, 3]) == 6
    assert sum_list([1, 2, 3, 4]) == 10
    assert sum_list([1, 2, 3, 4, 5]) == 15
