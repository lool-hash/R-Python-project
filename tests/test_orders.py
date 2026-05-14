"""
Order & Cart API Tests
=======================
Tests cover: adding to cart, checkout, order history, status updates,
stock reduction, and out-of-stock validation.
"""


def _create_product(client, admin_headers, name="Widget", price=20.0, stock=10):
    """Helper: create and return a product dict."""
    res = client.post("/products/", json={
        "name": name, "price": price, "stock": stock
    }, headers=admin_headers)
    assert res.status_code == 201
    return res.json()


# ── Cart ──────────────────────────────────────────────────────────────────────

def test_cart_starts_empty(client, customer_headers):
    res = client.get("/cart/", headers=customer_headers)
    assert res.status_code == 200
    assert res.json() == []


def test_add_item_to_cart(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers)
    res = client.post("/cart/", json={"product_id": product["id"], "quantity": 2},
                      headers=customer_headers)
    assert res.status_code == 201
    assert res.json()["quantity"] == 2


def test_add_to_cart_out_of_stock(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers, stock=2)
    res = client.post("/cart/", json={"product_id": product["id"], "quantity": 99},
                      headers=customer_headers)
    assert res.status_code == 400


def test_add_same_product_merges_quantity(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers, stock=20)
    pid = product["id"]
    client.post("/cart/", json={"product_id": pid, "quantity": 3}, headers=customer_headers)
    client.post("/cart/", json={"product_id": pid, "quantity": 2}, headers=customer_headers)

    cart = client.get("/cart/", headers=customer_headers).json()
    item = next(i for i in cart if i["product_id"] == pid)
    assert item["quantity"] == 5  # 3 + 2 merged


def test_remove_from_cart(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers)
    item_id = client.post("/cart/", json={"product_id": product["id"], "quantity": 1},
                          headers=customer_headers).json()["id"]
    assert client.delete(f"/cart/{item_id}", headers=customer_headers).status_code == 204
    assert client.get("/cart/", headers=customer_headers).json() == []


def test_clear_cart(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers, stock=20)
    client.post("/cart/", json={"product_id": product["id"], "quantity": 1},
                headers=customer_headers)
    assert client.delete("/cart/", headers=customer_headers).status_code == 204
    assert client.get("/cart/", headers=customer_headers).json() == []


# ── Checkout ──────────────────────────────────────────────────────────────────

def test_checkout_success(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers, price=50.0, stock=10)
    client.post("/cart/", json={"product_id": product["id"], "quantity": 2},
                headers=customer_headers)

    res = client.post("/orders/checkout", headers=customer_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["total_price"] == 100.0   # 2 × $50
    assert data["status"] == "pending"
    assert len(data["items"]) == 1


def test_checkout_empty_cart_fails(client, customer_headers):
    res = client.post("/orders/checkout", headers=customer_headers)
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()


def test_checkout_reduces_stock(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers, price=10.0, stock=8)
    pid = product["id"]
    client.post("/cart/", json={"product_id": pid, "quantity": 3}, headers=customer_headers)
    client.post("/orders/checkout", headers=customer_headers)

    updated = client.get(f"/products/{pid}").json()
    assert updated["stock"] == 5    # 8 - 3 = 5


def test_checkout_clears_cart(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers, stock=10)
    client.post("/cart/", json={"product_id": product["id"], "quantity": 1},
                headers=customer_headers)
    client.post("/orders/checkout", headers=customer_headers)
    assert client.get("/cart/", headers=customer_headers).json() == []


# ── Order management ──────────────────────────────────────────────────────────

def test_customer_sees_own_orders(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers, stock=10)
    client.post("/cart/", json={"product_id": product["id"], "quantity": 1},
                headers=customer_headers)
    client.post("/orders/checkout", headers=customer_headers)

    res = client.get("/orders/", headers=customer_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_admin_sees_all_orders(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers, stock=10)
    client.post("/cart/", json={"product_id": product["id"], "quantity": 1},
                headers=customer_headers)
    client.post("/orders/checkout", headers=customer_headers)

    res = client.get("/orders/all", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_customer_cannot_see_all_orders(client, customer_headers):
    assert client.get("/orders/all", headers=customer_headers).status_code == 403


def test_admin_updates_order_status(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers, stock=10)
    client.post("/cart/", json={"product_id": product["id"], "quantity": 1},
                headers=customer_headers)
    order_id = client.post("/orders/checkout", headers=customer_headers).json()["id"]

    res = client.put(f"/orders/{order_id}/status",
                     json={"status": "shipped"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "shipped"


def test_cancel_pending_order_restores_stock(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers, price=10.0, stock=5)
    pid = product["id"]
    client.post("/cart/", json={"product_id": pid, "quantity": 2}, headers=customer_headers)
    order_id = client.post("/orders/checkout", headers=customer_headers).json()["id"]

    assert client.delete(f"/orders/{order_id}", headers=customer_headers).status_code == 204
    # Stock must be restored to 5
    assert client.get(f"/products/{pid}").json()["stock"] == 5


def test_cancel_non_pending_order_fails(client, admin_headers, customer_headers):
    product = _create_product(client, admin_headers, stock=10)
    client.post("/cart/", json={"product_id": product["id"], "quantity": 1},
                headers=customer_headers)
    order_id = client.post("/orders/checkout", headers=customer_headers).json()["id"]

    # Advance the order past pending
    client.put(f"/orders/{order_id}/status", json={"status": "shipped"},
               headers=admin_headers)

    res = client.delete(f"/orders/{order_id}", headers=customer_headers)
    assert res.status_code == 400
