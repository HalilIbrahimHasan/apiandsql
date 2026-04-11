import pandas as pd
import requests
from sqlalchemy import create_engine, text

# -----------------------------
# 1) CONFIG
# -----------------------------
BASE_URL = "https://talentifylabhealth.onrender.com"

DB_URL = (
    "postgresql://healthdb_oqr5_user:b5APz6meYG6RNDB6G9mbSYXJ1c72mLVe"
    "@dpg-d799o4hr0fns73ed7e40-a.oregon-postgres.render.com/healthdb_oqr5"
    "?sslmode=require"
)

USERNAME = "admin1"
PASSWORD = "Admin123"

engine = create_engine(DB_URL, pool_pre_ping=True)


# -----------------------------
# 2) AUTH
# -----------------------------
def get_token():
    url = f"{BASE_URL}/api/auth/login"

    credentials = {
        "username": USERNAME,
        "password": PASSWORD
    }

    resp = requests.post(url, json=credentials)
    resp.raise_for_status()

    return resp.json()["token"]


# -----------------------------
# 3) EXTRACT
# -----------------------------
def get_invoices_data():
    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{BASE_URL}/api/billing/invoices",
        headers=headers
    )

    print("Invoices status:", response.status_code)
    response.raise_for_status()

    return response.json()


# -----------------------------
# 4) TRANSFORM
# -----------------------------
def prepare_invoices_df(data):
    df = pd.DataFrame(data)

    print("Columns:", df.columns.tolist())
    print(df.head(3))

    # WHY: normalize columns
    df.columns = df.columns.str.strip().str.lower()

    # WHY: make sure needed columns exist
    needed_cols = ["id", "status", "total", "created_at", "updated_at"]
    for col in needed_cols:
        if col not in df.columns:
            df[col] = None

    # WHY: created_at datetime for trend analysis
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")

    # WHY: status normalized
    df["status"] = df["status"].astype(str).str.strip().str.lower()

    # WHY: total numeric for sums
    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0.0)

    # WHY: id cleanup
    df["id"] = df["id"].astype(str).str.strip()
    df.loc[df["id"].isin(["", "nan", "None", "null"]), "id"] = None

    before_count = len(df)

    df = df.dropna(subset=["id"]).copy()
    df = df.drop_duplicates(subset=["id"], keep="first").copy()

    after_count = len(df)

    print(f"Rows before cleanup: {before_count}")
    print(f"Rows after cleanup: {after_count}")

    return df


# -----------------------------
# 5) VALIDATE
# -----------------------------
def validate_invoices_df(df):
    if df.empty:
        raise Exception("Invoices dataframe is empty")

    if "id" not in df.columns:
        raise Exception("Missing id column")

    if df["id"].isna().sum() > 0:
        raise Exception("Invoices id still contains null values")


# -----------------------------
# 6) LOAD - CREATE TABLE
# -----------------------------
def create_invoices_table():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS invoices_curated (
                id TEXT PRIMARY KEY,
                status TEXT,
                total NUMERIC,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))


# -----------------------------
# 7) LOAD - INSERT / UPSERT
# -----------------------------
def load_invoices(df):
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO invoices_curated (
                    id, status, total, created_at, updated_at
                )
                VALUES (
                    :id, :status, :total, :created_at, :updated_at
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    status = EXCLUDED.status,
                    total = EXCLUDED.total,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at,
                    load_ts = CURRENT_TIMESTAMP;
            """), {
                "id": row["id"],
                "status": row["status"],
                "total": row["total"],
                "created_at": row["created_at"].to_pydatetime() if pd.notna(row["created_at"]) else None,
                "updated_at": row["updated_at"].to_pydatetime() if pd.notna(row["updated_at"]) else None,
            })

    print(f"Loaded {len(df)} invoice rows into DB")


# -----------------------------
# 8) MAIN
# -----------------------------
def main():
    print("Starting invoice ETL...")

    # Extract
    invoices_data = get_invoices_data()

    # Transform
    invoices_df = prepare_invoices_df(invoices_data)

    # Validate
    validate_invoices_df(invoices_df)

    # Load
    create_invoices_table()
    load_invoices(invoices_df)

    print("Invoice ETL completed successfully")


if __name__ == "__main__":
    main()