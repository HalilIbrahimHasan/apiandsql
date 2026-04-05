import os
import requests
import pandas as pd
import plotly.express as px

# =========================
# API CONFIG
# =========================
BASE_URL = os.getenv("HEALTH_API_BASE_URL", "https://talentifylabhealth.onrender.com")
USERNAME = os.getenv("HEALTH_API_USERNAME", "admin1")
PASSWORD = os.getenv("HEALTH_API_PASSWORD", "Admin123")

LOGIN_URL = f"{BASE_URL}/api/auth/login"
ORDERS_URL = f"{BASE_URL}/api/orders"
RESULTS_URL = f"{BASE_URL}/api/results"
INVOICES_URL = f"{BASE_URL}/api/billing/invoices"
PATIENTS_URL = f"{BASE_URL}/api/patients"
TEST_TYPES_URL = f"{BASE_URL}/api/tests/types"
USERS_URL = f"{BASE_URL}/api/users"


# =========================
# API HELPERS
# =========================
def login_session() -> requests.Session:
    session = requests.Session()
    resp = session.post(
        LOGIN_URL,
        json={"username": USERNAME, "password": PASSWORD},
        timeout=60
    )
    resp.raise_for_status()

    body = resp.json()
    token = body.get("token")
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})

    return session


def fetch_json(session: requests.Session, url: str):
    resp = session.get(url, timeout=60)
    resp.raise_for_status()
    return resp.json()


# =========================
# DATAFRAME PREP
# =========================
def to_df(payload) -> pd.DataFrame:
    if isinstance(payload, list):
        return pd.DataFrame(payload)
    if isinstance(payload, dict):
        return pd.DataFrame([payload])
    return pd.DataFrame()


def ensure_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA
    return df


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = ensure_columns(df, [
        "order_id", "patient_user_id", "ordered_by_doctor_id",
        "ordered_at", "priority", "status", "notes"
    ])
    df = df.copy()
    df["ordered_at"] = pd.to_datetime(df["ordered_at"], errors="coerce")
    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["priority"] = df["priority"].astype(str).str.strip().str.lower()
    df["order_id"] = pd.to_numeric(df["order_id"], errors="coerce").astype("Int64")
    df["patient_user_id"] = pd.to_numeric(df["patient_user_id"], errors="coerce").astype("Int64")
    df["ordered_by_doctor_id"] = pd.to_numeric(df["ordered_by_doctor_id"], errors="coerce").astype("Int64")
    return df


def clean_results(df: pd.DataFrame) -> pd.DataFrame:
    df = ensure_columns(df, [
        "result_id", "order_id", "test_type_id", "performed_by", "performed_at",
        "value", "flag", "doctor_reviewed_by", "doctor_reviewed_at",
        "publish_status", "published_at"
    ])
    df = df.copy()
    df["performed_at"] = pd.to_datetime(df["performed_at"], errors="coerce")
    df["doctor_reviewed_at"] = pd.to_datetime(df["doctor_reviewed_at"], errors="coerce")
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
    df["flag"] = df["flag"].astype(str).str.strip().str.lower()
    df["value_num"] = pd.to_numeric(df["value"], errors="coerce")
    df["result_id"] = pd.to_numeric(df["result_id"], errors="coerce").astype("Int64")
    df["order_id"] = pd.to_numeric(df["order_id"], errors="coerce").astype("Int64")
    df["test_type_id"] = pd.to_numeric(df["test_type_id"], errors="coerce").astype("Int64")
    df["performed_by"] = pd.to_numeric(df["performed_by"], errors="coerce").astype("Int64")
    df["doctor_reviewed_by"] = pd.to_numeric(df["doctor_reviewed_by"], errors="coerce").astype("Int64")
    return df


def clean_invoices(df: pd.DataFrame) -> pd.DataFrame:
    df = ensure_columns(df, [
        "invoice_id", "patient_user_id", "patient_id", "total",
        "status", "created_at", "paid_at"
    ])
    df = df.copy()
    df["invoice_id"] = pd.to_numeric(df["invoice_id"], errors="coerce").astype("Int64")
    df["patient_user_id"] = pd.to_numeric(df["patient_user_id"], errors="coerce").astype("Int64")
    df["patient_id"] = pd.to_numeric(df["patient_id"], errors="coerce").astype("Int64")
    df["patient_key"] = df["patient_user_id"].fillna(df["patient_id"]).astype("Int64")
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["paid_at"] = pd.to_datetime(df["paid_at"], errors="coerce")
    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0.0)
    return df


def clean_patients(df: pd.DataFrame) -> pd.DataFrame:
    df = ensure_columns(df, [
        "patient_id", "user_id", "first_name", "last_name", "email",
        "date_of_birth", "gender", "current_status", "admission_date",
        "discharge_date", "allergies"
    ])
    df = df.copy()
    df["patient_key"] = pd.to_numeric(df["patient_id"], errors="coerce")
    df["patient_key"] = df["patient_key"].fillna(pd.to_numeric(df["user_id"], errors="coerce")).astype("Int64")
    df["current_status"] = df["current_status"].astype(str).str.strip().str.upper()
    for col in ["admission_date", "discharge_date", "date_of_birth"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def clean_test_types(df: pd.DataFrame) -> pd.DataFrame:
    df = ensure_columns(df, [
        "test_type_id", "name", "unit", "normal_min", "normal_max",
        "critical_min", "critical_max", "result_type"
    ])
    df = df.copy()
    df["test_type_id"] = pd.to_numeric(df["test_type_id"], errors="coerce").astype("Int64")
    df["name"] = df["name"].astype(str).str.strip()
    return df


def clean_users(df: pd.DataFrame) -> pd.DataFrame:
    df = ensure_columns(df, ["user_id", "first_name", "last_name", "username", "role"])
    df = df.copy()
    df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce").astype("Int64")
    df["full_name"] = (
        df["first_name"].fillna("").astype(str).str.strip() + " " +
        df["last_name"].fillna("").astype(str).str.strip()
    ).str.strip()
    df["full_name"] = df["full_name"].where(df["full_name"] != "", df["username"])
    return df


# =========================
# ENRICH DATA
# =========================
def enrich_results(results_df, orders_df, test_types_df, users_df):
    doctors_df = users_df.rename(columns={"user_id": "doctor_user_id", "full_name": "doctor_name"})
    nurses_df = users_df.rename(columns={"user_id": "nurse_user_id", "full_name": "performed_by_name"})
    reviewers_df = users_df.rename(columns={"user_id": "reviewer_user_id", "full_name": "reviewed_by_name"})

    out = results_df.merge(
        test_types_df[["test_type_id", "name", "unit"]],
        on="test_type_id",
        how="left"
    ).rename(columns={"name": "test_name"})

    out = out.merge(
        orders_df[["order_id", "patient_user_id", "ordered_at", "status", "ordered_by_doctor_id"]],
        on="order_id",
        how="left",
        suffixes=("", "_order")
    ).rename(columns={"status": "order_status"})

    out = out.merge(
        nurses_df[["nurse_user_id", "performed_by_name"]],
        left_on="performed_by",
        right_on="nurse_user_id",
        how="left",
        suffixes=("", "_nurse")
    ).drop(columns=["nurse_user_id"], errors="ignore")

    # In some payloads pandas can suffix duplicate names after merges.
    if "performed_by_name" not in out.columns:
        alt = [c for c in out.columns if c.startswith("performed_by_name")]
        if alt:
            out["performed_by_name"] = out[alt[0]]

    out = out.merge(
        reviewers_df[["reviewer_user_id", "reviewed_by_name"]],
        left_on="doctor_reviewed_by",
        right_on="reviewer_user_id",
        how="left",
        suffixes=("", "_reviewer")
    ).drop(columns=["reviewer_user_id"], errors="ignore")

    if "reviewed_by_name" not in out.columns:
        alt = [c for c in out.columns if c.startswith("reviewed_by_name")]
        if alt:
            out["reviewed_by_name"] = out[alt[0]]

    out = out.merge(
        doctors_df[["doctor_user_id", "doctor_name"]],
        left_on="ordered_by_doctor_id",
        right_on="doctor_user_id",
        how="left",
        suffixes=("", "_doctor")
    ).drop(columns=["doctor_user_id"], errors="ignore")

    if "doctor_name" not in out.columns:
        alt = [c for c in out.columns if c.startswith("doctor_name")]
        if alt:
            out["doctor_name"] = out[alt[0]]

    for col in ["performed_by_name", "reviewed_by_name", "doctor_name"]:
        if col not in out.columns:
            out[col] = "Unknown"
        else:
            out[col] = out[col].fillna("Unknown")

    return out


# =========================
# WORKFLOWS
# =========================
def viz_operational_backlog_orders(orders_df: pd.DataFrame):
    '''
    BUSINESS: Operations / Admin Dashboard.
    VALUE: Shows backlog and throughput by order status to detect bottlenecks and SLA risk.
    '''
    status_counts = orders_df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]

    fig = px.bar(
        status_counts,
        x="status",
        y="count",
        title="Operational KPI: Orders by Status (Backlog / Throughput)"
    )
    fig.show()


def viz_priority_by_status_stacked(orders_df: pd.DataFrame):
    '''
    BUSINESS: Operations / Capacity Planning.
    VALUE: Compares urgent vs routine volume inside each status.
    '''
    pivot = (
        orders_df.groupby(["status", "priority"])
        .size()
        .reset_index(name="count")
    )

    fig = px.bar(
        pivot,
        x="status",
        y="count",
        color="priority",
        barmode="stack",
        title="Operations KPI: Priority Mix Within Each Status"
    )
    fig.show()


def viz_nurse_productivity(results_df: pd.DataFrame):
    '''
    BUSINESS: Lab Management / Nurse Supervisor.
    VALUE: Measures lab throughput by staff member.
    '''
    counts = results_df["performed_by_name"].value_counts().reset_index()
    counts.columns = ["performed_by_name", "result_count"]

    fig = px.bar(
        counts,
        x="performed_by_name",
        y="result_count",
        title="Lab KPI: Results Entered per Staff (Throughput / Productivity)"
    )
    fig.show()


def viz_clinical_risk_flag_distribution(results_df: pd.DataFrame):
    '''
    BUSINESS: Clinical Quality / Patient Safety.
    VALUE: Monitors normal vs abnormal vs critical distribution.
    '''
    flag_counts = results_df["flag"].value_counts().reset_index()
    flag_counts.columns = ["flag", "count"]

    fig = px.pie(
        flag_counts,
        names="flag",
        values="count",
        title="Clinical KPI: Normal vs Abnormal vs Critical (Risk Monitoring)"
    )
    fig.show()


def viz_revenue_and_cashflow(invoices_df: pd.DataFrame):
    '''
    BUSINESS: Finance / Billing.
    VALUE: Tracks revenue volume over time and paid vs unpaid split.
    '''
    status_counts = invoices_df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig1 = px.pie(
        status_counts,
        names="status",
        values="count",
        title="Billing KPI: Paid vs Unpaid (Cashflow / AR)"
    )
    fig1.show()

    daily = (
        invoices_df.dropna(subset=["created_at"])
        .assign(day=lambda d: d["created_at"].dt.date)
        .groupby("day")["total"].sum()
        .reset_index()
    )
    fig2 = px.line(
        daily,
        x="day",
        y="total",
        title="Finance KPI: Daily Revenue Trend (Invoice Totals)"
    )
    fig2.show()


# =========================
# MAIN
# =========================
def main():
    session = login_session()

    orders_df = clean_orders(to_df(fetch_json(session, ORDERS_URL)))
    results_df = clean_results(to_df(fetch_json(session, RESULTS_URL)))
    invoices_df = clean_invoices(to_df(fetch_json(session, INVOICES_URL)))
    patients_df = clean_patients(to_df(fetch_json(session, PATIENTS_URL)))
    test_types_df = clean_test_types(to_df(fetch_json(session, TEST_TYPES_URL)))
    users_df = clean_users(to_df(fetch_json(session, USERS_URL)))

    results_df = enrich_results(results_df, orders_df, test_types_df, users_df)

    print("Orders:", orders_df.shape)
    print("Results:", results_df.shape)
    print("Invoices:", invoices_df.shape)
    print("Patients:", patients_df.shape)

    viz_operational_backlog_orders(orders_df)
    viz_priority_by_status_stacked(orders_df)
    viz_nurse_productivity(results_df)
    viz_clinical_risk_flag_distribution(results_df)
    viz_revenue_and_cashflow(invoices_df)


if __name__ == "__main__":
    main()