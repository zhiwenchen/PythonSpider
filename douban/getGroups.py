# 得到用户加入的小组
import re
import sys

import requests
from bs4 import BeautifulSoup

# 获得url的HTML响应
def get_HTML_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}
    try:
        r = requests.get(url,headers=headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        html = r.text
        return html
    except:
        return None

def get_user_groups(user_id):
    # 小组url
    groups = []
    group_url = 'https://www.douban.com/group/people/'+str(user_id)+'/joins'
    html = get_HTML_text(group_url)
    if html == None or html == '':
        return groups
    soup = BeautifulSoup(html, 'lxml')
    gs = soup('a',attrs = {"href": re.compile(r'^https\:\/\/www\.douban\.com\/group\/\w+\/$'),"title":True})
    if gs is not None:
        for g in gs:
            groups.append(g['title'])
    return groups

if __name__ == '__main__':
    print(get_user_groups(sys.argv[1]))