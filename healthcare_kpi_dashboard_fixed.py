from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


BASE_URL = os.getenv("HEALTH_API_BASE_URL", "https://talentifylabhealth.onrender.com")
USERNAME = os.getenv("HEALTH_API_USERNAME", "admin1")
PASSWORD = os.getenv("HEALTH_API_PASSWORD", "Admin123")
OUTPUT_DIR = os.getenv("HEALTH_KPI_OUTPUT_DIR", ".")


@dataclass
class ApiConfig:
    base_url: str
    username: str
    password: str


class HealthcareApiClient:
    def __init__(self, config: ApiConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.token: Optional[str] = None

    def login(self) -> None:
        url = f"{self.config.base_url}/api/auth/login"
        resp = self.session.post(
            url,
            json={"username": self.config.username, "password": self.config.password},
            timeout=60,
        )
        resp.raise_for_status()
        body = resp.json()
        self.token = body.get("token")
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def get_json(self, endpoint: str) -> Any:
        url = f"{self.config.base_url}{endpoint}"
        resp = self.session.get(url, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def fetch_users(self) -> pd.DataFrame:
        data = self.get_json("/api/users")
        return pd.DataFrame(data if isinstance(data, list) else [data])

    def fetch_orders(self) -> pd.DataFrame:
        data = self.get_json("/api/orders")
        return pd.DataFrame(data if isinstance(data, list) else [data])

    def fetch_results(self) -> pd.DataFrame:
        data = self.get_json("/api/results")
        return pd.DataFrame(data if isinstance(data, list) else [data])

    def fetch_invoices(self) -> pd.DataFrame:
        data = self.get_json("/api/billing/invoices")
        return pd.DataFrame(data if isinstance(data, list) else [data])

    def fetch_test_types(self) -> pd.DataFrame:
        data = self.get_json("/api/tests/types")
        return pd.DataFrame(data if isinstance(data, list) else [data])


def _ensure_columns(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df


def _to_datetime(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def clean_users(users: pd.DataFrame) -> pd.DataFrame:
    users = users.copy()
    users = _ensure_columns(users, [
        "user_id", "first_name", "last_name", "username", "role",
        "status", "created_at", "updated_at"
    ])
    users["full_name"] = (
        users["first_name"].fillna("").astype(str).str.strip() + " " +
        users["last_name"].fillna("").astype(str).str.strip()
    ).str.strip()
    users["display_name"] = users["full_name"].where(users["full_name"].ne(""), users["username"])
    users = _to_datetime(users, ["created_at", "updated_at"])
    return users


def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    orders = orders.copy()
    orders = _ensure_columns(orders, [
        "order_id", "patient_user_id", "ordered_by_doctor_id",
        "ordered_at", "priority", "status", "notes"
    ])
    for c in ["order_id", "patient_user_id", "ordered_by_doctor_id"]:
        orders[c] = pd.to_numeric(orders[c], errors="coerce").astype("Int64")
    orders = _to_datetime(orders, ["ordered_at"])
    orders["order_month"] = orders["ordered_at"].dt.to_period("M").astype(str)
    return orders


def clean_results(results: pd.DataFrame) -> pd.DataFrame:
    results = results.copy()
    results = _ensure_columns(results, [
        "result_id", "order_id", "test_type_id", "performed_by", "performed_at",
        "value", "flag", "doctor_reviewed_by", "doctor_reviewed_at",
        "publish_status", "published_at"
    ])
    for c in ["result_id", "order_id", "test_type_id", "performed_by", "doctor_reviewed_by"]:
        results[c] = pd.to_numeric(results[c], errors="coerce").astype("Int64")
    results = _to_datetime(results, ["performed_at", "doctor_reviewed_at", "published_at"])
    results["numeric_value"] = pd.to_numeric(results["value"], errors="coerce")
    results["hours_to_review"] = (
        (results["doctor_reviewed_at"] - results["performed_at"]).dt.total_seconds() / 3600
    )
    results["hours_to_publish"] = (
        (results["published_at"] - results["performed_at"]).dt.total_seconds() / 3600
    )
    results["is_published"] = results["publish_status"].astype(str).str.lower().eq("published") | results["published_at"].notna()
    return results


def clean_invoices(invoices: pd.DataFrame) -> pd.DataFrame:
    invoices = invoices.copy()
    invoices = _ensure_columns(invoices, [
        "invoice_id", "patient_user_id", "patient_id",
        "total", "status", "created_at", "paid_at"
    ])
    invoices["patient_user_id"] = pd.to_numeric(invoices["patient_user_id"], errors="coerce").astype("Int64")
    invoices["patient_id"] = pd.to_numeric(invoices["patient_id"], errors="coerce").astype("Int64")
    invoices["patient_key"] = invoices["patient_user_id"].fillna(invoices["patient_id"]).astype("Int64")
    invoices["invoice_id"] = pd.to_numeric(invoices["invoice_id"], errors="coerce").astype("Int64")
    invoices["total"] = pd.to_numeric(invoices["total"], errors="coerce")
    invoices = _to_datetime(invoices, ["created_at", "paid_at"])
    invoices["days_to_pay"] = (
        (invoices["paid_at"] - invoices["created_at"]).dt.total_seconds() / 86400
    )
    return invoices


def clean_test_types(test_types: pd.DataFrame) -> pd.DataFrame:
    test_types = test_types.copy()
    test_types = _ensure_columns(test_types, [
        "test_type_id", "name", "unit", "result_type",
        "normal_min", "normal_max", "critical_min", "critical_max"
    ])
    test_types["test_type_id"] = pd.to_numeric(test_types["test_type_id"], errors="coerce").astype("Int64")
    for c in ["normal_min", "normal_max", "critical_min", "critical_max"]:
        test_types[c] = pd.to_numeric(test_types[c], errors="coerce")
    return test_types


def build_model(users: pd.DataFrame, orders: pd.DataFrame, results: pd.DataFrame,
                invoices: pd.DataFrame, test_types: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    users = clean_users(users)
    orders = clean_orders(orders)
    results = clean_results(results)
    invoices = clean_invoices(invoices)
    test_types = clean_test_types(test_types)

    doctors = users[users["username"].astype(str).str.startswith("doc", na=False)].copy()
    nurses = users[users["username"].astype(str).str.startswith("nurse", na=False)].copy()
    patients = users[users["username"].astype(str).str.startswith("patient", na=False)].copy()

    orders_enriched = orders.merge(
        doctors[["user_id", "display_name", "username"]].rename(columns={
            "user_id": "ordered_by_doctor_id",
            "display_name": "ordering_doctor_name",
            "username": "ordering_doctor_username"
        }),
        on="ordered_by_doctor_id",
        how="left"
    ).merge(
        patients[["user_id", "display_name", "username"]].rename(columns={
            "user_id": "patient_user_id",
            "display_name": "patient_name",
            "username": "patient_username"
        }),
        on="patient_user_id",
        how="left"
    )

    results_enriched = results.merge(
        test_types[["test_type_id", "name", "unit", "result_type"]],
        on="test_type_id",
        how="left"
    ).merge(
        nurses[["user_id", "display_name", "username"]].rename(columns={
            "user_id": "performed_by",
            "display_name": "nurse_name",
            "username": "nurse_username"
        }),
        on="performed_by",
        how="left"
    ).merge(
        doctors[["user_id", "display_name", "username"]].rename(columns={
            "user_id": "doctor_reviewed_by",
            "display_name": "reviewing_doctor_name",
            "username": "reviewing_doctor_username"
        }),
        on="doctor_reviewed_by",
        how="left"
    ).merge(
        orders_enriched[["order_id", "patient_user_id", "ordered_by_doctor_id", "ordering_doctor_name", "patient_name", "ordered_at", "priority", "status"]],
        on="order_id",
        how="left"
    )

    invoices_enriched = invoices.merge(
        patients[["user_id", "display_name", "username"]].rename(columns={
            "user_id": "patient_key",
            "display_name": "patient_name",
            "username": "patient_username"
        }),
        on="patient_key",
        how="left"
    )

    return {
        "users": users,
        "orders": orders_enriched,
        "results": results_enriched,
        "invoices": invoices_enriched,
        "test_types": test_types,
        "doctors": doctors,
        "nurses": nurses,
        "patients": patients,
    }


def kpi_summary(model: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    orders = model["orders"]
    results = model["results"]
    invoices = model["invoices"]

    summary = {
        "total_orders": int(orders["order_id"].nunique()) if not orders.empty else 0,
        "total_results": int(results["result_id"].nunique()) if not results.empty else 0,
        "published_results": int(results.loc[results["is_published"], "result_id"].nunique()) if not results.empty else 0,
        "publish_rate_pct": round(100 * results["is_published"].mean(), 2) if not results.empty else 0.0,
        "avg_hours_to_review": round(results["hours_to_review"].dropna().mean(), 2) if not results.empty else 0.0,
        "avg_hours_to_publish": round(results["hours_to_publish"].dropna().mean(), 2) if not results.empty else 0.0,
        "invoice_count": int(invoices["invoice_id"].nunique()) if not invoices.empty else 0,
        "total_billed": round(invoices["total"].fillna(0).sum(), 2) if not invoices.empty else 0.0,
        "avg_invoice_amount": round(invoices["total"].dropna().mean(), 2) if not invoices.empty else 0.0,
        "paid_invoice_rate_pct": round(
            100 * invoices["status"].astype(str).str.lower().eq("paid").mean(), 2
        ) if not invoices.empty else 0.0,
    }
    return pd.DataFrame([summary])


def doctor_performance_kpis(model: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    orders = model["orders"]
    results = model["results"]

    ordered = (
        orders.groupby(["ordered_by_doctor_id", "ordering_doctor_name"], dropna=False)
        .agg(
            orders_created=("order_id", "nunique"),
            unique_patients=("patient_user_id", "nunique")
        )
        .reset_index()
    )

    reviewed = (
        results.groupby(["doctor_reviewed_by", "reviewing_doctor_name"], dropna=False)
        .agg(
            results_reviewed=("result_id", "nunique"),
            published_results=("is_published", "sum"),
            avg_review_hours=("hours_to_review", "mean"),
            avg_publish_hours=("hours_to_publish", "mean")
        )
        .reset_index()
    )

    merged = ordered.merge(
        reviewed,
        left_on="ordered_by_doctor_id",
        right_on="doctor_reviewed_by",
        how="outer"
    )

    merged["doctor_name"] = merged["ordering_doctor_name"].combine_first(merged["reviewing_doctor_name"])
    merged["orders_created"] = merged["orders_created"].fillna(0).astype(int)
    merged["unique_patients"] = merged["unique_patients"].fillna(0).astype(int)
    merged["results_reviewed"] = merged["results_reviewed"].fillna(0).astype(int)
    merged["published_results"] = merged["published_results"].fillna(0).astype(int)
    merged["avg_review_hours"] = merged["avg_review_hours"].round(2)
    merged["avg_publish_hours"] = merged["avg_publish_hours"].round(2)

    return merged[[
        "doctor_name", "orders_created", "unique_patients",
        "results_reviewed", "published_results",
        "avg_review_hours", "avg_publish_hours"
    ]].sort_values(["orders_created", "results_reviewed"], ascending=False)


def nurse_performance_kpis(model: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    results = model["results"]
    if results.empty:
        return pd.DataFrame(columns=["staff_name", "results_performed", "avg_publish_hours", "critical_results", "abnormal_results"])

    out = (
        results.groupby(["performed_by", "nurse_name"], dropna=False)
        .agg(
            results_performed=("result_id", "nunique"),
            avg_publish_hours=("hours_to_publish", "mean"),
            critical_results=("flag", lambda s: s.astype(str).str.lower().eq("critical").sum()),
            abnormal_results=("flag", lambda s: s.astype(str).str.lower().isin(["abnormal", "high"]).sum())
        )
        .reset_index()
        .rename(columns={"nurse_name": "staff_name"})
    )
    out["avg_publish_hours"] = out["avg_publish_hours"].round(2)
    return out.sort_values("results_performed", ascending=False)


def test_type_kpis(model: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    results = model["results"]
    if results.empty:
        return pd.DataFrame(columns=["test_name", "result_count", "published_rate_pct", "avg_numeric_value", "critical_rate_pct"])

    out = (
        results.groupby("name", dropna=False)
        .agg(
            result_count=("result_id", "nunique"),
            published_rate_pct=("is_published", "mean"),
            avg_numeric_value=("numeric_value", "mean"),
            critical_rate_pct=("flag", lambda s: s.astype(str).str.lower().eq("critical").mean())
        )
        .reset_index()
        .rename(columns={"name": "test_name"})
    )
    out["published_rate_pct"] = (out["published_rate_pct"] * 100).round(2)
    out["critical_rate_pct"] = (out["critical_rate_pct"] * 100).round(2)
    out["avg_numeric_value"] = out["avg_numeric_value"].round(2)
    return out.sort_values("result_count", ascending=False)


def billing_kpis(model: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    invoices = model["invoices"]
    if invoices.empty:
        return pd.DataFrame(columns=["patient_name", "invoice_count", "total_billed", "avg_days_to_pay", "paid_invoices"])

    out = (
        invoices.groupby(["patient_key", "patient_name"], dropna=False)
        .agg(
            invoice_count=("invoice_id", "nunique"),
            total_billed=("total", "sum"),
            avg_days_to_pay=("days_to_pay", "mean"),
            paid_invoices=("status", lambda s: s.astype(str).str.lower().eq("paid").sum())
        )
        .reset_index()
    )
    out["total_billed"] = out["total_billed"].round(2)
    out["avg_days_to_pay"] = out["avg_days_to_pay"].round(2)
    return out.sort_values("total_billed", ascending=False)


def order_trend_chart(model: Dict[str, pd.DataFrame]) -> go.Figure:
    orders = model["orders"]
    if orders.empty:
        return px.bar(pd.DataFrame({"order_month": [], "orders": []}), x="order_month", y="orders", title="Orders by Month")
    trend = (
        orders.groupby("order_month", dropna=False)["order_id"]
        .nunique()
        .reset_index(name="orders")
        .sort_values("order_month")
    )
    return px.bar(trend, x="order_month", y="orders", title="Orders by Month")


def doctor_orders_chart(model: Dict[str, pd.DataFrame]) -> go.Figure:
    df = doctor_performance_kpis(model).head(15)
    if df.empty:
        return px.bar(pd.DataFrame({"doctor_name": [], "orders_created": []}), x="doctor_name", y="orders_created", title="Top Doctors by Orders")
    return px.bar(df, x="doctor_name", y="orders_created", title="Top Doctors by Orders")


def nurse_results_chart(model: Dict[str, pd.DataFrame]) -> go.Figure:
    df = nurse_performance_kpis(model).head(15)
    if df.empty:
        return px.bar(pd.DataFrame({"staff_name": [], "results_performed": []}), x="staff_name", y="results_performed", title="Top Nurses/Lab Staff by Results")
    return px.bar(df, x="staff_name", y="results_performed", title="Top Nurses/Lab Staff by Results")


def publish_status_chart(model: Dict[str, pd.DataFrame]) -> go.Figure:
    results = model["results"]
    if results.empty:
        return px.pie(pd.DataFrame({"status": [], "count": []}), names="status", values="count", title="Published vs Not Published")
    df = pd.DataFrame({
        "status": ["Published", "Not Published"],
        "count": [int(results["is_published"].sum()), int((~results["is_published"]).sum())]
    })
    return px.pie(df, names="status", values="count", title="Published vs Not Published")


def invoice_status_chart(model: Dict[str, pd.DataFrame]) -> go.Figure:
    invoices = model["invoices"]
    if invoices.empty:
        return px.bar(pd.DataFrame({"status": [], "count": []}), x="status", y="count", title="Invoices by Status")
    df = (
        invoices.assign(status=invoices["status"].astype(str).str.title())
        .groupby("status")["invoice_id"]
        .nunique()
        .reset_index(name="count")
    )
    return px.bar(df, x="status", y="count", title="Invoices by Status")


def critical_tests_chart(model: Dict[str, pd.DataFrame]) -> go.Figure:
    df = test_type_kpis(model).head(15)
    if df.empty:
        return px.bar(pd.DataFrame({"test_name": [], "critical_rate_pct": []}), x="test_name", y="critical_rate_pct", title="Critical Rate by Test Type")
    return px.bar(df, x="test_name", y="critical_rate_pct", title="Critical Rate by Test Type")


def save_outputs(model: Dict[str, pd.DataFrame]) -> None:
    out_dir = OUTPUT_DIR
    summary = kpi_summary(model)
    doctor_kpis = doctor_performance_kpis(model)
    nurse_kpis = nurse_performance_kpis(model)
    test_kpis = test_type_kpis(model)
    bill_kpis = billing_kpis(model)

    summary.to_csv(f"{out_dir}/kpi_summary.csv", index=False)
    doctor_kpis.to_csv(f"{out_dir}/doctor_kpis.csv", index=False)
    nurse_kpis.to_csv(f"{out_dir}/nurse_kpis.csv", index=False)
    test_kpis.to_csv(f"{out_dir}/test_type_kpis.csv", index=False)
    bill_kpis.to_csv(f"{out_dir}/billing_kpis.csv", index=False)

    figs = [
        order_trend_chart(model),
        doctor_orders_chart(model),
        nurse_results_chart(model),
        publish_status_chart(model),
        invoice_status_chart(model),
        critical_tests_chart(model),
    ]
    titles = [
        "orders_by_month",
        "top_doctors_by_orders",
        "top_nurses_by_results",
        "publish_status_split",
        "invoice_status_split",
        "critical_rate_by_test_type",
    ]

    for fig, title in zip(figs, titles):
        fig.write_html(f"{out_dir}/{title}.html", include_plotlyjs="cdn")

    combined_path = f"{out_dir}/healthcare_kpi_dashboard.html"
    with open(combined_path, "w", encoding="utf-8") as f:
        f.write("<html><head><title>Healthcare KPI Dashboard</title></head><body>")
        f.write("<h1>Healthcare KPI Dashboard</h1>")
        f.write("<h2>Summary</h2>")
        f.write(summary.to_html(index=False))
        for fig, title in zip(figs, titles):
            f.write(f"<h2>{title.replace('_', ' ').title()}</h2>")
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write("</body></html>")

    print("Saved files:")
    for name in [
        "kpi_summary.csv",
        "doctor_kpis.csv",
        "nurse_kpis.csv",
        "test_type_kpis.csv",
        "billing_kpis.csv",
        "orders_by_month.html",
        "top_doctors_by_orders.html",
        "top_nurses_by_results.html",
        "publish_status_split.html",
        "invoice_status_split.html",
        "critical_rate_by_test_type.html",
        "healthcare_kpi_dashboard.html",
    ]:
        print(f" - {out_dir}/{name}")


def main() -> None:
    config = ApiConfig(
        base_url=BASE_URL,
        username=USERNAME,
        password=PASSWORD,
    )
    client = HealthcareApiClient(config)
    client.login()

    users = client.fetch_users()
    orders = client.fetch_orders()
    results = client.fetch_results()
    invoices = client.fetch_invoices()
    test_types = client.fetch_test_types()

    model = build_model(users, orders, results, invoices, test_types)
    save_outputs(model)


if __name__ == "__main__":
    main()