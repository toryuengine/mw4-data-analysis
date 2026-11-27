"""武器のアタッチメントを総当たりして、選んだステータスの偏差値の平均が高いカスタムを出力する。

    .venv\\Scripts\\python.exe main5.py <武器id> [最大セット数] [固定するアタッチメント ...]

計算は src/custom_score.py の rank_customs() が全部行う。ここは引数を受け取って表示するだけ。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from brute_force import parse_item  # noqa: E402
from custom_score import DEFAULT_MAX_COUNT, rank_customs  # noqa: E402

# 偏差値を出す項目の番号（src/stat_catalog.py の STAT_CATALOG の番号）
STATS = [1, 2, 3, 4, 5, 6, 18, 21, 26]
TOP = 20

USAGE = """使い方: python main5.py <武器id> [最大セット数] [固定するアタッチメント ...]
  武器id               weapon テーブルの id
  最大セット数         付けるアタッチメントの最大数（省略時 5）
  固定するアタッチメント  必ず付けるもの。'スロット名:ident' で何個でも
例: python main5.py 10
    python main5.py 10 5 stock:1"""


def parse_args(args):
    if not args:
        raise SystemExit(USAGE)
    try:
        weapon_id = int(args[0])
        max_count = int(args[1]) if len(args) >= 2 else DEFAULT_MAX_COUNT
    except ValueError:
        raise SystemExit(USAGE)
    fixed = {}
    for text in args[2:]:
        try:
            slot, ident = parse_item(text)
        except ValueError as e:
            raise SystemExit(str(e))
        if slot in fixed:
            raise SystemExit(f"{slot} が 2 回指定されています（1 スロットに 1 つまで）")
        fixed[slot] = ident
    return weapon_id, max_count, fixed


def fmt_value(v):
    if v is None:
        return "-"
    return f"{v:.0f}" if abs(v) >= 100 else f"{v:.2f}".rstrip("0").rstrip(".")


def print_result(result, max_count):
    """rank_customs() の結果を表示する（main6.py からも使う）。"""
    weapon = result["weapon"]
    print(f"武器: {weapon['name']}（id {weapon['id']}）  最大セット数: {max_count}  "
          f"組み合わせ数: {result['total']:,}")
    print("項目: " + " / ".join(label for _, label, _ in result["stats"]))
    print("偏差値はこの武器の全組み合わせの中で計算（50 が平均）")
    print()

    for r in result["results"]:
        parts = " / ".join(f"{name}" for _, (_, name) in r["attachments"].items()) or "（なし）"
        print(f"{r['rank']:>2}位  平均 {r['average']:.1f}  {parts}")
        detail = "  ".join(
            f"{label} {fmt_value(r['values'][col])}({r['scores'][col]:.0f})"
            for col, label, _ in result["stats"] if r["scores"][col] is not None
        )
        print(f"      {detail}")


if __name__ == "__main__":
    weapon_id, max_count, fixed = parse_args(sys.argv[1:])
    try:
        result = rank_customs(weapon_id, max_count=max_count, fixed=fixed, stats=STATS, top=TOP)
    except ValueError as e:
        raise SystemExit(str(e))
    print_result(result, max_count)
