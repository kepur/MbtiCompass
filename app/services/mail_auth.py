#-*-coding:utf8-*-
import requests
html=requests.get('http://tu.hanhande.com/')
print(html.text)