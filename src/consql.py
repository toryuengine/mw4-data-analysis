import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()
from decimal import Decimal

conn = mysql.connector.connect(
    host = os.getenv("DB_HOST"),
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD"),
    database = os.getenv("DB_NAME")
)

#全検索
sql_1 = """SELECT * FROM mw4.weapon;"""

#超接近キルタイム
sql_2 = """SELECT ads_in_time, rpm, muzzle_velocity, range1_damage FROM mw4.weapon;"""
rangetable = """"""

#ダメージテーブルに応じて、威力の変化を記述する
sql3 = """SELECT ads_in_time, rpm, muzzle_velocity, """
cursor = conn.cursor()


cursor.execute(sql_2)

rows = cursor.fetchall()

for m in range(1, 30):
    print(m, "メートル")
    for row in rows:
        #ads速度,連射速度,マズル速度,ダメージ
        ads, rpm, mv, dmg = row

        #5mの位置に到達する時間
        ms = m / mv
        # print(ms)

        #1回転あたりの時間
        rpm1 = 1/((rpm/60)/1000)


        rpms = Decimal(str(1 / ((rpm/60)/1000)))

        HP = 100
        time = ads
        while(HP > 0):
            time = (ms + rpms) + time
            HP = HP - dmg

        print(time/1000) #キルタイム
