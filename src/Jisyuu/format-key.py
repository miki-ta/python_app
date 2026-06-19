#(1)
print("私は{name}です".format(name="ミドリ"))
#(2)
fmt = "年齢は{age}歳で、{job}をしています"
s = fmt.format(age=22, job="プログラマー")
print(s)

print("年齢は{age}才で、{job}をしています".format(age=39,job="エンジニア"))

age=39
job="エンジニア"
s="年齢は{0}で、仕事は{1}をしています".format(age,job) 
print(s)


age=39
job="エンジニア"
s=f"年齢は{age}歳で、仕事は{job}"
print(s)