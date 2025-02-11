import pandas as pd
from typing import Tuple

def unify_local_group_ids(
    df: pd.DataFrame,
    local_id_col: str = "LLMGroupID",
    global_id_col: str = "UnifiedGroupID",
    start_count: int = 1,
    prefix: str = "G"
) -> Tuple[pd.DataFrame, int]:
    """
    DataFrame 内のローカルグループIDを一意なグローバルIDに変換し、
    (変換後df, 次のカウンタ) を返す。

    例:
      - LLM が各チャンク内で G1, G2... を返すが、別チャンク同士で被る可能性がある
      - これをチャンクごとに一意化するため、G1 -> G1, G2 -> G2 と割り当てつつ
        次のチャンクでは新しい連番を使う (例: G3, G4 ...)
    """
    df = df.copy()

    # ローカルID一覧を取得
    local_ids = df[local_id_col].unique()

    mapping = {}
    current_count = start_count

    for lid in local_ids:
        mapping[lid] = f"{prefix}{current_count}"
        current_count += 1

    # 新たなカラムへマッピング
    df[global_id_col] = df[local_id_col].map(mapping)

    return df, current_count
