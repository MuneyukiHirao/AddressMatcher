import pytest
import pandas as pd
from data_ingestion import load_customer_data

def test_load_customer_data_valid(tmp_path):
    """
    正常系のテスト:
    想定どおりのカラムを持つCSVを用意し、読み込みが問題なく行われることを確認
    """
    # テスト用CSVファイルのパスを生成
    csv_file = tmp_path / "test_valid.csv"
    
    # テスト用CSVの内容を作成
    data = {
        "CustomerDisplayName": ["SampleCustomer1", "SampleCustomer2"],
        "locationname": ["Amelia Quarry", "Aggregates"],
        "DistributorName": ["Distributor1", "Distributor2"],
        "AccountNo": ["MARTI003", "54046"],
        "Address1": ["12301 Patrick Henry Hwy", "1000 WASHINGTON PIKE"],
        "Address2": ["", ""],
        "City": ["Amelia Court House", "BRIDGEVILLE"],
        "StateName": ["VIRGINIA", "PENNSYLVANIA"],
        "PostalCode": ["23002", "15017"],
        "CountryName": ["United States of America", "United States of America"]
    }
    df_test = pd.DataFrame(data)
    df_test.to_csv(csv_file, index=False)
    
    # 関数の呼び出し
    df_result = load_customer_data(str(csv_file))
    
    # DataFrame の行数・カラム数を検証
    assert len(df_result) == 2
    assert set(df_result.columns) == set(df_test.columns)

def test_load_customer_data_missing_file():
    """
    CSVファイルが存在しない場合、FileNotFoundError が発生することを確認
    """
    with pytest.raises(FileNotFoundError):
        load_customer_data("no_such_file.csv")

def test_load_customer_data_missing_columns(tmp_path):
    """
    必須カラムが不足している場合、ValueError が発生することを確認
    """
    # テスト用CSVファイルのパスを生成
    csv_file = tmp_path / "test_missing_columns.csv"
    
    # "CustomerDisplayName" カラムをあえて省略して書き出す
    data = {
        "locationname": ["Amelia Quarry"],
        "DistributorName": ["Distributor1"],
        "AccountNo": ["MARTI003"],
        "Address1": ["12301 Patrick Henry Hwy"],
        "Address2": [""],
        "City": ["Amelia Court House"],
        "StateName": ["VIRGINIA"],
        "PostalCode": ["23002"],
        "CountryName": ["United States of America"]
    }
    df_test = pd.DataFrame(data)
    df_test.to_csv(csv_file, index=False)
    
    with pytest.raises(ValueError) as exc_info:
        load_customer_data(str(csv_file))
    
    # エラーメッセージに欠落カラムの名前が含まれるか確認
    assert "CustomerDisplayName" in str(exc_info.value)
