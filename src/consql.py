import mysql.connector
from decimal import Decimal

def ttt():
    conn = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "root",
        database = "mw4"
    )

    #全検索
    sql_1 = """SELECT * FROM mw4.weapon;"""

    #超接近キルタイム
    sql_2 = """SELECT ads_in_time, rpm, muzzle_velocity, name FROM mw4.weapon;"""

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
            ads, rpm, mv, name = weapons[r]

            # 上限が None のレンジは「それ以降ずっと続く」ので無限大として扱う
            range1, range2, range3 = range_table[r]
            if range1 is None:
                range1 = float("inf")

            if range2 is None:
                range2 = float("inf")

            print("レンジ変数", range1, range2, range3)

            if m < range1:
                dmg = int(damage_table[r][0])
                print("ダメージテーブル1")

            elif m < range2:
                dmg = int(damage_table[r][1])
                print("ダメージテーブル2")

            else:
                # range2 以上（range3 を超える距離も含む）はすべてダメージレンジ3
                dmg = int(damage_table[r][2])
                print("ダメージテーブル3")
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

            print(name, time/1000) #キルタイム


def killtime():
    pass



# 全探索
class BruteForceSearch:

    # db接続
    def conndb(self):
        # cursor は接続を弱参照でしか持たないため、self に保持して接続が消えないようにする
        self.conn = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "root",
        database = "mw4"
        )

        cursor = self.conn.cursor()
        return cursor


    # 武器情報を取得する
    def get_weapon_info(self, tblist):
        cursor = self.conndb()
        tbvalue = []
        for tb in tblist:
            print("tb",tb)
            sql = f"SELECT*FROM mw4.{tb};"
            print("sql", sql)
            cursor.execute(sql)
            rows = cursor.fetchall()
            print("fetch", rows)
            tbvalue.append(rows)

        return tbvalue
    


    def __init__(self):
        self.tablelist = ["weapon", "ammo", "barrel", "laser", "magazine", "muzzle", "rear_grip", "site", "stock","underbarrel"]
        self.tbvalues = self.get_weapon_info(self.tablelist)
        print(self.tbvalues)


    def run(self):
        print(len(self.tbvalues))


    #キルタイムを取得する
    def getkilltime():
        pass


    # カスタムをセットして、武器のステータスを算出する
    # 武器名,　アタッチメントキーを選択する
    def setcustom(weapon, attachmentkey):
        pass
        

        





if __name__ == "__main__":
    bfs = BruteForceSearch()
    bfs.ppp()

    att = {
        "ammo": 1,
        "barrel": 2,
        "laser": 3,
        "magazine": 4,
        "muzzle": 5,
        "rear_grip": 6,
        "site": 7,
        "stock": 8,
        "underbarrel": 9,
    }
    
    bfs.setcustom("1", att)