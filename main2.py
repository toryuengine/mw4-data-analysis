"""DB の武器ステータスから、各武器の偏差値を出力する。

偏差値の計算は src/standard_score.py の関数を使う。
DB の接続情報は .env から読み込む（.env.example を参照）。
"""

import os
import sys
import unicodedata

import mysql.connector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from standard_score import standard_scores_by_key  # noqa: E402
from db import DB_CONFIG  # noqa: E402,F401  main3 / main4 もここから使う
from stat_catalog import STAT_CATALOG, DEFAULT_SELECTED  # noqa: E402
from stat_catalog import select_stats as _select_stats  # noqa: E402

# 偏差値を出す項目の番号（src/stat_catalog.py の STAT_CATALOG の番号）
# 実行時に `python main2.py 1 2 3` のように番号を渡すと、こちらより優先される
SELECTED = DEFAULT_SELECTED


def select_stats(numbers):
    try:
        return _select_stats(numbers)
    except ValueError as e:
        raise SystemExit(str(e))


STATS = select_stats(SELECTED)


def fetch_weapons():
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM weapon ORDER BY id")
        return cursor.fetchall()
    finally:
        conn.close()


def calc_scores(weapons):
    """{カラム名: {武器名: 偏差値}} を返す。"""
    scores = {}
    for col, _, higher_is_better in STATS:
        values = {w["name"]: w[col] for w in weapons}
        scores[col] = standard_scores_by_key(values, higher_is_better)
    return scores


def calc_average(weapons, scores):
    """{武器名: 全ステータスの偏差値の平均} を返す。None の項目は除く。"""
    averages = {}
    for w in weapons:
        vals = [scores[col][w["name"]] for col, _, _ in STATS if scores[col][w["name"]] is not None]
        averages[w["name"]] = sum(vals) / len(vals) if vals else None
    return averages


def width(text):
    """全角文字を 2 として、画面上の幅を数える。"""
    return sum(2 if unicodedata.east_asian_width(ch) in "FWA" else 1 for ch in text)


def pad(text, size, right=False):
    space = " " * max(size - width(text), 0)
    return space + text if right else text + space


def fmt(score):
    return "-" if score is None else f"{score:.1f}"


def print_table(weapons, scores, averages):
    name_w = max(width(w["name"]) for w in weapons) + 2
    col_w = max(9, max(width(label) for _, label, _ in STATS) + 2)

    header = pad("武器", name_w) + "".join(pad(label, col_w, right=True) for _, label, _ in STATS)
    header += pad("平均", col_w, right=True)
    print(header)
    print("-" * width(header))

    ranked = sorted(weapons, key=lambda w: averages[w["name"]] or 0, reverse=True)
    for w in ranked:
        name = w["name"]
        line = pad(name, name_w)
        line += "".join(pad(fmt(scores[col][name]), col_w, right=True) for col, _, _ in STATS)
        line += pad(fmt(averages[name]), col_w, right=True)
        print(line)


def print_catalog():
    print("番号  項目")
    for n, (col, label, higher_is_better) in STAT_CATALOG.items():
        direction = "大きいほど良い" if higher_is_better else "小さいほど良い"
        print(f"{n:>4}  {pad(label, 14)}{pad(col, 22)}{direction}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["list"]:
        print_catalog()
        sys.exit()
    if args:
        try:
            STATS = select_stats([int(a) for a in args])
        except ValueError:
            raise SystemExit("番号は整数で指定してください（例: python main2.py 1 2 3）")

    weapons = fetch_weapons()
    scores = calc_scores(weapons)
    averages = calc_average(weapons, scores)

    print("偏差値（50 が平均。高いほど良い。平均の高い順）")
    print()
    print_table(weapons, scores, averages)
