

class SuperClass:
    def hoge(self):
        print("SuperClass.hoge")

class SubClass(SuperClass):
    def hoge(self):
        print("SubClass.hoge")

it = SubClass()
it.hoge()

