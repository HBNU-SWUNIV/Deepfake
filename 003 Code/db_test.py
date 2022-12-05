import pymysql

# MySQL Connection 연결
conn = pymysql.connect("DB info")
cur = conn.cursor()

'''
sql = "CREATE table team_chat(\
    date char(30),\
    gid decimal,\
    uid decimal,\
    dialog TEXT(65535));"

sql = "create database dialog character set utf8mb4 collate utf8mb4_general_ci;"

sql = "drop database dialog"
sql = "CREATE table team_chat(\
    date char(30),\
    gid decimal,\
    uid decimal,\
    dialog TEXT(65535));"

#sql = "drop table team_chat"

sql = "insert into team_chat(date, gid, uid, dialog) values('2022-03-14 06:59:30', -637440428, 5199199910, '잠깐만');"
cur.execute(sql)
'''

sql = "select * from team_chat;"
cur.execute(sql)

rows = cur.fetchall()

print(rows)

cur.execute(sql)

#rows = cur.fetchall()
#print(rows)
cur.close()