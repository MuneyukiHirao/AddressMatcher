import pytest
import pandas as pd
from preliminary_grouping import preliminary_grouping

def test_preliminary_grouping_basic():
    """
    基本的なグルーピングが想定通り行われるかテスト。
    """
    data = {
        "CountryName": ["USA", "USA", "USA", "CANADA", "CANADA"],
        "StateName": ["TX", "TX", "CA", "ON", "ON"],
        "City": ["Dallas", "Dallas", "Los Angeles", "Toronto", "Toronto"],
        "Address1": ["Addr1", "Addr2", "Addr3", "Addr4", "Addr5"]
    }
    df_test = pd.DataFrame(data)

    # グルーピング (デフォルトは [CountryName, StateName, City])
    sub_dfs = preliminary_grouping(df_test)

    # 期待結果:
    #  1) USA-TX-Dallas => 2件
    #  2) USA-CA-Los Angeles => 1件
    #  3) CANADA-ON-Toronto => 2件
    # 合計3グループに分割

    assert len(sub_dfs) == 3

    # どのグループにも max_chunk_size を超えるものはないはず
    assert sum(len(df_sub) for df_sub in sub_dfs) == len(df_test)

    print("SUCCESS: test_preliminary_grouping_basic passed")

def test_preliminary_grouping_chunk_split():
    """
    max_chunk_sizeより多い場合にチャンク分割されることをテスト。
    """
    data = {
        "CountryName": ["USA"] * 6,
        "StateName": ["TX"] * 6,
        "City": ["Dallas"] * 6,
        "Address1": [f"Addr{i}" for i in range(6)]
    }
    df_test = pd.DataFrame(data)

    # max_chunk_sizeを3にして、6件 => 2チャンクに分割される想定
    sub_dfs = preliminary_grouping(df_test, max_chunk_size=3)

    # 1つのグループ (USA,TX,Dallas) に6件が含まれる => 2チャンク
    assert len(sub_dfs) == 2
    assert len(sub_dfs[0]) == 3
    assert len(sub_dfs[1]) == 3

    print("SUCCESS: test_preliminary_grouping_chunk_split passed")

def test_preliminary_grouping_custom_group_cols():
    """
    group_colsをカスタム指定した場合のテスト。
    """
    data = {
        "CountryName": ["USA", "USA", "USA"],
        "StateName": ["TX", "TX", "CA"],
        "City": ["Dallas", "Houston", "Los Angeles"],
        "DistributorName": ["Dist1", "Dist1", "Dist2"],
    }
    df_test = pd.DataFrame(data)

    # StateNameではなく DistributorName でグルーピングしてみる
    sub_dfs = preliminary_grouping(df_test, group_cols=["CountryName", "DistributorName"])

    # 期待結果:
    #   - Country=USA, DistributorName=Dist1 => 2行
    #   - Country=USA, DistributorName=Dist2 => 1行
    assert len(sub_dfs) == 2
    assert sum(len(df_sub) for df_sub in sub_dfs) == len(df_test)

    print("SUCCESS: test_preliminary_grouping_custom_group_cols passed")
