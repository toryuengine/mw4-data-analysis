"""サブマシンガンを総当たりして、武器ごとに偏差値の平均が高いカスタムを出力する。

    .venv\\Scripts\\python.exe main6.py [最大セット数]

対象の武器は下の WEAPON_IDS に書く（DB からカテゴリーで探すことはしない）。
1 丁ずつ src/custom_score.py の rank_customs() を呼び、main5.py と同じ形で上位を表示する。
偏差値は武器ごとに、その武器の全組み合わせの中で計算する。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from custom_score import DEFAULT_MAX_COUNT, rank_customs  # noqa: E402
from main5 import STATS, TOP, print_result  # noqa: E402

# 対象のサブマシンガン（weapon テーブルの id）
WEAPON_IDS = [10]  # VEL 46

USAGE = """使い方: python main6.py [最大セット数]
  最大セット数  付けるアタッチメントの最大数（省略時 5）
例: python main6.py
    python main6.py 3"""


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

    for i, weapon_id in enumerate(WEAPON_IDS):
        if i:
            print()
            print("=" * 80)
        try:
            result = rank_customs(weapon_id, max_count=max_count, stats=STATS, top=TOP)
        except ValueError as e:
            print(f"武器id {weapon_id}: {e}")
            continue
        print_result(result, max_count)
