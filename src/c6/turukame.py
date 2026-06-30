# 鶴・亀・タコ・イカを表すクラスを定義 --- (*1)
class Turu:
    def get_name(self):
        return "鶴"
    def get_legs(self):
        return 2

class Kame:
    def get_name(self):
        return "亀"
    def get_legs(self):
        return 4

class Tako:
    def get_name(self):
        return "タコ"
    def get_legs(self):
        return 8

class Ika:
    def get_name(self):
        return "イカ"
    def get_legs(self):
        return 10

# 鶴亀算を解く関数 --- (*2)
def calc_turukame(turu, kame, heads, legs):
    turu_l = turu.get_legs()
    kame_l = kame.get_legs()
    turu_name = turu.get_name()
    kame_name = kame.get_name()
    kame_num = (legs - (turu_l * heads)) // (kame_l - turu_l)
    turu_num = heads - kame_num
    print("---")
    print("頭=", heads, "足=", legs)
    print(turu_name, "=", turu_num)
    print(kame_name, "=", kame_num)
    return (turu_num, kame_num)


# モジュールではない時に以下を実行する --- (*3)
if __name__ == '__main__':
    # 鶴亀算で問題を解く
    calc_turukame(Turu(), Kame(), heads=10, legs=28)
    calc_turukame(Tako(), Ika(),  heads=11, legs=100)


