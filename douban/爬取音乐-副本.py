import json
import csv
import time
import re
import requests
import traceback
from bs4 import BeautifulSoup
import bs4

file = 'D:\\music.csv'
tags = ['华语','日语','欧美']
base_info = {'豆瓣ID':'','音乐名':'','又名':'','表演者':'','流派':'','专辑类型':'','介质':'','发行时间':'','出版者':'','唱片数':'',
    '条形码':'','ISRC(中国)':'','其他版本':'','相关电影':'','评分':'','评价人数':''}
header = list(base_info.keys())
#向csv文件中写入数据
def write_to_csv(file,row):
    csvfile = open(file,'a',newline='',encoding='UTF8')
    try:
        writer = csv.writer(csvfile)
        writer.writerow(row)
    except IOError as e:
        print(e)
    finally:
        csvfile.close()

# 获得url的HTML响应
def get_HTML_text(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
               'Connection':'close'}
    html = ""
    while html == "":
        try:
            r = requests.get(url,headers=headers,timeout=10)
            r.raise_for_status()
            r.encoding = 'utf-8'
            html = r.text
            return html
        except Exception as e:
            print("Connection refused by the server...")
            print("sleep for 2 seconds")
            time.sleep(2)
            continue

# 获得音乐的url链接列表
# 每次返回20个
# tag:音乐标签
# start:起始位置
# https://music.douban.com/tag/华语/?type=T&start=20
def get_music_url(tag,start):
    urls = []
    url = "https://music.douban.com/tag/"+tag+"/?type=T&start="+str(start)
    html = get_HTML_text(url)
    soup = BeautifulSoup(html, 'lxml')
    a = soup('a', class_='nbg') #具有对应url的a标签
    for u in a:
        urls.append(u['href'])
    return urls

# 获得相应的信息
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

def get_music():
    write_to_csv(file, header) # 写入头部
    urls = get_music_url('华语',0)
    mid = 0
    for url in urls:
        # m = base_info.deepcopy()
        m = ['' for i in range(16)]
        try:
            html = get_HTML_text(url)
            soup = BeautifulSoup(html, "lxml")
            music_name = soup.find('h1').find('span').text
            m[0] = url.split('/')[-2] #豆瓣ID
            m[1] = music_name #音乐名称
            text = soup.find(attrs={'id': 'info'})
            info = get_info(text)
            for s in info:
                if s is not "":
                    label = re.split(':', s, 1)[0]
                    if label in header:
                        index = header.index(label)
                        m[index] = re.split(':',s,1)[1]
            # comments = get_comments(url)
            # write_to_csv(file, m)
            write_to_csv(file,m)
            mid += 1
            print("成功保存",mid,"条数据")
        except Exception as e:
            print('保存失败:')
            print(traceback.format_exc())

if __name__ == '__main__':
    get_music()