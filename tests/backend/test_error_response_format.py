def test_unauthorized_error_has_standard_structure(client):
    response = client.get("/api/projects/")
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_AUTHENTICATED"
    assert body["error"]["message"] == "Not authenticated"
    assert body["detail"] == "Not authenticated"
    assert "request_id" in body["error"]
    assert response.headers.get("X-Request-ID")


def test_validation_error_has_standard_structure(client):
    response = client.post("/api/auth/register", json={"username": "only_name"})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Validation failed"
    assert "details" in body["error"]


def test_cors_header_present_for_local_frontend_origin(client):
    response = client.get(
        "/api/projects/",
        headers={"Origin": "http://127.0.0.1:5173"},
    )
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"


def test_cors_header_present_for_dynamic_local_dev_port(client):
    response = client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://127.0.0.1:5175",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:5175"

