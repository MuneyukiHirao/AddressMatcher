import pandas as pd

def normalize_addresses(
    df: pd.DataFrame,
    city_map: dict = None,
    state_map: dict = None,
    address_map: dict = None
) -> pd.DataFrame:
    """
    住所レコード（City, StateName, Address1, Address2）の表記ゆれを
    辞書ベースで正規化する。

    Parameters:
        df (pd.DataFrame): DataFrame (すでにCleaning/Formatting済みを想定)
        city_map (dict): { "RALIEGH": "RALEIGH", ... } のようなCityName修正用マップ
        state_map (dict): { "VA": "VIRGINIA", ... } のようなStateName修正用マップ
        address_map (dict): { "St.": "Street", ... } のようなAddress修正用マップ

    Returns:
        pd.DataFrame: 正規化後のDataFrame
    """
    df = df.copy()

    if city_map is None:
        city_map = {}
    if state_map is None:
        state_map = {}
    if address_map is None:
        address_map = {}

    # 1. CityName の変換
    if "City" in df.columns:
        df["City"] = df["City"].apply(lambda x: city_map[x] if x in city_map else x)

    # 2. StateName の変換
    if "StateName" in df.columns:
        df["StateName"] = df["StateName"].apply(lambda x: state_map[x] if x in state_map else x)

    # 3. Address1, Address2 の一括変換（辞書内のキーが含まれていれば置換）
    #    ※ ここでは単純に "St." → "Street" などの部分置換を想定
    if "Address1" in df.columns:
        df["Address1"] = df["Address1"].apply(lambda x: _replace_address_text(x, address_map))
    if "Address2" in df.columns:
        df["Address2"] = df["Address2"].apply(lambda x: _replace_address_text(x, address_map))

    return df

def _replace_address_text(text: str, addr_map: dict) -> str:
    """
    部分文字列の置換を連続的に適用するヘルパー関数
    例: "1234 Main St." -> "1234 Main Street"
    """
    for k, v in addr_map.items():
        text = text.replace(k, v)
    return text
