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


def get_patients_data():
    token = {
            "Authorization": f"Bearer {get_token()}"
        }


    response = requests.get('https://talentifylabhealth.onrender.com/api/patients', headers=token)

    print(response.status_code)

    return response.json()



def prepare_patients_df(data):
    df = pd.DataFrame(data)

    # WHY: empty strings should be treated as missing values.
    for col in ["admission_date", "discharge_date"]:
        if col in df.columns:
            df[col] = df[col].replace("", pd.NA)
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # WHY: normalize status.
    df["current_status"] = df["current_status"].astype(str).str.strip().str.upper()

    return df