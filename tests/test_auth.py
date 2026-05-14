def test_register_success(client):
    res = client.post("/auth/register", json={
        "email": "user@example.com", "username": "testuser",
        "password": "password123", "role": "customer"
    })
    assert res.status_code == 201
    assert res.json()["email"] == "user@example.com"
    assert res.json()["role"] == "customer"


def test_register_duplicate_email(client):
    p = {"email": "dup@test.com", "username": "u1", "password": "pass123", "role": "customer"}
    client.post("/auth/register", json=p)
    p["username"] = "u2"
    res = client.post("/auth/register", json=p)
    assert res.status_code == 400
    assert "Email already registered" in res.json()["detail"]


def test_register_duplicate_username(client):
    client.post("/auth/register", json={"email": "a@test.com", "username": "same", "password": "pass123", "role": "customer"})
    res = client.post("/auth/register", json={"email": "b@test.com", "username": "same", "password": "pass123", "role": "customer"})
    assert res.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={"email": "login@test.com", "username": "loginuser", "password": "mypass", "role": "customer"})
    res = client.post("/auth/login", json={"email": "login@test.com", "password": "mypass"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "u@test.com", "username": "u", "password": "correct", "role": "customer"})
    res = client.post("/auth/login", json={"email": "u@test.com", "password": "wrong"})
    assert res.status_code == 401


def test_get_me(client, admin_headers):
    res = client.get("/auth/me", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["role"] == "admin"


def test_get_me_no_token(client):
    assert client.get("/auth/me").status_code == 401


def test_get_me_invalid_token(client):
    assert client.get("/auth/me", headers={"Authorization": "Bearer bad"}).status_code == 401
