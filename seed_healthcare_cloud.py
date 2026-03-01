import os
import time
import random
import string
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests


# =========================
# CONFIG
# =========================
BASE_URL = "https://talentifylabhealth-2edp.onrender.com/api"

ADMIN_USERNAME = "admin1"
ADMIN_PASSWORD = "Admin123"

# Data volume
STAFF_USERS_TOTAL = 40          # mix doctor + nurse
PATIENTS_TOTAL = 5000           # big dataset
ORDERS_PER_PATIENT = (1, 2)     # min/max orders per patient
TESTS_PER_ORDER = (2, 5)        # min/max test types per order

# Throttling / stability
REQUEST_TIMEOUT = 30
SLEEP_EVERY_N_REQUESTS = 50
SLEEP_SECONDS = 0.4

# If you re-run, consider starting from a different offset so usernames/emails remain unique.
RUN_SUFFIX = os.getenv("RUN_SUFFIX", "v1")


# =========================
# HELPERS: random identity
# =========================
FIRST_NAMES = ["John", "Maria", "David", "Sarah", "Michael", "Emily", "Daniel", "Olivia", "James", "Sophia"]
LAST_NAMES = ["Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas"]

def r_choice(xs): return xs[random.randint(0, len(xs) - 1)]

def rand_phone() -> str:
    # US-like dummy
    return f"+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"

def rand_ssn() -> str:
    # dummy format; not a real SSN
    return f"{random.randint(100, 899)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

def slug(n: int) -> str:
    return f"{n:05d}"

def safe_email(prefix: str) -> str:
    # unique-ish email (use your domain style)
    return f"{prefix}.{RUN_SUFFIX}@example.com"

def strong_password() -> str:
    return "Pass" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10)) + "!"

def rand_dob() -> str:
    year = random.randint(1950, 2006)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year:04d}-{month:02d}-{day:02d}"


# =========================
# “Accurate” test value generator
# (fallback to generic)
# =========================
def generate_value_for_test(test_name: str) -> Tuple[str, str]:
    """
    Returns (value_as_string, flag)
    flag: normal / abnormal / critical (swagger says these)
    :contentReference[oaicite:1]{index=1}
    """
    name = (test_name or "").lower()

    # Glucose fasting (mg/dL)
    if "glucose" in name:
        v = random.gauss(95, 12)
        v = max(50, min(240, v))
        flag = "normal" if 70 <= v <= 99 else ("abnormal" if v < 70 or v <= 180 else "critical")
        return (f"{v:.0f}", flag)

    # HbA1c (%)
    if "hba1c" in name or "a1c" in name:
        v = random.gauss(5.6, 0.7)
        v = max(4.0, min(14.0, v))
        flag = "normal" if v < 5.7 else ("abnormal" if v < 10 else "critical")
        return (f"{v:.1f}", flag)

    # LDL (mg/dL)
    if "ldl" in name:
        v = random.gauss(110, 30)
        v = max(30, min(300, v))
        flag = "normal" if v < 100 else ("abnormal" if v < 190 else "critical")
        return (f"{v:.0f}", flag)

    # HDL (mg/dL)
    if "hdl" in name:
        v = random.gauss(55, 12)
        v = max(15, min(120, v))
        flag = "normal" if v >= 40 else ("abnormal" if v >= 25 else "critical")
        return (f"{v:.0f}", flag)

    # Triglycerides (mg/dL)
    if "trig" in name:
        v = random.gauss(140, 60)
        v = max(30, min(800, v))
        flag = "normal" if v < 150 else ("abnormal" if v < 500 else "critical")
        return (f"{v:.0f}", flag)

    # Total cholesterol (mg/dL)
    if "cholesterol" in name and "total" in name:
        v = random.gauss(190, 35)
        v = max(80, min(400, v))
        flag = "normal" if v < 200 else ("abnormal" if v < 300 else "critical")
        return (f"{v:.0f}", flag)

    # Creatinine (mg/dL)
    if "creatinine" in name:
        v = random.gauss(1.0, 0.25)
        v = max(0.3, min(6.0, v))
        flag = "normal" if 0.6 <= v <= 1.3 else ("abnormal" if v < 3.0 else "critical")
        return (f"{v:.2f}", flag)

    # BUN (mg/dL)
    if "bun" in name:
        v = random.gauss(14, 6)
        v = max(3, min(120, v))
        flag = "normal" if 7 <= v <= 20 else ("abnormal" if v < 60 else "critical")
        return (f"{v:.0f}", flag)

    # WBC (K/uL)
    if "wbc" in name:
        v = random.gauss(7.0, 1.8)
        v = max(0.5, min(40.0, v))
        flag = "normal" if 4.0 <= v <= 11.0 else ("abnormal" if v < 25.0 else "critical")
        return (f"{v:.1f}", flag)

    # Hemoglobin Hgb (g/dL)
    if "hemoglobin" in name or "hgb" in name:
        v = random.gauss(14.0, 1.8)
        v = max(4.0, min(22.0, v))
        flag = "normal" if 12.0 <= v <= 17.5 else ("abnormal" if v < 20.0 else "critical")
        return (f"{v:.1f}", flag)

    # Urine protein (mg/dL)
    if "protein" in name and "urine" in name:
        v = abs(random.gauss(10, 20))
        v = max(0, min(400, v))
        flag = "normal" if v < 15 else ("abnormal" if v < 200 else "critical")
        return (f"{v:.0f}", flag)

    # Rapid covid/flu result (string)
    if "covid" in name or "flu" in name or "rapid" in name:
        value = "Negative" if random.random() < 0.85 else "Positive"
        flag = "normal" if value == "Negative" else "abnormal"
        return (value, flag)

    # generic numeric-ish fallback
    v = random.gauss(50, 15)
    v = max(0, min(999, v))
    return (f"{v:.1f}", "normal")


# =========================
# HTTP client
# =========================
@dataclass
class ApiClient:
    base_url: str
    token: Optional[str] = None
    request_count: int = 0

    def headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _throttle(self):
        self.request_count += 1
        if self.request_count % SLEEP_EVERY_N_REQUESTS == 0:
            time.sleep(SLEEP_SECONDS)

    def post(self, path: str, json: Optional[dict] = None) -> Any:
        self._throttle()
        url = self.base_url + path
        r = requests.post(url, headers=self.headers(), json=json, timeout=REQUEST_TIMEOUT)
        if not r.ok:
            raise RuntimeError(f"POST {path} failed: {r.status_code} {r.text[:300]}")
        return r.json() if r.text else None

    def put(self, path: str, json: Optional[dict] = None) -> Any:
        self._throttle()
        url = self.base_url + path
        r = requests.put(url, headers=self.headers(), json=json, timeout=REQUEST_TIMEOUT)
        if not r.ok:
            raise RuntimeError(f"PUT {path} failed: {r.status_code} {r.text[:300]}")
        return r.json() if r.text else None

    def get(self, path: str, params: Optional[dict] = None) -> Any:
        self._throttle()
        url = self.base_url + path
        r = requests.get(url, headers=self.headers(), params=params, timeout=REQUEST_TIMEOUT)
        if not r.ok:
            raise RuntimeError(f"GET {path} failed: {r.status_code} {r.text[:300]}")
        return r.json() if r.text else None


# =========================
# API actions (from swagger)
# =========================
def login_admin(client: ApiClient, username: str, password: str) -> str:
    # /auth/login expects Auth {username, password} :contentReference[oaicite:2]{index=2}
    resp = client.post("/auth/login", {"username": username, "password": password})
    # your system previously returned {"token": "..."} in earlier examples
    token = None
    if isinstance(resp, dict):
        token = resp.get("token") or resp.get("access_token") or resp.get("jwt")
    if not token:
        raise RuntimeError(f"Login succeeded but token not found in response: {resp}")
    client.token = token
    return token

def get_test_types(client: ApiClient) -> List[dict]:
    # GET /tests/types :contentReference[oaicite:3]{index=3}
    data = client.get("/tests/types")
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected test types response: {data}")
    return data

def create_user(client: ApiClient, first_name: str, last_name: str, email: str, username: str) -> dict:
    # POST /users with UserCreate required fields :contentReference[oaicite:4]{index=4}
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "ssn": rand_ssn(),
        "phone": rand_phone(),
        "username": username,
        "password": strong_password(),
    }
    return client.post("/users", payload)

def approve_user(client: ApiClient, user_id: int) -> None:
    # POST /users/{user_id}/approve :contentReference[oaicite:5]{index=5}
    client.post(f"/users/{user_id}/approve", {})

def update_user_role_status(client: ApiClient, user_id: int, role: str, status: str = "APPROVED") -> dict:
    # PUT /users/{user_id} with UserUpdate {role,status} :contentReference[oaicite:6]{index=6}
    return client.put(f"/users/{user_id}", {"role": role, "status": status})

def update_patient_profile(client: ApiClient, patient_id: int) -> dict:
    # PUT /patients/{patient_id} with PatientUpdate :contentReference[oaicite:7]{index=7}
    payload = {
        "date_of_birth": rand_dob(),
        "gender": random.choice(["M", "F"]),
        "current_status": random.choice(["INPATIENT", "OUTPATIENT"]),
        "admission_date": None,
        "discharge_date": None,
        "allergies": random.choice(["None", "Penicillin", "Peanuts", "Latex"]),
        "emergency_contact_name": f"{r_choice(FIRST_NAMES)} {r_choice(LAST_NAMES)}",
        "emergency_contact_phone": rand_phone(),
    }
    return client.put(f"/patients/{patient_id}", payload)

def create_assignment(client: ApiClient, doctor_user_id: int, patient_user_id: int) -> dict:
    # POST /assignments with Assignment :contentReference[oaicite:8]{index=8}
    payload = {"doctor_user_id": doctor_user_id, "patient_user_id": patient_user_id, "active": True}
    return client.post("/assignments", payload)

def create_order(client: ApiClient, patient_user_id: int, doctor_user_id: int, test_type_ids: List[int]) -> dict:
    # POST /orders with OrderCreate {patient_user_id, priority, test_type_ids, notes} :contentReference[oaicite:9]{index=9}
    payload = {
        "patient_user_id": patient_user_id,
        "priority": random.choice(["routine", "urgent"]),
        "test_type_ids": test_type_ids,
        "notes": f"Auto-generated order by doctor {doctor_user_id}",
    }
    return client.post("/orders", payload)

def create_result(client: ApiClient, order_id: int, test_type_id: int, value: str) -> dict:
    # POST /results with ResultCreate {order_id, test_type_id, value} :contentReference[oaicite:10]{index=10}
    return client.post("/results", {"order_id": order_id, "test_type_id": test_type_id, "value": value})

def update_result(client: ApiClient, result_id: int, patch: dict) -> dict:
    # PUT /results/{result_id} expects Result object :contentReference[oaicite:11]{index=11}
    return client.put(f"/results/{result_id}", patch)

def update_order_status(client: ApiClient, order_id: int, patch: dict) -> dict:
    # PUT /orders/{order_id} expects Order object; we’ll send minimal fields + status if allowed by backend :contentReference[oaicite:12]{index=12}
    return client.put(f"/orders/{order_id}", patch)


# =========================
# MAIN GENERATION
# =========================
def main():
    random.seed(42)

    client = ApiClient(BASE_URL)
    print("Logging in as admin...")
    token = login_admin(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    print("✅ Logged in. Token length:", len(token))

    # Get test types once
    test_types = get_test_types(client)
    # Expect items to have test_type_id + name (common); handle fallback keys
    test_type_id_name = []
    for t in test_types:
        tid = t.get("test_type_id") or t.get("id")
        name = t.get("name") or t.get("test_name") or str(tid)
        if tid is not None:
            test_type_id_name.append((int(tid), str(name)))
    if not test_type_id_name:
        raise RuntimeError("No test types found from /tests/types")

    print("✅ Test types:", len(test_type_id_name))

    # 1) Create staff users (mix of doctor/nurse)
    staff: List[dict] = []
    doctor_ids: List[int] = []
    nurse_ids: List[int] = []

    print(f"Creating {STAFF_USERS_TOTAL} staff users (doctor/nurse mix)...")
    for i in range(STAFF_USERS_TOTAL):
        first = r_choice(FIRST_NAMES)
        last = r_choice(LAST_NAMES)
        u = slug(i + 1)
        username = f"staff_{u}_{RUN_SUFFIX}"
        email = safe_email(username)

        created = create_user(client, first, last, email, username)
        user_id = int(created.get("user_id") or created.get("id"))
        approve_user(client, user_id)

        role = "DOCTOR" if (i % 2 == 0) else "NURSE"
        update_user_role_status(client, user_id, role=role, status="APPROVED")

        staff.append({"user_id": user_id, "role": role, "username": username})
        (doctor_ids if role == "DOCTOR" else nurse_ids).append(user_id)

        if (i + 1) % 10 == 0:
            print(f"  - staff created: {i+1}/{STAFF_USERS_TOTAL}")

    print("✅ Doctors:", len(doctor_ids), "| Nurses:", len(nurse_ids))

    # 2) Create patients + profiles + assignments + orders + results
    print(f"Creating {PATIENTS_TOTAL} patients + orders + results...")
    created_patients = 0
    created_orders = 0
    created_results = 0

    for p in range(PATIENTS_TOTAL):
        first = r_choice(FIRST_NAMES)
        last = r_choice(LAST_NAMES)
        u = slug(p + 1)
        username = f"patient_{u}_{RUN_SUFFIX}"
        email = safe_email(username)

        # create user
        created = create_user(client, first, last, email, username)
        patient_user_id = int(created.get("user_id") or created.get("id"))
        approve_user(client, patient_user_id)
        update_user_role_status(client, patient_user_id, role="PATIENT", status="APPROVED")

        # patient profile
        update_patient_profile(client, patient_user_id)

        # choose a doctor for this patient, assign
        doctor_user_id = random.choice(doctor_ids)
        create_assignment(client, doctor_user_id=doctor_user_id, patient_user_id=patient_user_id)

        # create orders (1-2 typical)
        n_orders = random.randint(ORDERS_PER_PATIENT[0], ORDERS_PER_PATIENT[1])
        for _ in range(n_orders):
            k_tests = random.randint(TESTS_PER_ORDER[0], TESTS_PER_ORDER[1])
            chosen = random.sample(test_type_id_name, k=k_tests)
            chosen_ids = [tid for tid, _ in chosen]

            order = create_order(client, patient_user_id=patient_user_id, doctor_user_id=doctor_user_id, test_type_ids=chosen_ids)
            order_id = int(order.get("order_id") or order.get("id"))
            created_orders += 1

            # nurse performs results for each test
            nurse_user_id = random.choice(nurse_ids)

            # mark order in progress (if backend allows partial patch; if not, it will raise)
            # If this fails in your backend, comment these 3 lines.
            try:
                update_order_status(client, order_id, {"status": "in_progress"})
            except Exception:
                pass

            for tid, tname in chosen:
                value, flag = generate_value_for_test(tname)
                res = create_result(client, order_id=order_id, test_type_id=tid, value=value)
                result_id = int(res.get("result_id") or res.get("id"))
                created_results += 1

                # update result with performed_by / flag / draft
                try:
                    update_result(client, result_id, {
                        "result_id": result_id,
                        "order_id": order_id,
                        "test_type_id": tid,
                        "value": value,
                        "flag": flag,
                        "performed_by": nurse_user_id,
                        "publish_status": "draft",
                    })
                except Exception:
                    # backend might auto-fill these; ignore if strict
                    pass

            # doctor reviews -> published
            try:
                update_order_status(client, order_id, {"status": "reviewed"})
                update_order_status(client, order_id, {"status": "published"})
            except Exception:
                pass

        created_patients += 1

        if (p + 1) % 100 == 0:
            print(f"  - patients: {p+1}/{PATIENTS_TOTAL} | orders: {created_orders} | results: {created_results}")

    print("\n✅ DONE")
    print("Patients:", created_patients)
    print("Orders:", created_orders)
    print("Results:", created_results)
    print("Staff:", len(staff))


if __name__ == "__main__":
    main()
