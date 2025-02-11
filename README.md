
# AddressMatcher

This project demonstrates how to use a Large Language Model (LLM) to aggregate and unify address data from multiple distributors, ultimately creating a deduplicated customer master. The workflow is organized into the following modules:

1. **Data Ingestion**  
2. **Data Cleaning & Formatting**  
3. **Address Normalization**  
4. **Preliminary Grouping**  
5. **LLM Matching**  
6. **Review & Consolidation**

After processing, it can output the final unified dataset (for instance, in **result.xlsx**).

---

## Directory Structure (Example)

```
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

Place your **`customer_data.csv`** (around 200 rows, for example) in the same directory or an appropriate path. The main script **`run_end_to_end.py`** orchestrates the entire workflow.

---

## Setup

1. **Python Version**  
   Recommended Python 3.9 or above (older versions might require adjustments to typing annotations).

2. **Create a Virtual Environment (Optional)**

\`\`\`bash
python -m venv venv
source venv/bin/activate
\`\`\`

3. **Install Dependencies**

\`\`\`bash
pip install -r requirements.txt
\`\`\`

Contents of `requirements.txt` might include:
- `pandas`
- `openai`
- `python-dotenv`
- `pytest`
- ... etc.

4. **Set up .env**

\`\`\`bash
# .env
OPENAI_API_KEY=sk-xxxxxx
\`\`\`

---

## Modules Overview

### data_ingestion.py

\`\`\`python
def load_customer_data(file_path: str) -> pd.DataFrame:
    """
    Reads a CSV, validates mandatory columns, and returns a DataFrame.
    """
\`\`\`

- Loads the CSV data.
- Checks required columns.

### data_cleaning_formatting.py

\`\`\`python
def clean_and_format_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans up whitespace, unifies casing, and applies simple postal code formatting.
    """
\`\`\`

- Removes extra whitespace
- Normalizes City / StateName casing
- Handles missing values

### address_normalization.py

\`\`\`python
def normalize_addresses(
    df: pd.DataFrame,
    city_map: dict = None,
    state_map: dict = None,
    address_map: dict = None
) -> pd.DataFrame:
    """
    Applies dictionary-based normalization of city names, state names, etc.
    """
\`\`\`

- Dictionary-based string replacements
- Fixes common abbreviations or alternate spellings

### preliminary_grouping.py

\`\`\`python
def preliminary_grouping(
    df: pd.DataFrame,
    group_cols: List[str] = None,
    max_chunk_size: int = 50
) -> List[pd.DataFrame]:
    """
    Groups by columns (e.g., Country, State, City) and splits large groups into chunks.
    """
\`\`\`

- Groups by Country / State / City
- If a group exceeds a certain size, it is split into multiple chunks for easier processing

### llm_matching.py

\`\`\`python
def perform_llm_matching(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calls the LLM (o3-mini) to assign group IDs (G1, G2, etc.) for potential duplicates.
    """
\`\`\`

- Submits a chunk of address rows to the LLM
- Expects JSON output with index-to-group mapping
- If parsing fails, uses a fallback ID

### group_id_unifier.py

\`\`\`python
def unify_local_group_ids(
    df: pd.DataFrame,
    local_id_col: str = "LLMGroupID",
    global_id_col: str = "UnifiedGroupID",
    start_count: int = 1,
    prefix: str = "G"
) -> Tuple[pd.DataFrame, int]:
    """
    Ensures globally unique group IDs across multiple chunks.
    """
\`\`\`

- The LLM might reuse "G1" in multiple chunks
- This module converts each chunk's local IDs to a set of globally unique IDs

### review_consolidation.py

\`\`\`python
def review_and_consolidate(
    df: pd.DataFrame,
    suspicious_threshold: int = 50,
    mark_singleton: bool = False
) -> pd.DataFrame:
    """
    Flags extremely large groups (>= threshold) or certain edge cases for human review.
    """
\`\`\`

- Aggregates by group ID
- Marks suspicious groups with `NeedsReview`
- Allows for splitting/merging groups later

---

## End-to-End Execution: run_end_to_end.py

\`\`\`python
def run_end_to_end(csv_path: str):
    """
    Conducts the entire flow and exports the final DataFrame as result.xlsx.
    """
\`\`\`

1. Load CSV (`load_customer_data`)
2. Clean & format addresses (`clean_and_format_data`), then normalize (`normalize_addresses`)
3. Group by Country/State/City (`preliminary_grouping`) and split into sub-DataFrames
4. For each chunk, call `perform_llm_matching` to assign group IDs
5. Convert local group IDs to unique global IDs via `unify_local_group_ids`
6. Combine all chunks, run `review_and_consolidate`
7. Output **`result.xlsx`**

Example CLI usage:

\`\`\`bash
python run_end_to_end.py
\`\`\`

Make sure you have an `.env` file containing your API key.

---

## Testing

Use **pytest**:

\`\`\`bash
pytest -v
\`\`\`

The `tests/` directory contains unit tests for each module. Note that the LLM Matching tests may employ mocks to avoid actual token usage.

---

## Notes & Caveats

- **LLM JSON Output** can be inconsistent or truncated. Fine-tuning the prompt (in `llm_prompt.txt`) and adjusting chunk sizes can help.
- **Data with Missing Country/State** might be grouped incorrectly. Pre-processing or manual review is advised.
- **Large-scale Data** (e.g., 30k rows) requires grouping to control LLM call frequency. Further optimization (e.g., similarity-based filters) may be necessary.
- A manual **Review & Consolidation** step is essential to catch false positives/negatives from the LLM.

---

## License

This sample is offered under an MIT-like license. Please test thoroughly and adapt to your own use cases at your own responsibility.

---
```
