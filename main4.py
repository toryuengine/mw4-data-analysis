"""アタッチメントの組み合わせを総当たりで作り、件数と例を出力する。

    .venv\\Scripts\\python.exe main4.py <武器id> [最大セット数] [固定するアタッチメント ...]

組み合わせは src/brute_force.py で作り、付けられない組み合わせは incompatible.json で除く。
DB の接続情報は .env（src/db.py）。
"""

import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from brute_force import combinations, load_rules, parse_item  # noqa: E402
from db import ROOT, fetch_attachments, fetch_weapon  # noqa: E402

RULES_PATH = os.path.join(ROOT, "incompatible.json")

DEFAULT_MAX_COUNT = 5   # 最大セット数を省略したとき（ゲームの装着上限）
SHOW = 10               # 例として表示する組み合わせの数

USAGE = """使い方: python main4.py <武器id> [最大セット数] [固定するアタッチメント ...]
  武器id               weapon テーブルの id
  最大セット数         付けるアタッチメントの最大数（省略時 5）
  固定するアタッチメント  必ず付けるもの。'スロット名:ident' で何個でも
例: python main4.py 10
    python main4.py 10 5 stock:1 muzzle:2"""


def parse_args(args):
    """(武器id, 最大セット数, {スロット名: ident}) を返す。"""
    if not args:
        raise SystemExit(USAGE)
    try:
        weapon_id = int(args[0])
        max_count = int(args[1]) if len(args) >= 2 else DEFAULT_MAX_COUNT
    except ValueError:
        raise SystemExit(USAGE)
    if max_count < 0:
        raise SystemExit("最大セット数は 0 以上にしてください")

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


def describe(combo, names):
    if not combo:
        return "（なし）"
    return " / ".join(f"{slot}:{ident} {names[slot][ident]}" for slot, ident in combo.items())


if __name__ == "__main__":
    weapon_id, max_count, fixed = parse_args(sys.argv[1:])
    try:
        weapon = fetch_weapon(weapon_id)
        attachments = fetch_attachments(weapon_id)
        unavailable, incompatible = load_rules(RULES_PATH, weapon_id)

        names = {slot: {i: row["name"] for i, row in rows.items()} for slot, rows in attachments.items()}
        slots = {slot: list(rows) for slot, rows in attachments.items()}

        counts = Counter()
        examples = []
        for combo in combinations(slots, max_count, unavailable, incompatible, fixed):
            counts[len(combo)] += 1
            if len(examples) < SHOW:
                examples.append(combo)
    except ValueError as e:
        raise SystemExit(str(e))

    print(f"武器: {weapon['name']}（id {weapon_id}）  最大セット数: {max_count}")
    print("スロットごとの候補数: " + ", ".join(f"{s} {len(v)}" for s, v in attachments.items()))
    print(f"incompatible.json: 付けられない {sum(len(v) for v in unavailable.values())} 件 / "
          f"組み合わせ不可 {len(incompatible)} 組")
    if fixed:
        print("固定: " + describe(fixed, names))
    print()
    print("付ける数ごとの組み合わせ数")
    for n in sorted(counts):
        print(f"  {n} 個: {counts[n]:,}")
    print(f"  合計: {sum(counts.values()):,}")
    print()
    print(f"組み合わせの例（先頭 {len(examples)} 件）")
    for combo in examples:
        print("  " + describe(combo, names))
