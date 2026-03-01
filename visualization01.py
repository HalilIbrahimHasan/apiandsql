import pandas as pd
import plotly.express as px

# =========================
# SAMPLE DATA (replace later with API payloads)
# =========================
SAMPLE_RESULTS = [
    {
        "result_id": 6722,
        "order_id": 1627,
        "test_type_id": 17,
        "performed_by": 1,
        "performed_at": "2026-02-15T06:05:40.628859",
        "value": "45.0",
        "flag": "normal",
        "doctor_reviewed_by": None,
        "doctor_reviewed_at": None,
        "publish_status": "draft",
        "published_at": None,
        "test_name": "Alkaline Phosphatase (ALP)",
        "unit": "U/L",
        "normal_min": 44.0,
        "normal_max": 147.0,
        "critical_min": 30.0,
        "critical_max": 200.0,
        "result_type": "numeric",
        "performed_by_name": "Admin User",
        "reviewed_by_name": None,
        "patient_user_id": 1197,
        "ordered_at": "2026-02-15T06:05:39.528643",
        "order_status": "published",
        "doctor_name": "Admin User"
    },
    {
        "result_id": 6724,
        "order_id": 1627,
        "test_type_id": 8,
        "performed_by": 1,
        "performed_at": "2026-02-15T06:05:42.928914",
        "value": "48.1",
        "flag": "normal",
        "doctor_reviewed_by": None,
        "doctor_reviewed_at": None,
        "publish_status": "draft",
        "published_at": None,
        "test_name": "Chloride (Cl)",
        "unit": "mmol/L",
        "normal_min": 98.0,
        "normal_max": 107.0,
        "critical_min": 95.0,
        "critical_max": 110.0,
        "result_type": "numeric",
        "performed_by_name": "Admin User",
        "reviewed_by_name": None,
        "patient_user_id": 1197,
        "ordered_at": "2026-02-15T06:05:39.528643",
        "order_status": "published",
        "doctor_name": "Admin User"
    },
    {
        "result_id": 6723,
        "order_id": 1627,
        "test_type_id": 32,
        "performed_by": 1,
        "performed_at": "2026-02-15T06:05:41.728833",
        "value": "14.8",
        "flag": "normal",
        "doctor_reviewed_by": None,
        "doctor_reviewed_at": None,
        "publish_status": "draft",
        "published_at": None,
        "test_name": "Iron",
        "unit": "µg/dL",
        "normal_min": 65.0,
        "normal_max": 175.0,
        "critical_min": 40.0,
        "critical_max": 200.0,
        "result_type": "numeric",
        "performed_by_name": "Admin User",
        "reviewed_by_name": None,
        "patient_user_id": 1197,
        "ordered_at": "2026-02-15T06:05:39.528643",
        "order_status": "published",
        "doctor_name": "Admin User"
    }
]

SAMPLE_ORDERS = [
    {
        "order_id": 1665,
        "patient_user_id": 1222,
        "ordered_by_doctor_id": 1,
        "ordered_at": "2026-02-15T06:11:17.527369",
        "priority": "urgent",
        "status": "in_progress",
        "notes": "Auto-generated order"
    },
    {
        "order_id": 1664,
        "patient_user_id": 1221,
        "ordered_by_doctor_id": 1,
        "ordered_at": "2026-02-15T06:11:07.431385",
        "priority": "urgent",
        "status": "published",
        "notes": "Auto-generated order"
    },
    {
        "order_id": 1663,
        "patient_user_id": 1220,
        "ordered_by_doctor_id": 1,
        "ordered_at": "2026-02-15T06:10:57.735274",
        "priority": "routine",
        "status": "published",
        "notes": "Auto-generated order"
    }
]

SAMPLE_INVOICES = [
    {
        "invoice_id": 3,
        "patient_user_id": 8,
        "total": 3970.0,
        "status": "unpaid",
        "created_at": "2026-02-13T00:17:46.628911",
        "paid_at": None
    },
    {
        "invoice_id": 2,
        "patient_user_id": 7,
        "total": 245.0,
        "status": "unpaid",
        "created_at": "2026-02-10T00:17:46.558785",
        "paid_at": None
    },
    {
        "invoice_id": 1,
        "patient_user_id": 6,
        "total": 145.0,
        "status": "paid",
        "created_at": "2026-02-07T00:17:46.555074",
        "paid_at": None
    }
]

SAMPLE_PATIENTS = [
    {
        "patient_id": 778,
        "first_name": "Janice",
        "last_name": "Adams",
        "email": "janice.adams92@gmail.com",
        "date_of_birth": None,
        "gender": None,
        "current_status": "OUTPATIENT",
        "admission_date": "",
        "discharge_date": "",
        "allergies": None
    },
    {
        "patient_id": 818,
        "first_name": "Ann",
        "last_name": "Allen",
        "email": "ann.allen132@outlook.com",
        "date_of_birth": None,
        "gender": None,
        "current_status": "OUTPATIENT",
        "admission_date": "",
        "discharge_date": "",
        "allergies": None
    },
    {
        "patient_id": 758,
        "first_name": "Bobby",
        "last_name": "Allen",
        "email": "bobby.allen72@yahoo.com",
        "date_of_birth": None,
        "gender": None,
        "current_status": "OUTPATIENT",
        "admission_date": "",
        "discharge_date": "",
        "allergies": None
    },
    {
        "patient_id": 877,
        "first_name": "Ralph",
        "last_name": "Allen",
        "email": "ralph.allen191@outlook.com",
        "date_of_birth": None,
        "gender": None,
        "current_status": "OUTPATIENT",
        "admission_date": "",
        "discharge_date": "",
        "allergies": None
    }
]


# =========================
# DATAFRAME PREP
# =========================
def to_df(payload: list) -> pd.DataFrame:
    return pd.DataFrame(payload)

def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ordered_at"] = pd.to_datetime(df["ordered_at"], errors="coerce")
    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["priority"] = df["priority"].astype(str).str.strip().str.lower()
    return df

def clean_results(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["performed_at"] = pd.to_datetime(df["performed_at"], errors="coerce")
    df["ordered_at"] = pd.to_datetime(df["ordered_at"], errors="coerce")
    df["published_at"] = pd.to_datetime(df.get("published_at"), errors="coerce")
    df["flag"] = df["flag"].astype(str).str.strip().str.lower()
    df["test_name"] = df["test_name"].astype(str).str.strip()
    df["performed_by_name"] = df["performed_by_name"].fillna("Unknown").astype(str).str.strip()
    # numeric conversions (safe)
    df["value_num"] = pd.to_numeric(df["value"], errors="coerce")
    return df

def clean_invoices(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0.0)
    return df

def clean_patients(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["current_status"] = df["current_status"].astype(str).str.strip().str.upper()
    # normalize empty strings to NA
    for col in ["admission_date", "discharge_date"]:
        if col in df.columns:
            df[col] = df[col].replace("", pd.NA)
    return df


# =========================
# WORKFLOWS (business description first)
# =========================
def viz_operational_backlog_orders(orders_df: pd.DataFrame):
    """
    BUSINESS: Operations / Admin Dashboard.
    VALUE: Shows backlog and throughput by order status (e.g., in_progress vs published) to detect bottlenecks and SLA risk.
    NEED IT SERVES: "Are orders getting stuck?" (Operational KPI, Backlog monitoring, Throughput).
    """
    print("\n[Workflow 1] Operational Backlog & Throughput — Order Status Distribution")
    print(viz_operational_backlog_orders.__doc__.strip())

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
    """
    BUSINESS: Operations / Capacity Planning.
    VALUE: Compares urgent vs routine volume inside each status to ensure urgent work isn't trapped in backlog.
    NEED IT SERVES: "Is urgent work moving faster?" (Case mix, SLA prioritization, Workload segmentation).
    """
    print("\n[Workflow 2] Priority Mix by Status — Urgent vs Routine")
    print(viz_priority_by_status_stacked.__doc__.strip())

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
    """
    BUSINESS: Lab Management / Nurse Supervisor.
    VALUE: Measures lab throughput by staff member (results entered per nurse) to track productivity and staffing needs.
    NEED IT SERVES: "Who is producing results and at what volume?" (Productivity metric, Workload distribution).
    """
    print("\n[Workflow 3] Lab Productivity — Results Entered per Staff")
    print(viz_nurse_productivity.__doc__.strip())

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
    """
    BUSINESS: Clinical Quality / Patient Safety.
    VALUE: Monitors normal vs abnormal vs critical distribution to detect risk spikes and prioritize review workflows.
    NEED IT SERVES: "Are abnormal/critical rates increasing?" (Clinical KPI, Risk monitoring, Alert triage).
    """
    print("\n[Workflow 4] Clinical Risk Monitoring — Flag Distribution")
    print(viz_clinical_risk_flag_distribution.__doc__.strip())

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
    """
    BUSINESS: Finance / Billing.
    VALUE: Tracks revenue volume over time and paid vs unpaid split to manage cashflow and accounts receivable (AR).
    NEED IT SERVES: "Is unpaid growing?" (Revenue analytics, Cashflow monitoring, AR health).
    """
    print("\n[Workflow 5] Revenue & Billing Health — Paid vs Unpaid + Revenue Trend")
    print(viz_revenue_and_cashflow.__doc__.strip())

    # Pie: paid vs unpaid
    status_counts = invoices_df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig1 = px.pie(status_counts, names="status", values="count", title="Billing KPI: Paid vs Unpaid (Cashflow / AR)")
    fig1.show()

    # Line: revenue trend by day (created_at)
    daily = (
        invoices_df.dropna(subset=["created_at"])
        .assign(day=lambda d: d["created_at"].dt.date)
        .groupby("day")["total"].sum()
        .reset_index()
    )
    fig2 = px.line(daily, x="day", y="total", title="Finance KPI: Daily Revenue Trend (Invoice Totals)")
    fig2.show()


# =========================
# MAIN
# =========================
def main():
    # 1) Convert samples -> DataFrames
    orders_df = clean_orders(to_df(SAMPLE_ORDERS))
    results_df = clean_results(to_df(SAMPLE_RESULTS))
    invoices_df = clean_invoices(to_df(SAMPLE_INVOICES))
    patients_df = clean_patients(to_df(SAMPLE_PATIENTS))  # not used in these 5 visuals yet

    # 2) Run 5 effective workflows
    viz_operational_backlog_orders(orders_df)
    viz_priority_by_status_stacked(orders_df)
    viz_nurse_productivity(results_df)
    viz_clinical_risk_flag_distribution(results_df)
    viz_revenue_and_cashflow(invoices_df)

if __name__ == "__main__":
    main()
