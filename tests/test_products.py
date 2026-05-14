"""
Product API Tests
==================
Tests cover: listing, filtering, single-product fetch, create, update, delete.
Admin-only routes are tested with both admin and customer tokens.
"""


# ── GET /products ─────────────────────────────────────────────────────────────

def test_get_products_empty(client):
    """Product list is empty on a fresh database."""
    res = client.get("/products/")
    assert res.status_code == 200
    assert res.json() == []


def test_create_product_as_admin(client, admin_headers):
    """Admin can create a product successfully."""
    res = client.post("/products/", json={
        "name": "Test Laptop",
        "description": "A powerful laptop",
        "price": 999.99,
        "stock": 10,
    }, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Test Laptop"
    assert data["price"] == 999.99
    assert data["stock"] == 10


def test_create_product_as_customer_forbidden(client, customer_headers):
    """Regular customers cannot create products (403 Forbidden)."""
    res = client.post("/products/", json={
        "name": "Sneaky Product",
        "price": 1.0,
        "stock": 1,
    }, headers=customer_headers)
    assert res.status_code == 403


def test_create_product_no_auth(client):
    """Unauthenticated requests to create products return 401."""
    res = client.post("/products/", json={"name": "X", "price": 1.0, "stock": 1})
    assert res.status_code == 401


def test_get_product_by_id(client, admin_headers):
    """Fetching a product by ID returns the correct data."""
    create_res = client.post("/products/", json={
        "name": "Headphones",
        "price": 49.99,
        "stock": 5,
    }, headers=admin_headers)
    product_id = create_res.json()["id"]

    res = client.get(f"/products/{product_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Headphones"


def test_get_product_not_found(client):
    """Fetching a non-existent product returns 404."""
    assert client.get("/products/99999").status_code == 404


def test_update_product_as_admin(client, admin_headers):
    """Admin can update a product's price and stock."""
    product_id = client.post("/products/", json={
        "name": "Old Name", "price": 10.0, "stock": 3
    }, headers=admin_headers).json()["id"]

    res = client.put(f"/products/{product_id}", json={"price": 25.0, "stock": 50},
                     headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["price"] == 25.0
    assert res.json()["stock"] == 50


def test_delete_product_as_admin(client, admin_headers):
    """Admin can delete a product; subsequent GET returns 404."""
    product_id = client.post("/products/", json={
        "name": "ToDelete", "price": 5.0, "stock": 1
    }, headers=admin_headers).json()["id"]

    assert client.delete(f"/products/{product_id}", headers=admin_headers).status_code == 204
    assert client.get(f"/products/{product_id}").status_code == 404


def test_search_products(client, admin_headers):
    """Search by name returns matching products only."""
    client.post("/products/", json={"name": "Apple iPhone", "price": 800.0, "stock": 5},
                headers=admin_headers)
    client.post("/products/", json={"name": "Samsung Galaxy", "price": 600.0, "stock": 3},
                headers=admin_headers)

    res = client.get("/products/?search=Apple")
    assert res.status_code == 200
    names = [p["name"] for p in res.json()]
    assert all("Apple" in n for n in names)


def test_filter_by_price_range(client, admin_headers):
    """Price range filter returns only products within bounds."""
    client.post("/products/", json={"name": "Cheap Item", "price": 5.0, "stock": 10},
                headers=admin_headers)
    client.post("/products/", json={"name": "Expensive Item", "price": 500.0, "stock": 2},
                headers=admin_headers)

    res = client.get("/products/?min_price=100&max_price=600")
    assert res.status_code == 200
    prices = [p["price"] for p in res.json()]
    assert all(100 <= p <= 600 for p in prices)


def test_filter_in_stock(client, admin_headers):
    """in_stock=true returns only products with stock > 0."""
    client.post("/products/", json={"name": "In Stock", "price": 10.0, "stock": 5},
                headers=admin_headers)
    client.post("/products/", json={"name": "Out Stock", "price": 10.0, "stock": 0},
                headers=admin_headers)

    res = client.get("/products/?in_stock=true")
    assert res.status_code == 200
    assert all(p["stock"] > 0 for p in res.json())


def test_invalid_price_rejected(client, admin_headers):
    """Products with price <= 0 are rejected by Pydantic validation."""
    res = client.post("/products/", json={"name": "Free Item", "price": 0, "stock": 1},
                      headers=admin_headers)
    assert res.status_code == 422
