import pandas as pd
import plotly.express as px
import requests

# -----------------------------
# 1) DATA (API'den gelmiş gibi)
# -----------------------------
def get_token():
    url = "https://talentifylabhealth.onrender.com/api/auth/login"

    credentials = {
        "username": "admin1",
        "password": "Admin123"
    }

    resp = requests.post(url, json=credentials)
    resp.raise_for_status()

    return resp.json()["token"]


def get_invoices_data():
    token = {
            "Authorization": f"Bearer {get_token()}"
        }


    response = requests.get('https://talentifylabhealth.onrender.com/api/billing/invoices', headers=token)

    print(response.status_code)

    return response.json()



def prepare_invoices_df(data):
    df = pd.DataFrame(data)

    # WHY: created_at datetime for trend analysis (revenue over time).
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    # WHY: status normalized (Paid vs paid).
    df["status"] = df["status"].astype(str).str.strip().str.lower()

    # WHY: total numeric for sums.
    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0.0)

    return df


# -----------------------------
# FLOW 6: Billing / Cashflow Board (Paid vs Unpaid)
# -----------------------------
def flow_6_billing_cashflow(invoices_df):
    """
    DESCRIPTION (Business):
    Finance checks paid vs unpaid invoices to manage cashflow and accounts receivable (AR).
    This chart quickly shows if unpaid invoices are growing.
    """
    print("\nFLOW 6:", flow_6_billing_cashflow.__doc__.strip())

    counts = invoices_df["status"].value_counts().reset_index()
    counts.columns = ["status", "count"]

    fig = px.pie(
        counts,
        names="status",
        values="count",
        title="Finance Board: Paid vs Unpaid (Cashflow / AR)"
    )
    fig.show()



# =========================================================
# MAIN (run everything)
# =========================================================
def main():
    # request / Get / Read billing data API
     invoices_data = get_invoices_data()

     # Prepare and call ready data Pandas : cleanup / transform data adding / removing
     invoices_df = prepare_invoices_df(invoices_data)

     # Capacity & finance boards
     flow_6_billing_cashflow(invoices_df)