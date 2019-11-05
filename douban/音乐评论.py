import requests
import re
from bs4 import BeautifulSoup
import json
import pymysql
import bs4
import csv
header = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
}

def get_soup(url):
    res = requests.get(url,headers = header)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text,"html.parser")
    return soup



# 根据page_url获取本页的所有长评，并返回
#  [i["data-cid"],'1',username,'是否看过',star,data,title,text,agree,disagree,obj_id] 见表设计
def long_comment(page_url):
    soup = get_soup(page_url)
    items1 = soup.find(attrs={"class": "review-list"})
    items2 = items1.find_all('div', recursive=False)
    comment = []
    for i in items2:
        obj_id = re.findall(r'\d+',page_url)[0]
        username = i.find(class_='name').text
        data = i.find(class_='main-meta').text.strip()
        try:
            star = i.find('span',attrs = {"class":"main-title-rating"})
            star = re.findall(r'\d+',star['class'][0])[0]
        except Exception:
            star = ''
        main = i.find(class_='main-bd')
        title = main.select('h2 a')[0].text
        agree_text = main.find(class_='action-btn up').text
        disagree_text = main.find(class_ = 'action-btn down').text
        try:
            agree = re.findall(r'\d+',agree_text)[0]
        except Exception:
            agree = '0'
        try:
            disagree = re.findall(r'\d+',disagree_text)[0]
        except Exception:
            disagree = '0'
        text_url1 = main.find(attrs = {"class":"hidden"})['id']
        text_url2 = re.findall(r'\d+',text_url1)[0]
        text_url3 = 'https://music.douban.com/j/review/'+text_url2+'/full'
        text = re.sub(r'\s',' ',json.loads(get_soup(text_url3).text)['html'])
        comment_item = [i["data-cid"],'2','1',username,'',star,data,title,text,agree,disagree,obj_id]
        comment.append(comment_item)
    return comment


# 根据page_url获取本页的所有长短评，并返回
# [i["data-cid"],'0',username,'是否看过',star,data,'长评标题',text,agree,'无用数量',obj_id] 见表设计
def short_comment(page_url):
    comment = []
    soup = get_soup(page_url)
    items = soup.find_all(attrs = {"class":"comment-item"})
    obj_id = re.findall(r'\d+',page_url)[0]
    for i in items:
        agree = i.find(attrs={"class":"vote-count"}).text
        text = i.find('p').text.strip()
        comment_info = i.find(class_= "comment-info")
        try:
            star = comment_info.find('span',attrs = {"class":"rating"})
            star = re.findall(r'\d+',star['class'][1])[0]
        except Exception:
            star = ''


        data = comment_info.find('span',attrs = {"class":""}).text
        username = comment_info.find('a').text
        comment_item = [i["data-cid"],'2','0',username,'',star,data,'',text,agree,'',obj_id]
        comment.append(comment_item)
    return comment


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

# 爬取长评评论，存入csv
# 参数：每首歌的评论url，爬取页数
def get_long_comment(base_url,page):
    for i in range(page):
        page_url = base_url+str(20*i)
        try:
            comment = long_comment(page_url)
            for c in comment:
                write_to_csv('D:\\long_comment.csv',c)
        except Exception as e:
            print(e)
        print("long" + str(i) + "is success")

# 爬取短评评论，存入csv
# 参数：每首歌的评论url，爬取页数
def get_short_comment(base_url,page):
    for i in range(page):
        page_url = base_url+str(i+1)
        try:
            comment = short_comment(page_url)
            for c in comment:
                write_to_csv('D:\\short_comment.csv',c)
        except Exception as e:
            print(e)
        print("short" + str(i) + "is success")

if __name__ == '__main__':
    c_head = ['cid','class_type', 'comment_type', 'user', 'statue', 'star', 'time', 'title', 'content', 'help_num', 'helpless_num','obj_id']
    write_to_csv('D:\\short_comment.csv', c_head)
    write_to_csv('D:\\long_comment.csv', c_head)
    long_base_url = 'https://music.douban.com/subject/1401853/reviews?start='
    short_base_url = 'https://music.douban.com/subject/1401853/comments/hot?p='
    get_long_comment(long_base_url,2)
    get_short_comment(short_base_url, 15)