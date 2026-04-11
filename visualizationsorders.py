import pandas as pd
import plotly.express as px
import requests





# ETL : Extract the data, Transform the data, data visualization / Load Data Warehouse
# ETL : Extract the data, Load Data Warehouse /  Transform the data


# -----------------------------
# 1) CONFIG
# -----------------------------
BASE_URL = "https://talentifylabhealth.onrender.com"
USERNAME = "admin1"
PASSWORD = "Admin123"



# -----------------------------
# 2) AUTH
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
# 3) EXTRACT
# -----------------------------
def get_orders_data():
    headers = {
        "Authorization": f"Bearer {get_token()}"
    }

    url = f"{BASE_URL}/api/orders"

    response = requests.get(url, headers=headers, timeout=30)
    print("Orders status:", response.status_code)
    response.raise_for_status()

    return response.json()


# -----------------------------
# 4) TRANSFORM
# -----------------------------
def prepare_orders_df(data):
    df = pd.DataFrame(data)

    print("Columns:", df.columns.tolist())
    print(df.head(3))

    df.columns = df.columns.str.strip().str.lower()

    needed_cols = [
        "order_id",
        "patient_user_id",
        "ordered_by_doctor_id",
        "ordered_at",
        "priority",
        "status",
        "notes"
    ]
    for col in needed_cols:
        if col not in df.columns:
            df[col] = None

    # datetime parse
    df["ordered_at"] = pd.to_datetime(df["ordered_at"], errors="coerce")

    # text normalize
    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["priority"] = df["priority"].astype(str).str.strip().str.lower()
    df["notes"] = df["notes"].astype(str).str.strip()

    # primary key cleanup just for data quality
    df["order_id"] = df["order_id"].astype(str).str.strip()
    df.loc[df["order_id"].isin(["", "nan", "None", "null"]), "order_id"] = None

    before_count = len(df)
    df = df.dropna(subset=["order_id"]).copy()
    df = df.drop_duplicates(subset=["order_id"], keep="first").copy()
    after_count = len(df)

    print(f"Rows before cleanup: {before_count}")
    print(f"Rows after cleanup: {after_count}")

    return df


# -----------------------------
# 5) VALIDATE
# -----------------------------
def validate_orders_df(df):
    if df.empty:
        raise Exception("Orders dataframe is empty")

    if "order_id" not in df.columns:
        raise Exception("Missing order_id column")

    if df["order_id"].isna().sum() > 0:
        raise Exception("Orders order_id still contains null values")


# -----------------------------
# FLOW 3: Operational Backlog
# -----------------------------
def flow_3_orders_backlog(df):
    """
    DESCRIPTION:
    Shows order volume by status to monitor backlog and throughput.
    """
    print("\nFLOW 3: Orders by Status")

    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]

    fig = px.bar(
        status_counts,
        x="status",
        y="count",
        text="count",
        title="Operational Board: Orders by Status"
    )
    fig.show()


# -----------------------------
# FLOW 4: Priority Mix
# -----------------------------
def flow_4_priority_mix(df):
    """
    DESCRIPTION:
    Shows urgent vs routine distribution inside each status group.
    """
    print("\nFLOW 4: Priority Mix by Status")

    grouped = df.groupby(["status", "priority"]).size().reset_index(name="count")

    fig = px.bar(
        grouped,
        x="status",
        y="count",
        color="priority",
        barmode="stack",
        title="Operations: Priority Mix by Status"
    )
    fig.show()


# -----------------------------
# BONUS FLOW: Orders by Day
# -----------------------------
def flow_5_orders_trend(df):
    """
    DESCRIPTION:
    Shows daily order trend over time.
    """
    print("\nFLOW 5: Orders Trend by Day")

    trend_df = df.dropna(subset=["ordered_at"]).copy()
    trend_df["order_date"] = trend_df["ordered_at"].dt.date

    grouped = trend_df.groupby("order_date").size().reset_index(name="count")

    fig = px.line(
        grouped,
        x="order_date",
        y="count",
        markers=True,
        title="Orders Trend by Day"
    )
    fig.show()


# -----------------------------
# MAIN
# -----------------------------
def main():
    print("Starting Orders Visualization Flow...")

    # Extract
    data = get_orders_data()

    # Transform
    df = prepare_orders_df(data)

    # Validate
    validate_orders_df(df)

    # Visuals only
    flow_3_orders_backlog(df)
    flow_4_priority_mix(df)
    flow_5_orders_trend(df)

    print("Visualization flow completed successfully 🎉")


if __name__ == "__main__":
    main()