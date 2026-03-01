import pandas as pd
import plotly.express as px

# -----------------------------
# 1) DATA (API'den gelmiş gibi)
# -----------------------------
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

df = pd.DataFrame(data)

# date format
df["date_of_birth"] = pd.to_datetime(df["date_of_birth"])
df["admission_date"] = pd.to_datetime(df["admission_date"], errors="coerce")
df["discharge_date"] = pd.to_datetime(df["discharge_date"], errors="coerce")

# age
today = pd.Timestamp.today()
df["age"] = ((today - df["date_of_birth"]).dt.days / 365.25).astype(int)

# ---------------------------------
# 2) CHART 1: Gender distribution
# ---------------------------------
# fig1 = px.pie(
#     df,
#     names="gender",
#     title="Gender Distribution"
# )
# fig1.show()

# # ---------------------------------
# # 3) CHART 2: Patient Status count
# # ---------------------------------
# status_counts = df["current_status"].value_counts().reset_index()
# status_counts.columns = ["current_status", "count"]

# fig2 = px.bar(
#     status_counts,
#     x="current_status",
#     y="count",
#     title="Patient Status Counts",
#     text="count"
# )
# fig2.show()

# # ---------------------------------
# # 4) CHART 3: Age distribution (hist)
# # ---------------------------------
# fig3 = px.histogram(
#     df,
#     x="age",
#     nbins=10,
#     title="Age Distribution"
# )
# fig3.show()

# ---------------------------------
# 5) CHART 4: Allergies count
# ---------------------------------
allergy_counts = df["allergies"].value_counts().reset_index()
allergy_counts.columns = ["allergies", "count"]

fig4 = px.bar(
    allergy_counts,
    x="allergies",
    y="count",
    title="Allergies Frequency",
    text="count"
)
fig4.show()

# ---------------------------------
# 6) CHART 5: Admission timeline (scatter)
# (Only shows patients who have admission_date)
# ---------------------------------
# admitted = df.dropna(subset=["admission_date"])

# fig5 = px.scatter(
#     admitted,
#     x="admission_date",
#     y="patient_id",
#     color="current_status",
#     hover_data=["first_name", "last_name", "gender", "age"],
#     title="Admissions Timeline"
# )
# fig5.show()
