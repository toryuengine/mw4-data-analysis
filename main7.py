"""VEL 46 のアタッチメントを総当たりして、ADS・腰撃ちキックの偏差値の平均が高いカスタムを出力する。

    .venv\\Scripts\\python.exe main7.py [最大セット数]

項目は 21 ADS / 35 腰水平キック / 36 腰垂直キック（src/stat_catalog.py の番号）。
計算は src/custom_score.py の rank_customs()、表示は main5.py の print_result() を使う。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from custom_score import DEFAULT_MAX_COUNT, rank_customs  # noqa: E402
from main5 import print_result  # noqa: E402

WEAPON_ID = 10  # VEL 46
# 偏差値を出す項目の番号（src/stat_catalog.py の STAT_CATALOG の番号）
STATS = [21, 35, 36]
TOP = 20

USAGE = """使い方: python main7.py [最大セット数]
  最大セット数  付けるアタッチメントの最大数（省略時 5）
例: python main7.py
    python main7.py 3"""


def parse_args(args):
    if len(args) > 1:
        raise SystemExit(USAGE)
    try:
        max_count = int(args[0]) if args else DEFAULT_MAX_COUNT
    except ValueError:
        raise SystemExit(USAGE)
    if max_count < 0:
        raise SystemExit("最大セット数は 0 以上にしてください")
    return max_count


if __name__ == "__main__":
    max_count = parse_args(sys.argv[1:])
    try:
        result = rank_customs(WEAPON_ID, max_count=max_count, stats=STATS, top=TOP)
    except ValueError as e:
        raise SystemExit(str(e))
    print_result(result, max_count)
