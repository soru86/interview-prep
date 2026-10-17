"""Integration tests for /api/v1/users endpoints."""


def test_health_check(client):
    """GET /health returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_user(client):
    """POST /api/v1/users/ registers a new user."""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "alice@example.com",
            "password": "secret123",
            "full_name": "Alice Wonderland",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice Wonderland"
    assert "id" in data
    assert "hashed_password" not in data  # must never leak


def test_create_duplicate_user(client):
    """Registering the same email twice returns 400."""
    payload = {"email": "bob@example.com", "password": "pass"}
    client.post("/api/v1/users/", json=payload)
    response = client.post("/api/v1/users/", json=payload)
    assert response.status_code == 400


def test_login_and_me(client):
    """Full auth flow: register → login → GET /me."""
    # Register
    client.post(
        "/api/v1/users/",
        json={"email": "carol@example.com", "password": "mypass"},
    )
    # Login (OAuth2 form)
    login_resp = client.post(
        "/api/v1/users/login",
        data={"username": "carol@example.com", "password": "mypass"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # Authenticated request
    me_resp = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "carol@example.com"


def test_login_invalid_credentials(client):
    """Login with wrong password returns 401."""
    client.post(
        "/api/v1/users/",
        json={"email": "dave@example.com", "password": "right"},
    )
    resp = client.post(
        "/api/v1/users/login",
        data={"username": "dave@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_unauthenticated_list_users(client):
    """GET /api/v1/users/ without a token returns 401."""
    resp = client.get("/api/v1/users/")
    assert resp.status_code == 401
