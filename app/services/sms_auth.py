#
import urllib.request
import urllib
import time
li1='''<a target="_blank" href="http://www.54niaoyou.in/index.php?app=article&ac=show&id=17852">☑鸟友网向全网征集极品资源，投稿3个极品资源送100金币☑重要的事说三遍</a>'''
href=li1.find(r'href="')
print(href)
html=li1.find(r'">')
print(html)
url=li1[href+6:html]
print(url)
print(type(url))
a=url.replace("amp;","")
print(a)
con=urllib.request.urlopen(a).read()
z_con=con.decode('UTF-8')
print(z_con)
filename = url[-8:]
print(filename)
abc=open(filename,'w').write(str(z_con))