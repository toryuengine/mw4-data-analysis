"""キルタイム（TTK：Time To Kill）を算出する。

撃ち始めてから、敵の HP を 0 にする弾が当たるまでの時間（ミリ秒）を計算する。

    1発のダメージ   = 距離 d が入る段階の rangeN_damage
    必要な弾数(STK) = ceil(HP ÷ 1発のダメージ)
    発射間隔        = 60000 ÷ rpm
    キルタイム      = pre_fire_delay + (STK - 1) × 発射間隔 + d ÷ muzzle_velocity × 1000

- 全弾が胴体に当たる前提（距離別ダメージだけを使う）
- 弾の飛ぶ時間は最後の1発の分だけ足す（全弾同じ速さで飛ぶため）
- 距離の境目は次の段階に入れる（0-30 / 30-∞ なら、30m は 2 段階目）
- rpm どおりに撃ち続ける前提。バースト武器の間隔の違いは考えない

武器の一覧やDBへの接続は持たない。weapon テーブルの1行を辞書で渡す。
"""

import math

DEFAULT_HP = 100


def damage_stages(weapon):
    """[(距離上限, ダメージ), ...] を近い順に返す。上限が NULL の段階は ∞ にする。"""
    stages = []
    for n in (1, 2, 3):
        damage = weapon.get(f"range{n}_damage")
        if damage is None:
            continue
        limit = weapon.get(f"range{n}_max")
        stages.append((math.inf if limit is None else float(limit), int(damage)))
    return stages


def damage_at(weapon, distance):
    """距離 distance(m) での1発のダメージを返す。"""
    stages = damage_stages(weapon)
    if not stages:
        raise ValueError(f"{weapon.get('name')}: 距離別ダメージがありません")
    for limit, damage in stages:
        if distance < limit:
            return damage
    return stages[-1][1]


def shots_to_kill(damage, hp=DEFAULT_HP):
    """倒すのに必要な弾数を返す。"""
    if damage <= 0:
        raise ValueError("ダメージが 0 以下です")
    return math.ceil(hp / damage)


def fire_interval(weapon):
    """発射間隔(ms) を返す。"""
    return 60000 / float(weapon["rpm"])


def travel_time(weapon, distance):
    """弾が distance(m) 先に届くまでの時間(ms) を返す。"""
    return distance / float(weapon["muzzle_velocity"]) * 1000


def kill_time(weapon, distance, hp=DEFAULT_HP, include_ads=False):
    """キルタイムの計算結果を辞書で返す。

    戻り値:
        damage        : 1発のダメージ
        stk           : 必要な弾数
        ttk           : キルタイム(ms)。include_ads=True なら ads_in_time を足した値
        enough_ammo   : 1マガジンで倒せるか（stk <= magazine_size）
    """
    damage = damage_at(weapon, distance)
    stk = shots_to_kill(damage, hp)

    ttk = float(weapon.get("pre_fire_delay") or 0)
    ttk += (stk - 1) * fire_interval(weapon)
    ttk += travel_time(weapon, distance)
    if include_ads:
        ttk += float(weapon.get("ads_in_time") or 0)

    magazine = weapon.get("magazine_size")
    return {
        "damage": damage,
        "stk": stk,
        "ttk": ttk,
        "enough_ammo": magazine is None or stk <= magazine,
    }


if __name__ == "__main__":
    # 動作確認用のサンプル（HAN 86 の値。武器の一覧ではない）
    sample = {
        "name": "sample", "rpm": 741, "muzzle_velocity": 615.0, "pre_fire_delay": 0,
        "ads_in_time": 250, "magazine_size": 30,
        "range1_max": 32, "range1_damage": 23,
        "range2_max": None, "range2_damage": 19,
        "range3_max": None, "range3_damage": None,
    }
    for d in (10, 31, 32, 50):
        r = kill_time(sample, d)
        ads = kill_time(sample, d, include_ads=True)
        print(f"{d}m: {r['damage']}dmg x {r['stk']}発  TTK {r['ttk']:.1f}ms  ADS込み {ads['ttk']:.1f}ms")
