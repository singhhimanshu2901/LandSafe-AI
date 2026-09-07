import requests
import uuid

BASE_URL = "http://localhost:8000/api/v1"

# 1. Login
fake_phone = f"999F{uuid.uuid4().hex[:4]}"
requests.post(f"{BASE_URL}/auth/register", json={"name": "Field A", "phone": fake_phone, "password": "pass", "role": "citizen"})
token = requests.post(f"{BASE_URL}/auth/login", data={"username": fake_phone, "password": "pass"}).json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Create Report
r_report = requests.post(f"{BASE_URL}/reports", json={"lat": 26.5, "lon": 91.5, "category": "LANDSLIDE"}, headers=headers)
report_id = r_report.json()["id"]

# 3. Test Invalid File Upload (wrong mime type)
r_bad = requests.post(f"{BASE_URL}/reports/{report_id}/evidence", files={"file": ("test.txt", b"hello", "text/plain")}, headers=headers)
print("Invalid mime type test:", r_bad.status_code, r_bad.json())

# 4. Test Valid Image Upload (should 503 since no supabase keys)
r_img = requests.post(f"{BASE_URL}/reports/{report_id}/evidence", files={"file": ("test.jpg", b"fakeimg", "image/jpeg")}, headers=headers)
print("Valid image test:", r_img.status_code, r_img.json())

# 5. Test Unauthorized User
fake_phone2 = f"999F{uuid.uuid4().hex[:4]}"
requests.post(f"{BASE_URL}/auth/register", json={"name": "Field B", "phone": fake_phone2, "password": "pass", "role": "citizen"})
token2 = requests.post(f"{BASE_URL}/auth/login", data={"username": fake_phone2, "password": "pass"}).json()["access_token"]
headers2 = {"Authorization": f"Bearer {token2}"}

r_unauth = requests.post(f"{BASE_URL}/reports/{report_id}/evidence", files={"file": ("test.jpg", b"fakeimg", "image/jpeg")}, headers=headers2)
print("Unauthorized cross-user test:", r_unauth.status_code, r_unauth.json())
