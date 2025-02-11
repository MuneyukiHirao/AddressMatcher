import pandas as pd
from run_llm_matching import run_llm_matching_demo
from review_and_consolidation import review_and_consolidate, show_multi_record_groups

def run_review_and_consolidation_demo(csv_path: str):
    """
    (例示) Preliminary Grouping -> LLM Matching -> 複数のサブDFを得て
    それらをreview_and_consolidate でまとめ、複数レコードを含むグループを表示。
    """
    # ここでは例として run_llm_matching_demo を呼び出し、
    # 実際には1つしかSubDFをマッチングしていないが...
    # 本来は複数サブDFを LLM Matching した結果のリストを用意する想定。
    # デモのため、同じSubDFを2回マッチングしたふりをする。

    from run_preliminary_grouping import run_preliminary_grouping
    from llm_matching import perform_llm_matching

    sub_dfs = run_preliminary_grouping(csv_path)

    # LLM Matching を各サブDFに対して実行
    matched_sub_dfs = []
    for df_sub in sub_dfs:
        df_matched = perform_llm_matching(df_sub)
        matched_sub_dfs.append(df_matched)

    # Review & Consolidation
    df_consolidated = review_and_consolidate(matched_sub_dfs)
    print("\n--- Consolidated DataFrame Sample ---")
    print(df_consolidated.head(10))

    # 人間向けに複数レコードを含むグループを確認
    print("\n--- Multi-record groups ---")
    show_multi_record_groups(df_consolidated, group_col="GlobalGroupID")

if __name__ == "__main__":
    csv_file_path = "customer_data.csv"
    run_review_and_consolidation_demo(csv_file_path)
