import pytest
import pandas as pd
from address_normalization import normalize_addresses

def test_normalize_addresses_basic():
    """
    基本的な辞書ベース置換が正しく行われることをテスト。
    """
    df_test = pd.DataFrame({
        "CustomerDisplayName": ["SampleCustomer1"],
        "City": ["RALIEGH"],
        "StateName": ["VA"],
        "Address1": ["1234 Main St."],
        "Address2": [""]
    })

    city_map = {
        "RALIEGH": "RALEIGH"
    }
    state_map = {
        "VA": "VIRGINIA"
    }
    address_map = {
        "St.": "Street"
    }

    df_result = normalize_addresses(df_test, city_map, state_map, address_map)
    
    # 変換結果を検証
    assert df_result.loc[0, "City"] == "RALEIGH"
    assert df_result.loc[0, "StateName"] == "VIRGINIA"
    assert df_result.loc[0, "Address1"] == "1234 Main Street"
    assert df_result.loc[0, "Address2"] == ""

    print("SUCCESS: test_normalize_addresses_basic passed")

def test_normalize_addresses_no_match():
    """
    マッピングに存在しない場合、そのまま残るかを確認。
    """
    df_test = pd.DataFrame({
        "CustomerDisplayName": ["SampleCustomer2"],
        "City": ["RALIEGH"],       # 変換用意
        "StateName": ["VA "],      # 前段でstrip済み想定だが、あえてスペース込み
        "Address1": ["5678 Broadway Ave."],
        "Address2": ["Suite 100"]
    })

    # マップを空にする (変換しない)
    city_map = {}
    state_map = {}
    address_map = {}

    df_result = normalize_addresses(df_test, city_map, state_map, address_map)
    
    # 変換しないので、そのまま
    assert df_result.loc[0, "City"] == "RALIEGH"
    # "VA " というスペースは前段Cleaningで削除されている想定だが、
    # ここではNormalizationモジュールはそのまま扱う（例示）。
    assert df_result.loc[0, "StateName"] == "VA "
    assert df_result.loc[0, "Address1"] == "5678 Broadway Ave."
    assert df_result.loc[0, "Address2"] == "Suite 100"

    print("SUCCESS: test_normalize_addresses_no_match passed")

def test_normalize_addresses_partial_address_replace():
    """
    Address1, Address2 の部分文字列置換を複数実行するケース。
    例: "St."→"Street", "Ave."→"Avenue" など
    """
    df_test = pd.DataFrame({
        "CustomerDisplayName": ["SampleCustomer3"],
        "City": ["RALEIGH"],
        "StateName": ["VIRGINIA"],
        "Address1": ["123 St. Dr."],
        "Address2": ["Ave. B"]
    })

    address_map = {
        "St.": "Street",
        "Ave.": "Avenue",
        " Dr.": " Drive"  # 前にスペース含むパターンを想定
    }

    df_result = normalize_addresses(df_test, address_map=address_map)
    
    # City, StateName は変換辞書未指定なのでそのまま
    assert df_result.loc[0, "City"] == "RALEIGH"
    assert df_result.loc[0, "StateName"] == "VIRGINIA"

    # Address1, Address2 の部分置換検証
    assert df_result.loc[0, "Address1"] == "123 Street Drive"
    assert df_result.loc[0, "Address2"] == "Avenue B"

    print("SUCCESS: test_normalize_addresses_partial_address_replace passed")
