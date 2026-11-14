# Call of Duty のアタッチメントを理論値で一番いいカスタムを作成してみる

## はじめに

皆さんは Call of Duty（以下 CoD）をやったことがありますか？もしくは今もやっていますか？

私は Ghosts からやり始めたので、かれこれ 10 年以上プレイしていることになります。そんな CoD 老害の私ですが、2019 年の CoD から「これはやりづらいな」と思う仕様が出てきました。それは

**アタッチメントが多すぎる！！**

ということです。

2019 年に発売された CoD では、ゲームエンジンが刷新されました。当時はグラフィックの圧倒的な進化に興奮したのを覚えていますが、同時にアタッチメントの多さに気が遠くなったのも覚えています（今でも気が遠くなりながらアタッチメントを調整しています）。

この新エンジンの CoD では、アタッチメントが撃ち合いの勝敗を大きく左右します。武器に合ったアタッチメントを付けてみて、合わなければ別のものに付け替えて……と調整を重ねて、使いやすい構成に仕上げていく必要があります。

しかし、私は単に撃ち合いを楽しみたいだけのプレイヤーです。この構成を考える手間をどうしても省きたい。

そこで、**プログラミングを使って理論的に一番良いアタッチメント構成を決めてしまおう！** と考えました。

この記事では、ステータスごとに重みを付けて最適な組み合わせを計算するスクリプトを、Python と MySQL で作っていきます。例として HAN 86 を使います。

## 今回のコードについて

先に言っておくと、今回のコードは AI を使ってサクッと作りました。まずは「重みを付けて最適な構成を出す」ところまで動かしてみたかったので、細かい作り込みはしていません。

重みの決め方についてはまだ雑なままなので、ここは今後もう少し深掘りしていくつもりです。

## データの準備

武器本体とアタッチメントのステータスを MySQL に入れました。武器本体は実際の数値、アタッチメントは増減値（+7 や -4 など）です。

アタッチメントはスロットごとにテーブルを分けています。

| テーブル | スロット | 件数 |
|---|---|---|
| muzzle | マズル | 8 |
| barrel | バレル | 6 |
| laser | レーザー | 7 |
| site | サイト | 23 |
| stock | ストック | 4 |
| underbarrel | アンダーバレル | 8 |
| ammo | 弾薬 | 5 |
| rear_grip | リアグリップ | 3 |
| magazine | マガジン | 2 |

```sql
CREATE TABLE weapon (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL COMMENT '武器名',
  power INT COMMENT '威力',
  `range` INT COMMENT '射程',
  accuracy INT COMMENT '命中率',
  mobility INT COMMENT '機動性',
  handling INT COMMENT '操作性',
  rpm INT COMMENT 'RPM',
  magazine_size INT COMMENT '装弾数',
  reserve_ammo INT COMMENT '予備弾数'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO weapon (name, power, `range`, accuracy, mobility, handling, rpm, magazine_size, reserve_ammo)
VALUES ('HAN 86', 27, 49, 57, 58, 62, 740, 30, 90);
```

アタッチメントのテーブルも同じ形です。データはスプレッドシートにまとめて、CSV で取り込みました。

## 考え方

各アタッチメントに「ステータスの増減 × 重み」の合計で点数を付けて、スロットごとに一番点数が高いものを選び、その中から上位 5 つを付けます。

```
点数 = 威力×重み + 射程×重み + 命中率×重み + 機動性×重み + 操作性×重み + ...
```

全組み合わせだと約 3,900 万通りありますが、今回は単純な足し算なのでこのやり方で全探索と同じ答えになります（念のため全探索でも確認しました）。

## コード

```python
import pymysql

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
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "mw4",
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
```

## 結果

とりあえず重みは全部同じ 20% にして回してみました。

```
武器: HAN 86
重み: 威力 20%, 射程 20%, 命中率 20%, 機動性 20%, 操作性 20%

アタッチメント
  レーザー     QFL-S4.5  +1.80
  マズル      B16 ヘリカル  +1.60
  バレル      HAN 86 サイレンサー 413MM  +1.60
  アンダーバレル  GW ドミ9  +1.40
  弾薬       5.56 NATO 高速弾  +1.20
  合計 +7.60

ステータス
  威力       27 ->   33 (+6)
  射程       49 ->   64 (+15)
  命中率      57 ->   76 (+19)
  機動性      58 ->   58
  操作性      62 ->   60 (-2)
  RPM     740 ->  740
  装弾数      30 ->   30
  予備弾数     90 ->   90
```

機動性はそのままで、命中率と射程がしっかり伸びる構成になりました。操作性が少し下がるくらいなので、悪くないんじゃないかなと思います。

## おわりに

とりあえず「重みを付けて最適な構成を出す」ところまではできました。

ただ、今回は重みを全部同じにしただけなので、正直これが本当にベストかと言われると微妙なところです。実際の撃ち合いでは、威力と機動性が同じ価値ということはないはずです。

次回は、

- どのステータスをどれくらい重視すべきか
- 武器の種類（AR、SMG など）で重みを変えるべきか
- ステータスの上限や「命中率 70 以上」みたいな条件をどう入れるか

あたりを、もう少し深掘りしてみようと思います。
