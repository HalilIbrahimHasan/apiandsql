import pandas as pd
import plotly.express as px
import requests

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL = "https://talentifylabhealth.onrender.com"
USERNAME = "admin1"
PASSWORD = "Admin123"


# -----------------------------
# AUTH
# -----------------------------
def get_token():
    url = f"{BASE_URL}/api/auth/login"

    credentials = {
        "username": USERNAME,
        "password": PASSWORD
    }

    resp = requests.post(url, json=credentials, timeout=30)
    resp.raise_for_status()

    return resp.json()["token"]


# -----------------------------
# EXTRACT
# -----------------------------
def get_results_data():
    headers = {
        "Authorization": f"Bearer {get_token()}"
    }

    url = f"{BASE_URL}/api/results"

    response = requests.get(url, headers=headers, timeout=30)
    print("Results status:", response.status_code)
    response.raise_for_status()

    return response.json()


# -----------------------------
# TRANSFORM
# -----------------------------
def prepare_results_df(data):
    df = pd.DataFrame(data)

    print("Columns:", df.columns.tolist())
    print(df.head(3))

    df.columns = df.columns.str.strip().str.lower()

    needed_cols = [
        "result_id",
        "order_id",
        "performed_at",
        "value",
        "flag",
        "publish_status",
        "published_at",
        "test_name",
        "unit",
        "normal_min",
        "normal_max",
        "critical_min",
        "critical_max",
        "result_type",
        "performed_by_name",
        "reviewed_by_name",
        "patient_user_id",
        "ordered_at",
        "order_status",
        "doctor_name"
    ]
    for col in needed_cols:
        if col not in df.columns:
            df[col] = None

    # datetime
    df["ordered_at"] = pd.to_datetime(df["ordered_at"], errors="coerce")
    df["performed_at"] = pd.to_datetime(df["performed_at"], errors="coerce")
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")

    # normalize text
    df["order_status"] = df["order_status"].astype(str).str.strip().str.lower()
    df["publish_status"] = df["publish_status"].astype(str).str.strip().str.lower()
    df["flag"] = df["flag"].astype(str).str.strip().str.lower()
    df["result_type"] = df["result_type"].astype(str).str.strip().str.lower()

    df["performed_by_name"] = df["performed_by_name"].fillna("Unknown").astype(str).str.strip()
    df["doctor_name"] = df["doctor_name"].fillna("Unknown").astype(str).str.strip()

    # numeric
    df["value_num"] = pd.to_numeric(df["value"], errors="coerce")
    df["critical_min_num"] = pd.to_numeric(df["critical_min"], errors="coerce")
    df["critical_max_num"] = pd.to_numeric(df["critical_max"], errors="coerce")

    # critical logic
    df["is_critical"] = False

    numeric_mask = df["value_num"].notna()

    df.loc[numeric_mask, "is_critical"] = (
        (df.loc[numeric_mask, "value_num"] < df.loc[numeric_mask, "critical_min_num"]) |
        (df.loc[numeric_mask, "value_num"] > df.loc[numeric_mask, "critical_max_num"])
    )

    df["is_critical"] = df["is_critical"] | df["flag"].eq("critical")

    # keep only published rows first
    df = df[df["publish_status"] == "published"].copy()

    # latest result per order
    df = df.sort_values("published_at", ascending=False)
    df = df.drop_duplicates(subset=["order_id"], keep="first")

    print("Final dataset size (order-level):", len(df))

    return df


# -----------------------------
# VALIDATE
# -----------------------------
def validate_results_df(df):
    if df.empty:
        raise Exception("Results dataframe is empty after filtering")


# -----------------------------
# FLOW 1: Critical vs Not
# -----------------------------
def flow_1_critical_results(df):
    print("\nFLOW 1: Critical vs Not")

    counts = df["is_critical"].map({
        True: "critical",
        False: "not_critical"
    }).value_counts().reset_index()

    counts.columns = ["critical_label", "count"]

    fig = px.pie(
        counts,
        names="critical_label",
        values="count",
        title="Clinical Risk (Order Level)"
    )
    fig.show()


# -----------------------------
# FLOW 2: SLA
# -----------------------------
def flow_2_sla(df):
    print("\nFLOW 2: SLA (Turnaround Time)")

    df = df.copy()
    df["tat_min"] = (
        (df["performed_at"] - df["ordered_at"]).dt.total_seconds() / 60
    )

    fig = px.histogram(
        df,
        x="tat_min",
        nbins=20,
        title="Turnaround Time Distribution (minutes)"
    )
    fig.show()


# -----------------------------
# FLOW 3: Staff Productivity
# -----------------------------
def flow_3_staff(df):
    print("\nFLOW 3: Staff Productivity")

    staff_counts = df.groupby("performed_by_name")["order_id"].nunique().reset_index()
    staff_counts.columns = ["performed_by_name", "order_count"]

    fig = px.bar(
        staff_counts,
        x="performed_by_name",
        y="order_count",
        text="order_count",
        title="Orders Processed per Staff"
    )
    fig.show()


# -----------------------------
# FLOW 4: Publish Status
# -----------------------------
def flow_4_publish(df):
    print("\nFLOW 4: Publish Status")

    counts = df["publish_status"].value_counts().reset_index()
    counts.columns = ["publish_status", "count"]

    fig = px.pie(
        counts,
        names="publish_status",
        values="count",
        title="Publish Status (Order Level)"
    )
    fig.show()


# -----------------------------
# BONUS FLOW 5: Order Status
# -----------------------------
def flow_5_order_status(df):
    print("\nFLOW 5: Order Status")

    counts = df["order_status"].value_counts().reset_index()
    counts.columns = ["order_status", "count"]

    fig = px.bar(
        counts,
        x="order_status",
        y="count",
        text="count",
        title="Order Status (Latest Published Result per Order)"
    )
    fig.show()


# -----------------------------
# MAIN
# -----------------------------
def main():
    print("Starting Results FINAL Flow... 🚀")

    data = get_results_data()
    df = prepare_results_df(data)

    validate_results_df(df)

    flow_1_critical_results(df)
    flow_2_sla(df)
    flow_3_staff(df)
    flow_4_publish(df)
    flow_5_order_status(df)

    print("Results flow completed successfully 🎉")


if __name__ == "__main__":
    main()