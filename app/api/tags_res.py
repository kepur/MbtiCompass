li1=[1,2,3,4,5,6,7,8,9,10,11,'hello',"www.baidu.com","word","Python","bbcom",12.32,0.67]
print('write list li1 into a file')
fli1=open('../schemas/location_schema.py', 'w')
i=0
while i<= len(li1)-1:
    if isinstance(li1[i],str):
        fli1.write(li1[i]+'\n')
    else:
        fli1.write(str(li1[i])+'\n')
    i=i+1
fli1.close()