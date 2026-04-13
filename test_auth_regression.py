"""Quick authenticated user regression test for guest checkout changes."""
import requests
import time
import sys

BASE = "http://127.0.0.1:8899/api"

print("Logging in...")
r = requests.post(f"{BASE}/auth/login/", json={"email": "testuser@test.com", "password": "TestPass123!"})
if r.status_code != 200:
    print(f"Login failed: {r.status_code} {r.text[:200]}")
    sys.exit(1)

tokens = r.json()
auth = {"Authorization": f"Bearer {tokens['access']}"}
print(f"Logged in OK")

# Find variant
r = requests.get(f"{BASE}/products/")
products = r.json().get("results", [])
variant_id = None
for prod in products:
    r2 = requests.get(f"{BASE}/products/{prod['id']}/")
    for v in r2.json().get("variants", []):
        if v["stock"] > 0:
            variant_id = v["id"]
            break
    if variant_id:
        break

if not variant_id:
    print("No in-stock variant")
    sys.exit(1)

# Get governorate
r = requests.get(f"{BASE}/shipping/governorates/")
gov_id = r.json()[0]["id"]

# Add to cart
r = requests.post(f"{BASE}/cart/add/", headers=auth, json={"variant_id": variant_id, "quantity": 1})
print(f"Add to cart: {r.status_code} {'OK' if r.status_code == 200 else r.text[:100]}")

# Place COD order
r = requests.post(f"{BASE}/orders/place/", headers=auth, json={
    "full_name": "Auth Test User",
    "full_address": "Auth Test Address",
    "phone_number": "01234567890",
    "country": "Egypt",
    "governorate_id": gov_id,
    "payment_method": "cod",
})
print(f"Place COD order: {r.status_code} {'OK' if r.status_code == 201 else r.text[:200]}")

if r.status_code == 201:
    order_id = r.json().get("order_id")
    print(f"Order ID: {order_id}")

# Order history
r = requests.get(f"{BASE}/orders/history/", headers=auth)
print(f"Order history: {r.status_code} {'OK' if r.status_code == 200 else r.text[:100]}")
orders = r.json()
print(f"Total orders: {len(orders)}")

# Online payment test
r = requests.post(f"{BASE}/cart/add/", headers=auth, json={"variant_id": variant_id, "quantity": 1})
print(f"Re-add to cart: {r.status_code}")

time.sleep(11)

r = requests.post(f"{BASE}/orders/place/", headers=auth, json={
    "full_name": "Auth Online User",
    "full_address": "Online Address",
    "phone_number": "01299998888",
    "country": "Egypt",
    "governorate_id": gov_id,
    "payment_method": "card",
})
print(f"Place online order: {r.status_code} {'OK' if r.status_code == 201 else r.text[:200]}")

if r.status_code == 201:
    oid = r.json().get("order_id")
    # Paymob checkout
    r = requests.post(f"{BASE}/payment/paymob/create-checkout/", headers=auth, json={"order_id": str(oid)})
    print(f"Paymob checkout (auth): {r.status_code} {'OK - got URL' if r.status_code == 200 else r.text[:200]}")

print("\nAll auth regression tests completed!")
