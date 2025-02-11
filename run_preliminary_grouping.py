import pandas as pd
from data_ingestion import load_customer_data
from data_cleaning_formatting import clean_and_format_data
from address_normalization import normalize_addresses
from preliminary_grouping import preliminary_grouping

def run_preliminary_grouping(csv_path: str):
    """
    customer_data.csvを読み込み、クリーニング・正規化を経て
    Preliminary Grouping を行い、グループ数と各チャンクの件数を出力する。
    ただし、グループ内のレコード数が2件以上の場合のみ表示する。
    """
    # 1. データ読み込み (Data Ingestion)
    df_raw = load_customer_data(csv_path)

    # 2. クリーニング (Data Cleaning & Formatting)
    df_cleaned = clean_and_format_data(df_raw)

    # 3. 住所の簡易正規化 (Address Normalization)
    city_map = {
        "RALIEGH": "RALEIGH",
        # 必要に応じて表記ゆれを追加
    }
    state_map = {
        "VA": "VIRGINIA",
        # 必要に応じて追加
    }
    address_map = {
        "St.": "Street",
        # 必要に応じて追加
    }
    df_normalized = normalize_addresses(
        df_cleaned,
        city_map=city_map,
        state_map=state_map,
        address_map=address_map
    )

    # 4. グルーピング
    sub_dfs = preliminary_grouping(df_normalized, max_chunk_size=50)

    # 5. 結果確認
    print(f"Total Groups (including chunk splits): {len(sub_dfs)}")
    displayed_count = 0

    for i, sub_df in enumerate(sub_dfs, start=1):
        if len(sub_df) >= 2:
            displayed_count += 1
#            print(f"--- Group {i} ---")
#            print(f"Record Count: {len(sub_df)}")
            # 先頭数行だけ表示
#            print(sub_df.head(3))
#            print()

    print(f"Displayed groups (with 2+ records): {displayed_count}")

    return sub_dfs

if __name__ == "__main__":
    # 実行例: python run_preliminary_grouping.py
    csv_file_path = "customer_data.csv"  # 200件程度のデータが格納されている想定
    grouped_dataframes = run_preliminary_grouping(csv_file_path)
