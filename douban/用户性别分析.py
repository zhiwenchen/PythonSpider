import re

from bs4 import BeautifulSoup
from aip import AipFace
from MyUtils import *

APP_ID = '17791414'
API_KEY = 'vaW7A8XYhWfuQ3XjXRDo3wfr'
SECRET_KEY = 'zA7FLrfyFuC8qyMiHhXGO6ttKFqjMgCG'
client = AipFace(APP_ID,API_KEY,SECRET_KEY)

# 根据头像得到性别
def get_gender_by_head(head_url):
    option = {}
    # face_type 真实人脸/卡通人脸 type:human: 真实人脸 cartoon: 卡通人脸
    option['face_field'] = 'gender,face_type'
    imageType = 'URL'
    res = client.detect(head_url, imageType, option)
    result = res['result']
    if result != None:
        gender = result['face_list'][0]['gender']
        print(gender)
        if gender['probability'] >= 0.5:
            return gender['type']
        else:
            return None
    return None

# 得到用户看过的电影的标签
def get_user_movie_tags(user_id):
    pass

# 得到用户看过的书籍的标签
def get_user_book_tags(user_id):
    pass

# 得到用户的简介
def get_user_intro(user_id):
    url = 'https://www.douban.com/people/' + str(user_id) + '/' #用户主页
    html = get_HTML_text(url)
    soup = BeautifulSoup(html, 'lxml')
    intro = soup.find(id='intro_display') # 用户简介
    if intro is not None:
        introduction = intro.text
    else:
        introduction = None
    return introduction

# 得到用户加入的小组
def get_user_groups(user_id):
    # 小组url
    groups = []
    group_url = 'https://www.douban.com/group/people/'+str(user_id)+'/joins'
    html = get_HTML_text(group_url)
    soup = BeautifulSoup(html, 'lxml')
    gs = soup('a',attrs = {"href": re.compile(r'^https\:\/\/www\.douban\.com\/group\/\w+\/$'),"title":True})
    if gs is not None:
        for g in gs:
            groups.append(g['title'])
    return groups

def predict_user_gender():
    filename = 'D:\\users.csv'
    #根据用户昵称、用户签名、用户小组三个方面来判断用户性别
    # 获取用户信息,'introduction'
    write_to_csv(filename,['url','name','head','gender'])
    users = get_users(200)
    for user in users:
        id = user[0] #用户id
        name = user[1] #用户昵称
        head = user[2]
        gender = get_gender_by_head(head)

# url = 'https://img1.doubanio.com/icon/ul56154739-8.jpg'
# get_gender_by_head(url)
print(get_user_groups('lazybobo'))
print(get_user_intro('lazybobo'))






