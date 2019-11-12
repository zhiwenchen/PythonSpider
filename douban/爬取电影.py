import json
import re
import datetime
from MyUtils import *
from bs4 import BeautifulSoup
r_head = ('评论ID','类型','子类型','状态','评分','时间','标题','内容','有用数','无用数','目标id','用户id','用户名','用户头像')

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
            cid = comment.attrs['data-cid'] #评论ID
            votes = int(comment.find(class_='votes').string)  # num
            c_info = comment.find(class_='comment-info')
            avatar = comment.find(class_='avatar').find('img').attrs['src']
            user = c_info.find('a').text # 用户昵称
            uid = c_info.find('a').attrs['href'].split('/')[-2] # 用户id
            rating = c_info.find(class_='rating')
            if rating is not None:
                rate = int(rating.attrs['class'][0][-2:]) / 10
            else:
                rate = None
            time = c_info.find(class_='comment-time').attrs['title']
            c_time = datetime.datetime.strptime(time,"%Y-%m-%d %H:%M:%S")
            short = comment.find(class_='short').string
            s = 0 if status == 'P' else 1
            comments.append([cid,1, 0, s, rate, c_time, None, short, votes, None,movie_id,uid,user,avatar])
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
# 类型:int型：电影存1,书籍存2,音乐存3
# 子类型:int型：短评存0,长评存1
# 是否看过:int型：看过存0,想看存1,无此项(影评无此项)则为null
# 目标id:电影id、书籍id、音乐id
def get_reviews(movie_id,start,reviews):
    url = 'https://movie.douban.com/subject/'+str(movie_id)+'/reviews?sort=hotest&start='+str(start)
    html = get_HTML_text(url)
    soup = BeautifulSoup(html, 'lxml')
    rs = soup(class_='review-item')
    for r in rs:
        rid = int(r.attrs['id'])
        uid = r.find(class_='avator').attrs['href'].split('/')[-2]
        avator = r.find(class_='avator').find('img').attrs['src']
        name = r.find(class_='name').text
        rating = r.find(class_='main-title-rating')
        if rating is not None:
            rate = int(rating.attrs['class'][0][-2:]) // 10
        else:
            rate = None
        time = r.find(class_='main-meta').text
        r_time = datetime.datetime.strptime(time,"%Y-%m-%d %H:%M:%S")
        title = r.select('.main-bd>h2')[0].text
        #reply = (r.find(class_='reply').text)[:-2]  # 回应数
        url1 = 'https://movie.douban.com/j/review/'+str(rid)+'/full'
        res = requests.get(url1).json()
        soup = BeautifulSoup(res['html'], 'lxml')
        content = soup.text
        votes = res['votes']
        useful_count = int(votes['useful_count'])
        useless_count = int(votes['useless_count'])
        reviews.append([rid,1,1,None,rate,r_time,title,content,useful_count,useless_count,str(movie_id),uid,name,avator])

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
    while start < comments_F_num and start < comments_num: # 得到未看评论
        get_comments(movie_id,start,'F',comments)
        start += 20
    start = 0
    while start < r_num and start < reviews_num: # 得到所有影评
        get_reviews(movie_id, start, reviews)
        start += 20

    return m
# region = ("中国大陆","美国","中国香港","中国台湾","日本","韩国","英国","法国","德国","意大利","西班牙","印度",
#           "泰国","俄罗斯","伊朗","加拿大","澳大利亚","爱尔兰","瑞典","巴西","丹麦")
def get_movies():
    # movie_sql = 'insert into movie values(%s'+ ',%s'*15 + ')'
    # comment_sql = 'insert into comment values(%s' +',%s'*11 + ')'
    movies_csv = 'D:\\movies.csv'
    comments_csv = 'D:\\comments.csv'
    start = 0
    for i in range(10):
        urls = get_movies_url(start)
        for url in urls:
            comments = []
            reviews = []
            try:
                m = get_movie_all(url,comments,20,reviews,20)
                value = [x for x in m if m.index(x)!=6]
                write_to_mysql('movie',value)
                regions = m[6] # 得到国家和地区
                if regions is not None:
                    region = regions.split('/')
                    for reg in region:
                        reg = reg.strip()
                        if reg != '':
                            region_id = get_region_id(reg)
                            if region_id is not None:
                                pass
                                write_to_movie_region([m[0],region_id])
                for c in comments:
                    write_to_mysql('comment',c[:-2])
                    write_to_mysql('user',c[-3:])
                for r in reviews:
                    write_to_mysql('comment',r[:-2])
                    write_to_mysql('user',r[-3:])
            except Exception as e:
                print(traceback.format_exc())
                continue
        start += 20
        print('成功存储20条......')

if __name__ == '__main__':
    # get_movies()
    m_id = 10741834
    url = 'https://movie.douban.com/subject/' + str(m_id) +'/'
    m = get_movie_all(url,[],0,[],0)
    value = [x for x in m if m.index(x) != 6]
    write_to_mysql('movie',value)

