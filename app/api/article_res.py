fr=open('../schemas/payment_schema.py', 'w')
li1=['hello',"www.baidu.com","word","Python","bbcom"]
li2=[1,2,3,4,5,6,7,8,9,10,11]
li=li1+li2
print(li)
i=0
while i<len(li1):
    fr.write(li1[i]+'\n')
    i=i+1
i=0
while i<len(li2):
    fr.write(str(li2[i])+'\n')
    i=i+1
fr.close()