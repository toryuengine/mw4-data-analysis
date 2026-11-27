"""偏差値（standard score）を算出する。

渡された数値の集まりの中で、各値が平均からどれだけ離れているかを
「平均 50・標準偏差 10」の尺度に直して返す。

    偏差値 = 50 + 10 × (値 - 平均) ÷ 標準偏差

武器の一覧やDBへの接続は持たない。呼び出し側が比べたい値を渡す。
"""

from decimal import Decimal
from statistics import mean, pstdev


def standard_scores(values, higher_is_better=True):
    """値ごとの偏差値を、渡された順番のリストで返す。

    values           : 数値のリスト（int / float / Decimal）。None は計算から除き、結果も None になる
    higher_is_better : False にすると、値が小さいほど偏差値が高くなる（エイム開始速度・リロード速度など）

    全部が同じ値のとき（標準偏差が 0）は、全員 50 にする。
    """
    nums = [float(v) for v in values if v is not None]
    if not nums:
        return [None for _ in values]

    avg = mean(nums)
    sd = pstdev(nums)  # 偏差値は母標準偏差で計算する

    scores = []
    for v in values:
        if v is None:
            scores.append(None)
        elif sd == 0:
            scores.append(50.0)
        else:
            diff = float(v) - avg
            if not higher_is_better:
                diff = -diff
            scores.append(50 + 10 * diff / sd)
    return scores


def standard_scores_by_key(data, higher_is_better=True):
    """{名前: 値} の辞書を受け取り、{名前: 偏差値} の辞書で返す。"""
    keys = list(data)
    scores = standard_scores([data[k] for k in keys], higher_is_better)
    return dict(zip(keys, scores))


if __name__ == "__main__":
    # 動作確認用のサンプル値（武器の一覧ではない）
    sample = {"A": 30, "B": 40, "C": 50, "D": 60, "E": Decimal("70"), "F": None}
    for name, score in standard_scores_by_key(sample).items():
        print(name, sample[name], "->", None if score is None else round(score, 1))

    print("小さいほど良い場合")
    for name, score in standard_scores_by_key(sample, higher_is_better=False).items():
        print(name, sample[name], "->", None if score is None else round(score, 1))
