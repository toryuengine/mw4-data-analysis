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
    def setcustom(self, weapon, attkey):
    # 武器の取得
        weapon_value = self.get_weapon(weapon)

    # アタッチメントの取得/後からデータクラスに変更する事20261115
        ammo_value = self.get_ammo(attkey["ammo"]) #弾種
        barrel_value = self.get_barrel(attkey["barrel"])
        laser_value = self.get_laser(attkey["laser"])
        magazine_value = self.get_magazine(attkey["magazine"])
        muzzle_value = self.get_muzzle(attkey["muzzle"])
        reargrip_value = self.get_reargrip(attkey["rear_grip"])
        site_value = self.get_site(attkey["site"])
        stock_value = self.get_stock(attkey["stock"])
        underbarrel_value = self.get_underbarrel(attkey["underbarrel"])


        ## 後で一つに丸止めること/データーセットに値を突っ込む
        from custom_data import CustomData
        self.customdata = CustomData(
            ammo=ammo_value,
            barrel=barrel_value,
            laser=laser_value,
            magazine=magazine_value,
            muzzle=muzzle_value,
            rear_grip=reargrip_value,
            site=site_value,
            stock=stock_value,
            underbarrel=underbarrel_value
        )

        # 裏で計算しておく
        self.calculateweaponstats()
        print("選択された----------------")
        print(self.customdata)
        
        print("aaa", weapon_value)
        result = self.censorship(attkey)
        if result:
            print("アタッチメント数が多いです")
            return "設置されているアタッチメント数が多いです" 
        # ammo = self.apply_ammo(attkey)

        print("アタッチメント数に問題はなかった")

        pass


# 選択された武器の情報を出力する
    def get_weapon(self, iden):
        if iden == 0:
            return 0
        for i, data in enumerate(self.tbvalues[0]):
            if iden == data[0]:
                return self.tbvalues[0][i]


## 選択された"ammo"
    def get_ammo(self, iden):
        if iden == 0:
            return 0
            
        for data in self.tbvalues[1]:
            if iden == data[2]: # identカラム
                return data 


    def get_barrel(self, iden):
        if iden == 0:
            return 0
        
        for data in self.tbvalues[2]:
            if iden == data[2]: # identカラム
                return data

            
    def get_laser(self, iden):
        if iden == 0:
            return 0
        
        for data in self.tbvalues[3]:
            if iden == data[2]: # identカラム
                return data


    def get_magazine(self, iden):
        if iden == 0:
            return 0
    
        for data in self.tbvalues[4]:
            if iden == data[2]:
                return data


            
    def get_muzzle(self, iden):
        if iden == 0:
            return 0
        
        for data in self.tbvalues[5]:
            if iden == data[2]:
                return data

            
    def get_reargrip(self, iden):
        if iden == 0:
            return 0
        
        for data in self.tbvalues[6]:
            if iden == data[2]:
                return data

    def get_site(self, iden):
        if iden == 0:
            return 0
        
        for data in self.tbvalues[7]:
            if iden == data[2]:
                return data

    def get_stock(self, iden):
        if iden == 0:
            return 0
        
        for data in self.tbvalues[8]:
            if iden == data[2]:
                return data


    def get_underbarrel(self, iden):
        if iden == 0:
            return 0
        
        for data in self.tbvalues[9]:
            if iden == data[2]:
                return data
        


    # アタッチメントが5つ以上付けられている
    def censorship(self, key):
        tablelist = [
            "ammo", 
            "barrel", 
            "laser", 
            "magazine", 
            "muzzle", 
            "rear_grip", 
            "site", 
            "stock",
            "underbarrel"
            ]
        #カウントするためのもの
        count = 0

        for tb in tablelist:
            if not key[f"{tb}"] == 0:
                count+=1

        #5つ以上のアタッチメントが付けられていたらアウト
        if count >= 5:
            return True

        else :
            return False


        
    ## アタッチメントを付けた結果のステータスを出力する
    def calculateweaponstats(self):
        tablelist = ["ammo", "barrel", "laser", "magazine", "muzzle",
                     "rear_grip", "site", "stock", "underbarrel"]

        result = {}
        for tb in tablelist:
            result[tb] = getattr(self.customdata, tb)
        print("--------result----------")
        print(result)
        print("--------result----------")

        return result







    def calcu_ammo(self):
        pass
        

    def calcu_barrel(self):
        pass

    def calcu_laser(self):
        pass

    def calcu_magazine(self):
        pass

    def calcu_muzzle(self):
        pass


    def calcu_rear_grip(self):
        pass

    def calcu_site(self):
        pass

    def calcu_stock(self):
        pass

    def calcu_underbarrel(self):
        pass






    def apply_ammo():
        pass

        





if __name__ == "__main__":
    bfs = BruteForceSearch()

    att = {
        "ammo": 2,
        "barrel": 0,
        "laser": 1,
        "magazine": 1,
        "muzzle": 2,
        "rear_grip": 1,
        "site": 0,
        "stock": 0,
        "underbarrel": 0
    }
    
    bfs.setcustom(1, att)
