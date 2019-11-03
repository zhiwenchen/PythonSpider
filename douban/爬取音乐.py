import requests
import re
from bs4 import BeautifulSoup
import json
import pymysql

header = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
}
mov_num = 200


url = 'https://music.douban.com/subject/34785471/'


def get_soup(url):
    res = requests.post(url, headers=header)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, "html.parser")
    return soup


# 获取音乐字段 Music_name,Singer,Type,Album_type,Medium,Issue_time,Publisher,Comment_num,Comment_href
def get_music_info(soup):
    # 获取表单信息
    info = soup.find(attrs={"id": "info"})
    music_name = soup.find('h1')
    info.text
    result = info.text.split()
    for i in result:
        if re.search(r':', i, re.M | re.I):
            result.remove(i)

    comment_info = soup.find(attrs={"class": "mod-hd"})
    comment_a = comment_info.find_all('a')[1]
    comment_href = comment_a['href']
    comment_num = re.findall(r'\d+', comment_a.text)[0]
    result.append(comment_num)
    result.append(comment_href)
    result.insert(0, music_name)
    print(result)
    return result


# 传入音乐基本信息，存入mysql的music_info表
def write_mysql1(list):
    # 创建connection连接
    conn = pymysql.connect(host='localhost', port=3306, database='douban', user='root', password='x5', charset='utf8')
    # 获取cursor对象
    cs1 = conn.cursor()
    # 执行sql语句
    #     query = 'insert into '+table+'values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    query = 'insert into music_info (Music_name,Singer,Type,Album_type,Medium,Issue_time,Publisher,Comment_num,Comment_href)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    values = (list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7], list[8])
    cs1.execute(query, values)
    # 提交之前的操作，如果之前已经执行多次的execute，那么就都进行提交
    conn.commit()
    # 关闭cursor对象
    cs1.close()
    # 关闭connection对象
    conn.close()


# 根据url爬取音乐基本并存入数据库
def get_base_info(url):
    soup = get_soup(url)
    result = get_music_info(soup)
    print(result)


#     write_mysql1(result)


def write_mysql2(list):
    conn = pymysql.connect(host='localhost', port=3306, database='douban', user='root', password='x5', charset='utf8')
    cs1 = conn.cursor()
    query = 'insert into music_info (Music_name,Singer,Type,Album_type,Medium,Issue_time,Publisher,Comment_num,Comment_href)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    values = (list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7], list[8])
    cs1.execute(query, values)
    conn.commit()
    cs1.close()
    conn.close()


if __name__ == '__main__':
    get_base_info('https://music.douban.com/subject/34815690/')
