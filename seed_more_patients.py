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

# We are NOT creating staff again. We will reuse existing doctors/nurses.
NEW_PATIENTS_TOTAL = int(os.getenv("NEW_PATIENTS_TOTAL", "1500"))
PATIENT_START = int(os.getenv("PATIENT_START", "301"))  # because you already created ~300 patients
ORDERS_PER_PATIENT = (1, 2)
TESTS_PER_ORDER = (2, 5)

REQUEST_TIMEOUT = 30
SLEEP_EVERY_N_REQUESTS = 50
SLEEP_SECONDS = 0.4

# Keep the same suffix if you want them grouped; change if you want a new batch namespace
RUN_SUFFIX = os.getenv("RUN_SUFFIX", "v1")

# =========================
# HELPERS
# =========================
FIRST_NAMES = ["John", "Maria", "David", "Sarah", "Michael", "Emily", "Daniel", "Olivia", "James", "Sophia"]
LAST_NAMES = ["Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas"]

def r_choice(xs): return xs[random.randint(0, len(xs) - 1)]

def rand_phone() -> str:
    return f"+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"

def rand_ssn() -> str:
    return f"{random.randint(100, 899)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

def slug(n: int) -> str:
    return f"{n:05d}"

def safe_email(prefix: str) -> str:
    return f"{prefix}.{RUN_SUFFIX}@example.com"

def strong_password() -> str:
    return "Pass" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10)) + "!"

def rand_dob() -> str:
    year = random.randint(1950, 2006)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year:04d}-{month:02d}-{day:02d}"

def generate_value_for_test(test_name: str) -> Tuple[str, str]:
    name = (test_name or "").lower()

    if "glucose" in name:
        v = random.gauss(95, 12)
        v = max(50, min(240, v))
        flag = "normal" if 70 <= v <= 99 else ("abnormal" if v < 70 or v <= 180 else "critical")
        return (f"{v:.0f}", flag)

    if "hba1c" in name or "a1c" in name:
        v = random.gauss(5.6, 0.7)
        v = max(4.0, min(14.0, v))
        flag = "normal" if v < 5.7 else ("abnormal" if v < 10 else "critical")
        return (f"{v:.1f}", flag)

    if "ldl" in name:
        v = random.gauss(110, 30)
        v = max(30, min(300, v))
        flag = "normal" if v < 100 else ("abnormal" if v < 190 else "critical")
        return (f"{v:.0f}", flag)

    if "hdl" in name:
        v = random.gauss(55, 12)
        v = max(15, min(120, v))
        flag = "normal" if v >= 40 else ("abnormal" if v >= 25 else "critical")
        return (f"{v:.0f}", flag)

    if "trig" in name:
        v = random.gauss(140, 60)
        v = max(30, min(800, v))
        flag = "normal" if v < 150 else ("abnormal" if v < 500 else "critical")
        return (f"{v:.0f}", flag)

    if "cholesterol" in name and "total" in name:
        v = random.gauss(190, 35)
        v = max(80, min(400, v))
        flag = "normal" if v < 200 else ("abnormal" if v < 300 else "critical")
        return (f"{v:.0f}", flag)

    if "creatinine" in name:
        v = random.gauss(1.0, 0.25)
        v = max(0.3, min(6.0, v))
        flag = "normal" if 0.6 <= v <= 1.3 else ("abnormal" if v < 3.0 else "critical")
        return (f"{v:.2f}", flag)

    if "bun" in name:
        v = random.gauss(14, 6)
        v = max(3, min(120, v))
        flag = "normal" if 7 <= v <= 20 else ("abnormal" if v < 60 else "critical")
        return (f"{v:.0f}", flag)

    if "wbc" in name:
        v = random.gauss(7.0, 1.8)
        v = max(0.5, min(40.0, v))
        flag = "normal" if 4.0 <= v <= 11.0 else ("abnormal" if v < 25.0 else "critical")
        return (f"{v:.1f}", flag)

    if "hemoglobin" in name or "hgb" in name:
        v = random.gauss(14.0, 1.8)
        v = max(4.0, min(22.0, v))
        flag = "normal" if 12.0 <= v <= 17.5 else ("abnormal" if v < 20.0 else "critical")
        return (f"{v:.1f}", flag)

    if "protein" in name and "urine" in name:
        v = abs(random.gauss(10, 20))
        v = max(0, min(400, v))
        flag = "normal" if v < 15 else ("abnormal" if v < 200 else "critical")
        return (f"{v:.0f}", flag)

    if "covid" in name or "flu" in name or "rapid" in name:
        value = "Negative" if random.random() < 0.85 else "Positive"
        flag = "normal" if value == "Negative" else "abnormal"
        return (value, flag)

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


# =========================
# API actions
# =========================
def login_admin(client: ApiClient, username: str, password: str) -> str:
    resp = client.post("/auth/login", {"username": username, "password": password})
    token = None
    if isinstance(resp, dict):
        token = resp.get("token") or resp.get("access_token") or resp.get("jwt")
    if not token:
        raise RuntimeError(f"Login ok but token missing: {resp}")
    client.token = token
    return token

def get_test_types(client: ApiClient) -> List[Tuple[int, str]]:
    data = client.get("/tests/types")
    pairs: List[Tuple[int, str]] = []
    for t in (data or []):
        tid = t.get("test_type_id") or t.get("id")
        name = t.get("name") or t.get("test_name") or str(tid)
        if tid is not None:
            pairs.append((int(tid), str(name)))
    if not pairs:
        raise RuntimeError("No test types from /tests/types")
    return pairs

def get_existing_staff_ids(client: ApiClient) -> Tuple[List[int], List[int]]:
    # Pull all users; filter by role
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
    client.post(f"/users/{user_id}/approve", {})

def update_user_role_status(client: ApiClient, user_id: int, role: str, status: str = "APPROVED") -> dict:
    return client.put(f"/users/{user_id}", {"role": role, "status": status})

def update_patient_profile(client: ApiClient, patient_id: int) -> dict:
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
    return client.post("/assignments", {"doctor_user_id": doctor_user_id, "patient_user_id": patient_user_id, "active": True})

def create_order(client: ApiClient, patient_user_id: int, test_type_ids: List[int]) -> dict:
    payload = {
        "patient_user_id": patient_user_id,
        "priority": random.choice(["routine", "urgent"]),
        "test_type_ids": test_type_ids,
        "notes": "Auto-generated order",
    }
    return client.post("/orders", payload)

def create_result(client: ApiClient, order_id: int, test_type_id: int, value: str) -> dict:
    return client.post("/results", {"order_id": order_id, "test_type_id": test_type_id, "value": value})

def update_result(client: ApiClient, result_id: int, patch: dict) -> dict:
    return client.put(f"/results/{result_id}", patch)

def update_order_status(client: ApiClient, order_id: int, patch: dict) -> dict:
    return client.put(f"/orders/{order_id}", patch)


# =========================
# MAIN
# =========================
def main():
    random.seed(42)

    client = ApiClient(BASE_URL)
    print("Login...")
    login_admin(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    print("✅ logged in")

    test_types = get_test_types(client)
    doctors, nurses = get_existing_staff_ids(client)
    print(f"✅ staff loaded | doctors={len(doctors)} nurses={len(nurses)}")
    print(f"✅ test types={len(test_types)}")
    print(f"Creating {NEW_PATIENTS_TOTAL} NEW patients starting from index {PATIENT_START}...")

    created_patients = 0
    created_orders = 0
    created_results = 0

    for i in range(PATIENT_START, PATIENT_START + NEW_PATIENTS_TOTAL):
        first = r_choice(FIRST_NAMES)
        last = r_choice(LAST_NAMES)

        username = f"patient_{slug(i)}_{RUN_SUFFIX}"
        email = safe_email(username)

        # 1) create + approve + role
        u = create_user(client, first, last, email, username)
        patient_user_id = int(u.get("user_id") or u.get("id"))
        approve_user(client, patient_user_id)
        update_user_role_status(client, patient_user_id, role="PATIENT", status="APPROVED")

        # 2) patient profile
        update_patient_profile(client, patient_user_id)

        # 3) assignment with random doctor
        doctor_id = random.choice(doctors)
        create_assignment(client, doctor_user_id=doctor_id, patient_user_id=patient_user_id)

        # 4) orders + results + publish
        n_orders = random.randint(*ORDERS_PER_PATIENT)
        for _ in range(n_orders):
            k_tests = random.randint(*TESTS_PER_ORDER)
            chosen = random.sample(test_types, k=k_tests)
            chosen_ids = [tid for tid, _ in chosen]

            order = create_order(client, patient_user_id=patient_user_id, test_type_ids=chosen_ids)
            order_id = int(order.get("order_id") or order.get("id"))
            created_orders += 1

            nurse_id = random.choice(nurses)

            # optional status transitions
            try:
                update_order_status(client, order_id, {"status": "in_progress"})
            except Exception:
                pass

            for tid, tname in chosen:
                value, flag = generate_value_for_test(tname)
                res = create_result(client, order_id=order_id, test_type_id=tid, value=value)
                result_id = int(res.get("result_id") or res.get("id"))
                created_results += 1

                # attach performed_by/flag/publish_status if backend allows
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
                update_order_status(client, order_id, {"status": "reviewed"})
                update_order_status(client, order_id, {"status": "published"})
            except Exception:
                pass

        created_patients += 1

        if created_patients % 50 == 0:
            print(f"  - patients {created_patients}/{NEW_PATIENTS_TOTAL} | orders={created_orders} | results={created_results}")

    print("\n✅ DONE")
    print("New patients:", created_patients)
    print("Orders:", created_orders)
    print("Results:", created_results)

if __name__ == "__main__":
    main()
