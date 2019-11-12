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
    res = requests.get(url, headers=header)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, "html.parser")
    return soup


# 根据page_url获取本页的所有长评，并返回
#  [i["data-cid"],'1',username,'是否看过',star,data,title,text,agree,disagree,obj_id] 见表设计
def long_comment(page_url):
    soup = get_soup(page_url)
    items1 = soup.find(attrs={"class": "review-list"})
    items2 = items1.find_all('div', recursive=False)
    comment = []
    for i in items2:
        user_avatar = i.find('img')['src']
        user_id_url = i.find('a')['href']
        user_id = user_id_url.split('/')[-2]
        obj_id = re.findall(r'\d+', page_url)[0]
        username = i.find(class_='name').text
        data = i.find(class_='main-meta').text.strip()
        try:
            star = i.find('span', attrs={"class": "main-title-rating"})
            star = re.findall(r'\d+', star['class'][0])[0]
            star = int(int(star) / 10)
        except Exception:
            star = None
        main = i.find(class_='main-bd')
        title = main.select('h2 a')[0].text
        agree_text = main.find(class_='action-btn up').text
        disagree_text = main.find(class_='action-btn down').text
        try:
            agree = re.findall(r'\d+', agree_text)[0]
        except Exception:
            agree = '0'
        try:
            disagree = re.findall(r'\d+', disagree_text)[0]
        except Exception:
            disagree = '0'
        text_url1 = main.find(attrs={"class": "hidden"})['id']
        text_url2 = re.findall(r'\d+', text_url1)[0]
        text_url3 = 'https://music.douban.com/j/review/' + text_url2 + '/full'
        text = re.sub(r'\s', ' ', json.loads(get_soup(text_url3).text)['html'])
        comment_item = [int(i["data-cid"]), 3, 1, None, star, data, title, text, int(agree), int(disagree), int(obj_id),
                        user_id, username, user_avatar]
        comment.append(comment_item)
    return comment


# 根据page_url获取本页的所有短评，并返回
# [i["data-cid"],'0',username,'是否看过',star,data,'长评标题',text,agree,'无用数量',obj_id] 见表设计
def short_comment(page_url):
    comment = []
    soup = get_soup(page_url)
    items = soup.find_all(attrs={"class": "comment-item"})
    obj_id = re.findall(r'\d+', page_url)[0]
    for i in items:
        user_avatar = i.find('img')['src']
        user_id_url = i.find('a')['href']
        user_id = user_id_url.split('/')[-2]
        agree = i.find(attrs={"class": "vote-count"}).text
        text = i.find('p').text.strip()
        comment_info = i.find(class_="comment-info")
        try:
            star = comment_info.find('span', attrs={"class": "rating"})
            star = re.findall(r'\d+', star['class'][1])[0]
            star = int(int(star) / 10)
        except Exception:
            star = None

        data = comment_info.find('span', attrs={"class": ""}).text
        username = comment_info.find('a').text
        comment_item = [int(i["data-cid"]), 3, 0, None, star, data, 'NULL', text, int(agree), None, int(obj_id),
                        user_id, username, user_avatar]
        #         print(comment_item)
        comment.append(comment_item)
    return comment


# 向csv文件中写入数据
def write_to_csv(file, row):
    csvfile = open(file, 'a', newline='', encoding='utf-8-sig')
    try:
        writer = csv.writer(csvfile)
        writer.writerow(row)
    except IOError as e:
        print(e)
    finally:
        csvfile.close()


# 传入音乐基本信息，存入mysql的music_info表
# 传评论 和用户
def write_mysql(list, conn):
    cs1 = conn.cursor()
    query = "insert into comment()values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    values = (
    list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7], list[8], list[9], list[10], list[11])
    query2 = "insert into user()values(%s,%s,%s)"
    values2 = (list[11], list[12], list[13])
    cs1.execute(query, values)
    conn.commit()
    cs1.execute(query2, values2)
    conn.commit()
    cs1.close()


# 爬取长评评论，存入csv/mysql
# 参数：每首歌的评论url，爬取页数
def get_long_comment(base_url, page, conn):
    for i in range(page):
        page_url = base_url + str(20 * i)
        try:
            comment = long_comment(page_url)
            for c in comment:
                try:
                    write_mysql(c, conn)
                except Exception:
                    pass
        except Exception as e:
            pass
        print("long" + str(i) + "is success")


# 爬取短评评论，存入csv/mysql
# 参数：每首歌的评论url，爬取页数
def get_short_comment(base_url, page, conn):
    for i in range(page):
        page_url = base_url + str(i + 1)
        try:
            comment = short_comment(page_url)
            for c in comment:
                try:
                    write_mysql(c, conn)
                except Exception:
                    pass
        except Exception as e:
            print(e)
        print("short" + str(i) + "is success")


# 根据页url获取本页所有的音乐url
def get_music_url(page_url):
    soup = get_soup(page_url)
    music_item = soup.find_all('a', attrs={"class": "nbg"})
    music_item_url = [i['href'] for i in music_item]
    return music_item_url


if __name__ == '__main__':
    # conn = pymysql.connect(host='localhost', port=3306, database='douban', user='root', password='x5', charset='utf8')
    conn = pymysql.connect(host='118.25.133.235', port=3306, database='douban_analysys', user='root',password='YiGuanXYZ.@()85258638', charset='utf8')

    page = 3
    for i in range(3,10):
        print('------------------------page' + str(i) + '评论')
        page_url = 'https://music.douban.com/tag/%E5%8D%8E%E8%AF%AD?start=' + str(i * 20) + '&type=T'
        urls = get_music_url(page_url)
        for u in urls:
            long_base_url = u + 'reviews?start='
            short_base_url = u + 'comments/hot?p='
            get_long_comment(long_base_url, 2, conn)
            get_short_comment(short_base_url, 2, conn)
    #     short_base_url = 'https://music.douban.com/subject/1401853/comments/hot?p='
    #     get_short_comment(short_base_url, 2,conn)

    conn.close()

# 前六十首音乐评论已经爬取，长40+短40