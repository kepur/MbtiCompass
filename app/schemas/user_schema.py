li1=[1,2,3,4,5,6,7,8,9,10,11,'hello',"www.baidu.com","word","Python","bbcom",12.32,0.67]

def wr_fi(li_str,file_name):
  abc=open(file_name,'w')
  i=0
  while i<=len(li_str):
    if isinstance(li_str[i],int):
        abc.write(str(li_str[i]))
    elif isinstance(li_str[i],float):
        abc.write(str(li_str[i]))
    else:
        abc.write(li_str[i])
    i=i+1
    abc.close()
wr_fi(li1,'b.txt')


