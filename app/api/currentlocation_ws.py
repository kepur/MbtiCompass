m=[[11,22,33],[44,55,66],[77,88,99]]
print(m[0][0])
for i in range (len(m)):
    for j in range(len(m)):
        print(m[i][j])

for i in range(len(m)):
    for j in range(len(m)):
        mm=m[i][j]+100
        a=[]
        a.append(mm)
        print(a)
n=[('naxi',44,1.70),('bob',17,1.86)]
for (name,age,high) in n:
    print(name,high)
