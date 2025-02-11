import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

def get_llm_client():
    """
    .env から OPENAI_API_KEY を読み込み、OpenAI クライアントを返す。
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in environment (OPENAI_API_KEY).")
    return OpenAI(api_key=api_key)

def perform_llm_matching(df: pd.DataFrame) -> pd.DataFrame:
    """
    与えられた DataFrame(1グループ or 1チャンク) を LLM に渡し、
    その中で「どの行が同一住所か」をグルーピングする。
    LLM には外部ファイル llm_prompt.txt を使ってプロンプトを指定。
    JSON 形式で (row_index -> group_id) を返してもらい、結果を DataFrame に反映。

    - "Fallback_xxx" が付く場合は、JSON パースに失敗したフォールバック。
    """

    # 1件以下ならLLM呼び出し不要
    if len(df) <= 1:
        df = df.copy()
        df["LLMGroupID"] = [f"Single_{i}" for i in range(len(df))]
        return df

    client = get_llm_client()

    # address_block を組み立て
    address_list_str = []
    for i, row in df.iterrows():
        address_list_str.append(
            f"Index:{i}, Address1:{row.get('Address1','')}, "
            f"Address2:{row.get('Address2','')}, City:{row.get('City','')}, "
            f"State:{row.get('StateName','')}, Zip:{row.get('PostalCode','')}, "
            f"Country:{row.get('CountryName','')}"
        )
    address_block = "\n".join(address_list_str)

    # llm_prompt.txt 読み込み
    with open("llm_prompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # (A) .replace を使って、{address_block} 部分だけ置換
    user_prompt = prompt_template.replace("{address_block}", address_block)

    # LLM呼び出し
    response = client.chat.completions.create(
        model="o3-mini",
        reasoning_effort="medium",
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    raw_answer = response.choices[0].message.content.strip()

    # JSON パースを試みる
    df_result = df.copy()
    df_result["LLMGroupID"] = None
    try:
        match_list = json.loads(raw_answer)  # JSONデコード
        # match_list は [{"index": int, "group_id": str}, ...] のはず
        group_map = {}
        for item in match_list:
            idx = item["index"]
            gid = item["group_id"]
            group_map[idx] = gid

        # DataFrame に反映
        for i in df_result.index:
            if i in group_map:
                df_result.at[i, "LLMGroupID"] = group_map[i]
            else:
                df_result.at[i, "LLMGroupID"] = f"Fallback_{i}"

    except (json.JSONDecodeError, KeyError, TypeError):
        # JSON不正やキー不足 → フォールバック
        for i in df_result.index:
            df_result.at[i, "LLMGroupID"] = f"Fallback_{i}"

    return df_result
