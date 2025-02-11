import pandas as pd
from typing import Optional

def load_customer_data(file_path: str) -> pd.DataFrame:
    """
    CSVファイルを読み込み、DataFrameとして返す。

    Parameters:
        file_path (str): 読み込むCSVファイルのパス

    Returns:
        pd.DataFrame: CSVの内容をDataFrameに格納したもの

    Raises:
        FileNotFoundError: 指定されたパスにファイルが存在しない場合
        ValueError: カラムが足りないなど、想定外の形式の場合
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}") from e
    
    # 想定するカラム一覧（必要に応じて調整）
    required_columns = [
        "CustomerDisplayName",
        "locationname",
        "DistributorName",
        "AccountNo",
        "Address1",
        "Address2",
        "City",
        "StateName",
        "PostalCode",
        "CountryName"
    ]
    
    # 必須カラムがそろっているか確認
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"必須カラムが不足しています: {missing_columns}")
    
    return df
