import pandas as pd
import re

def clean_and_format_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrame内の住所データをクリーニングし、フォーマットを統一する。
    - 余分な空白の除去
    - City/StateName の大文字化
    - CountryName が空の場合は "United States of America" を補完
    - PostalCode の簡易フォーマット修正 (5桁または 5桁-4桁を想定)
    """
    df = df.copy()

    # 1. 文字列カラムの両端の空白除去
    str_columns = [
        "CustomerDisplayName", "locationname", "DistributorName",
        "AccountNo", "Address1", "Address2", "City", "StateName",
        "PostalCode", "CountryName"
    ]
    for col in str_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 2. City, StateName を大文字化
    if "City" in df.columns:
        df["City"] = df["City"].str.upper()
    if "StateName" in df.columns:
        df["StateName"] = df["StateName"].str.upper()

    # 3. CountryName が空の場合は補完
    if "CountryName" in df.columns:
        df["CountryName"] = df["CountryName"].replace("", None)
        df["CountryName"] = df["CountryName"].fillna("United States of America")

    # 4. PostalCode の簡易フォーマット修正
    if "PostalCode" in df.columns:
        df["PostalCode"] = df["PostalCode"].apply(_normalize_postal_code)

    return df

def _normalize_postal_code(postal_code: str) -> str:
    """
    簡易的に郵便番号を整形する関数。
    - 入力が 5桁数字 or 5桁-4桁数字ならそのまま
    - 上記でない場合は、そのまま返す
    """
    postal_code = postal_code.strip()
    import re
    # 5桁（数字のみ）
    if re.match(r'^\d{5}$', postal_code):
        return postal_code
    # 5桁-4桁
    if re.match(r'^\d{5}-\d{4}$', postal_code):
        return postal_code

    return postal_code
