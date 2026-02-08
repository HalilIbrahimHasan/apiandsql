import os
import requests
import pandas as pd
import plotly.express as px


API_URL = "https://talentifylabhealth.onrender.com/api/results"

# ✅ Option A (recommended): set env var first
# export TALENTIFYLAB_TOKEN="eyJhbGciOi..."
TOKEN = os.getenv("TALENTIFYLAB_TOKEN") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluMSIsInJvbGUiOiJBRE1JTiIsImV4cCI6MTc3MDE4Mjk0OCwiaWF0IjoxNzcwMDk2NTQ4fQ.bEQbjmu00IOVikTBrL5_7sFs9gvEUja50t79j134-7c"



def fetch_results(api_url=API_URL, token=TOKEN, timeout=90, retries=3):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            print(f"🔄 Attempt {attempt}/{retries}...")
            resp = requests.get(api_url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ReadTimeout as e:
            last_error = e
            print("⏳ Timeout… retrying")
        except requests.exceptions.RequestException:
            raise

    raise RuntimeError("API did not respond after retries") from last_error



def clean_results_to_df(payload: dict | list) -> pd.DataFrame:
    """
    Cleans API payload into a DataFrame.
    Handles common shapes:
      - list of results
      - {"results": [...]} or {"data": [...]}
    Tries to parse dates and numeric fields.
    """
    # Normalize payload shape
    if isinstance(payload, dict):
        if "results" in payload and isinstance(payload["results"], list):
            records = payload["results"]
        elif "data" in payload and isinstance(payload["data"], list):
            records = payload["data"]
        else:
            # fallback: treat dict as single record
            records = [payload]
    else:
        records = payload

    if not records:
        return pd.DataFrame()

    df = pd.json_normalize(records)

    # --- Guess common column names (safe + flexible) ---
    # date-like columns
    date_candidates = [c for c in df.columns if c.lower() in {"date", "created_at", "createdat", "result_date", "timestamp"}]
    if not date_candidates:
        # fallback: pick first column containing "date" or "time"
        date_candidates = [c for c in df.columns if ("date" in c.lower()) or ("time" in c.lower())]

    if date_candidates:
        date_col = date_candidates[0]
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    else:
        date_col = None

    # numeric-like columns (common: value, result, measured_value)
    numeric_candidates = [c for c in df.columns if c.lower() in {"value", "result", "measured_value", "lab_value"}]
    if not numeric_candidates:
        # fallback: any column that looks numeric after coercion (but skip IDs)
        possible = [c for c in df.columns if "id" not in c.lower()]
        best = None
        best_count = 0
        for c in possible:
            coerced = pd.to_numeric(df[c], errors="coerce")
            count = coerced.notna().sum()
            if count > best_count:
                best, best_count = c, count
        if best_count > 0:
            numeric_candidates = [best]

    value_col = numeric_candidates[0] if numeric_candidates else None
    if value_col:
        df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    # test-name column (common: test_type, testName)
    test_candidates = [c for c in df.columns if c.lower() in {"test_type", "testtype", "test_name", "testname", "analyte"}]
    test_col = test_candidates[0] if test_candidates else None

    # remove rows with no numeric values if value_col exists
    if value_col:
        df = df[df[value_col].notna()].copy()

    # sort by date if we have it
    if date_col:
        df = df.sort_values(date_col)

    # store metadata for plotting (optional)
    df.attrs["date_col"] = date_col
    df.attrs["value_col"] = value_col
    df.attrs["test_col"] = test_col

    return df


def plot_results(df: pd.DataFrame, title: str = "Patient Lab Results"):
    """Creates a convenient Plotly chart (line/scatter)."""
    if df.empty:
        print("No data returned from API.")
        return None

    date_col = df.attrs.get("date_col")
    value_col = df.attrs.get("value_col")
    test_col = df.attrs.get("test_col")

    if not value_col:
        raise ValueError(f"Could not infer numeric result column. Columns: {list(df.columns)}")

    # If no date, just index-based
    if not date_col:
        df = df.reset_index(drop=True)
        x = df.index
        x_label = "Record #"
    else:
        x = date_col
        x_label = date_col

    # If there are multiple test types, color by test
    if test_col and df[test_col].nunique() > 1:
        fig = px.line(
            df,
            x=x,
            y=value_col,
            color=test_col,
            markers=True,
            title=title,
            hover_data=[c for c in df.columns if c not in {value_col}],
        )
    else:
        fig = px.scatter(
            df,
            x=x,
            y=value_col,
            trendline=None,
            title=title,
            hover_data=[c for c in df.columns if c not in {value_col}],
        )

    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=value_col,
        legend_title=(test_col if test_col else "Series"),
    )

    fig.show()
    return fig


if __name__ == "__main__":
    payload = fetch_results()
    df = clean_results_to_df(payload)
    print("Rows:", len(df))
    print("Columns:", list(df.columns))
    plot_results(df, title="TalentifyLabHealth • Results")
