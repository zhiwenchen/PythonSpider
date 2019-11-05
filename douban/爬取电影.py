import json
import csv
import time
import re
import requests
import traceback
from bs4 import BeautifulSoup

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
    html = get_HTML_text(url)
    data = json.loads(html)['data']
    for d in data:
        urls.append(d['url'])
    return urls


c_head = ['cid', 'type', 'user', 'status', 'rate',
              'time', 'head', 'content', 'useful_count', 'useless_count']
#获得短评
# type:#0为短评  1为长评#status：P为看过，F为未看
#rating：为数字 #head:短评为None
#helpless_num：短评为None
def get_m_comments(subject_id,start,status,comments):
    url = "https://movie.douban.com/subject/"+str(subject_id)+"/comments?limit=20&sort=new_score&start="+str(start)+"&status="+str(status)
    html = get_HTML_text(url)
    soup = BeautifulSoup(html,"lxml")
    cs = soup(class_='comment-item')
    for comment in cs:
        cid = comment.attrs['data-cid']
        votes = int(comment.find(class_='votes').string) #num
        c_info = comment.find(class_='comment-info')
        user = c_info.find('a').text
        rating = c_info.find(class_='rating')
        if rating is not None:
            rate = int(rating.attrs['class'][0][-2:])/10
        else:
            rate = None
        time = c_info.find(class_='comment-time').attrs['title']
        short = comment.find(class_='short').string
        comments.append([cid,0,user,status,rate,time,None,short,votes,None])

#获得完整影评

#获得影评
def get_reviews(subject_id,start,reviews):
    url = 'https://movie.douban.com/subject/'+subject_id+'/reviews?sort=hotest&start='+str(start)
    html = get_HTML_text(url)
    soup = BeautifulSoup(html, 'lxml')
    rs = soup(class_='review-item')
    for r in rs:
        rid = r.attrs['id']
        name = r.find(class_='name').string
        rating = r.find(class_='main-title-rating')
        rate = int(rating.attrs['class'][0][-2:]) / 10
        time = r.find(class_='main-meta').text
        title = r.select('.main-bd>h2')[0].text
        reply = (r.find(class_='reply').text)[:-2]
        url1 = 'https://movie.douban.com/j/review/'+rid+'/full'
        res = requests.get(url1).json()
        soup = BeautifulSoup(res['html'], 'lxml')
        content = soup.text
        votes = res['votes']
        useful_count = votes['useful_count']
        useless_count = votes['useless_count']
        reviews.append([rid,1,name,None,rate,time,title,content,useful_count,useless_count,reply])

def get_movies():
    mid = 1 #序号
    start = 0
    m_head = ('ID','电影名','导演','编剧','主演','类型','制片国家/地区','语言','上映日期',
              '片长','又名','IMDb链接','短评数量','影评数量','评分','评价数量')
    file = 'D:\\movies.csv'
    write_to_csv(file,m_head)
    for i in range(5):
        urls = get_movies_url(start)
        for url in urls:
            m = []
            try:
                html = get_HTML_text(url)
                soup = BeautifulSoup(html,"html.parser")
                movie_name = soup.find('h1').find('span').text
                rate = soup.find('strong',class_='rating_num').text
                rating_people = soup.find('a',class_='rating_people').find('span').text
                comments_num = soup.select('#comments-section h2 .pl a')[0].text
                reviews_num = soup.find('a',attrs={'href':'reviews'}).text
                m.append(mid)
                m.append(movie_name)
                text = soup.find(attrs={'id':'info'}).text
                text.strip()
                info = text.split('\n')
                for s in info:
                    if s is not "":
                        label = re.split(':',s,1)[0]
                        if label in m_head:
                            m.append(re.split(':',s,1)[1])
                #comments = get_comments(url)
                #write_to_csv(file,m)
                print(rate,rating_people,comments_num,reviews_num)
                #print('成功写入', mid, '条数据')
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
    c_head = ['评论ID', '类型(长/短)', '用户', '状态(已/未看)', '评分',
              '评价时间', '标题', '内容', '有用数', '无用数']
    # #爬取评论
    # c_file = 'D:\\已看短评.csv'
    # #c_file = 'D:\\未看短评.csv'
    # url = 'https://movie.douban.com/subject/30166972/'

    # s_id = url.split('/')[-2]
    # start = 0
    #
    # write_to_csv(c_file,c_head)
    # for i in range(5):
    #     comments = []
    #     get_m_comments(s_id,start,'P',comments)
    #     for comment in comments:
    #         write_to_csv(c_file,comment)
    #     start += 20


    #爬取影评
    c_file = 'D:\\影评.csv'
    r_head = ['评论ID','类型','用户名','状态','评分','时间','标题','内容','有用数','无用数','回应']
    url = 'https://movie.douban.com/subject/30166972/'
    s_id = url.split('/')[-2]
    start = 0
    write_to_csv(c_file,r_head)
    for i in range(5):
        reviews = []
        get_reviews(s_id,start,reviews)
        for r in reviews:
            write_to_csv(c_file,r)
        start += 20

    get_movies()


