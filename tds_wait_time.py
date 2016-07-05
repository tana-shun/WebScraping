# -*- coding: utf-8 -*-

import http.cookiejar
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import pprint
import pymysql
# モジュール読み込み
import pymysql.cursors

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
values = {
    'name' : 'Michael Foord',
    'location' : 'Northampton',
    'language' : 'Python'
}
headers = {
    'User-Agent': user_agent
}

data = urllib.parse.urlencode(values)
data = data.encode('utf-8')

# gps(緯度経度)情報を送り、クッキーにディズニー内にいることを書き込む
url = 'http://info.tokyodisneyresort.jp/s/gps/tdl_index.html?nextUrl=http%3A%2F%2Finfo.tokyodisneyresort.jp%2Frt%2Fs%2Frealtime%2Ftdl_attraction.html&lat=35.630658&lng=139.882869'
req = urllib.request.Request(url, data, headers)
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.open(req)

# クッキーにディズニー内にいる情報が書き込まれているため、アクセスできる
url = 'http://info.tokyodisneyresort.jp/rt/s/realtime/tds_attraction.html'
req = urllib.request.Request(url, data, headers)
res = opener.open(req)
html = res.read()
soup = BeautifulSoup(html.decode('utf-8'), "html.parser")

#パーク閉演時用
#soup = BeautifulSoup(open("index.html"))

# MySQLに接続する
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             db='Disneys',
                             charset='utf8',
                             # cursorclassを指定することで
                             # Select結果をtupleではなくdictionaryで受け取れる
                             cursorclass = pymysql.cursors.DictCursor)

print("--------------------------------------------------------------------------------------")
#改行
print()

#タイトル
pprint.pprint(soup.head.get_text())

#改行
print()
print("--------------------------------------------------------------------------------------")
# アトラクション名格納用リスト
atr_name = []

#アトラクション待ち時間格納用リスト
atr_time = []

#アトラクション名をリストに格納
for y in soup.find_all(class_="about"):
    atr_name.append(y.get_text())

#アトラクション待ち時間をリストに格納
for x in soup.find_all(class_="waitTime"):
    atr_time.append(x.get_text())

#アトラクション情報格納用ディクショナリ
atr_info = {}

#インデックスカウンタ
i = 0

#ディクショナリにアトラクション名とアトラクション待ち時間を格納
for z in atr_name:
    if(z.find("中止")) != -1:
        atr_info.update({z:0})
        # Insert処理
        with connection.cursor() as cursor:
            sql = "INSERT INTO tds_wait_time (Atr_name, Atr_time) VALUES (%s, %s)"
            r = cursor.execute(sql, (z, 0))
    elif(z.find("終了")) != -1:
        atr_info.update({z:0})
        # Insert処理
        with connection.cursor() as cursor:
            sql = "INSERT INTO tds_wait_time (Atr_name, Atr_time) VALUES (%s, %s)"
            r = cursor.execute(sql, (z, 0))
    elif(z.find("のみ")) != -1:
        atr_info.update({z:0})
        # Insert処理
        with connection.cursor() as cursor:
            sql = "INSERT INTO tds_wait_time (Atr_name, Atr_time) VALUES (%s, %s)"
            r = cursor.execute(sql, (z, 0))
    else:
        atr_info.update({z:atr_time[i]})
        # Insert処理
        with connection.cursor() as cursor:
            sql = "INSERT INTO tds_wait_time (Atr_name, Atr_time) VALUES (%s, %s)"
            r = cursor.execute(sql, (z, atr_time[i]))
        i = i + 1

pprint.pprint(atr_info)

print("--------------------------------------------------------------------------------------")

# autocommitではないので、明示的にコミットする
connection.commit()

# MySQLから切断する
connection.close()