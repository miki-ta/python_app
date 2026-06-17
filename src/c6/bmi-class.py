# BMIを計算するクラス
class BMI:
    def __init__(self, weight, height):
        ''' 初期化 '''
        self.weight = weight
        self.height = height
        self.calcBMI()

    def calcBMI(self):
        ''' BMIを計算する '''
        h = self.height / 100
        self.bmi = self.weight / (h ** 2)

    def printJudge(self):
        ''' 結果を表示する '''
        print("---")
        print("BMI=", self.bmi)
        b = self.bmi
        if (b < 18.5): print("痩せ型")
        elif (b < 25): print("標準")
        elif (b < 30): print("肥満(軽)")
        else: print("肥満(重)")

# 一人目 
person1 = BMI(weight=65, height=170)
person1.printJudge()

# 二人目
person2 = BMI(76, 165)
person2.printJudge()

# 三人目
person3 = BMI(50, 180)
person3.printJudge()


