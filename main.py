import os

import pymysql
from dotenv import load_dotenv

load_dotenv()

WEAPON_NAME = "HAN 86"
MAX_ATTACHMENTS = 5

# 重み(%)  合計が100でなくても比率で換算する
WEIGHTS = {
    "power":         20,  # 威力
    "range":         20,  # 射程
    "accuracy":      20,  # 命中率
    "mobility":      20,  # 機動性
    "handling":      20,  # 操作性
    "rpm":            0,  # RPM
    "magazine_size":  0,  # 装弾数
    "reserve_ammo":   0,  # 予備弾数
}

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

STAT_LABELS = {
    "power": "威力",
    "range": "射程",
    "accuracy": "命中率",
    "mobility": "機動性",
    "handling": "操作性",
    "rpm": "RPM",
    "magazine_size": "装弾数",
    "reserve_ammo": "予備弾数",
}

SLOT_LABELS = {
    "muzzle": "マズル",
    "barrel": "バレル",
    "laser": "レーザー",
    "site": "サイト",
    "stock": "ストック",
    "underbarrel": "アンダーバレル",
    "ammo": "弾薬",
    "rear_grip": "リアグリップ",
    "magazine": "マガジン",
}


def fetch_all(cursor, table):
    cursor.execute(f"SELECT * FROM `{table}` ORDER BY id")
    return list(cursor.fetchall())


with pymysql.connect(**DB_CONFIG) as conn:
    with conn.cursor() as cur:
        weapon = fetch_all(cur, "weapon")
        site = fetch_all(cur, "site")
        ammo = fetch_all(cur, "ammo")
        barrel = fetch_all(cur, "barrel")
        laser = fetch_all(cur, "laser")
        magazine = fetch_all(cur, "magazine")
        muzzle = fetch_all(cur, "muzzle")
        rear_grip = fetch_all(cur, "rear_grip")
        stock = fetch_all(cur, "stock")
        underbarrel = fetch_all(cur, "underbarrel")

slots = {
    "muzzle": muzzle,
    "barrel": barrel,
    "laser": laser,
    "site": site,
    "stock": stock,
    "underbarrel": underbarrel,
    "ammo": ammo,
    "rear_grip": rear_grip,
    "magazine": magazine,
}


def normalize(weights):
    total = sum(abs(w) for w in weights.values())
    if total == 0:
        raise ValueError("WEIGHTS がすべて 0 です")
    return {stat: w / total for stat, w in weights.items()}


def score(part, weights):
    return sum(part[stat] * w for stat, w in weights.items())


def find_best(weights, max_attachments):
    # パーツ同士の点数は独立しているので、各スロットの最高点を上から取れば最適解になる
    candidates = []
    for slot, parts in slots.items():
        if not parts:
            continue
        best = max(parts, key=lambda p: score(p, weights))
        s = score(best, weights)
        if s > 0:
            candidates.append((s, slot, best))
    candidates.sort(key=lambda c: c[0], reverse=True)
    return candidates[:max_attachments]


def total_stats(base, chosen):
    result = {stat: base[stat] for stat in STAT_LABELS}
    for _, _, part in chosen:
        for stat in STAT_LABELS:
            result[stat] += part[stat]
    return result


if __name__ == "__main__":
    base = next(w for w in weapon if w["name"] == WEAPON_NAME)
    weights = normalize(WEIGHTS)
    chosen = find_best(weights, MAX_ATTACHMENTS)

    print("武器:", base["name"])
    print("重み:", ", ".join(f"{STAT_LABELS[k]} {v * 100:.0f}%" for k, v in weights.items() if v))
    print()
    print("アタッチメント")
    for s, slot, part in chosen:
        print(f"  {SLOT_LABELS[slot]:<8} {part['name']}  {s:+.2f}")
    print(f"  合計 {sum(c[0] for c in chosen):+.2f}")
    print()
    print("ステータス")
    final = total_stats(base, chosen)
    for stat, label in STAT_LABELS.items():
        diff = final[stat] - base[stat]
        diff_text = f" ({diff:+d})" if diff else ""
        print(f"  {label:<6} {base[stat]:>4} -> {final[stat]:>4}{diff_text}")
