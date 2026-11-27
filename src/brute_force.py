"""アタッチメントの組み合わせを総当たりで作る。

- 各スロットから「付けない」か「1つ選ぶ」
- 付ける数は max_count 個まで
- incompatible.json の内容で、付けられないアタッチメントと、一緒に付けられない組み合わせを除く

組み合わせは {スロット名: ident} の辞書で返す（何も付けない組み合わせは {}）。
武器の一覧やDBへの接続は持たない。
"""

import json

SLOTS = ["muzzle", "barrel", "laser", "site", "stock", "underbarrel", "ammo", "rear_grip", "magazine"]


def parse_item(text):
    """"stock:1" を ("stock", 1) にする。"""
    try:
        slot, ident = text.split(":")
        ident = int(ident)
    except ValueError:
        raise ValueError(f"'スロット名:ident' の形ではありません: {text!r}")
    if slot not in SLOTS:
        raise ValueError(f"スロット名が正しくありません: {text!r}")
    return slot, ident


def load_rules(path, weapon_id):
    """incompatible.json から、指定した武器のルールを読む。

    戻り値: (unavailable, incompatible)
        unavailable  : {スロット名: {ident, ...}}
        incompatible : {frozenset({(スロット名, ident), (スロット名, ident)}), ...}
    ファイルに武器がなければ、制限なしとして空を返す。
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    rule = data.get(str(weapon_id), {})

    unavailable = {}
    for slot, idents in rule.get("unavailable", {}).items():
        if slot not in SLOTS:
            raise ValueError(f"unavailable のスロット名が正しくありません: {slot!r}")
        unavailable[slot] = set(idents)

    incompatible = set()
    for pair in rule.get("incompatible", []):
        if len(pair) != 2:
            raise ValueError(f"incompatible の 1 組は 2 つで書いてください: {pair!r}")
        a, b = parse_item(pair[0]), parse_item(pair[1])
        incompatible.add(frozenset({a, b}))

    return unavailable, incompatible


def check_fixed(fixed, slots, max_count, unavailable, incompatible):
    """固定するアタッチメントが付けられるか確かめる。だめなら ValueError。"""
    if len(fixed) > max_count:
        raise ValueError(f"固定するアタッチメント（{len(fixed)} 個）が最大セット数（{max_count}）より多いです")
    for slot, ident in fixed.items():
        if ident not in slots.get(slot, []):
            raise ValueError(f"{slot}:{ident} はこの武器のアタッチメントにありません")
        if ident in unavailable.get(slot, set()):
            raise ValueError(f"{slot}:{ident} は incompatible.json で付けられないアタッチメントです")
    items = list(fixed.items())
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if frozenset({a, b}) in incompatible:
                raise ValueError(f"{a[0]}:{a[1]} と {b[0]}:{b[1]} は incompatible.json で一緒に付けられません")


def combinations(slots, max_count, unavailable=None, incompatible=None, fixed=None):
    """組み合わせを 1 つずつ返すジェネレーター。

    slots        : {スロット名: [ident, ...]}（その武器に付けられるアタッチメント）
    max_count    : 付けるアタッチメントの最大数（固定するアタッチメントも数に含む）
    unavailable  : load_rules の戻り値（省略時は制限なし）
    incompatible : load_rules の戻り値（省略時は制限なし）
    fixed        : {スロット名: ident}。必ず付けるアタッチメント（省略時はなし）
    """
    if max_count < 0:
        raise ValueError("max_count は 0 以上にしてください")
    unavailable = unavailable or {}
    incompatible = incompatible or set()
    fixed = fixed or {}
    check_fixed(fixed, slots, max_count, unavailable, incompatible)

    available = {}
    for slot in SLOTS:
        if slot in fixed:
            continue  # 固定したスロットは選び直さない
        idents = [i for i in slots.get(slot, []) if i not in unavailable.get(slot, set())]
        if idents:
            available[slot] = idents
    order = list(available)

    chosen = dict(fixed)

    def conflicts(item):
        return any(frozenset({item, other}) in incompatible for other in chosen.items())

    def walk(index):
        if index == len(order):
            yield dict(chosen)
            return

        slot = order[index]
        # このスロットには付けない
        yield from walk(index + 1)

        # このスロットに 1 つ付ける
        if len(chosen) < max_count:
            for ident in available[slot]:
                if conflicts((slot, ident)):
                    continue
                chosen[slot] = ident
                yield from walk(index + 1)
                del chosen[slot]

    yield from walk(0)


if __name__ == "__main__":
    # 動作確認用のサンプル（武器の一覧ではない）
    sample_slots = {"stock": [1, 2, 3], "muzzle": [1, 2], "ammo": [1]}
    unavailable = {"stock": {3}}
    incompatible = {frozenset({("stock", 1), ("muzzle", 2)})}

    for combo in combinations(sample_slots, 2, unavailable, incompatible):
        print(combo)

    print("stock:2 を固定")
    for combo in combinations(sample_slots, 2, unavailable, incompatible, fixed={"stock": 2}):
        print(combo)
