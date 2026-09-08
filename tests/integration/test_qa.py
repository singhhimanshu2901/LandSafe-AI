import requests
import uuid

BASE_URL = "http://localhost:8000/api/v1"

results = []

def record(test_name, status, detail=""):
    results.append({"test": test_name, "status": status, "detail": detail})
    print(f"[{status}] {test_name}: {detail}")

# 1. Health
try:
    r = requests.get(f"{BASE_URL}/health")
    if r.status_code == 200:
        record("Health Check", "PASS", r.json())
    else:
        record("Health Check", "FAIL", r.status_code)
except Exception as e:
    record("Health Check", "FAIL", str(e))

# 2. Invalid Auth (401)
try:
    r = requests.post(f"{BASE_URL}/reports", json={"lat": 26.0, "lon": 91.0, "category": "LANDSLIDE"})
    if r.status_code == 401:
        record("Auth 401 Check", "PASS", "Rejected missing token")
    else:
        record("Auth 401 Check", "FAIL", f"Status {r.status_code}")
except Exception as e:
    record("Auth 401 Check", "FAIL", str(e))

# 3. Validation Error (422)
try:
    r = requests.get(f"{BASE_URL}/locations/not-a-uuid")
    if r.status_code == 422:
        record("Validation 422 Check", "PASS", "Rejected invalid UUID")
    else:
        record("Validation 422 Check", "FAIL", f"Status {r.status_code}")
except Exception as e:
    record("Validation 422 Check", "FAIL", str(e))

# 4. Auth & Role Escalation Check
# We'll create a mock user and an admin user, then test access.
fake_phone = f"999{uuid.uuid4().hex[:6]}"
try:
    # Register Citizen
    r_cit = requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Citizen Bob", "phone": fake_phone, "password": "pass", "role": "citizen"
    })
    
    if r_cit.status_code == 200:
        record("Register Citizen", "PASS")
        # Login
        r_login = requests.post(f"{BASE_URL}/auth/login", data={"username": fake_phone, "password": "pass"})
        token = r_login.json()["access_token"]
        
        # Access Admin Endpoint
        r_admin = requests.patch(f"{BASE_URL}/reports/{uuid.uuid4()}/status", 
                                 json={"status": "VERIFIED"}, 
                                 headers={"Authorization": f"Bearer {token}"})
        if r_admin.status_code == 403:
            record("Admin Role Enforcement", "PASS", "Citizen blocked from admin API")
        elif r_admin.status_code == 404:
            # If 404, it means it bypassed auth and hit DB
            record("Admin Role Enforcement", "FAIL", "Citizen allowed but report not found (404)")
        else:
            record("Admin Role Enforcement", "FAIL", f"Status {r_admin.status_code}")
    else:
        record("Register Citizen", "FAIL", r_cit.text)
except Exception as e:
    record("Auth Roles Check", "FAIL", str(e))

# 5. Data Quality Endpoint Check
try:
    # Get locations
    locs = requests.get(f"{BASE_URL}/locations").json()
    if len(locs) > 0:
        loc_id = locs[0]["id"]
        # Hit Intelligence
        r_intel = requests.get(f"{BASE_URL}/intelligence/{loc_id}")
        if r_intel.status_code == 200:
            data = r_intel.json()
            record("Data Quality Engine", "PASS", f"Weather Status: {data['weather']['status']}")
            record("Explainable AI Payload", "PASS", f"Explanation: {data.get('ai_explanation', {}).get('human_explanation', 'N/A')}")
        else:
            record("Data Quality Engine", "FAIL", r_intel.text)
    else:
        record("Data Quality Engine", "BLOCKED", "No locations found")
except Exception as e:
    record("Data Quality Engine", "FAIL", str(e))

# 6. SQLi Test (Location ID)
try:
    if len(locs) > 0:
        r_sqli = requests.get(f"{BASE_URL}/intelligence/1' OR '1'='1")
        if r_sqli.status_code == 422:
            record("SQLi Defense UUID", "PASS", "Rejected invalid UUID string before SQL")
        else:
            record("SQLi Defense UUID", "FAIL", f"Status {r_sqli.status_code}")
except Exception as e:
    record("SQLi Defense UUID", "FAIL", str(e))

print("\n--- Summary ---")
for res in results:
    print(f"[{res['status']}] {res['test']}")
