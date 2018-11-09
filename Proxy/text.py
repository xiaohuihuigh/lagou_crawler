#coding:utf8
import re
from bs4 import BeautifulSoup as bf
with open('test.html','r')as f:
    soup= bf(f.readlines(),'html.parser')
text = soup.text
pat = re.compile('本机IP:.*?(d+\.d+\.d+\.d+)')
print(text.find(pat))
