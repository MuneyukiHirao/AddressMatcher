# AddressMatcher

本プロジェクトは、**大規模言語モデル (LLM)** を活用して複数の代理店から寄せ集めた住所データをあいまいマッチングし、  
最終的に重複のない顧客マスタを再構築するための **サンプル実装** です。

以下のステップで構成されており、それぞれのモジュールが責務を分担しています:

1. **Data Ingestion**  
2. **Data Cleaning & Formatting**  
3. **Address Normalization**  
4. **Preliminary Grouping**  
5. **LLM Matching**  
6. **Review & Consolidation**  

最終的には、**`result.xlsx`** などの形式で統合後の顧客データを出力することを想定しています。

---

## ディレクトリ構成例

```text
AddressMatcher/
├── data_ingestion.py
├── data_cleaning_formatting.py
├── address_normalization.py
├── preliminary_grouping.py
├── llm_matching.py
├── review_consolidation.py
├── group_id_unifier.py
├── run_end_to_end.py
├── llm_prompt.txt
├── requirements.txt
└── tests/
    ├── test_data_ingestion.py
    ├── test_data_cleaning_formatting.py
    ├── test_address_normalization.py
    ├── test_preliminary_grouping.py
    ├── test_llm_matching.py
    ├── test_review_consolidation.py
    └── ...
```

> **Note**:  
> - **`customer_data.csv`** (200件などのデータ) は同ディレクトリ、または同階層に配置する想定です。  
> - **`.env`** に **`OPENAI_API_KEY`** を設定しておき、LLM 呼び出し時に利用します。

---

## セットアップ

1. **Python バージョン**  
   - Python 3.9 以上を推奨 (3.8 以下でも型アノテーション部分を調整すれば動く場合があります)

2. **仮想環境の作成 (任意)**  
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **依存パッケージのインストール**  
   ```bash
   pip install -r requirements.txt
   ```
   `requirements.txt` には以下のようなパッケージが含まれます:
   - `pandas`
   - `openai`
   - `python-dotenv`
   - `pytest`
   - など

4. **`.env` ファイルを用意**  
   ```bash
   # .env
   OPENAI_API_KEY=sk-xxxxxxxxxxxx
   ```

---

## モジュール概要

### data_ingestion.py

```python
def load_customer_data(file_path: str) -> pd.DataFrame:
    """
    CSV を読み込み、必須カラムのチェックを行う。
    """
```

- **CSV 読み込み**
- **カラム名のバリデーション**

---

### data_cleaning_formatting.py

```python
def clean_and_format_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    文字列の空白除去・大文字化・郵便番号の簡易フォーマットなど。
    """
```

- **余分な空白削除**
- **City / StateName の大文字化**
- **NULL/欠損の補完**

---

### address_normalization.py

```python
def normalize_addresses(
    df: pd.DataFrame,
    city_map: dict = None,
    state_map: dict = None,
    address_map: dict = None
) -> pd.DataFrame:
    """
    市区町村や州名の表記ゆれを辞書ベースで置換する。
    """
```

- **辞書ベースの表記ゆれ修正** (City, StateName, Address1/2 の略称など)

---

### preliminary_grouping.py

```python
def preliminary_grouping(
    df: pd.DataFrame,
    group_cols: List[str] = None,
    max_chunk_size: int = 50
) -> List[pd.DataFrame]:
    """
    Country × State × City などでグルーピングし、大きい場合はチャンクに分割。
    """
```

- **国・州・市でグループ化**
- **レコード数が多い場合はチャンク分割**

---

### llm_matching.py

```python
def perform_llm_matching(df: pd.DataFrame) -> pd.DataFrame:
    """
    LLM (o3-mini) を呼び出して、同一住所グループに G1, G2... を付与。
    JSON パース失敗時は Fallback_xxx を付与。
    """
```

- **チャンク単位で LLM に投げ、あいまいマッチング**
- **フォールバック**: JSON パース不可時に `"Fallback_xxx"` を付与

---

### group_id_unifier.py

```python
def unify_local_group_ids(
    df: pd.DataFrame,
    local_id_col: str = "LLMGroupID",
    global_id_col: str = "UnifiedGroupID",
    start_count: int = 1,
    prefix: str = "G"
) -> Tuple[pd.DataFrame, int]:
    """
    チャンク内で重複する G1, G2... をグローバルにユニークなIDに連番付け。
    """
```

- **チャンクごとに被る G1, G2, ... を連番で振り直し**
- **衝突しないグローバル ID へ変換**

---

### review_consolidation.py

```python
def review_and_consolidate(
    df: pd.DataFrame,
    suspicious_threshold: int = 50,
    mark_singleton: bool = False
) -> pd.DataFrame:
    """
    LLMGroupID ごとに件数を数え、大きすぎる or 小さすぎるグループにフラグ。
    最終的に FinalGroupID を確定する前の準備処理。
    """
```

- **LLMGroupID の分布を確認**
- **NeedsReview=True を付与** (フラグ付け)
- **実運用では UI などで分割 / 統合し、FinalGroupID を確定**

---

## 実行例: run_end_to_end.py

```python
def run_end_to_end(csv_path: str):
    """
    一連の処理を流して result.xlsx に結果出力。
    """
```

1. `load_customer_data` で CSV 取り込み  
2. `clean_and_format_data`, `normalize_addresses` で住所のクリーニング・正規化  
3. `preliminary_grouping` で小分け (max_chunk_size=50 など)  
4. `perform_llm_matching` で LLM 呼び出し → LLMGroupID 付与  
5. `unify_local_group_ids` でチャンク間の G1, G2... をグローバル連番化  
6. `review_and_consolidate` で NeedsReview を付けて人間レビュー準備  
7. 最終的に `result.xlsx` に出力

コマンドライン実行例:

```bash
python run_end_to_end.py
```

---

## テスト

```bash
pytest -v
```

- `tests/` フォルダに各モジュールのユニットテストを配置。
- LLM Matching 部分では **mock** を使って実際のトークン消費を避ける事例が含まれています。

---

## 注意事項

1. **LLM 応答の不確実性**  
   - JSON が壊れたり、誤ったグループ判定を下すことがあります。  
   - チャンクサイズを適切に設定し、**プロンプト (llm_prompt.txt) の文言強化**などで改善可能。

2. **国・州が欠損のケース**  
   - Preliminary Grouping 時に混在するかもしれません。前処理で埋めるか検討してください。

3. **大量データ (3万件等) におけるコスト**  
   - デフォルトのチャンクサイズ 50 でも十分大きい可能性あり。  
   - LLM モデルの速度・料金プランと要相談。

4. **UI レビュー**  
   - `review_and_consolidate` はあくまでフラグ付けの例示。  
   - 本番運用では人間が UI で最終修正するフローが必須です。

---

## ライセンス

本リポジトリのサンプルコードは MIT License (または同等の自由なライセンス) を想定しています。  
ただし、実運用には十分なテストや追加設計を行い、**自己責任**でご利用ください。

---

## 今後の展望

- **UI 開発**: NeedsReview が付いた住所グループを GUI 上で分割・統合  
- **外部API連携**: 郵便局や地理情報 API 等と連携して住所の正規化精度を高める  
- **大規模化**: Spark / Dask 等の分散処理基盤を使い、さらにスケールさせる  
