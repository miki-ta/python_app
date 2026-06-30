
class A:
    def print(self):
        print("A")

class AB(A):
    def print(self):
        print("AB")

class AC(A):
    def print(self):
        print("AC")

class D(AB, AC):
    pass

obj = D()
obj.print()

