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

