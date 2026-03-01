import pandas as pd
import plotly.express as px


# -----------------------------
# 1) DATA (API'den gelmiş gibi)
# -----------------------------
def get_patient_data():
    data = [
        {
            "patient_id": 6,
            "first_name": "John",
            "last_name": "Patient",
            "email": "pjohn@example.com",
            "date_of_birth": "1980-05-15",
            "gender": "M",
            "current_status": "OUTPATIENT",
            "admission_date": None,
            "discharge_date": None,
            "allergies": "Penicillin"
        },
        {
            "patient_id": 7,
            "first_name": "Maria",
            "last_name": "Patient",
            "email": "pmaria@example.com",
            "date_of_birth": "1975-08-22",
            "gender": "F",
            "current_status": "OUTPATIENT",
            "admission_date": None,
            "discharge_date": None,
            "allergies": "None"
        },
        {
            "patient_id": 8,
            "first_name": "Kevin",
            "last_name": "Patient",
            "email": "pkevin@example.com",
            "date_of_birth": "1990-12-10",
            "gender": "M",
            "current_status": "INPATIENT",
            "admission_date": "2026-02-01",
            "discharge_date": None,
            "allergies": "Latex"
        }
    ]

    return data


# -----------------------------
# 2) Convert to DataFrame + clean
# -----------------------------
def prepare_dataframe(data):
    df = pd.DataFrame(data)

    # Convert string dates to real datetime
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"])
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
    data = get_patient_data()
    df = prepare_dataframe(data)

    chart_gender(df)
    chart_status(df)
    chart_age(df)
    chart_allergies(df)
    chart_admissions(df)


if __name__ == "__main__":
    main()
