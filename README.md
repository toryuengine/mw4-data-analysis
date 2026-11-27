# mw4-data-analysis

# テーブル構成

データベース名：`mw4`（文字コード utf8mb4）

## 一覧

| テーブル | 内容 | 件数 |
|---|---|---|
| category | 武器カテゴリー | 1 |
| weapon | 武器本体のステータス | 9 |
| muzzle | アタッチメント：マズル | 8 |
| barrel | アタッチメント：バレル | 6 |
| laser | アタッチメント：レーザー | 7 |
| site | アタッチメント：サイト | 23 |
| stock | アタッチメント：ストック | 4 |
| underbarrel | アタッチメント：アンダーバレル | 8 |
| ammo | アタッチメント：弾薬 | 5 |
| rear_grip | アタッチメント：リアグリップ | 3 |
| magazine | アタッチメント：マガジン | 2 |

## 関連

```mermaid
erDiagram
    category ||--o{ weapon : "category_id"
```

アタッチメントの各テーブルは `weapon_id` で武器に紐付く（今は全行 HAN 86）。

---

## category

武器カテゴリー。

| カラム | 型 | NULL | キー | 内容 |
|---|---|---|---|---|
| id | INT | × | PK（自動採番） | |
| name | VARCHAR(50) | × | UNIQUE | カテゴリー名 |

| id | name |
|---|---|
| 1 | アサルト |

---

## weapon

武器本体のステータス。ゲーム内の詳細ステータス画面の値を、銃 1 丁につき 1 行で持つ。

- 画面上で「なし」と表示される項目は NULL
- 単位は列には含めず、下表の「単位」の通りに数値だけを入れる

### 基本

| カラム | 型 | NULL | キー | 内容 | 単位 |
|---|---|---|---|---|---|
| id | INT | × | PK（自動採番） | | |
| name | VARCHAR(100) | × | | 武器名 | |
| category_id | INT | ○ | FK → category.id | カテゴリー | |
| fire_mode | VARCHAR(50) | ○ | | 射撃モード（例：`セミ,オート`） | |

### バー（5 項目）

| カラム | 型 | 内容 |
|---|---|---|
| power | INT | 威力 |
| range | INT | 射程距離 |
| accuracy | INT | 命中率 |
| mobility | INT | 機動性 |
| handling | INT | 操作性 |

`range` は MySQL の予約語なので、SQL ではバッククォートで囲む。

### 連射速度

| カラム | 型 | 内容 | 単位 |
|---|---|---|---|
| rpm | INT | 連射速度 | RPM |
| pre_fire_delay | INT | 射撃前遅延 | ms |
| rechamber_speed | INT | 再装填速度 | ms |

### 威力

| カラム | 型 | 内容 | 単位 |
|---|---|---|---|
| penetration | DECIMAL(5,1) | 弾丸の貫通力 | インチ |
| flinch | DECIMAL(4,2) | ひるみ付与 | X |

### 機動性

| カラム | 型 | 内容 | 単位 |
|---|---|---|---|
| move_speed | DECIMAL(4,2) | 移動速度 | m/s |
| ads_move_speed | DECIMAL(4,2) | エイム時移動速度 | m/s |
| fire_move_speed | DECIMAL(4,2) | 射撃時の移動速度 | m/s |
| strafe_speed | DECIMAL(4,2) | 横移動速度 | m/s |
| crouch_speed | DECIMAL(4,2) | しゃがみ速度 | m/s |
| sprint_speed | DECIMAL(4,2) | ダッシュ速度 | m/s |
| tac_sprint_speed | DECIMAL(4,2) | タクティカルダッシュ速度 | m/s |
| tac_sprint_duration | DECIMAL(4,1) | タクティカルダッシュ持続時間 | 秒 |

### 射程距離

| カラム | 型 | 内容 | 単位 |
|---|---|---|---|
| muzzle_velocity | DECIMAL(6,1) | マズル速度 | m/s |
| zoom | DECIMAL(3,1) | ズーム倍率 | X |

### 弾薬

| カラム | 型 | 内容 |
|---|---|---|
| magazine_size | INT | 装弾数 |
| reserve_ammo | INT | 予備弾数 |

### 操作性

| カラム | 型 | 内容 | 単位 |
|---|---|---|---|
| ads_in_time | INT | エイム開始速度 | ms |
| ads_out_time | INT | エイム解除速度 | ms |
| sprint_to_fire | INT | ダッシュ後射撃速度 | ms |
| raise_time | INT | 構え速度 | ms |
| drop_time | INT | ドロップ速度 | ms |
| reload_time | INT | リロード速度 | ms |

### 命中率（エイム時）

| カラム | 型 | 内容 | 単位 |
|---|---|---|---|
| ads_recoil_h | DECIMAL(5,1) | エイム時の水平反動制御 | °/s |
| ads_recoil_v | DECIMAL(5,1) | エイム時の垂直反動制御 | °/s |
| ads_kick_h | DECIMAL(5,1) | エイム時の水平ガンキック | °/s |
| ads_kick_v | DECIMAL(5,1) | エイム時の垂直ガンキック | °/s |
| ads_spread | DECIMAL(5,2) | エイム時のブレ | °/s |
| ads_sway | DECIMAL(5,2) | エイム時の銃の揺れ | ° |
| ads_rechamber_accuracy | DECIMAL(5,2) | エイム時再装填精度 | |

### 命中率（腰だめ撃ち）

| カラム | 型 | 内容 | 単位 |
|---|---|---|---|
| hip_recoil_h | DECIMAL(5,1) | 腰だめ撃ち時の水平反動制御 | °/s |
| hip_recoil_v | DECIMAL(5,1) | 腰だめ撃ち時の垂直反動制御 | °/s |
| hip_kick_h | DECIMAL(5,1) | 腰だめ撃ち時の水平ガンキック | °/s |
| hip_kick_v | DECIMAL(5,1) | 腰だめ撃ち時の垂直ガンキック | °/s |
| hip_spread | DECIMAL(5,2) | 腰だめ撃ち時のブレ | °/s |
| hip_sway | DECIMAL(5,2) | 腰だめ撃ち時の銃の揺れ | ° |
| hip_rechamber_accuracy | DECIMAL(5,2) | 腰だめ撃ち時の再装填精度 | |
| hip_turn_spread | DECIMAL(5,1) | 腰だめ撃ち旋回時のブレ | ° |
| hip_strafe_accuracy | DECIMAL(5,2) | 横移動時の腰だめ撃ち命中率 | ° |
| hit_flinch | DECIMAL(4,2) | 被弾時のひるみ | X |

### 部位別ダメージ

画面のダメージ分布の数値を、上から順に入れる。

| カラム | 型 | 内容 |
|---|---|---|
| dmg_head | INT | 頭 |
| dmg_head_multiplier | DECIMAL(3,2) | 頭の倍率（`29 (X1.3)` の 1.3） |
| dmg_neck | INT | 首 |
| dmg_upper_torso | INT | 胸 |
| dmg_lower_torso | INT | 腹 |
| dmg_upper_arm | INT | 上腕 |
| dmg_lower_arm | INT | 前腕 |
| dmg_upper_leg | INT | 太もも |
| dmg_lower_leg | INT | すね |

### 距離別ダメージ

最大 3 段階。使わない段階は NULL。最後の段階は `max` を NULL（＝∞）にする。

| カラム | 型 | 内容 | 単位 |
|---|---|---|---|
| range1_max | INT | 1 段階目の距離上限 | m |
| range1_damage | INT | 1 段階目のダメージ | |
| range2_max | INT | 2 段階目の距離上限 | m |
| range2_damage | INT | 2 段階目のダメージ | |
| range3_max | INT | 3 段階目の距離上限 | m |
| range3_damage | INT | 3 段階目のダメージ | |

例：

| 画面の表示 | range1_max | range1_damage | range2_max | range2_damage | range3_max | range3_damage |
|---|---|---|---|---|---|---|
| 0-30: 23 / 30-∞: 19 | 30 | 23 | NULL | 19 | NULL | NULL |
| 0-21: 31 / 21-43: 25 / 43-∞: 22 | 21 | 31 | 43 | 25 | NULL | 22 |

---

## アタッチメント（9 テーブル共通）

`muzzle` / `barrel` / `laser` / `site` / `stock` / `underbarrel` / `ammo` / `rear_grip` / `magazine` はすべて同じ構成。

weapon と同じステータス列を持つ（`category_id` と `fire_mode` は除く）。値はアタッチメントを付けたときの元の武器のステータスからの**増減**で、プラスもマイナスもある。変化しない項目は 0。全列 NULL 不可・初期値 0。

### アタッチメント専用の列

| カラム | 型 | NULL | キー | 内容 |
|---|---|---|---|---|
| id | INT | × | PK（自動採番） | |
| weapon_id | INT | × | FK → weapon.id | 対応する武器 |
| ident | INT | × | UNIQUE（weapon_id, ident） | 武器ごとのアタッチメント番号（1, 2, 3 …） |
| name | VARCHAR(100) | × | | アタッチメント名 |

### ステータス列

| カラム | 型 | 内容 |
|---|---|---|
| power / range / accuracy / mobility / handling | INT | バーの増減値（例：+7、-4） |
| rpm / magazine_size / reserve_ammo | INT | 増減値 |
| 上記以外（pre_fire_delay 〜 range3_damage） | DECIMAL(6,2) | 元の武器のステータスからの増減率（%） |

列の名前と並び順は weapon と同じ。各列の意味は上の weapon の表を参照。

---

## ソースファイル

### main2.py

DB の weapon テーブルから全武器のステータスを取り出し、`src/standard_score.py` で偏差値を計算して、武器ごとの一覧を出力する。

```
.venv\Scripts\python.exe main2.py
```

- DB の接続情報は `.env` から読み込む（`.env.example` をコピーして作成）
- 出力は「平均」（各ステータスの偏差値の平均）の高い順。50 が全武器の平均で、高いほど良い
- 偏差値を出すステータスは、ファイル先頭の `STATS` で決める。`(カラム名, 表示名, 大きいほど良いか)` の形で追加・削除できる
  - ADS（エイム開始速度）やリロードのような時間は短いほど良いので `False`
- 値が NULL の武器は、その項目を `-` と表示し、平均からも除く

出力例：

```
武器                威力     射程   命中率   機動性   操作性      RPM   マズル      ADS リロード     平均
---------------------------------------------------------------------------------------------------------
M4                  39.3     44.1     56.0     63.0     64.6     60.2     45.4     62.3     72.5     56.4
CRONEN OSPREY       39.3     55.9     50.6     63.0     58.0     64.7     45.4     62.3     60.5     55.5
...
```

### main3.py

DB の weapon テーブルから全武器のステータスを取り出し、`src/killtime.py` で距離ごとのキルタイムを計算して出力する。DB 接続と表の整形は `main2.py` の関数を使う。

```
.venv\Scripts\python.exe main3.py
```

- 出力は 4 つの表
  - 撃ち始めからのキルタイム（ミリ秒）
  - エイム開始からのキルタイム（`ads_in_time` を足した値）
  - ダッシュ後からのキルタイム（`sprint_to_fire`＝ダッシュ硬直を足した値。腰だめ撃ちの前提）
  - 距離ごとの「1発のダメージ x 必要な弾数」
- キルタイムの表は、全距離の平均が短い順
- 出す距離はファイル先頭の `DISTANCES`、敵の体力は `HP` で変えられる
- `*` は 1 マガジンでは倒せない、`※` はオート射撃がない武器（rpm どおりに撃ち続ける前提なので、実際より速く出ることがある）

出力例：

```
■ 撃ち始めから
武器                   5m     10m     15m     20m     30m     40m     50m    平均
---------------------------------------------------------------------------------
PATRIOT XMR           287     295     303     310     326     342     357     317
ODEN                  297     304     312     319     333     348     362     325
...
```

### src/killtime.py

キルタイム（TTK）を算出するファイル。撃ち始めてから、敵の HP を 0 にする弾が当たるまでの時間（ミリ秒）を計算する。

```
1発のダメージ   = 距離 d が入る段階の rangeN_damage
必要な弾数(STK) = ceil(HP ÷ 1発のダメージ)
発射間隔        = 60000 ÷ rpm
キルタイム      = pre_fire_delay + (STK - 1) × 発射間隔 + d ÷ muzzle_velocity × 1000
```

- 全弾が胴体に当たる前提（距離別ダメージだけを使い、部位別ダメージは使わない）
- 弾の飛ぶ時間は最後の 1 発の分だけ足す（全弾同じ速さで飛ぶため）
- 距離の境目は次の段階に入れる（`0-30 / 30-∞` なら、30m は 2 段階目）
- rpm どおりに撃ち続ける前提。バースト武器の間隔の違いは考えない
- 武器の一覧やDB接続は持たない。weapon テーブルの 1 行を辞書で渡す

| 関数 | 内容 |
|---|---|
| `damage_at(weapon, distance)` | 距離 distance(m) での 1 発のダメージ |
| `shots_to_kill(damage, hp=100)` | 倒すのに必要な弾数 |
| `kill_time(weapon, distance, hp=100, include_ads=False, include_sprint=False)` | `{damage, stk, ttk, enough_ammo}` を返す。`ttk` がキルタイム(ms)。`include_ads=True` で ADS 込み、`include_sprint=True` でダッシュ硬直（`sprint_to_fire`）込み |

```python
from killtime import kill_time

kill_time(weapon, 10)                        # {'damage': 23, 'stk': 5, 'ttk': 340.1, 'enough_ammo': True}
kill_time(weapon, 10, include_ads=True)      # ttk に ads_in_time を足した値
kill_time(weapon, 10, include_sprint=True)   # ttk に sprint_to_fire を足した値
```

両方を True にすると単純に足し算する。ゲーム内でダッシュ硬直とエイム開始が同時に進むかは未確認。

### src/standard_score.py

偏差値（standard score）を算出するファイル。渡された数値の集まりの中で、各値を「平均 50・標準偏差 10」の尺度に直す。

```
偏差値 = 50 + 10 × (値 - 平均) ÷ 標準偏差（母標準偏差）
```

- 武器の一覧やDB接続は持たない。比べたい値は呼び出し側から渡す
- `standard_scores(values, higher_is_better=True)`：リストを受け取り、同じ順番で偏差値のリストを返す
- `standard_scores_by_key(data, higher_is_better=True)`：`{名前: 値}` の辞書を受け取り、`{名前: 偏差値}` を返す
- `higher_is_better=False` にすると、値が小さいほど偏差値が高くなる（エイム開始速度・リロード速度など）
- `None` の値は計算から除き、結果も `None`。全部同じ値のときは全員 50

```python
from standard_score import standard_scores_by_key

standard_scores_by_key({"A": 250, "B": 240, "C": 275}, higher_is_better=False)
```
