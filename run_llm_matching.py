import pandas as pd
from run_preliminary_grouping import run_preliminary_grouping
from llm_matching import perform_llm_matching

def run_llm_matching_demo(csv_path: str):
    """
    Preliminary Grouping => 先頭のチャンクを順に LLM Matching => 
    2件以上同一グループになったサブDataFrameのみ上位10件を表示
    """
    sub_dfs = run_preliminary_grouping(csv_path)
    if not sub_dfs:
        print("No sub DataFrames generated.")
        return

    displayed_count = 0

    for i, sub_df in enumerate(sub_dfs, start=1):
        # サブDataFrameが1行だけの場合はスキップ（そもそもグルーピングできない）
        if len(sub_df) < 2:
            continue

        # LLMでマッチング実行
        df_matched = perform_llm_matching(sub_df)

        # グループIDごとの件数を集計
        group_sizes = df_matched.groupby("LLMGroupID").size()

        # 同じgroup_idに2件以上割り当てられているものがあれば表示対象
        if any(group_sizes >= 2):
            displayed_count += 1
            print(f"\n=== LLM Matching on chunk #{i} (size={len(sub_df)}) ===")
            print(df_matched)

            # 表示数が10に達したら打ち切り
            if displayed_count == 10:
                break

    if displayed_count == 0:
        print("No chunk had 2 or more addresses grouped together by LLM.")

if __name__ == "__main__":
    csv_file_path = "customer_data.csv"  # 200件程度のデータを想定
    run_llm_matching_demo(csv_file_path)
