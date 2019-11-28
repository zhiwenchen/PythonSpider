import datetime
import re
import bs4
from bs4 import BeautifulSoup
from MyUtils import *

user_head=('用户id','用户名','用户头像')
#获得书籍短评
# type:#0为短评  1为长评
#rating：为数字 #head:短评为None
#helpless_num：短评为None
def get_comments(book_id,page,comments):
    url = "https://book.douban.com/subject/"+str(book_id)+"/comments/new?p="+str(page)
    try:
        html = get_HTML_text(url)
        soup = BeautifulSoup(html,"lxml")
        cs = soup(class_='comment-item')
        for comment in cs:
            cid = comment.attrs['data-cid']
            votes = int(comment.find(class_='vote-count').string)  # num
            avatar = comment.find(class_='avatar').find('img').attrs['src']
            c_info = comment.find(class_='comment-info')
            uid = c_info.find('a').attrs['href'].split('/')[-2]  # 用户id
            user = c_info.find('a').text
            rating = c_info.find(class_='rating')
            if rating is not None:
                rate = int(rating.attrs['class'][1][-2:]) / 10
            else:
                rate = None
            time = c_info('span')[-1].text
            short = comment.find(class_='short').string
            comments.append([cid,2, 0, None, rate, datetime.datetime.strptime(time,"%Y-%m-%d"), None, short, votes, None,book_id,uid,user,avatar])
    except Exception as e:
        print(traceback.format_exc())

# 获得书评
# 类型:int型：电影存1,书籍存2,音乐存3
# 子类型:int型：短评存0,长评存1
# 是否看过:int型：看过存0,想看存1,无此项(影评无此项)则为null
# 目标id:电影id、书籍id、音乐id
c_head = ('评论ID','类型','用户名','状态','评分','时间','标题','内容','有用数','无用数','目标id','用户id','用户名','头像')
def get_reviews(book_id,page,reviews):
    url = 'https://book.douban.com/subject/'+str(book_id)+'/reviews?sort=time&start='+str((page-1)*20)
    html = get_HTML_text(url)
    soup = BeautifulSoup(html, 'lxml')
    rs = soup(class_='review-item')
    for r in rs:
        rid = int(r.attrs['id'])
        name = r.find(class_='name').text
        uid = r.find(class_='avator').attrs['href'].split('/')[-2]
        avator = r.find(class_='avator').find('img').attrs['src']
        rating = r.find(class_='main-title-rating')
        if rating is not None:
            rate = int(rating.attrs['class'][0][-2:]) // 10
        else:
            rate = None
        time = r.find(class_='main-meta').text
        title = r.select('.main-bd>h2')[0].text
        url1 = 'https://movie.douban.com/j/review/'+str(rid)+'/full'

        res = requests.get(url1,headers=headers,timeout=10).json()
        soup = BeautifulSoup(res['html'], 'lxml')
        content = soup.text
        votes = res['votes']
        useful_count = int(votes['useful_count'])
        useless_count = int(votes['useless_count'])
        reviews.append([rid,2,1,None,rate,datetime.datetime.strptime(time,"%Y-%m-%d %H:%M:%S"),title,content,useful_count,useless_count,str(book_id),uid,name,avator])

b_head = ('id','书籍名','作者','出版社','出品方','副标题','原作名',
          '译者','出版年','页数','定价','装帧','丛书','ISBN','封面','标签','评分','评价人数','简介')
head = ('作者','出版社','出品方','副标题','原作名',
          '译者','出版年','页数','定价','装帧','丛书','ISBN')

# start_page:开始的页数(1为第一页)
# page_nums:要爬取的页数
def get_book_all(url,comments,c_start_page,c_page_num,reviews,r_start_page,r_page_num):
    b = [None for _i in range(len(b_head))]
    book_id = int(url.split('/')[-2])  # 书籍ID
    html = get_HTML_text(url)
    soup = BeautifulSoup(html, "lxml")
    book_name = soup.find('h1').find('span').text  # 书籍名
    book_cover = soup.find(id='mainpic').find('img').attrs['src']
    link_report = soup.find(id='link-report') #书籍简介
    hidden = link_report.find(class_='all hidden')
    if hidden is not None:
        intro = hidden.find(class_='intro').text
    else:
        intro = link_report.find(class_='intro').text
    sort = '' #标签
    tags = soup(class_='tag')
    for i in range(len(tags)):
        if i < len(tags) - 1:
            sort += tags[i].text + '/'
        else:
            sort += tags[i].text
    rate = soup.find('strong', class_='rating_num').text
    if rate == None or rate == '':
        rating_num = None  # 评分
    else:
        rating_num = float(rate)
    r_people = soup.find('a', class_='rating_people')
    if r_people == None:
        rating_people = 0
    else:
        rating_people = int(r_people.find('span').text.strip())  # 评价人数
    comments_num = int((soup.select('.mod-hd h2 .pl a')[0].text)[3:-2])
    reviews_num = int((soup.find('a', attrs={'href': 'reviews'}).text)[3:-2])
    b[0], b[1], b[-5],b[-4], b[-3], b[-2],b[-1]= book_id, book_name, book_cover, sort,rating_num,rating_people,intro
    text = soup.find(attrs={'id': 'info'})
    info = []
    spans = text('span',recursive=False)
    for span in spans:
        i = 0
        sp = span
        s = ''
        while(True and i<50):
            i += 1
            if sp.name == 'br':
                info.append(s)
                break
            elif isinstance(sp,bs4.NavigableString):
                if(sp != None):
                    s += sp.strip()
            sp = sp.next
    for s1 in info:
        if s1 is not "":
            label = re.split(':', s1, 1)[0]
            if label in head:
                index = b_head.index(label)
                b[index] = re.split(':', s1, 1)[1].strip()
    if b[9] is not None: # 页数
        b[9] = int(b[9])
    if b[10] is not None:
        b[10] = float(b[10][:-1]) #价格
    if b[2] is not None:
        b[2] = re.sub(r'\s|\n|\r','',b[2]) # 去掉作者里的空白符
    while c_start_page <= c_page_num and (c_start_page-1)*20 < comments_num:
        get_comments(book_id,c_start_page,comments)
        c_start_page += 1
    while r_start_page <= r_page_num and (r_start_page-1)*20 < reviews_num:
        get_reviews(book_id,r_start_page,reviews)
        r_start_page += 1
    return b

def get_book_url(start):
    urls = []
    url = "https://book.douban.com/tag/小说?type=T&start=" + str(start)
    html = get_HTML_text(url)
    soup = BeautifulSoup(html,'lxml')
    items = soup('li',class_='subject-item')
    for item in items:
        href = item.select('div.info>h2>a')[0].attrs['href']
        urls.append(href)
    return urls

def get_books():
    start = 80
    get_connection()
    for i in range(36):
        urls = get_book_url(start)
        for url in urls:
            try:
                comments, reviews = [], []
                b = get_book_all(url, comments, 1,5, reviews, 1, 2)
                write_to_book(b)
                for r in reviews:
                    try:
                        write_to_mysql('comment', r[:-2])
                        write_to_user(r[-3:])
                        # write_to_mysql('user', r[-3:])
                    except Exception as e:
                        print(e)
                        continue
                for c in comments:
                    try:
                        write_to_mysql('comment', c[:-2])
                        write_to_user(c[-3:])
                        # write_to_mysql('user', c[-3:])
                    except Exception as e:
                        print(e)
                        continue
            except Exception as e:
                print(traceback.format_exc())
                continue
        start += 20
        print("[",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"]成功存储"+str(start)+"条......")
    close_connection()

if __name__ == '__main__':
    get_books()