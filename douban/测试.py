import requests
from bs4 import BeautifulSoup
import re
import json
import bs4

def get_info(text):
    info = []
    spans = text('span',recursive=False)
    for span in spans:
        sp = span
        s = ''
        while(True):
            if sp.name == 'br':
                info.append(s)
                break
            elif isinstance(sp,bs4.NavigableString):
                if(sp != None):
                    s += sp.strip()
            sp = sp.next
    return info

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'}
url = "https://music.douban.com/tag/%E5%8D%8E%E8%AF%AD?type=T&start="+str(0)
r= requests.get(url,headers=headers)
soup = BeautifulSoup(r.text,'html.parser')
a = soup.find_all('a',attrs={'class':'nbg'})
#class_='nbg'
urls = []
for x in a:
    urls.append(x['href'])
url1 = urls[0]
r = requests.get(url1,headers=headers)
soup = BeautifulSoup(r.text,'lxml')
info = soup.find('div',id='info')

print(get_info(info))