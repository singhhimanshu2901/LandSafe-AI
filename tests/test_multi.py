import requests
import uuid
import time

BASE_URL = "http://localhost:8000/api/v1"

print("--- MULTI DEVICE SIMULATION ---")

# 1. Device A: Login (or Register & Login)
fake_phone_a = f"999A{uuid.uuid4().hex[:4]}"
requests.post(f"{BASE_URL}/auth/register", json={"name": "Field A", "phone": fake_phone_a, "password": "pass", "role": "citizen"})
token_a = requests.post(f"{BASE_URL}/auth/login", data={"username": fake_phone_a, "password": "pass"}).json()["access_token"]
print("Device A: Logged in successfully.")

# 2. Device A: Submit hazard report
r_report = requests.post(
    f"{BASE_URL}/reports", 
    json={"lat": 26.5, "lon": 91.5, "category": "FLASH_FLOOD", "severity": "high", "description": "Flood blocking the main road."},
    headers={"Authorization": f"Bearer {token_a}"}
)
report_id = r_report.json()["id"]
print(f"Device A: Submitted report {report_id}.")

# 3. Device B: Login as Admin
fake_phone_b = f"999B{uuid.uuid4().hex[:4]}"
requests.post(f"{BASE_URL}/auth/register", json={"name": "Admin B", "phone": fake_phone_b, "password": "pass", "role": "district_admin"})
token_b = requests.post(f"{BASE_URL}/auth/login", data={"username": fake_phone_b, "password": "pass"}).json()["access_token"]
print("Device B: Logged in as Admin successfully.")

# 4. Device B: Fetch reports and verify it's there
r_fetch = requests.get(f"{BASE_URL}/reports", headers={"Authorization": f"Bearer {token_b}"})
reports = r_fetch.json()
found = any(r["id"] == report_id for r in reports)
print(f"Device B: Verified report appears in list: {found}")

# 5. Device B: Change status to VERIFIED
r_update = requests.patch(
    f"{BASE_URL}/reports/{report_id}/status", 
    json={"status": "VERIFIED", "resolution_notes": "Team dispatched."},
    headers={"Authorization": f"Bearer {token_b}"}
)
print(f"Device B: Updated status to VERIFIED (Status Code: {r_update.status_code})")

# 6. Device A: Refetches the report
time.sleep(1) # simulate time passing
r_fetch_a = requests.get(f"{BASE_URL}/reports", headers={"Authorization": f"Bearer {token_a}"})
reports_a = r_fetch_a.json()
target = next(r for r in reports_a if r["id"] == report_id)
print(f"Device A: Sees report status is now '{target['status']}'")
print(f"Device A: Sees admin notes: {target['description']}")
