"""武器のアタッチメントを総当たりして、選んだステータスの偏差値の平均が高いカスタムを返す。

    from custom_score import rank_customs
    result = rank_customs(10)                      # VEL 46 を 5 個まで、上位 20 件
    result = rank_customs(10, stats=[3, 21, 26])   # 項目を番号で選ぶ（stat_catalog.py）

流れ:
    1. DB から武器とアタッチメントを読む（db.py）
    2. incompatible.json のルールで、付けられない組み合わせを除いて総当たり（brute_force.py）
    3. 組み合わせごとに、アタッチメントを付けた後のステータスを計算する（apply_attachments）
    4. 項目ごとに、その武器の全組み合わせの中での偏差値を出す（standard_score.py）
    5. 選んだ項目の偏差値の平均が高い順に、上位 top 件を返す

アタッチメントを付けた後のステータス:
    - バーの項目（威力・射程・命中率・機動性・操作性・RPM・装弾数・予備弾数）は増減値を足す
    - それ以外は % を足し合わせてから掛ける：基本値 × (1 + %の合計 ÷ 100)
    - 基本値が NULL の項目は NULL のまま
"""

import os

from brute_force import combinations, load_rules
from db import ROOT, fetch_attachments, fetch_weapon
from standard_score import standard_scores
from stat_catalog import DEFAULT_SELECTED, select_stats

RULES_PATH = os.path.join(ROOT, "incompatible.json")
DEFAULT_MAX_COUNT = 5
DEFAULT_TOP = 20

# アタッチメントの値が「増減値」の項目。それ以外は「%」
DELTA_COLUMNS = {"power", "range", "accuracy", "mobility", "handling", "rpm", "magazine_size", "reserve_ammo"}


def apply_attachments(base_value, column, attachment_values):
    """アタッチメントを付けた後の値を返す。

    base_value        : 武器の基本値（None なら None を返す）
    column            : カラム名
    attachment_values : 付けたアタッチメントのその項目の値のリスト
    """
    if base_value is None:
        return None
    total = sum(float(v or 0) for v in attachment_values)
    if column in DELTA_COLUMNS:
        return float(base_value) + total
    return float(base_value) * (1 + total / 100)


def rank_customs(weapon_id, max_count=DEFAULT_MAX_COUNT, fixed=None, stats=None, top=DEFAULT_TOP,
                 rules_path=RULES_PATH):
    """上位のカスタムを返す。

    weapon_id : weapon テーブルの id
    max_count : 付けるアタッチメントの最大数（固定するアタッチメントも含む）
    fixed     : 必ず付けるアタッチメント {スロット名: ident}
    stats     : 偏差値を出す項目の番号のリスト（stat_catalog.py）。省略時は DEFAULT_SELECTED
    top       : 返す件数

    戻り値の辞書:
        weapon  : weapon テーブルの行
        total   : 総当たりした組み合わせの数
        stats   : [(カラム名, 表示名, 大きいほど良いか), ...]
        results : 上位 top 件。各要素は
                  {rank, average, attachments: {スロット名: (ident, 名前)},
                   values: {カラム名: 付けた後の値}, scores: {カラム名: 偏差値}}
    """
    stat_defs = select_stats(stats or DEFAULT_SELECTED)
    weapon = fetch_weapon(weapon_id)
    attachments = fetch_attachments(weapon_id)
    unavailable, incompatible = load_rules(rules_path, weapon_id)

    slots = {slot: list(rows) for slot, rows in attachments.items()}
    combos = list(combinations(slots, max_count, unavailable, incompatible, fixed))

    # 項目ごとに、全組み合わせの「付けた後の値」と偏差値を出す
    columns = [col for col, _, _ in stat_defs]
    values = {}
    scores = {}
    for col, _, higher_is_better in stat_defs:
        values[col] = [
            apply_attachments(weapon[col], col, [attachments[s][i][col] for s, i in combo.items()])
            for combo in combos
        ]
        scores[col] = standard_scores(values[col], higher_is_better)

    averages = []
    for n in range(len(combos)):
        row = [scores[col][n] for col in columns if scores[col][n] is not None]
        averages.append(sum(row) / len(row) if row else None)

    # 平均が高い順。同じ平均なら付ける数が少ないほうを上にする
    order = sorted(
        (n for n in range(len(combos)) if averages[n] is not None),
        key=lambda n: (-averages[n], len(combos[n])),
    )

    results = []
    for rank, n in enumerate(order[:top], start=1):
        combo = combos[n]
        results.append({
            "rank": rank,
            "average": averages[n],
            "attachments": {s: (i, attachments[s][i]["name"]) for s, i in combo.items()},
            "values": {col: values[col][n] for col in columns},
            "scores": {col: scores[col][n] for col in columns},
        })

    return {"weapon": weapon, "total": len(combos), "stats": stat_defs, "results": results}
