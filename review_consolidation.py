import pandas as pd
from typing import Dict, List

def review_and_consolidate(
    df: pd.DataFrame,
    suspicious_threshold: int = 50,
    mark_singleton: bool = False
) -> pd.DataFrame:
    """
    LLM Matchingの結果を持つDataFrameを受け取り、NeedsReview フラグを付ける簡易処理。

    - グループサイズ >= suspicious_threshold のグループにフラグ付け (大きすぎるグループ)
    - mark_singleton=True に設定した場合のみ、グループサイズ=1のものもフラグ付けする
    - 最終的に "FinalGroupID" = "LLMGroupID" をコピー
    """

    df = df.copy()
    if "LLMGroupID" not in df.columns:
        raise ValueError("DataFrame does not contain LLMGroupID column.")

    # groupbyで各グループの件数を数える
    #print(df.columns)
    #print(df.dtypes)
    # Optional: check shape, sample values
    #print(df[["LLMGroupID"]].head())
    group_sizes = df.groupby("LLMGroupID").size()

    # 大きいグループ
    large_groups = group_sizes[group_sizes >= suspicious_threshold].index.tolist()

    # デフォルトで全行 False
    df["NeedsReview"] = False

    # しきい値超えグループにフラグ付け
    for g_id in large_groups:
        df.loc[df["LLMGroupID"] == g_id, "NeedsReview"] = True

    # 単一レコードのフラグ付けは任意設定
    if mark_singleton:
        single_groups = group_sizes[group_sizes == 1].index.tolist()
        for g_id in single_groups:
            df.loc[df["LLMGroupID"] == g_id, "NeedsReview"] = True

    # FinalGroupID は一旦そのままコピー
    df["FinalGroupID"] = df["LLMGroupID"]

    return df

def merge_groups(df: pd.DataFrame, old_ids: List[str], new_id: str) -> pd.DataFrame:
    """
    指定された複数の old_ids (LLMGroupID or FinalGroupID) を一つの new_id に統合する。
    例: merge_groups(df, old_ids=["G1","G2"], new_id="G1_G2_MERGED")

    Parameters:
        df (pd.DataFrame): "FinalGroupID" 列を持つDataFrame
        old_ids (List[str]): 統合対象となるIDのリスト
        new_id (str): 統合後のID
    """
    df = df.copy()
    if "FinalGroupID" not in df.columns:
        raise ValueError("DataFrame does not contain FinalGroupID column.")

    mask = df["FinalGroupID"].isin(old_ids)
    df.loc[mask, "FinalGroupID"] = new_id
    return df

def split_group(
    df: pd.DataFrame, group_to_split: str, condition_func
) -> pd.DataFrame:
    """
    1つの FinalGroupID にまとめられているレコードを、condition_func に従って2つに分割する例。
    たとえば "郵便番号が特定値なら別グループ" などの独自ロジックを condition_func で判定。

    Parameters:
        df (pd.DataFrame): "FinalGroupID" 列を持つDataFrame
        group_to_split (str): 分割対象となる FinalGroupID
        condition_func (callable): レコード(row)を受け取り True/False を返す関数
                                   True の行だけ別グループにする
    Returns:
        pd.DataFrame
    """
    df = df.copy()
    if "FinalGroupID" not in df.columns:
        raise ValueError("DataFrame does not contain FinalGroupID column.")

    # 対象レコードを抽出
    target_mask = (df["FinalGroupID"] == group_to_split)

    # condition_func(row) が True の行だけ別グループ ID を振る
    new_id = group_to_split + "_SPLIT"
    for idx in df[target_mask].index:
        row = df.loc[idx]
        if condition_func(row):
            df.at[idx, "FinalGroupID"] = new_id

    return df
