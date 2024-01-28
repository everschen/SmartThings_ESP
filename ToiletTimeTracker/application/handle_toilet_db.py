#!/usr/bin/env python3

import smtplib
from email.mime.text import MIMEText
import time
import mysql.connector


def send_email(title, content, sleep):
	if(title == None or content == None):
		print("parameters number error")
		exit(1)
	subject = title
	sender = "your_email_address"
	recver = "your_email_address"
	password = "your_email_password"
	message = MIMEText(content,"plain","utf-8")
	 
	message['Subject'] = subject
	message['To'] = recver
	message['From'] = sender

	if sleep:
		time.sleep(8 * 60 * 60)
	 
	smtp = smtplib.SMTP_SSL("smtp.163.com",994) #???smtp???
	smtp.login(sender,password)#?????
	smtp.sendmail(sender,[recver],message.as_string()) #as_string ? message ????????
	smtp.close()

# 连接到 MySQL 数据库
connection = mysql.connector.connect(
    host='your_db_host',
    user='your_db_user',
    password='your_db_password',
    database='live_monitor'
)

# 创建一个游标对象
cursor = connection.cursor()

# 执行 SQL 查询语句
table_name = 'toilet'
query = f'SELECT * FROM {table_name} WHERE toilet_id=1 AND send_notification=0 AND duration > 180000;'
cursor.execute(query)

# 获取查询结果
result = cursor.fetchall()

def update_send_notification(id):
    cursor = connection.cursor()
    query = "UPDATE toilet SET send_notification = 1 WHERE id = %s"
    values = (id,)
    cursor.execute(query, values)
    connection.commit()


# 打印结果
for row in result:
    print(row)
    #print(row.)
    (id, duration, toilet_id, mac, datetime, send_notification) = row
    print(duration, datetime)
    #send notification
    seconds = duration//1000
    title = str(datetime) + "次卫卫生间使用了" + str(seconds//60) +"分钟" + str(seconds%60) + "秒"
    send_email(title, title, False)

    #update db send_notification field
    update_send_notification(id)

# 关闭游标和连接
cursor.close()
connection.close()
