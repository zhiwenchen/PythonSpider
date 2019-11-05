import csv
import json
import re
import time
import traceback
import pymysql
import requests
from bs4 import BeautifulSoup

#向mysql中插入数据
# sql:要执行的sql语句
# values:要插入的数据
def write_to_mysql(sql,values):
    connection = pymysql.connect(host='118.25.133.235',
                           port=3306,
                           user='root',
                           database='douban_analysys',
                           password='YiGuanXYZ.@()85258638',
                           charset='utf8')
    try:
        # 获取cursor对象
        with connection.cursor() as cursor:
            # 执行sql语句
            cursor.execute(sql, values)
            # 提交之前的操作，如果之前已经执行多次的execute，那么就都进行提交
            connection.commit()
    except Exception as e:
        print(traceback.format_exc())
    finally:
        # 关闭connection对象
        connection.close()

#向csv文件中写入数据
def write_to_csv(file,row):
    csvfile = open(file,'a',newline='',encoding='utf-8-sig')
    try:
        writer = csv.writer(csvfile)
        writer.writerow(row)
    except IOError as e:
        print(e)
    finally:
        csvfile.close()

# 获得url的HTML响应
def get_HTML_text(url):
    # 定义头部信息
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
               'Connection':'close'}
    html = ""
    i = 0
    while html == "" and i < 5:
        try:
            r = requests.get(url,headers=headers,timeout=10)
            r.raise_for_status()
            r.encoding = 'utf-8'
            html = r.text
            return html
        except Exception as e:
            i += 1
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
    try:
        html = get_HTML_text(url)
        data = json.loads(html)['data']
        for d in data:
            urls.append(d['url'])
        return urls
    except Exception as e:
        print(traceback.format_exc())
        return urls

c_head = ['评论ID', '类型(长/短)', '用户', '状态(已/未看)', '评分',
          '评价时间', '标题', '内容', '有用数', '无用数']
#获得短评
# type:#0为短评  1为长评#status：P为看过，F为未看
#rating：为数字 #head:短评为None
#helpless_num：短评为None
def get_comments(movie_id,start,status,comments):
    url = "https://movie.douban.com/subject/"+str(movie_id)+"/comments?limit=20&sort=new_score&start="+str(start)+"&status="+str(status)
    try:
        html = get_HTML_text(url)
        soup = BeautifulSoup(html,"lxml")
        cs = soup(class_='comment-item')
        for comment in cs:
            cid = comment.attrs['data-cid']
            votes = int(comment.find(class_='votes').string)  # num
            c_info = comment.find(class_='comment-info')
            user = c_info.find('a').text
            rating = c_info.find(class_='rating')
            if rating is not None:
                rate = int(rating.attrs['class'][0][-2:]) / 10
            else:
                rate = None
            time = c_info.find(class_='comment-time').attrs['title']
            short = comment.find(class_='short').string
            s = 0 if status == 'P' else 1
            comments.append([cid,0, 0, user, s, rate, time, None, short, votes, None,movie_id])
    except Exception as e:
        print(traceback.format_exc())

#得到未看短评的数量
def get_comments_F_num(movie_id):
    url = 'https://movie.douban.com/subject/'+ str(movie_id) +'/comments?status=F'
    html = get_HTML_text(url)
    soup = BeautifulSoup(html,'lxml')
    t =soup.find('ul',class_='CommentTabs').find('li',class_='is-active').text
    res = re.search(r'\d+',t)
    if res:
        return int(res.group(0))
    else:
        return 0

# 获得影评
# 类型:int型：电影存0,书籍存1,音乐存2
# 子类型:int型：短评存0,长评存1
# 是否看过:int型：看过存0,想看存1,无此项(影评无此项)则为null
# 目标id:电影id、书籍id、音乐id
r_head = ('评论ID','类型','子类型','用户名','状态','评分','时间','标题','内容','有用数','无用数','目标id')

def get_reviews(movie_id,start,reviews):
    url = 'https://movie.douban.com/subject/'+str(movie_id)+'/reviews?sort=hotest&start='+str(start)
    html = get_HTML_text(url)
    soup = BeautifulSoup(html, 'lxml')
    rs = soup(class_='review-item')
    for r in rs:
        rid = r.attrs['id']
        name = r.find(class_='name').text
        rating = r.find(class_='main-title-rating')
        if rating is not None:
            rate = int(rating.attrs['class'][0][-2:]) // 10
        else:
            rate = None
        time = r.find(class_='main-meta').text
        title = r.select('.main-bd>h2')[0].text
        #reply = (r.find(class_='reply').text)[:-2]
        url1 = 'https://movie.douban.com/j/review/'+rid+'/full'
        res = requests.get(url1).json()
        soup = BeautifulSoup(res['html'], 'lxml')
        content = soup.text
        votes = res['votes']
        useful_count = votes['useful_count']
        useless_count = votes['useless_count']
        reviews.append([rid,0,1,name,None,rate,time,title,content,useful_count,useless_count,movie_id])

# 短评数量
movie_head = ('ID','电影名','导演','编剧','主演','类型','制片国家/地区','语言','上映日期',
              '片长','又名','IMDb链接','短评数量','影评数量','评分','评价数量')
# 爬取一个电影所有的信息
# comments_num 要爬取的短评数量
# reviews_num 长评数量
def get_movie_all(url,comments,comments_num,reviews,reviews_num):
    m = [None for _i in range(len(movie_head))]
    movie_id = int(url.split('/')[-2]) #电影ID
    html = get_HTML_text(url)
    soup = BeautifulSoup(html, "lxml")
    movie_name = soup.find('h1').find('span').text #电影名
    rate = soup.find('strong', class_='rating_num').text
    if rate == None or rate == '':
        rating_num = None #评分
    else:
        rating_num = float(rate)
    r_people = soup.find('a', class_='rating_people')
    if r_people == None:
        rating_people = 0
    else:
        rating_people = int(r_people.find('span').text) # 评价人数
    comments_P_num = int((soup.select('#comments-section h2 .pl a')[0].text)[3:-2]) # 已看短评数量
    comments_F_num = get_comments_F_num(movie_id)
    c_num = comments_F_num + comments_P_num
    r_num = int((soup.find('a', attrs={'href': 'reviews'}).text)[3:-2]) # 影评数量
    m[0], m[1], m[-4], m[-3], m[-2], m[-1] = movie_id, movie_name, c_num, r_num, rating_num, rating_people
    text = soup.find(attrs={'id': 'info'}).text  # 包含电影的基本信息
    text.strip()
    info = text.split('\n')
    for s in info:
        s.strip()
        if s is not '':
            # split三个参数:正则表达式,要切割的字符串,切割几个
            label = re.split(':', s, 1)[0]  # 标签
            if label in movie_head:
                index = movie_head.index(label)
                value = re.split(':', s, 1)[1] # 值
                if label == '片长':
                    res = re.search(r'\d+',value.split('/')[0])
                    if res:
                        m[index] = int(res.group(0))
                    else:
                        res = None
                elif label == '上映日期':
                    l = re.split(':', s, 1)[1]
                    res = re.search(r'\d{4}\-\d{2}\-\d{2}', s)
                    if res:
                        m[index] = res.group(0)
                    else:
                        m[index] = None
                else:
                    m[index] = value  # 值
    start = 0
    while start < comments_P_num and start < comments_num: # 得到已看评论
        get_comments(movie_id,start,'P',comments)
        start += 20
    start = 0
    while start < comments_F_num and start < comments_num: # 得到未看看评论
        get_comments(movie_id,start,'F',comments)
        start += 20
    start = 0
    while start < r_num and start < reviews_num: # 得到所有影评
        get_reviews(movie_id, 0, reviews)
        start += 20

    return m

def get_movies():
    movie_sql = 'insert into movie values(%s'+ ',%s'*15+')'
    #comments_sql = ''
    #reviews_sql = ''
    start = 0
    movie_file = 'D:\\movies_info.csv'
    #comments_file = 'D:\\comments.csv'
    #reviews_file = 'D:\\reviews.csv'
    for i in range(1):
        urls = get_movies_url(start)
        for url in urls:
            #print(url)
            movies, comments, reviews = [], [], []
            m = get_movie_all(url,comments,0,reviews,0)
            write_to_csv(movie_file,m)
            #write_to_mysql(movie_sql,m)
            # for c in comments:
            #     write_to_csv(comments_file,c)
            # for r in reviews:
            #     write_to_csv(reviews_file,r)
        start += 20

if __name__ == '__main__':
    # address_sql = 'insert into address values(%s,%s,%s)'
    # write_to_mysql(address_sql, (1, 'test', 4))
    get_movies()



