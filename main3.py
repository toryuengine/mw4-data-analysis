"""DB の武器ステータスから、距離ごとのキルタイムを出力する。

キルタイムの計算は src/killtime.py の関数を使う。
DB 接続と表の整形は main2.py の関数を使う（接続情報は .env）。
"""

from main2 import fetch_weapons, pad, width
from killtime import DEFAULT_HP, kill_time  # main2 が src をパスに追加している

# キルタイムを出す距離(m)
DISTANCES = [5, 10, 15, 20, 30, 40, 50]

HP = DEFAULT_HP


def calc_table(weapons, include_ads=False, include_sprint=False):
    """{武器名: [各距離の計算結果, ...]} を返す。"""
    return {
        w["name"]: [
            kill_time(w, d, hp=HP, include_ads=include_ads, include_sprint=include_sprint)
            for d in DISTANCES
        ]
        for w in weapons
    }


def cell(result):
    """キルタイムを表示用の文字にする。1マガジンで倒せないときは * を付ける。"""
    text = f"{result['ttk']:.0f}"
    return text if result["enough_ammo"] else text + "*"


def print_table(title, weapons, table):
    name_w = max(width(w["name"]) for w in weapons) + 4
    col_w = 8

    # 全距離の平均が短い順
    def average(name):
        return sum(r["ttk"] for r in table[name]) / len(DISTANCES)

    ranked = sorted(weapons, key=lambda w: average(w["name"]))

    print(title)
    header = pad("武器", name_w) + "".join(pad(f"{d}m", col_w, right=True) for d in DISTANCES)
    header += pad("平均", col_w, right=True)
    print(header)
    print("-" * width(header))
    for w in ranked:
        name = w["name"]
        mark = "" if "オート" in (w.get("fire_mode") or "") else " ※"
        line = pad(name + mark, name_w)
        line += "".join(pad(cell(r), col_w, right=True) for r in table[name])
        line += pad(f"{average(name):.0f}", col_w, right=True)
        print(line)
    print()


def print_stk(weapons, table):
    """距離ごとの 1発のダメージ x 必要な弾数。"""
    name_w = max(width(w["name"]) for w in weapons) + 4
    col_w = 8
    print("1発のダメージ x 必要な弾数")
    header = pad("武器", name_w) + "".join(pad(f"{d}m", col_w, right=True) for d in DISTANCES)
    print(header)
    print("-" * width(header))
    for w in weapons:
        name = w["name"]
        line = pad(name, name_w)
        line += "".join(pad(f"{r['damage']}x{r['stk']}", col_w, right=True) for r in table[name])
        print(line)
    print()


if __name__ == "__main__":
    weapons = fetch_weapons()
    pure = calc_table(weapons)
    with_ads = calc_table(weapons, include_ads=True)
    with_sprint = calc_table(weapons, include_sprint=True)

    print(f"キルタイム（ミリ秒・HP {HP}・全弾胴体・短い順）")
    print()
    print_table("■ 撃ち始めから", weapons, pure)
    print_table("■ エイム開始から（ADS 込み）", weapons, with_ads)
    print_table("■ ダッシュ後から（ダッシュ硬直込み・腰だめ）", weapons, with_sprint)
    print_stk(weapons, pure)
    print("* … 1マガジンでは倒せない")
    print("※ … オート射撃がない武器。rpm どおりに撃ち続ける前提なので、実際より速く出ることがある")
