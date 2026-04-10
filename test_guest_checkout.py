"""
Test script for Guest Checkout feature.
Tests both authenticated and guest flows end-to-end.
"""
import requests
import uuid
import json
import sys

BASE = "http://127.0.0.1:8899/api"
DEVICE_ID = f"test-device-{uuid.uuid4().hex[:8]}"
PASS = 0
FAIL = 0

def report(test_name, passed, detail=""):
    global PASS, FAIL
    if passed:
        PASS += 1
        print(f"  ✅ {test_name}")
    else:
        FAIL += 1
        print(f"  ❌ {test_name} — {detail}")

def guest_headers():
    return {"X-Device-ID": DEVICE_ID}

# =====================================================
# PHASE 1: Find a valid product variant and governorate
# =====================================================
print("\n🔍 PHASE 1: Setup — finding test data...")

# Get a product with active variants
r = requests.get(f"{BASE}/products/")
if r.status_code != 200:
    print(f"  ❌ Cannot fetch products: {r.status_code}")
    sys.exit(1)

products = r.json().get("results", [])
if not products:
    print("  ❌ No products found in database. Cannot test.")
    sys.exit(1)

product_id = None
variant = None

for prod in products:
    pid = prod["id"]
    r2 = requests.get(f"{BASE}/products/{pid}/")
    det = r2.json()
    for v in det.get("variants", []):
        if v["stock"] > 0:
            product_id = pid
            variant = v
            break
    if variant:
        break

if not variant:
    print("  ❌ No in-stock variant found across all products. Cannot test orders.")
    sys.exit(1)

variant_id = variant["id"]
print(f"  Found variant id={variant_id}: {variant['product_name']} - {variant['volume']} (stock={variant['stock']})")

# Get governorates
r = requests.get(f"{BASE}/shipping/governorates/")
govs = r.json()
if not govs:
    print("  ❌ No governorates found. Cannot test orders.")
    sys.exit(1)

gov_id = govs[0]["id"]
print(f"  Found governorate id={gov_id}: {govs[0]['name']}")

# =====================================================
# PHASE 2: Guest Cart Operations
# =====================================================
print("\n🛒 PHASE 2: Guest Cart Operations...")

# Test: Get cart as guest (should create new empty cart)
r = requests.get(f"{BASE}/cart/", headers=guest_headers())
report("GET cart as guest", r.status_code == 200, f"status={r.status_code} body={r.text[:200]}")

# Test: Add to cart as guest
r = requests.post(f"{BASE}/cart/add/", headers=guest_headers(), json={
    "variant_id": variant_id,
    "quantity": 1
})
report("ADD to cart as guest", r.status_code == 200, f"status={r.status_code} body={r.text[:200]}")

# Verify cart has items
r = requests.get(f"{BASE}/cart/", headers=guest_headers())
cart_data = r.json()
has_items = len(cart_data.get("items", [])) > 0
report("Cart has items after add", has_items, f"items={cart_data.get('items', [])}")

# =====================================================
# PHASE 3: Guest Place Order — COD
# =====================================================
print("\n📦 PHASE 3: Guest Place Order (COD)...")

order_data = {
    "full_name": "Test Guest User",
    "full_address": "123 Test Street, Cairo",
    "phone_number": "01012345678",
    "country": "Egypt",
    "governorate_id": gov_id,
    "payment_method": "cod",
    "guest_email": "testguest@example.com",
    "order_notes": "Test guest order"
}

r = requests.post(f"{BASE}/orders/place/", headers=guest_headers(), json=order_data)
report("Place COD order as guest", r.status_code == 201, f"status={r.status_code} body={r.text[:300]}")

if r.status_code == 201:
    cod_order = r.json()
    report("Response has order_id", "order_id" in cod_order, str(cod_order))
    report("next_step is success_page", cod_order.get("next_step") == "success_page", str(cod_order))
    cod_order_id = cod_order.get("order_id")
    print(f"  📋 COD Order ID: {cod_order_id}")

# Test: Cart should be empty after COD order
r = requests.get(f"{BASE}/cart/", headers=guest_headers())
cart_data = r.json()
report("Cart empty after COD order", len(cart_data.get("items", [])) == 0, f"items count={len(cart_data.get('items', []))}")

# =====================================================
# PHASE 4: Guest Place Order — Online Payment
# =====================================================
print("\n💳 PHASE 4: Guest Place Order (Online Payment)...")

# Re-add to cart for online payment test
r = requests.post(f"{BASE}/cart/add/", headers=guest_headers(), json={
    "variant_id": variant_id,
    "quantity": 1
})
report("Re-add to cart for online test", r.status_code == 200, f"status={r.status_code}")

import time
time.sleep(11)  # Wait past the duplicate guard window

online_order_data = {
    "full_name": "Test Guest Online",
    "full_address": "456 Online Street, Cairo",
    "phone_number": "01098765432",
    "country": "Egypt",
    "governorate_id": gov_id,
    "payment_method": "card",
    "guest_email": "guestonline@example.com",
    "order_notes": ""
}

r = requests.post(f"{BASE}/orders/place/", headers=guest_headers(), json=online_order_data)
report("Place online order as guest", r.status_code == 201, f"status={r.status_code} body={r.text[:300]}")

online_order_id = None
if r.status_code == 201:
    online_order = r.json()
    report("next_step is payment_gateway", online_order.get("next_step") == "payment_gateway", str(online_order))
    online_order_id = online_order.get("order_id")
    print(f"  📋 Online Order ID: {online_order_id}")

# =====================================================
# PHASE 5: Guest Payment Gateway Access
# =====================================================
print("\n🏦 PHASE 5: Guest Payment Gateway Access...")

if online_order_id:
    # PayPal create order — should succeed (we expect PayPal API errors, but our code should NOT 404)
    r = requests.post(f"{BASE}/paypal/create-order/", headers=guest_headers(), json={
        "order_id": str(online_order_id)
    })
    # We expect either success or a PayPal API error — but NOT 404/403
    is_not_auth_error = r.status_code not in [401, 403, 404]
    report("PayPal create-order accessible to guest", is_not_auth_error, f"status={r.status_code} body={r.text[:200]}")

    # Stripe checkout — should succeed (we expect Stripe API errors, but not 404/403)
    r = requests.post(f"{BASE}/payment/create-checkout-session/", headers=guest_headers(), json={
        "order_id": str(online_order_id)
    })
    is_not_auth_error = r.status_code not in [401, 403, 404]
    report("Stripe checkout accessible to guest", is_not_auth_error, f"status={r.status_code} body={r.text[:200]}")

    # Paymob checkout — should succeed (we expect Paymob API errors, but not 404/403)
    r = requests.post(f"{BASE}/payment/paymob/create-checkout/", headers=guest_headers(), json={
        "order_id": str(online_order_id)
    })
    is_not_auth_error = r.status_code not in [401, 403, 404]
    report("Paymob checkout accessible to guest", is_not_auth_error, f"status={r.status_code} body={r.text[:200]}")
else:
    print("  ⏭️  Skipped — no online order to test with")

# =====================================================
# PHASE 6: Edge Cases
# =====================================================
print("\n⚠️  PHASE 6: Edge Cases...")

# Test: Place order without device ID (should fail)
r = requests.post(f"{BASE}/orders/place/", json=order_data)  # No headers
report("Order without Device-ID rejected", r.status_code == 400, f"status={r.status_code} body={r.text[:200]}")

# Test: Place order with empty cart
EMPTY_DEVICE = f"empty-{uuid.uuid4().hex[:8]}"
r = requests.get(f"{BASE}/cart/", headers={"X-Device-ID": EMPTY_DEVICE})  # Create empty cart
r = requests.post(f"{BASE}/orders/place/", headers={"X-Device-ID": EMPTY_DEVICE}, json=order_data)
report("Order with empty cart rejected", r.status_code in [400, 404], f"status={r.status_code} body={r.text[:200]}")

# Test: Payment gateway with wrong device ID (should 404 — ownership check)
if online_order_id:
    wrong_headers = {"X-Device-ID": "wrong-device-id-12345"}
    r = requests.post(f"{BASE}/paypal/create-order/", headers=wrong_headers, json={
        "order_id": str(online_order_id)
    })
    report("PayPal rejects wrong device_id", r.status_code == 404, f"status={r.status_code} body={r.text[:200]}")

    r = requests.post(f"{BASE}/payment/paymob/create-checkout/", headers=wrong_headers, json={
        "order_id": str(online_order_id)
    })
    report("Paymob rejects wrong device_id", r.status_code == 404, f"status={r.status_code} body={r.text[:200]}")

# =====================================================
# PHASE 7: Authenticated User Still Works
# =====================================================
print("\n👤 PHASE 7: Authenticated User Flow (regression check)...")

# Try to login — if it fails we skip auth tests
auth_r = requests.post(f"{BASE}/auth/login/", json={
    "email": "admin@admin.com",
    "password": "admin"
})

if auth_r.status_code == 200:
    tokens = auth_r.json()
    auth_headers = {"Authorization": f"Bearer {tokens['access']}"}

    # Add to cart as authenticated user
    r = requests.post(f"{BASE}/cart/add/", headers=auth_headers, json={
        "variant_id": variant_id,
        "quantity": 1
    })
    report("Auth user: add to cart", r.status_code == 200, f"status={r.status_code} body={r.text[:200]}")

    time.sleep(11)  # Wait past duplicate guard
    
    # Place COD order as authenticated user
    r = requests.post(f"{BASE}/orders/place/", headers=auth_headers, json={
        "full_name": "Admin User",
        "full_address": "Admin Address",
        "phone_number": "01111111111",
        "country": "Egypt",
        "governorate_id": gov_id,
        "payment_method": "cod",
        "order_notes": "Auth test order"
    })
    report("Auth user: place COD order", r.status_code == 201, f"status={r.status_code} body={r.text[:300]}")

    # Order history should work for authenticated user
    r = requests.get(f"{BASE}/orders/history/", headers=auth_headers)
    report("Auth user: order history works", r.status_code == 200, f"status={r.status_code}")
else:
    print(f"  ⏭️  Skipped auth tests — login failed (status={auth_r.status_code}). Try different credentials.")

# =====================================================
# SUMMARY
# =====================================================
print(f"\n{'='*50}")
print(f"📊 RESULTS: {PASS} passed, {FAIL} failed out of {PASS+FAIL} tests")
print(f"{'='*50}")

if FAIL > 0:
    sys.exit(1)
