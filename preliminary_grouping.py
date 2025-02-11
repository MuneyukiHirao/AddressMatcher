import pandas as pd
from typing import List, Tuple

def preliminary_grouping(
    df: pd.DataFrame,
    group_cols: List[str] = None,
    max_chunk_size: int = 50
) -> List[pd.DataFrame]:
    """
    与えられたDataFrameを指定したカラム(例: ["CountryName", "StateName", "City"])でグルーピングし、
    グループごとにサブDataFrameを作成する。
    さらに、グループ内のレコード数が max_chunk_size を超える場合、複数チャンクに分割する。

    Parameters:
        df (pd.DataFrame): 前段のクリーニング・正規化を終えたDataFrame
        group_cols (List[str]): グルーピングに使うカラムのリスト
        max_chunk_size (int): 1チャンクあたりの最大レコード数

    Returns:
        List[pd.DataFrame]: 分割後のサブDataFrameのリスト
    """
    if group_cols is None:
        group_cols = ["CountryName", "StateName", "City"]

    # グループ化
    grouped = df.groupby(group_cols)
    
    result_sub_dfs = []
    
    for _, group_df in grouped:
        group_df = group_df.copy()
        
        # レコード数が max_chunk_size を超える場合は分割
        num_records = len(group_df)
        if num_records > max_chunk_size:
            # 等分割するイメージ。実際はレコード順や意味づけによって調整可能
            chunks = _split_df_into_chunks(group_df, max_chunk_size)
            result_sub_dfs.extend(chunks)
        else:
            result_sub_dfs.append(group_df)
    
    return result_sub_dfs

def _split_df_into_chunks(df: pd.DataFrame, chunk_size: int) -> List[pd.DataFrame]:
    """
    DataFrameをchunk_sizeごとに切り分け、複数のDataFrameに分割してリストで返す。
    """
    # DataFrame の行インデックスをリセットしておくと扱いやすい
    df = df.reset_index(drop=True)
    chunks = []
    for start_idx in range(0, len(df), chunk_size):
        end_idx = start_idx + chunk_size
        chunk_df = df.iloc[start_idx:end_idx].copy()
        chunks.append(chunk_df)
    return chunks
