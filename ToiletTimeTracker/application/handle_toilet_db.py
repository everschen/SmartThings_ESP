#!/usr/bin/env python3


import smtplib
from email.mime.text import MIMEText
import time
import argparse
import mysql.connector

#########################################################################################

SENDER = "your_email_address"
RECVER = "your_email_address"
PASSWD = "your_email_password"
MAIL_SERVER = "smtp.163.com"
MAIL_SERVER_PORT = 994

DB_HOST='your_db_host'
DB_USER='your_db_user'
DB_PASSWD='your_db_password'
DB_NAME='live_monitor'

STOOL_TIME_MIN = 120000 #2 minutes
URINE_TIME_MIN = 40000  #40 seconds

#########################################################################################


def send_email(title, content, sleep):
	if(title == None or content == None):
		print("parameters number error")
		exit(1)
	subject = title
	sender = SENDER
	recver = RECVER
	password = PASSWD
	message = MIMEText(content,"plain","utf-8")
	 
	message['Subject'] = subject
	message['To'] = recver
	message['From'] = sender

	if sleep:
		time.sleep(8 * 60 * 60)
	 
	smtp = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_SERVER_PORT)
	smtp.login(sender,password)
	smtp.sendmail(sender,[recver],message.as_string())
	smtp.close()

# 连接到 MySQL 数据库
connection = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWD,
    database=DB_NAME
)



def update_send_notification(id):
    cursor = connection.cursor()
    query = "UPDATE toilet SET send_notification = 1 WHERE id = %s"
    values = (id,)
    cursor.execute(query, values)
    connection.commit()


parser = argparse.ArgumentParser(description='add force to send eamil')
parser.add_argument('-s', action='store_true', help='add force to send eamil')
args = parser.parse_args()



print("----------------------------all time------------------------------------------------------------")
# 创建一个游标对象
cursor = connection.cursor()
table_name = 'toilet'
query = f'SELECT * FROM {table_name} WHERE toilet_id=1 AND duration >= {URINE_TIME_MIN} AND DATE(`timestamp`) = CURDATE() order by id DESC;'
cursor.execute(query)

id_list = []
content = ""
firstone = True
result = cursor.fetchall()
for row in result:
    print(row)
    #print(row.)
    (id, duration, toilet_id, mac, datetime, send_notification) = row
    print(duration, datetime)
    if not send_notification:
       id_list.append(id)
    seconds = duration//1000
    if firstone:
        title = str(datetime) + "次卫卫生间使用了" + str(seconds//60) +"分钟" + str(seconds%60) + "秒 "
        firstone = False
    
    if duration >= STOOL_TIME_MIN:
        content += str(datetime) + "   " + str(seconds//60) +"分钟" + str(seconds%60) + "秒" +" ---> (stool?)\n"
    else:
        content += str(datetime) + "   " + str(seconds//60) +"分钟" + str(seconds%60) + "秒" +"\n"

if id_list:
    print("since have new stool record, will notify")
    send_email(title, content, False)
    for id in id_list:
        update_send_notification(id)
else:
    if args.s:
        print("force to send eamil, will notify")
        send_email(title, content, False)

# print("----------------------------stool time------------------------------------------------------------")
# # 创建一个游标对象
# cursor = connection.cursor()
# table_name = 'toilet'
# query = f'SELECT * FROM {table_name} WHERE toilet_id=1 AND duration >= {STOOL_TIME_MIN} AND DATE(`timestamp`) = CURDATE() order by id DESC;'
# cursor.execute(query)

# id_list = []
# content = ""
# firstone = True
# result = cursor.fetchall()
# for row in result:
#     print(row)
#     #print(row.)
#     (id, duration, toilet_id, mac, datetime, send_notification) = row
#     print(duration, datetime)
#     if not send_notification:
#        id_list.append(id)
#     seconds = duration//1000
#     if firstone:
#         title = str(datetime) + "次卫卫生间使用了" + str(seconds//60) +"分钟" + str(seconds%60) + "秒 (stool)"
#         firstone = False
#     content += str(datetime) + "   " + str(seconds//60) +"分钟" + str(seconds%60) + "秒" +"\n"

# if id_list:
#     print("since have new stool record, will notify")
#     send_email(title, content, False)
#     for id in id_list:
#         update_send_notification(id)

# print("----------------------------urine time----------------------------------------------------------")
# cursor = connection.cursor()
# table_name = 'toilet'
# query = f'SELECT * FROM {table_name} WHERE toilet_id = 1  AND duration > {URINE_TIME_MIN}  AND duration < {STOOL_TIME_MIN}  AND DATE(`timestamp`) = CURDATE() order by id DESC;'
# cursor.execute(query)
# id_list = []
# # 获取查询结果
# result = cursor.fetchall()
# content = ""
# firstone = True
# for row in result:
#     print(row)
#     #print(row.)
#     (id, duration, toilet_id, mac, datetime, send_notification) = row
#     print(duration, datetime)
#     if not send_notification:
#        id_list.append(id)
#     #send notification
#     seconds = duration//1000
#     if firstone:
#         title = str(datetime) + "次卫卫生间使用了" + str(seconds//60) +"分钟" + str(seconds%60) + "秒 (urine)"
#         firstone = False
#     content += str(datetime) + "   " + str(seconds//60) +"分钟" + str(seconds%60) + "秒" +"\n"

# if id_list:
#     print("since have new urine record, will notify")
#     send_email(title, content, False)
#     for id in id_list:
#         update_send_notification(id)

# 关闭游标和连接
cursor.close()
connection.close()
