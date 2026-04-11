import requests
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime


# =========================================================
# CONFIG
# =========================================================
BASE_URL = "https://talentifylabhealth.onrender.com"

DB_URL = (
    "postgresql://healthdb_oqr5_user:b5APz6meYG6RNDB6G9mbSYXJ1c72mLVe"
    "@dpg-d799o4hr0fns73ed7e40-a.oregon-postgres.render.com/healthdb_oqr5"
    "?sslmode=require"
)

USERNAME = "admin1"
PASSWORD = "Admin123"

engine = create_engine(DB_URL, pool_pre_ping=True)


# =========================================================
# HELPERS
# =========================================================
def log(message: str) -> None:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {message}")


def safe_value(value):
    if pd.isna(value):
        return None
    return value


def debug_dataframe(df: pd.DataFrame, dataset_name: str) -> None:
    log(f"{dataset_name} columns: {list(df.columns)}")
    if not df.empty:
        try:
            log(f"{dataset_name} first 3 rows:\n{df.head(3).to_string()}")
        except Exception:
            log(f"{dataset_name} preview could not be printed")


def resolve_primary_key(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    df = df.copy()

    candidate_keys = [
        "id",
        "order_id",
        "result_id",
        "invoice_id",
        "uuid",
        "_id",
    ]

    found_key = None

    for col in candidate_keys:
        if col in df.columns:
            temp = df[col].copy()
            temp = temp.astype(str).str.strip()
            temp = temp.replace(["", "nan", "None", "null"], pd.NA)

            non_null_count = temp.notna().sum()
            if non_null_count > 0:
                found_key = col
                break

    if not found_key:
        raise Exception(
            f"{dataset_name}: no usable primary key found. Available columns: {list(df.columns)}"
        )

    log(f"{dataset_name}: using primary key column '{found_key}'")

    df["pk_id"] = df[found_key].astype(str).str.strip()
    df.loc[df["pk_id"].isin(["", "nan", "None", "null"]), "pk_id"] = None

    before_count = len(df)

    null_count = df["pk_id"].isna().sum()
    if null_count > 0:
        log(f"{dataset_name}: dropping {null_count} rows with null pk_id")
        df = df.dropna(subset=["pk_id"]).copy()

    duplicate_count = df["pk_id"].duplicated().sum()
    if duplicate_count > 0:
        log(f"{dataset_name}: dropping {duplicate_count} duplicate pk_id rows")
        df = df.drop_duplicates(subset=["pk_id"], keep="first").copy()

    after_count = len(df)
    log(f"{dataset_name}: row count before pk cleanup={before_count}, after={after_count}")

    if df.empty:
        raise Exception(f"{dataset_name}: empty after pk cleanup using '{found_key}'")

    return df


# =========================================================
# AUTH
# =========================================================
def login_session() -> requests.Session:
    session = requests.Session()

    login_url = f"{BASE_URL}/login"
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
    }

    log(f"Logging in at {login_url}")
    response = session.post(login_url, data=payload, timeout=30, allow_redirects=True)
    log(f"Login status: {response.status_code}")

    if response.status_code not in [200, 302]:
        raise Exception(f"Login failed. status={response.status_code} body={response.text[:300]}")

    return session


# =========================================================
# EXTRACT
# =========================================================
def fetch_data(session: requests.Session, dataset_name: str) -> pd.DataFrame:
    candidates = [
        f"{BASE_URL}/api/{dataset_name}",
        f"{BASE_URL}/api/v1/{dataset_name}",
        f"{BASE_URL}/{dataset_name}",
    ]

    last_error = None

    for url in candidates:
        try:
            log(f"Trying {url}")
            response = session.get(url, timeout=30)
            log(f"Status for {dataset_name}: {response.status_code}")

            if response.status_code == 401:
                last_error = f"{url} -> unauthorized"
                continue

            if response.status_code != 200:
                last_error = f"{url} -> status={response.status_code} body={response.text[:250]}"
                continue

            data = response.json()

            if isinstance(data, list):
                df = pd.DataFrame(data)
                log(f"{dataset_name}: fetched {len(df)} rows from {url}")
                return df

            if isinstance(data, dict):
                if "data" in data and isinstance(data["data"], list):
                    df = pd.DataFrame(data["data"])
                    log(f"{dataset_name}: fetched {len(df)} rows from {url}")
                    return df

                df = pd.DataFrame([data])
                log(f"{dataset_name}: fetched {len(df)} rows from {url}")
                return df

            last_error = f"{url} -> unsupported JSON structure"

        except Exception as exc:
            last_error = f"{url} -> {exc}"

    raise Exception(f"No valid endpoint found for {dataset_name}. Last error: {last_error}")


# =========================================================
# TRANSFORM
# =========================================================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip().lower() for col in df.columns]
    return df


def ensure_columns(df: pd.DataFrame, required_columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    return df


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    df = ensure_columns(
        df,
        [
            "id",
            "order_id",
            "patient_id",
            "doctor_id",
            "test_type",
            "status",
            "performed_by_name",
            "created_at",
            "updated_at",
        ],
    )
    df = resolve_primary_key(df, "orders")
    return df


def transform_invoices(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    df = ensure_columns(
        df,
        [
            "id",
            "invoice_id",
            "order_id",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ],
    )
    df = resolve_primary_key(df, "invoices")
    return df


def transform_results(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    df = ensure_columns(
        df,
        [
            "id",
            "result_id",
            "order_id",
            "result_value",
            "result_status",
            "critical_flag",
            "performed_by_name",
            "created_at",
            "updated_at",
        ],
    )
    df = resolve_primary_key(df, "results")
    return df


# =========================================================
# VALIDATIONS
# =========================================================
def validate_not_empty(df: pd.DataFrame, dataset_name: str) -> None:
    if df.empty:
        raise Exception(f"{dataset_name} dataset is empty")


def validate_required_id(df: pd.DataFrame, dataset_name: str) -> None:
    if "pk_id" not in df.columns:
        raise Exception(f"{dataset_name} missing pk_id column")

    if df["pk_id"].isna().sum() > 0:
        raise Exception(f"{dataset_name}.pk_id still contains null values")


# =========================================================
# LOAD - DDL
# =========================================================
def create_tables() -> None:
    log("Creating tables if not exist")

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders_curated (
                id TEXT PRIMARY KEY,
                patient_id TEXT,
                doctor_id TEXT,
                test_type TEXT,
                status TEXT,
                performed_by_name TEXT,
                created_at TEXT,
                updated_at TEXT,
                load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS invoices_curated (
                id TEXT PRIMARY KEY,
                order_id TEXT,
                amount NUMERIC,
                status TEXT,
                created_at TEXT,
                updated_at TEXT,
                load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS results_curated (
                id TEXT PRIMARY KEY,
                order_id TEXT,
                result_value TEXT,
                result_status TEXT,
                critical_flag TEXT,
                performed_by_name TEXT,
                created_at TEXT,
                updated_at TEXT,
                load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS etl_run_audit (
                run_id BIGSERIAL PRIMARY KEY,
                dataset_name TEXT,
                row_count INTEGER,
                load_status TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))


# =========================================================
# LOAD - AUDIT
# =========================================================
def insert_audit(
    dataset_name: str,
    row_count: int,
    load_status: str,
    error_message: str = None
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO etl_run_audit (dataset_name, row_count, load_status, error_message)
                VALUES (:dataset_name, :row_count, :load_status, :error_message)
            """),
            {
                "dataset_name": dataset_name,
                "row_count": row_count,
                "load_status": load_status,
                "error_message": error_message,
            }
        )


# =========================================================
# LOAD - UPSERT
# =========================================================
def load_orders(df: pd.DataFrame) -> None:
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO orders_curated (
                    id, patient_id, doctor_id, test_type, status,
                    performed_by_name, created_at, updated_at
                )
                VALUES (
                    :id, :patient_id, :doctor_id, :test_type, :status,
                    :performed_by_name, :created_at, :updated_at
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    patient_id = EXCLUDED.patient_id,
                    doctor_id = EXCLUDED.doctor_id,
                    test_type = EXCLUDED.test_type,
                    status = EXCLUDED.status,
                    performed_by_name = EXCLUDED.performed_by_name,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at,
                    load_ts = CURRENT_TIMESTAMP
            """), {
                "id": str(safe_value(row.get("pk_id"))),
                "patient_id": safe_value(row.get("patient_id")),
                "doctor_id": safe_value(row.get("doctor_id")),
                "test_type": safe_value(row.get("test_type")),
                "status": safe_value(row.get("status")),
                "performed_by_name": safe_value(row.get("performed_by_name")),
                "created_at": safe_value(row.get("created_at")),
                "updated_at": safe_value(row.get("updated_at")),
            })


def load_invoices(df: pd.DataFrame) -> None:
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO invoices_curated (
                    id, order_id, amount, status, created_at, updated_at
                )
                VALUES (
                    :id, :order_id, :amount, :status, :created_at, :updated_at
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    order_id = EXCLUDED.order_id,
                    amount = EXCLUDED.amount,
                    status = EXCLUDED.status,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at,
                    load_ts = CURRENT_TIMESTAMP
            """), {
                "id": str(safe_value(row.get("pk_id"))),
                "order_id": safe_value(row.get("order_id")),
                "amount": safe_value(row.get("amount")),
                "status": safe_value(row.get("status")),
                "created_at": safe_value(row.get("created_at")),
                "updated_at": safe_value(row.get("updated_at")),
            })


def load_results(df: pd.DataFrame) -> None:
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO results_curated (
                    id, order_id, result_value, result_status, critical_flag,
                    performed_by_name, created_at, updated_at
                )
                VALUES (
                    :id, :order_id, :result_value, :result_status, :critical_flag,
                    :performed_by_name, :created_at, :updated_at
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    order_id = EXCLUDED.order_id,
                    result_value = EXCLUDED.result_value,
                    result_status = EXCLUDED.result_status,
                    critical_flag = EXCLUDED.critical_flag,
                    performed_by_name = EXCLUDED.performed_by_name,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at,
                    load_ts = CURRENT_TIMESTAMP
            """), {
                "id": str(safe_value(row.get("pk_id"))),
                "order_id": safe_value(row.get("order_id")),
                "result_value": safe_value(row.get("result_value")),
                "result_status": safe_value(row.get("result_status")),
                "critical_flag": safe_value(row.get("critical_flag")),
                "performed_by_name": safe_value(row.get("performed_by_name")),
                "created_at": safe_value(row.get("created_at")),
                "updated_at": safe_value(row.get("updated_at")),
            })


# =========================================================
# PROCESS
# =========================================================
def process_dataset(session: requests.Session, dataset_name: str, transform_func, load_func) -> None:
    try:
        df = fetch_data(session, dataset_name)
        debug_dataframe(df, dataset_name)

        df = transform_func(df)

        validate_not_empty(df, dataset_name)
        validate_required_id(df, dataset_name)

        load_func(df)
        insert_audit(dataset_name, len(df), "SUCCESS")
        log(f"{dataset_name} loaded successfully: {len(df)} rows")

    except Exception as exc:
        insert_audit(dataset_name, 0, "FAILED", str(exc))
        log(f"{dataset_name} failed: {exc}")


# =========================================================
# MAIN
# =========================================================
def main() -> None:
    log("Starting ETL pipeline")
    create_tables()

    session = login_session()

    process_dataset(session, "orders", transform_orders, load_orders)
    process_dataset(session, "invoices", transform_invoices, load_invoices)
    process_dataset(session, "results", transform_results, load_results)

    log("ETL pipeline finished")


if __name__ == "__main__":
    main()