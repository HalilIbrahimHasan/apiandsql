import requests
import pandas as pd
import plotly.express as px




def get_token():
    url = "https://talentifylabhealth-2edp.onrender.com/api/auth/login"

    credentials = {
        "username": "admin1",
        "password": "Admin123"
    }

    resp = requests.post(url, json=credentials)
    resp.raise_for_status()

    return resp.json()["token"]


def get_results(token):
    url = "https://talentifylabhealth-2edp.onrender.com/api/patients"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


# -----------------------------
# 2) Convert to DataFrame + clean
# -----------------------------
def prepare_dataframe(data):
    df = pd.DataFrame(data)

    # Convert string dates to real datetime
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"],errors="coerce")
    df["admission_date"] = pd.to_datetime(df["admission_date"], errors="coerce")
    df["discharge_date"] = pd.to_datetime(df["discharge_date"], errors="coerce")

    # Create AGE column
    today = pd.Timestamp.today()
    df["age"] = ((today - df["date_of_birth"]).dt.days / 365.25).astype(int)

    return df


# -----------------------------
# 3) Chart 1: Gender Distribution
# -----------------------------
def chart_gender(df):
    fig = px.pie(df, names="gender", title="Gender Distribution")
    fig.show()


# -----------------------------
# 4) Chart 2: Patient Status Counts
# -----------------------------
def chart_status(df):
    status_counts = df["current_status"].value_counts().reset_index()
    status_counts.columns = ["current_status", "count"]

    fig = px.bar(
        status_counts,
        x="current_status",
        y="count",
        title="Patient Status Counts",
        text="count"
    )
    fig.show()


# -----------------------------
# 5) Chart 3: Age Distribution
# -----------------------------
def chart_age(df):
    fig = px.histogram(df, x="age", nbins=10, title="Age Distribution")
    fig.show()


# -----------------------------
# 6) Chart 4: Allergies Frequency
# -----------------------------
def chart_allergies(df):
    allergy_counts = df["allergies"].value_counts().reset_index()
    allergy_counts.columns = ["allergies", "count"]

    fig = px.bar(
        allergy_counts,
        x="allergies",
        y="count",
        title="Allergies Frequency",
        text="count"
    )
    fig.show()


# -----------------------------
# 7) Chart 5: Admissions Timeline
# -----------------------------
def chart_admissions(df):
    admitted = df.dropna(subset=["admission_date"])

    fig = px.scatter(
        admitted,
        x="admission_date",
        y="patient_id",
        color="current_status",
        hover_data=["first_name", "last_name", "gender", "age"],
        title="Admissions Timeline"
    )
    fig.show()


# -----------------------------
# MAIN (run everything)
# -----------------------------
def main():

    print(get_token())

    token = get_token()
    data = get_results(token)
    print(data)

    # data = get_results(get_token())
    df = prepare_dataframe(data)

    chart_gender(df)
    # chart_status(df)
    # chart_age(df)
    # chart_allergies(df)
    # chart_admissions(df)


if __name__ == "__main__":
    main()
