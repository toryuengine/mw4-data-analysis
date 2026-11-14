import mysql.connector
from decimal import Decimal

conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "root",
    database = "mw4"
)

#全検索
sql_1 = """SELECT * FROM mw4.weapon;"""

#超接近キルタイム
sql_2 = """SELECT ads_in_time, rpm, muzzle_velocity FROM mw4.weapon;"""

#レンジテーブル
sql3 = """SELECT range1_max, range2_max, range3_max FROM mw4.weapon;"""

#ダメージテーブル
sql4 = """SELECT range1_damage, range2_damage, range3_damage FROM mw4.weapon;"""



cursor = conn.cursor()



cursor.execute(sql_2)
weapons = cursor.fetchall()

#レンジテーブルの実行
cursor.execute(sql3)
range_table = list(cursor.fetchall())
print("レンジテーブル", range_table)

#ダメージテーブル
cursor.execute(sql4)
damage_table = cursor.fetchall()
print("ダメージテーブル", damage_table)


print("配列の数", len(weapons))


for m in range(1, 60):
    print(m, "メートル")
    for r in range(len(weapons)):
        #ads速度,連射速度,マズル速度,ダメージ
        ads, rpm, mv = weapons[r]

        # Noneであれば0に置き換える
        range1, range2, range3 = range_table[r]
        if range1 == None:
            range1 = 0

        if range2 == None:
            range2 = 0

        if range3 == None:
            range3 = 0
        
        
        # print("rennzi", range1, range2, range3)
        match m:
            case m if 0 > m and m > range1:
                dmg = int(damage_table[r][0])
                print("ダメージテーブル1")

            case m if m < range1 :
                dmg = int(damage_table[r][1])
                print("ダメージテーブル2")

            case m if m < range3:
                dmg = int(damage_table[r][2])
                print("ダメージテーブル3")

            case _:
                print("ダメージテーブルを見つけることができなかった")
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
