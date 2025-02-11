import pytest
import pandas as pd
from data_cleaning_formatting import clean_and_format_data

def test_clean_and_format_data_normal():
    """
    正常系テスト:
    - 空白除去
    - City/StateName の大文字化
    - CountryName 空の場合の補完
    - 郵便番号の簡易フォーマット
    """
    test_data = {
        "CustomerDisplayName": [" SampleCustomer1 "],
        "locationname": ["  Amelia Quarry  "],
        "DistributorName": [" Distributor1"],
        "AccountNo": ["MARTI003 "],
        "Address1": [" 12301 Patrick Henry Hwy "],
        "Address2": [" "],
        "City": ["  raLeigh  "],
        "StateName": [" vA "],
        "PostalCode": [" 27622-0013 "],
        "CountryName": [""]  # 空文字(補完対象)
    }
    df_test = pd.DataFrame(test_data)
    
    df_cleaned = clean_and_format_data(df_test)

    # アサーション
    assert df_cleaned.loc[0, "CustomerDisplayName"] == "SampleCustomer1"
    assert df_cleaned.loc[0, "locationname"] == "Amelia Quarry"
    assert df_cleaned.loc[0, "DistributorName"] == "Distributor1"
    assert df_cleaned.loc[0, "AccountNo"] == "MARTI003"
    assert df_cleaned.loc[0, "Address1"] == "12301 Patrick Henry Hwy"
    assert df_cleaned.loc[0, "Address2"] == ""  # strip()で空白だけだったら空文字
    assert df_cleaned.loc[0, "City"] == "RALEIGH"  # 大文字化
    assert df_cleaned.loc[0, "StateName"] == "VA"  # 大文字化
    assert df_cleaned.loc[0, "PostalCode"] == "27622-0013"
    assert df_cleaned.loc[0, "CountryName"] == "United States of America"

    print("SUCCESS: test_clean_and_format_data_normal passed")


def test_clean_and_format_data_postal_code():
    """
    郵便番号が5桁、5桁-4桁以外の場合の動作を確認
    """
    test_data = {
        "CustomerDisplayName": ["SampleCustomer1"],
        "locationname": ["Quarry"],
        "DistributorName": ["Distributor1"],
        "AccountNo": ["MARTI003"],
        "Address1": ["12301 Patrick Henry Hwy"],
        "Address2": [""],
        "City": ["RALEIGH"],
        "StateName": ["NC"],
        "PostalCode": ["ABC-1234"],  # 不正フォーマット
        "CountryName": ["United States of America"]
    }
    df_test = pd.DataFrame(test_data)
    
    df_cleaned = clean_and_format_data(df_test)
    # 今回はフォーマット変換できず、そのまま残る想定
    assert df_cleaned.loc[0, "PostalCode"] == "ABC-1234"

    print("SUCCESS: test_clean_and_format_data_postal_code passed")

# 下記テストは削除またはコメントアウト
# def test_clean_and_format_data_missing_columns():
#     """
#     カラムが不足している場合、clean_and_format_dataは想定外入力なので、
#     実際にはData Ingestionで弾く設計。
#     ここではテストしない or 削除する。
#     """
#     pass
