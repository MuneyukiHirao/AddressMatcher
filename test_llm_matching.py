import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from llm_matching import perform_llm_matching

def test_perform_llm_matching_basic():
    # テスト用データ（同じCity/Stateと想定）
    df_test = pd.DataFrame({
        "Address1": ["123 Main St", "123 Main Street", "456 Another Rd"],
        "Address2": ["", "", ""],
        "City": ["RALEIGH", "RALEIGH", "RALEIGH"],
        "StateName": ["NC", "NC", "NC"],
        "PostalCode": ["27601", "27601", "27605"],
        "CountryName": ["United States of America", "United States of America", "United States of America"]
    })

    # 想定するLLMの回答(JSON)
    # row 0,1 を G1 同一グループ、 row 2 を G2 と仮定
    mock_llm_response = '''
    [
      {"index": 0, "group_id": "G1"},
      {"index": 1, "group_id": "G1"},
      {"index": 2, "group_id": "G2"}
    ]
    '''

    # LLM呼び出し部分をモックし、上記の回答を返すようにする
    with patch("llm_matching.get_llm_client") as mock_get_client:
        mock_client_instance = MagicMock()
        mock_get_client.return_value = mock_client_instance
        
        # mock client の戻り値を設定
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = mock_llm_response
        
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        # 実行
        df_result = perform_llm_matching(df_test)

    # 検証
    assert "LLMGroupID" in df_result.columns
    assert df_result.loc[0, "LLMGroupID"] == "G1"
    assert df_result.loc[1, "LLMGroupID"] == "G1"
    assert df_result.loc[2, "LLMGroupID"] == "G2"

    print("SUCCESS: test_perform_llm_matching_basic passed")


def test_perform_llm_matching_json_error():
    """
    LLM から返された回答がJSONとしてパース不能な場合、フォールバックが動くかテスト。
    """
    df_test = pd.DataFrame({
        "Address1": ["A", "B"],
        "Address2": ["", ""],
        "City": ["CITY", "CITY"],
        "StateName": ["STATE", "STATE"],
        "PostalCode": ["12345", "12345"],
        "CountryName": ["USA", "USA"]
    })

    # JSONパースエラーを起こす回答をモック
    mock_llm_response = 'This is not valid JSON!!!'

    with patch("llm_matching.get_llm_client") as mock_get_client:
        mock_client_instance = MagicMock()
        mock_get_client.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = mock_llm_response
        
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        df_result = perform_llm_matching(df_test)

    # フォールバックとして全行にユニークな group_id を割り当て ( NoMatch_0, NoMatch_1 ) になる想定
    # 実装例では "Fallback_0", "Fallback_1" とか "NoMatch_0" など
    # perform_llm_matching の中身に合わせて確認
    # 現在の実装では "Fallback_{i}" を付与
    assert "LLMGroupID" in df_result.columns
    assert df_result.loc[0, "LLMGroupID"].startswith("Fallback_")
    assert df_result.loc[1, "LLMGroupID"].startswith("Fallback_")

    print("SUCCESS: test_perform_llm_matching_json_error passed")
