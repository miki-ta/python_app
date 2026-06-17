
def test_duck(it):
    it.sound()
    it.walk()

class Empty: pass

monkey = Empty()
monkey.sound = lambda : print("ウッキー")
monkey.walk = lambda : print("猿が歩く")

test_duck(monkey)


