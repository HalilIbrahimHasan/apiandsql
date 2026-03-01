import pandas as pd
import plotly.express as px

# =========================
# SAMPLE DATA (replace with API later)
# =========================
results = [
    {"result_id": 6722, "order_id": 1627, "performed_at": "2026-02-15T06:05:40.628859", "value": "45.0",
     "flag": "normal", "test_name": "Alkaline Phosphatase (ALP)", "performed_by_name": "Admin User"},
    {"result_id": 6724, "order_id": 1627, "performed_at": "2026-02-15T06:05:42.928914", "value": "48.1",
     "flag": "normal", "test_name": "Chloride (Cl)", "performed_by_name": "Admin User"},
    {"result_id": 6723, "order_id": 1627, "performed_at": "2026-02-15T06:05:41.728833", "value": "14.8",
     "flag": "normal", "test_name": "Iron", "performed_by_name": "Admin User"},
]

orders = [
    {"order_id": 1665, "patient_user_id": 1222, "ordered_at": "2026-02-15T06:11:17.527369",
     "priority": "urgent", "status": "in_progress"},
    {"order_id": 1664, "patient_user_id": 1221, "ordered_at": "2026-02-15T06:11:07.431385",
     "priority": "urgent", "status": "published"},
    {"order_id": 1663, "patient_user_id": 1220, "ordered_at": "2026-02-15T06:10:57.735274",
     "priority": "routine", "status": "published"},
]

invoices = [
    {"invoice_id": 3, "patient_user_id": 8, "total": 3970.0, "status": "unpaid", "created_at": "2026-02-13T00:17:46.628911"},
    {"invoice_id": 2, "patient_user_id": 7, "total": 245.0, "status": "unpaid", "created_at": "2026-02-10T00:17:46.558785"},
    {"invoice_id": 1, "patient_user_id": 6, "total": 145.0, "status": "paid", "created_at": "2026-02-07T00:17:46.555074"},
]


# =========================
# 1) MAKE DATAFRAMES
# =========================
def make_df(list_of_dicts):
    return pd.DataFrame(list_of_dicts)


# =========================
# 2) CLEAN DATA
# =========================
def clean_orders(df):
    df["status"] = df["status"].astype(str).str.lower().str.strip()
    df["priority"] = df["priority"].astype(str).str.lower().str.strip()
    df["ordered_at"] = pd.to_datetime(df["ordered_at"], errors="coerce")
    return df

def clean_results(df):
    df["flag"] = df["flag"].astype(str).str.lower().str.strip()
    df["test_name"] = df["test_name"].astype(str).str.strip()
    df["performed_by_name"] = df["performed_by_name"].fillna("Unknown").astype(str).str.strip()
    df["performed_at"] = pd.to_datetime(df["performed_at"], errors="coerce")
    df["value_num"] = pd.to_numeric(df["value"], errors="coerce")
    return df

def clean_invoices(df):
    df["status"] = df["status"].astype(str).str.lower().str.strip()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0)
    return df


# =========================
# WORKFLOW 1: Order Backlog
# =========================
def workflow_1_orders_by_status(orders_df):
    """
    BUSINESS: Operations
    NEED: See backlog (in_progress) vs completed (published).
    CHART: Bar chart (status counts)
    """
    print("\nWorkflow 1:", workflow_1_orders_by_status.__doc__.strip())

    counts = orders_df["status"].value_counts().reset_index()
    counts.columns = ["status", "count"]

    fig = px.bar(counts, x="status", y="count", title="Orders by Status (Backlog / Throughput)")
    fig.show()


# =========================
# WORKFLOW 2: Urgent vs Routine Mix
# =========================
def workflow_2_priority_mix(orders_df):
    """
    BUSINESS: Operations / SLA
    NEED: Make sure urgent orders are not stuck.
    CHART: Stacked bar (status x priority)
    """
    print("\nWorkflow 2:", workflow_2_priority_mix.__doc__.strip())

    grouped = orders_df.groupby(["status", "priority"]).size().reset_index(name="count")

    fig = px.bar(grouped, x="status", y="count", color="priority", barmode="stack",
                 title="Priority Mix by Status (Urgent vs Routine)")
    fig.show()


# =========================
# WORKFLOW 3: Nurse Productivity
# =========================
def workflow_3_results_by_staff(results_df):
    """
    BUSINESS: Lab / Nurse Manager
    NEED: See who entered more results (productivity).
    CHART: Bar chart (performed_by_name counts)
    """
    print("\nWorkflow 3:", workflow_3_results_by_staff.__doc__.strip())

    counts = results_df["performed_by_name"].value_counts().reset_index()
    counts.columns = ["performed_by_name", "result_count"]

    fig = px.bar(counts, x="performed_by_name", y="result_count",
                 title="Results Entered per Staff (Productivity)")
    fig.show()


# =========================
# WORKFLOW 4: Clinical Risk
# =========================
def workflow_4_flag_distribution(results_df):
    """
    BUSINESS: Clinical Quality
    NEED: Monitor abnormal/critical rates.
    CHART: Pie chart (flag distribution)
    """
    print("\nWorkflow 4:", workflow_4_flag_distribution.__doc__.strip())

    counts = results_df["flag"].value_counts().reset_index()
    counts.columns = ["flag", "count"]

    fig = px.pie(counts, names="flag", values="count",
                 title="Normal vs Abnormal vs Critical (Risk Monitoring)")
    fig.show()


# =========================
# WORKFLOW 5: Billing Health
# =========================
def workflow_5_paid_unpaid(invoices_df):
    """
    BUSINESS: Finance
    NEED: Track paid vs unpaid invoices (cashflow risk).
    CHART: Pie chart (paid/unpaid)
    """
    print("\nWorkflow 5:", workflow_5_paid_unpaid.__doc__.strip())

    counts = invoices_df["status"].value_counts().reset_index()
    counts.columns = ["status", "count"]

    fig = px.pie(counts, names="status", values="count", title="Paid vs Unpaid Invoices (Cashflow / AR)")
    fig.show()


# =========================
# MAIN
# =========================
def main():
    # 1) Create dfs
    orders_df = make_df(orders)
    results_df = make_df(results)
    invoices_df = make_df(invoices)

    # 2) Clean dfs
    orders_df = clean_orders(orders_df)
    results_df = clean_results(results_df)
    invoices_df = clean_invoices(invoices_df)

    # 3) Run workflows
    workflow_1_orders_by_status(orders_df)
    workflow_2_priority_mix(orders_df)
    workflow_3_results_by_staff(results_df)
    workflow_4_flag_distribution(results_df)
    workflow_5_paid_unpaid(invoices_df)

if __name__ == "__main__":
    main()
