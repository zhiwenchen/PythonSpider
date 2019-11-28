import csv
import time
import traceback
import pymysql
import requests

connection = None
config = {'host':'118.25.133.235',
          'port':3306,
          'user':'analysys_club',
          'database':'douban_analysys',
          'password':'YiGuanXYZ.@()85258638',
          'charset':'utf8'
}
# config = {'host':'localhost',
#           'port':3306,
#           'user':'root',
#           'database':'douban',
#           'password':'202810',
#           'charset':'utf8'
# }
def close_connection():
    global connection
    if connection is not None:
        connection.close()

def get_connection():
    global connection
    connection = pymysql.connect(**config)

# 得到地区名字对应的id
# name为地区的名字
# def get_region_id(name):
#     global connection
#     try:
#         # 获取cursor对象
#         with connection.cursor() as cursor:
#             sql = 'select id from region where name=%s'
#             # 执行sql语句
#             cursor.execute(sql,name)
#             result = cursor.fetchone()
#             # 提交之前的操作，如果之前已经执行多次的execute，那么就都进行提交
#             connection.commit()
#             return result
#     except Exception as e:
#         print(traceback.format_exc())
#         return None


# 向电影表中插入/更新数据
def write_to_movie(values):
    global connection
    try:
        # 获取cursor对象
        with connection.cursor() as cursor:
            sql = 'select id from movie where id=%s'
            cursor.execute(sql, values[0])
            id = cursor.fetchone()
            if id is None: # 没有记录则插入
                sql = 'insert into movie values(%s'+ ',%s'*(len(values)-1) + ')'
                cursor.execute(sql,values)
            else: # 有记录则更新
                sql = 'update movie set short_comment_number=%s,comment_number=%s,score=%s,score_number=%s where id='+str(id[0])
                cursor.execute(sql,values[-6:-2])
            connection.commit()
    except Exception as e:
        print(e)
# 向书籍表中插入/更新数据
def write_to_book(values):
    global connection
    try:
        # 获取cursor对象
        with connection.cursor() as cursor:
            sql = 'select id from book where id=%s'
            cursor.execute(sql, values[0])
            id = cursor.fetchone()
            if id is None: # 没有记录则插入
                sql = 'insert into book values(%s'+ ',%s'*(len(values)-1) + ')'
                cursor.execute(sql,values)
            else: # 有记录则更新
                sql = 'update book set grade=%s,number=%s where id='+str(id[0])
                cursor.execute(sql,values[-3:-1])
            connection.commit()
    except Exception as e:
        print(e)
#向mysql中插入数据
# sql:要执行的sql语句
# values:要插入的数据
def write_to_mysql(table,values):
    global connection
    try:
        # 获取cursor对象
        with connection.cursor() as cursor:
            sql1 = 'select id from ' + table + ' where id=%s'
            cursor.execute(sql1, values[0])
            id = cursor.fetchone()
            if id is None:
                sql = 'insert into '+ table +' values(%s'+ ',%s'*(len(values)-1) + ')'
                cursor.execute(sql, values)
            connection.commit()
    except Exception as e:
        print(e)

def write_to_user(values):
    global connection
    try:
        # 获取cursor对象
        with connection.cursor() as cursor:
            sql1 = 'select id from user where id=%s'
            cursor.execute(sql1, values[0])
            result = cursor.fetchone()
            if result is None:
                sql = 'insert into user values(%s,%s,%s,NULL)'
                cursor.execute(sql, values)
            connection.commit()
    except Exception as e:
        print(e)

def get_users(limit):
    global connection
    try:
        # 获取cursor对象
        with connection.cursor() as cursor:
            sql = 'select * from user limit %s'
            cursor.execute(sql,limit)
            result = cursor.fetchall()
            # 提交之前的操作，如果之前已经执行多次的execute，那么就都进行提交
            connection.commit()
            return result
    except Exception as e:
        print(e)
        return None

def write_to_movie_region(values):
    global connection
    try:
        # 获取cursor对象
        with connection.cursor() as cursor:
            sql1 = 'select * from movie_region where movie_id=%s and region_id=%s'
            cursor.execute(sql1, values)
            result = cursor.fetchone()
            if result is None:
                sql = 'insert into movie_region values(%s,%s)'
                cursor.execute(sql, values)
            # 提交之前的操作，如果之前已经执行多次的execute，那么就都进行提交
            connection.commit()
    except Exception as e:
        print(e)

#向csv文件中写入数据
def write_to_csv(file,row):
    csvfile = open(file,'a',newline='',encoding='utf-8')
    try:
        writer = csv.writer(csvfile)
        writer.writerow(row)
    except IOError as e:
        print(e)
    finally:
        csvfile.close()

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
               'Connection':'close'}
# 获得url的HTML响应
def get_HTML_text(url):
    for i in range(2):
        try:
            r = requests.get(url,headers=headers)
            r.raise_for_status()
            r.encoding = 'utf-8'
            html = r.text
            return html
        except Exception as e:
            print(traceback.format_exc())
            time.sleep(2)
            continue
    return None