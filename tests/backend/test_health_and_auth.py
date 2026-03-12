def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_and_login_success(client):
    register_resp = client.post("/api/auth/register", json={"username": "alice", "password": "secret"})
    assert register_resp.status_code == 200
    register_body = register_resp.json()
    assert register_body["username"] == "alice"
    assert "id" in register_body

    login_resp = client.post("/api/auth/login", json={"username": "alice", "password": "secret"})
    assert login_resp.status_code == 200
    login_body = login_resp.json()
    assert login_body["token_type"] == "bearer"
    assert login_body["user"]["username"] == "alice"
    assert "refresh_token" in login_body
    assert "." in login_body["access_token"]
    assert "." in login_body["refresh_token"]
    assert login_body["access_token"] != login_body["refresh_token"]


def test_refresh_token_flow(client):
    register_resp = client.post("/api/auth/register", json={"username": "bob", "password": "secret"})
    assert register_resp.status_code == 200

    login_resp = client.post("/api/auth/login", json={"username": "bob", "password": "secret"})
    assert login_resp.status_code == 200
    login_body = login_resp.json()
    refresh_token = login_body["refresh_token"]
    access_token = login_body["access_token"]

    refresh_resp = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 200
    refresh_body = refresh_resp.json()
    assert refresh_body["token_type"] == "bearer"
    assert "." in refresh_body["access_token"]
    assert refresh_body["access_token"] != access_token

    invalid_refresh = client.post("/api/auth/refresh", json={"refresh_token": access_token})
    assert invalid_refresh.status_code == 401


def test_register_duplicate_user(client):
    first = client.post("/api/auth/register", json={"username": "alice", "password": "secret"})
    assert first.status_code == 200

    duplicate = client.post("/api/auth/register", json={"username": "alice", "password": "secret2"})
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Username already exists"


def test_protected_api_requires_auth(client):
    response = client.get("/api/projects/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
