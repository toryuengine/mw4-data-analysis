"""偏差値を出せるステータスの一覧（番号で選ぶ）。

番号: (カラム名, 表示名, 大きいほど良いか)
時間・反動・ブレ・揺れ・被弾時のひるみ・キルタイムは小さいほど良いので False。

44・45 のキルタイムは DB の列ではなく、killtime.py で計算する値（COMPUTED）。
値を取り出すときは stat_value() を使う。
"""

from killtime import kill_time

# キルタイムを計算する距離(m)
KILLTIME_DISTANCE = 10

STAT_CATALOG = {
    # バー
    1:  ("power",               "威力",         True),
    2:  ("range",               "射程",         True),
    3:  ("accuracy",            "命中率",       True),
    4:  ("mobility",            "機動性",       True),
    5:  ("handling",            "操作性",       True),
    # 連射・威力
    6:  ("rpm",                 "RPM",          True),
    7:  ("pre_fire_delay",      "射撃前遅延",   False),
    8:  ("penetration",         "貫通力",       True),
    9:  ("flinch",              "ひるみ付与",   True),
    # 機動性
    10: ("move_speed",          "移動",         True),
    11: ("ads_move_speed",      "ADS移動",      True),
    12: ("fire_move_speed",     "射撃移動",     True),
    13: ("strafe_speed",        "横移動",       True),
    14: ("crouch_speed",        "しゃがみ",     True),
    15: ("sprint_speed",        "ダッシュ",     True),
    16: ("tac_sprint_speed",    "タクダッシュ", True),
    17: ("tac_sprint_duration", "タクダ持続",   True),
    # 射程・弾薬
    18: ("muzzle_velocity",     "マズル",       True),
    19: ("magazine_size",       "装弾数",       True),
    20: ("reserve_ammo",        "予備弾",       True),
    # 操作性
    21: ("ads_in_time",         "ADS",          False),
    22: ("ads_out_time",        "ADS解除",      False),
    23: ("sprint_to_fire",      "ダッシュ硬直", False),
    24: ("raise_time",          "構え",         False),
    25: ("drop_time",           "ドロップ",     False),
    26: ("reload_time",         "リロード",     False),
    # 命中率（エイム時）
    27: ("ads_recoil_h",        "ADS水平反動",  False),
    28: ("ads_recoil_v",        "ADS垂直反動",  False),
    29: ("ads_kick_h",          "ADS水平キック", False),
    30: ("ads_kick_v",          "ADS垂直キック", False),
    31: ("ads_spread",          "ADSブレ",      False),
    32: ("ads_sway",            "ADS揺れ",      False),
    # 命中率（腰だめ撃ち）
    33: ("hip_recoil_h",        "腰水平反動",   False),
    34: ("hip_recoil_v",        "腰垂直反動",   False),
    35: ("hip_kick_h",          "腰水平キック", False),
    36: ("hip_kick_v",          "腰垂直キック", False),
    37: ("hip_spread",          "腰ブレ",       False),
    38: ("hip_sway",            "腰揺れ",       False),
    39: ("hip_turn_spread",     "腰旋回ブレ",   False),
    40: ("hit_flinch",          "被弾ひるみ",   False),
    # ダメージ
    41: ("dmg_head",            "頭ダメージ",   True),
    42: ("range1_damage",       "近距離ダメ",   True),
    43: ("range1_max",          "近距離上限",   True),
    # キルタイム（KILLTIME_DISTANCE m・全弾胴体。killtime.py で計算）
    44: ("ttk",                 "キルタイム",   False),
    45: ("ttk_sprint",          "TTK硬直込み",  False),
}

DEFAULT_SELECTED = [1, 2, 3, 4, 5, 6, 18, 21, 26]

# DB の列ではなく計算で出す項目: カラム名 -> 武器の辞書から値を出す関数
COMPUTED = {
    "ttk":        lambda w: kill_time(w, KILLTIME_DISTANCE)["ttk"],
    "ttk_sprint": lambda w: kill_time(w, KILLTIME_DISTANCE, include_sprint=True)["ttk"],
}

# キルタイムの計算に使う weapon の列（アタッチメントを付けた後の値を作るときに使う）
TTK_COLUMNS = [
    "rpm", "muzzle_velocity", "pre_fire_delay", "sprint_to_fire", "magazine_size",
    "range1_max", "range1_damage", "range2_max", "range2_damage",
    "range3_max", "range3_damage", "range4_max", "range4_damage",
]


def stat_value(weapon, column):
    """武器の辞書から、その項目の値を返す（計算で出す項目にも対応）。"""
    if column in COMPUTED:
        return COMPUTED[column](weapon)
    return weapon[column]


def select_stats(numbers):
    """番号のリストから [(カラム名, 表示名, 大きいほど良いか), ...] を作る。知らない番号は ValueError。"""
    unknown = [n for n in numbers if n not in STAT_CATALOG]
    if unknown:
        raise ValueError(f"STAT_CATALOG にない番号です: {unknown}")
    return [STAT_CATALOG[n] for n in numbers]
