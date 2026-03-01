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

# Only create MORE patients (reuse existing doctors/nurses)
NEW_PATIENTS_TOTAL = 500
PATIENT_START = int(os.getenv("PATIENT_START", "2000"))  # bump this if you already seeded many
ORDERS_PER_PATIENT = (1, 2)
TESTS_PER_ORDER = (2, 5)

REQUEST_TIMEOUT = 30
SLEEP_EVERY_N_REQUESTS = 50
SLEEP_SECONDS = 0.4

RUN_SUFFIX = os.getenv("RUN_SUFFIX", "v1")

FIRST_NAMES = ["John", "Maria", "David", "Sarah", "Michael", "Emily", "Daniel", "Olivia", "James", "Sophia"]
LAST_NAMES = ["Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas"]

def r_choice(xs): return xs[random.randint(0, len(xs) - 1)]
def rand_phone() -> str: return f"+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"
def rand_ssn() -> str: return f"{random.randint(100, 899)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
def slug(n: int) -> str: return f"{n:05d}"
def safe_email(prefix: str) -> str: return f"{prefix}.{RUN_SUFFIX}@example.com"
def strong_password() -> str: return "Pass" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10)) + "!"
def rand_dob() -> str:
    y = random.randint(1950, 2006); m = random.randint(1, 12); d = random.randint(1, 28)
    return f"{y:04d}-{m:02d}-{d:02d}"

def generate_value_for_test(test_name: str) -> Tuple[str, str]:
    name = (test_name or "").lower()
    if "glucose" in name:
        v = max(50, min(240, random.gauss(95, 12)))
        flag = "normal" if 70 <= v <= 99 else ("abnormal" if v <= 180 else "critical")
        return (f"{v:.0f}", flag)
    if "hba1c" in name or "a1c" in name:
        v = max(4.0, min(14.0, random.gauss(5.6, 0.7)))
        flag = "normal" if v < 5.7 else ("abnormal" if v < 10 else "critical")
        return (f"{v:.1f}", flag)
    if "ldl" in name:
        v = max(30, min(300, random.gauss(110, 30)))
        flag = "normal" if v < 100 else ("abnormal" if v < 190 else "critical")
        return (f"{v:.0f}", flag)
    if "wbc" in name:
        v = max(0.5, min(40.0, random.gauss(7.0, 1.8)))
        flag = "normal" if 4.0 <= v <= 11.0 else ("abnormal" if v < 25.0 else "critical")
        return (f"{v:.1f}", flag)
    if "covid" in name or "flu" in name or "rapid" in name:
        val = "Negative" if random.random() < 0.85 else "Positive"
        return (val, "normal" if val == "Negative" else "abnormal")
    v = max(0, min(999, random.gauss(50, 15)))
    return (f"{v:.1f}", "normal")

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
        r = requests.post(self.base_url + path, headers=self.headers(), json=json, timeout=REQUEST_TIMEOUT)
        if not r.ok:
            raise RuntimeError(f"POST {path} failed: {r.status_code} {r.text[:300]}")
        return r.json() if r.text else None

    def put(self, path: str, json: Optional[dict] = None) -> Any:
        self._throttle()
        r = requests.put(self.base_url + path, headers=self.headers(), json=json, timeout=REQUEST_TIMEOUT)
        if not r.ok:
            raise RuntimeError(f"PUT {path} failed: {r.status_code} {r.text[:300]}")
        return r.json() if r.text else None

    def get(self, path: str, params: Optional[dict] = None) -> Any:
        self._throttle()
        r = requests.get(self.base_url + path, headers=self.headers(), params=params, timeout=REQUEST_TIMEOUT)
        if not r.ok:
            raise RuntimeError(f"GET {path} failed: {r.status_code} {r.text[:300]}")
        return r.json() if r.text else None

def login_admin(client: ApiClient):
    resp = client.post("/auth/login", {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    token = (resp or {}).get("token") or (resp or {}).get("access_token") or (resp or {}).get("jwt")
    if not token:
        raise RuntimeError(f"Login ok but token missing: {resp}")
    client.token = token

def get_test_types(client: ApiClient) -> List[Tuple[int, str]]:
    data = client.get("/tests/types")
    out = []
    for t in (data or []):
        tid = t.get("test_type_id") or t.get("id")
        name = t.get("name") or t.get("test_name") or str(tid)
        if tid is not None:
            out.append((int(tid), str(name)))
    if not out:
        raise RuntimeError("No test types from /tests/types")
    return out

def get_existing_staff_ids(client: ApiClient) -> Tuple[List[int], List[int]]:
    users = client.get("/users")
    doctors, nurses = [], []
    for u in (users or []):
        role = (u.get("role") or "").upper()
        uid = u.get("user_id") or u.get("id")
        if uid is None:
            continue
        if role == "DOCTOR":
            doctors.append(int(uid))
        elif role == "NURSE":
            nurses.append(int(uid))
    if not doctors or not nurses:
        raise RuntimeError(f"Staff missing. doctors={len(doctors)} nurses={len(nurses)}")
    return doctors, nurses

def create_user(client: ApiClient, first_name: str, last_name: str, email: str, username: str) -> dict:
    return client.post("/users", {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "ssn": rand_ssn(),
        "phone": rand_phone(),
        "username": username,
        "password": strong_password(),
    })

def approve_user(client: ApiClient, user_id: int):
    client.post(f"/users/{user_id}/approve", {})

def update_user_role(client: ApiClient, user_id: int, role: str):
    client.put(f"/users/{user_id}", {"role": role, "status": "APPROVED"})

def update_patient_profile(client: ApiClient, patient_id: int):
    client.put(f"/patients/{patient_id}", {
        "date_of_birth": rand_dob(),
        "gender": random.choice(["M", "F"]),
        "current_status": random.choice(["INPATIENT", "OUTPATIENT"]),
        "admission_date": None,
        "discharge_date": None,
        "allergies": random.choice(["None", "Penicillin", "Peanuts", "Latex"]),
        "emergency_contact_name": f"{r_choice(FIRST_NAMES)} {r_choice(LAST_NAMES)}",
        "emergency_contact_phone": rand_phone(),
    })

def create_assignment(client: ApiClient, doctor_user_id: int, patient_user_id: int):
    client.post("/assignments", {"doctor_user_id": doctor_user_id, "patient_user_id": patient_user_id, "active": True})

def create_order(client: ApiClient, patient_user_id: int, test_type_ids: List[int]) -> dict:
    return client.post("/orders", {
        "patient_user_id": patient_user_id,
        "priority": random.choice(["routine", "urgent"]),
        "test_type_ids": test_type_ids,
        "notes": "Auto-generated order",
    })

def create_result(client: ApiClient, order_id: int, test_type_id: int, value: str) -> dict:
    return client.post("/results", {"order_id": order_id, "test_type_id": test_type_id, "value": value})

def update_result(client: ApiClient, result_id: int, patch: dict):
    client.put(f"/results/{result_id}", patch)

def update_order_status(client: ApiClient, order_id: int, status: str):
    client.put(f"/orders/{order_id}", {"status": status})

def main():
    random.seed(42)
    client = ApiClient(BASE_URL)
    login_admin(client)

    test_types = get_test_types(client)
    doctors, nurses = get_existing_staff_ids(client)

    print(f"✅ Using existing staff | doctors={len(doctors)} nurses={len(nurses)}")
    print(f"✅ Creating {NEW_PATIENTS_TOTAL} new patients starting at {PATIENT_START}")

    orders_count = 0
    results_count = 0

    for idx in range(PATIENT_START, PATIENT_START + NEW_PATIENTS_TOTAL):
        first, last = r_choice(FIRST_NAMES), r_choice(LAST_NAMES)
        username = f"patient_{slug(idx)}_{RUN_SUFFIX}"
        email = safe_email(username)

        u = create_user(client, first, last, email, username)
        patient_id = int(u.get("user_id") or u.get("id"))

        approve_user(client, patient_id)
        update_user_role(client, patient_id, "PATIENT")
        update_patient_profile(client, patient_id)

        doctor_id = random.choice(doctors)
        create_assignment(client, doctor_id, patient_id)

        n_orders = random.randint(*ORDERS_PER_PATIENT)
        for _ in range(n_orders):
            chosen = random.sample(test_types, k=random.randint(*TESTS_PER_ORDER))
            chosen_ids = [tid for tid, _ in chosen]

            order = create_order(client, patient_id, chosen_ids)
            order_id = int(order.get("order_id") or order.get("id"))
            orders_count += 1

            nurse_id = random.choice(nurses)

            # status lifecycle
            try:
                update_order_status(client, order_id, "in_progress")
            except Exception:
                pass

            for tid, tname in chosen:
                value, flag = generate_value_for_test(tname)
                res = create_result(client, order_id, tid, value)
                result_id = int(res.get("result_id") or res.get("id"))
                results_count += 1
                try:
                    update_result(client, result_id, {
                        "result_id": result_id,
                        "order_id": order_id,
                        "test_type_id": tid,
                        "value": value,
                        "flag": flag,
                        "performed_by": nurse_id,
                        "publish_status": "draft",
                    })
                except Exception:
                    pass

            try:
                update_order_status(client, order_id, "reviewed")
                update_order_status(client, order_id, "published")
            except Exception:
                pass

        if (idx - PATIENT_START + 1) % 50 == 0:
            print(f"  - patients: {idx - PATIENT_START + 1}/{NEW_PATIENTS_TOTAL} | orders={orders_count} | results={results_count}")

    print("\n✅ DONE")
    print("Patients created:", NEW_PATIENTS_TOTAL)
    print("Orders created:", orders_count)
    print("Results created:", results_count)

if __name__ == "__main__":
    main()
