import pandas as pd

from data_ingestion import load_customer_data
from data_cleaning_formatting import clean_and_format_data
from address_normalization import normalize_addresses
from preliminary_grouping import preliminary_grouping
from llm_matching import perform_llm_matching
from review_consolidation import review_and_consolidate
from group_id_unifier import unify_local_group_ids

def run_end_to_end(csv_path: str):
    """
    一連の処理を実施し、最終的な結果をExcelに出力。
    - LLMGroupID が二重化しないよう修正し、各チャンク結合はaxis=0
    """
    # 1. Data Ingestion
    df_raw = load_customer_data(csv_path)
    print(f"=== Loaded data: {len(df_raw)} rows ===")

    # 2. Cleaning & Formatting
    df_cleaned = clean_and_format_data(df_raw)
    print(f"=== After Cleaning & Formatting: {len(df_cleaned)} rows ===")

    # 3. Address Normalization
    city_map = {"RALIEGH": "RALEIGH"}
    state_map = {"VA": "VIRGINIA"}
    address_map = {"St.": "Street"}

    df_normalized = normalize_addresses(
        df_cleaned,
        city_map=city_map,
        state_map=state_map,
        address_map=address_map
    )
    print(f"=== After Normalization: {len(df_normalized)} rows ===")

    # 4. Preliminary Grouping
    sub_dfs = preliminary_grouping(df_normalized, max_chunk_size=50)
    print(f"=== Preliminary Grouping => {len(sub_dfs)} chunks ===")

    # 5. LLM Matching + unify group IDs
    matched_chunks = []
    global_id_counter = 1  # 全チャンクを通じてユニークなIDをつけるためのカウンタ

    for i, sub_df in enumerate(sub_dfs, start=1):
        # 2件未満ならLLM呼び出し不要
        if len(sub_df) < 2:
            sub_df = sub_df.copy()
            sub_df["LLMGroupID"] = [f"Single_{i}"] * len(sub_df)
        else:
            sub_df = perform_llm_matching(sub_df)

        # まず「ローカル LLMGroupID」を「UnifiedGroupID」に変換し、かぶりを防ぐ
        sub_df, global_id_counter = unify_local_group_ids(
            df=sub_df,
            local_id_col="LLMGroupID",
            global_id_col="UnifiedGroupID",
            start_count=global_id_counter,
            prefix="G"
        )

        # ここで元の LLMGroupID は不要なので削除 or rename
        #   -> rename columns={"UnifiedGroupID": "LLMGroupID"}
        #      ただし元の LLMGroupID を残さないように drop
        sub_df.drop(columns=["LLMGroupID"], inplace=True, errors="ignore")
        sub_df.rename(columns={"UnifiedGroupID": "LLMGroupID"}, inplace=True)

        # 加工したチャンクをリストに格納
        matched_chunks.append(sub_df)

    # 全チャンクを「縦方向に」結合
    df_matched_all = pd.concat(matched_chunks, axis=0).reset_index(drop=True)

    # 万一重複カラムが発生した場合の保険
    df_matched_all = df_matched_all.loc[:, ~df_matched_all.columns.duplicated()].copy()

    print(f"=== LLM Matching + unify done. Combined rows: {len(df_matched_all)} ===")

    # 6. Review & Consolidation
    df_final = review_and_consolidate(
        df_matched_all,
        suspicious_threshold=50,
        mark_singleton=False
    )
    print("=== Review & Consolidation done. ===")

    # 結果を Excel 出力
    df_final.to_excel("result.xlsx", index=False)
    print("Output saved to result.xlsx")

    return df_final

if __name__ == "__main__":
    csv_file_path = "customer_data.csv"
    df_result = run_end_to_end(csv_file_path)
