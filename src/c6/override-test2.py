class SuperClass:
    def hoge(self, id):
        print("---")
        print("SuperClass.hoge=", id)

class SubClass(SuperClass):
    def hoge(self, id):
        super().hoge(id) # 基底クラスのhogeメソッドを呼び出す
        print("SubClass.hoge=", id)


# 基底クラスのhogeメソッドの実行例
rc = SuperClass()
rc.hoge(100)

# 派生クラスのhogeメソッドを実行する
sc = SubClass()
sc.hoge(300)

