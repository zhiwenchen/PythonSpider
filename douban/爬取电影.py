import json

import requests
from bs4 import BeautifulSoup

# 获得url的HTML响应
def get_HTML_text(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'}
    try:
        r = requests.post(url,headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""

# 获得电影的url链接列表
#每次返回20个
# start 起始位置
def get_movies_url(start):
    urls = []
    url = "https://movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags=&start=" + str(start)
    html = get_HTML_text(url)
    data = json.loads(html)['data']
    for d in data:
        urls.append(d['url'])
    return urls

def get_movies():
    start = 0
    for i in range(5):
        urls = get_movies_url(start)
        for url in urls:
            html = get_HTML_text(url)
            soup = BeautifulSoup(html,"html.parser")
            text = soup.find(attrs={'id':'info'}).text
            #text.split(':')
            print(text)
        start += 20

if __name__ == '__main__':
    get_movies()

