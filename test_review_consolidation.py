import pytest
import pandas as pd
from review_consolidation import review_and_consolidate, merge_groups, split_group

def test_review_and_consolidate():
    data = {
        "LLMGroupID": ["G1", "G1", "G1", "G2", "G3"],
        "Address1": ["A1", "A2", "A3", "B1", "C1"]
    }
    df_test = pd.DataFrame(data)
    # G1: 3件, G2: 1件, G3: 1件

    df_result = review_and_consolidate(df_test, suspicious_threshold=2)

    # G1 は3件 => suspicious_threshold(2)以上 => NeedsReview=True
    # G2, G3 は1件 => こちらも "1件だけ" なので NeedsReview=True (サンプルの方針)
    # よって全行 NeedsReview=True になる
    assert all(df_result["NeedsReview"])
    # FinalGroupID は LLMGroupID をコピー
    assert (df_result["FinalGroupID"] == df_result["LLMGroupID"]).all()

    print("SUCCESS: test_review_and_consolidate passed")

def test_merge_groups():
    df_test = pd.DataFrame({
        "FinalGroupID": ["G1", "G2", "G2", "G3"],
        "Address1": ["A1","B1","B2","C1"]
    })
    # G2 が2件、ほかは1件ずつ

    # G1 と G2 を "G12_Merged" に統合
    df_merged = merge_groups(df_test, old_ids=["G1", "G2"], new_id="G12_Merged")

    # 結果は G1, G2 => G12_Merged となる
    # G3 は変わらず
    assert list(df_merged["FinalGroupID"]) == ["G12_Merged","G12_Merged","G12_Merged","G3"]

    print("SUCCESS: test_merge_groups passed")

def test_split_group():
    df_test = pd.DataFrame({
        "FinalGroupID": ["G1", "G1", "G1"],
        "PostalCode": ["27601", "27601", "27602"]
    })
    # 全部G1だが、PostalCode = 27602 の行だけ別グループに分割

    def condition_func(row):
        return row["PostalCode"] == "27602"

    df_split = split_group(df_test, group_to_split="G1", condition_func=condition_func)

    # 結果 => G1 が2行、 G1_SPLIT が1行
    assert df_split["FinalGroupID"].tolist() == ["G1","G1","G1_SPLIT"]

    print("SUCCESS: test_split_group passed")
