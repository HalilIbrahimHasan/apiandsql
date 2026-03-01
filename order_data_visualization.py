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

token = {
        "Authorization": f"Bearer {get_token()}"
    }


response = requests.get('https://talentifylabhealth.onrender.com/api/orders', headers=token)

print(response.status_code)


df = pd.DataFrame(response.json())

# date format
df["ordered_at"] = pd.to_datetime(df["ordered_at"], errors="coerce")

# ---------------------------------
# 2) CHART 1: Status distribution (pie)
# ---------------------------------
# fig1 = px.pie(
#     df,
#     names="status",
#     title="Order Status Distribution"
# )
# fig1.show()

# ---------------------------------
# 3) CHART 2: Priority count (bar)
# ---------------------------------
# priority_counts = df["priority"].value_counts().reset_index()
# priority_counts.columns = ["priority", "count"]

# fig2 = px.bar(
#     priority_counts,
#     x="priority",
#     y="count",
#     title="Order Priority Counts",
#     text="count"
# )
# fig2.show()

# ---------------------------------
# 4) CHART 3: Orders per Doctor (bar)
# ---------------------------------
# doctor_counts = df["ordered_by_doctor_id"].value_counts().reset_index()
# doctor_counts.columns = ["doctor-name", "test-order"]

# fig3 = px.bar(
#     doctor_counts,
#     x="doctor-name",
#     y="test-order",
#     title="Orders per Doctor",
#     text="test-order"
# )
# fig3.show()

# ---------------------------------
# 5) CHART 4: Patient User ID distribution (hist)
# # ---------------------------------
# fig4 = px.histogram(
#     df,
#     x="patient_user_id",
#     nbins=10,
#     title="Patient User ID Distribution"
# )
# fig4.show()

# ---------------------------------
# 6) CHART 5: Orders timeline (scatter)
# ---------------------------------
fig5 = px.scatter(
    df,
    x="ordered_at",
    y="order_id",
    color="status",
    hover_data=["patient_user_id", "ordered_by_doctor_id", "priority", "notes"],
    title="Orders Timeline"
)
fig5.show()
