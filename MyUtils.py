import csv
import time
import traceback
import pymysql
import requests

config = {'host':'118.25.133.235',
          'port':3306,
          'user':'root',
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

# 得到地区名字对应的id
# name为地区的名字
def get_region_id(name):
    connection = pymysql.connect(**config)
    try:
        # 获取cursor对象
        with connection.cursor() as cursor:
            sql = 'select id from region where name=%s'
            # 执行sql语句
            cursor.execute(sql,name)
            result = cursor.fetchone()
            # 提交之前的操作，如果之前已经执行多次的execute，那么就都进行提交
            connection.commit()
            return result
    except Exception as e:
        print(traceback.format_exc())
        return None
    finally:
        # 关闭connection对象
        connection.close()

#向mysql中插入数据
# sql:要执行的sql语句
# values:要插入的数据

def write_to_mysql(table,values):
    connection = pymysql.connect(**config)
    try:
        # 获取cursor对象
        with connection.cursor() as cursor:
            sql1 = 'select id from ' + table + ' where id=%s'
            cursor.execute(sql1, values[0])
            id = cursor.fetchone()
            if id is not None:
                sql = 'insert into '+ table +' values(%s'+ ',%s'*(len(values)-1) + ')'
                cursor.execute(sql, values)
            # 提交之前的操作，如果之前已经执行多次的execute，那么就都进行提交
            connection.commit()
    except Exception as e:
        print(traceback.format_exc())
    finally:
        # 关闭connection对象
        connection.close()
def write_to_movie_region(values):
    connection = pymysql.connect(**config)
    try:
        # 获取cursor对象
        with connection.cursor() as cursor:
            sql1 = 'select * from movie_region where movies_id=%s and region_id=%s'
            cursor.execute(sql1, values)
            result = cursor.fetchone()
            if result is not None:
                sql = 'insert into movie_region values(%s,%s)'
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
    csvfile = open(file,'a',newline='',encoding='utf-8')
    try:
        writer = csv.writer(csvfile)
        writer.writerow(row)
    except IOError as e:
        print(e)
    finally:
        csvfile.close()

# 获得url的HTML响应
def get_HTML_text(url):
    html = ""
    i = 0
    while html == "" and i < 5:
        try:
            r = requests.get(url)
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