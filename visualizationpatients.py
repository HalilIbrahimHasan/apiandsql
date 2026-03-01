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


def get_patients_data():
    token = {
            "Authorization": f"Bearer {get_token()}"
        }


    response = requests.get('https://talentifylabhealth-2edp.onrender.com/api/patients', headers=token)

    print(response.status_code)

    return response.json()