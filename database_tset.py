import pymysql
conn = pymysql.connect(host='localhost', user='root', password='my142857SQL@&', database='fruit_system')
print("连接成功")
conn.close()