# (1) 二倍して1を引く方法
data = [ (i * 2 - 1) for i in range(1, 6) ]
print(data)

# (2) range()を工夫する方法
data = [ i for i in range(1, 11, 2) ]
print(data)

# (3) 内包表記で for と if を組み合わせる方法
data = [ i for i in range(1, 11) if i % 2 == 1 ]
print(data)

