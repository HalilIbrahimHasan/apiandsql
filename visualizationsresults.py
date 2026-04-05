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


# =========================================================
# 1) DATA (as if it came from API)
#    Later you will replace these functions with API calls.
# =========================================================
def get_results_data():

    token = {
            "Authorization": f"Bearer {get_token()}"
        }


    response = requests.get('https://talentifylabhealth.onrender.com/api/results', headers=token)

    print(response.status_code)

    return response.json()



    # =========================================================
# 2) Convert to DataFrame + CLEANUP (with WHY)
# =========================================================
def prepare_results_df(data):
    df = pd.DataFrame(data)

    # WHY: API returns dates as strings; datetime is needed to compute durations (SLA/TAT).
    df["ordered_at"] = pd.to_datetime(df["ordered_at"], errors="coerce")
    df["performed_at"] = pd.to_datetime(df["performed_at"], errors="coerce")
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")

    # WHY: "value" arrives as string; numeric allows thresholds & analytics (min/max, distribution).
    df["value_num"] = pd.to_numeric(df["value"], errors="coerce")

    # WHY: normalize text fields to avoid "Normal" vs "normal" bugs in groupby.
    df["flag"] = df["flag"].astype(str).str.strip().str.lower()
    df["publish_status"] = df["publish_status"].astype(str).str.strip().str.lower()
    df["test_name"] = df["test_name"].astype(str).str.strip()

    # WHY: missing names break charts; fill with "Unknown".
    df["performed_by_name"] = df.get("performed_by_name", pd.Series([])).fillna("Unknown").astype(str).str.strip()
    df["doctor_name"] = df.get("doctor_name", pd.Series([])).fillna("Unknown").astype(str).str.strip()

    # WHY: define a computed "is_critical" using clinical thresholds when available.
    # rule: critical if numeric and outside [critical_min, critical_max] OR flag == "critical"
    df["is_critical"] = False
    numeric_mask = df["result_type"].astype(str).str.lower().eq("numeric") & df["value_num"].notna()
    df.loc[numeric_mask, "is_critical"] = (
        (df.loc[numeric_mask, "value_num"] < pd.to_numeric(df.loc[numeric_mask, "critical_min"], errors="coerce")) |
        (df.loc[numeric_mask, "value_num"] > pd.to_numeric(df.loc[numeric_mask, "critical_max"], errors="coerce"))
    )
    df["is_critical"] = df["is_critical"] | df["flag"].eq("critical")

    # WHY: SLA metric: minutes from order to performed (lab turnaround).
    df["tat_order_to_perform_min"] = (df["performed_at"] - df["ordered_at"]).dt.total_seconds() / 60

    return df



    # =========================================================
# 3) WORKFLOWS (linked like a real business board)
#    Flow A finds critical results; Flow B checks if processed on time.
# =========================================================

# -----------------------------
# FLOW 1: Critical Results Board (Clinical Risk Board)
# -----------------------------
def flow_1_critical_results_board(results_df):
    """
    DESCRIPTION (Business):
    We check test results to see if any CRITICAL values exist on the board.
    If critical values exist, the next workflow will verify whether these orders were processed on time (SLA / TAT).
    """
    print("\nFLOW 1:", flow_1_critical_results_board.__doc__.strip())

    critical_counts = (
        results_df.assign(critical_label=lambda d: d["is_critical"].map({True: "critical", False: "not_critical"}))
        ["critical_label"]
        .value_counts()
        .reset_index()
    )
    critical_counts.columns = ["critical_label", "count"]

    fig = px.pie(
    critical_counts,
    names="critical_label",
    values="count",
    title="Clinical Risk Board: Critical vs Not Critical Results",
    color="critical_label",
    color_discrete_map={
        "Critical": "red",
        "Not Critical": "blue"
    }
    )
    fig.show()

    return results_df[results_df["is_critical"] == True].copy()



    # -----------------------------
# FLOW 2: SLA / Turnaround Check for Critical Results
# -----------------------------
def flow_2_sla_check_for_critical(critical_results_df):
    """
    DESCRIPTION (Business):
    If a result is critical, we must ensure it was processed quickly (Turnaround Time / SLA).
    This chart shows the distribution of minutes from ORDERED -> PERFORMED for critical results.
    """
    print("\nFLOW 2:", flow_2_sla_check_for_critical.__doc__.strip())

    # If there are no critical rows in the sample, still show empty-safe behavior.
    if critical_results_df.empty:
        print("No critical rows found in this sample. (On real data, this chart will populate.)")
        return

    fig = px.histogram(
        critical_results_df,
        x="tat_order_to_perform_min",
        nbins=10,
        title="SLA Check: Critical Results Turnaround Time (minutes)"
    )
    fig.show()


    # -----------------------------
# FLOW 5: Lab Productivity (Results entered per staff)
# -----------------------------
def flow_5_lab_productivity(results_df):
    """
    DESCRIPTION (Business):
    Lab managers check staff throughput to ensure enough capacity (nurse/lab workload).
    This chart shows how many results each staff member entered.
    """
    print("\nFLOW 5:", flow_5_lab_productivity.__doc__.strip())

    staff_counts = results_df["performed_by_name"].value_counts().reset_index()
    staff_counts.columns = ["performed_by_name", "result_count"]

    fig = px.bar(
        staff_counts,
        x="performed_by_name",
        y="result_count",
        text="result_count",
        title="Lab Board: Results Entered per Staff (Productivity)"
    )
    fig.show()


    


   # =========================================================
    # MAIN (run everything)
    # =========================================================

if __name__ == "__main__":
     # request / Get / Read orders data API
    results_data = get_results_data()

     # Prepare and call ready data Pandas : cleanup / transform data adding / removing
    results_df = prepare_results_df(results_data)


     # Linked workflows (A -> B) Find critical cases / results display board & Check sla respected
    critical_df = flow_1_critical_results_board(results_df)
    flow_2_sla_check_for_critical(critical_df)
    
    # Capacity & finance boards
    flow_5_lab_productivity(results_df)