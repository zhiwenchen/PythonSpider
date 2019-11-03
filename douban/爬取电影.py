import json
import csv
import time
import re
import requests
import traceback
from bs4 import BeautifulSoup

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

# 获得电影的url链接列表
#每次返回20个
# start 起始位置
def get_movies_url(start):
    urls = []
    url = "https://movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags=%E7%94%B5%E5%BD%B1&start=" + str(start)
    html = get_HTML_text(url)
    data = json.loads(html)['data']
    for d in data:
        urls.append(d['url'])
    return urls

#获得最近top10短评
def get_comments(url):
    comments = []
    url = url + "/comments?sort=new_score&status=P"
    html = get_HTML_text(url)
    soup = BeautifulSoup(html.text,'html.parser')
    i = 0
    for short in soup.find_all(attrs={'class': 'short'}):
        i += 1
        comments.append(short.text)
        if i >= 10:
            break
    return comments

#获得top10影评
def get_reviews(url):
    pass

def get_movies():
    mid = 1 #序号
    start = 0
    head = ('ID','电影名','导演','编剧','主演','类型','制片国家/地区','语言','上映日期','片长','又名','IMDb链接')
    file = 'D:\\movies.csv'
    write_to_csv(file,head)
    for i in range(5):
        urls = get_movies_url(start)
        for url in urls:
            m = []
            try:
                html = get_HTML_text(url)
                soup = BeautifulSoup(html,"html.parser")
                movie_name = soup.find('h1').find('span').text
                m.append(mid)
                m.append(movie_name)
                text = soup.find(attrs={'id':'info'}).text
                text.strip()
                info = text.split('\n')
                for s in info:
                    if s is not "":
                        label = re.split(':',s,1)[0]
                        if label in head:
                            m.append(re.split(':',s,1)[1])
                #comments = get_comments(url)
                write_to_csv(file,m)
                print('成功写入', mid, '条数据')
                mid += 1
            except Exception as e:
                print('写入失败:')
                print(traceback.format_exc())
                #continue
        start += 20

if __name__ == '__main__':
    # for i in range(5):
    #     urls = get_movies_url(0)
    #     for url in urls:
    #         print(url)

    # urls = get_movies_url(20)
    # for url in urls:
    #     html = get_HTML_text(url)
    #     soup = BeautifulSoup(html, "html.parser")
    #     movie_name = soup.find('h1').find('span').text
    #     print(movie_name)

    get_movies()

