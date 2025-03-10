help(ord)
for i in 'bilibili':
    list1=[]
    list1.append(ord(i))
    print(list1)
list2=[ord(x) for x in 'acfan']
print(list2)

uid=[x for x in range(1000) if x%2==1]
print(uid)
uid=[x for x in range(1000) if x%2==0]
print(uid)
tt=[ x ** 2 for x in range(10) ]

yy=[x+y for x in range(3) for y in range(3)]

str=[x+y for x in 'me' for y in 'nimeia']
print(str)
tuple1=[(x,y) for x in range(4) for y in range(3)]
print(tuple1)
res1=[x+m for x in [1,2] for m in [100,200,300,400] ]
print(res1)