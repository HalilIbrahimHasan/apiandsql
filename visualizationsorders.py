import pandas as pd
import plotly.express as px
import requests

# -----------------------------
# 1) DATA (API'den gelmiş gibi)
# -----------------------------
def get_token():
    url = "https://talentifylabhealth-2edp.onrender.com/api/auth/login"

    credentials = {
        "username": "admin1",
        "password": "Admin123"
    }

    resp = requests.post(url, json=credentials)
    resp.raise_for_status()

    return resp.json()["token"]


def get_orders_data():
    token = {
            "Authorization": f"Bearer {get_token()}"
        }


    response = requests.get('https://talentifylabhealth-2edp.onrender.com/api/orders', headers=token)

    print(response.status_code)

    return response.json()


def prepare_orders_df(data):
    df = pd.DataFrame(data)

    # WHY: ordered_at datetime enables daily trend and SLA segmentation.
    df["ordered_at"] = pd.to_datetime(df["ordered_at"], errors="coerce")

    # WHY: normalize status/priority text for consistent grouping.
    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["priority"] = df["priority"].astype(str).str.strip().str.lower()

    return df


# -----------------------------
# FLOW 3: Operational Backlog Board (Orders by Status)
# -----------------------------
def flow_3_orders_backlog(orders_df):
    """
    DESCRIPTION (Business):
    Operations checks whether orders are stuck (in_progress) or moving to published.
    This supports backlog monitoring and throughput tracking for daily hospital operations.
    """
    print("\nFLOW 3:", flow_3_orders_backlog.__doc__.strip())

    status_counts = orders_df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]

    fig = px.bar(
        status_counts,
        x="status",
        y="count",
        text="count",
        title="Operational Board: Orders by Status (Backlog / Throughput)"
    )
    fig.show()


# -----------------------------
# FLOW 4: Priority Mix (Urgent vs Routine inside each status)
# -----------------------------
def flow_4_priority_mix(orders_df):
    """
    DESCRIPTION (Business):
    If urgent orders are piling up in the backlog, that signals an SLA risk.
    This chart shows urgent vs routine distribution inside each order status.
    """
    print("\nFLOW 4:", flow_4_priority_mix.__doc__.strip())

    grouped = orders_df.groupby(["status", "priority"]).size().reset_index(name="count")

    fig = px.bar(
        grouped,
        x="status",
        y="count",
        color="priority",
        barmode="stack",
        title="Operations: Priority Mix by Status (Urgent vs Routine)"
    )
    fig.show()



# =========================================================
# MAIN (run everything)
# =========================================================
def main():

    # request / Get / Read orders data API
    orders_data = get_orders_data() 


    # Prepare and call ready data Pandas : cleanup / transform data adding / removing
    orders_df = prepare_orders_df(orders_data)


    # Operational boards
    flow_3_orders_backlog(orders_df)
    flow_4_priority_mix(orders_df)


if __name__ == "__main__":
    main()