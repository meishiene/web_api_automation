from scripts.alert_webhook_notify import build_payload


def test_build_payload_contains_required_fields():
    payload = build_payload(
        title="Audit Governance Alert",
        source="prod-audit-governance-run.ps1",
        status="alert",
        summary="threshold exceeded",
    )

    assert payload["title"] == "Audit Governance Alert"
    assert payload["source"] == "prod-audit-governance-run.ps1"
    assert payload["status"] == "alert"
    assert payload["summary"] == "threshold exceeded"
    assert "timestamp" in payload


def test_build_payload_includes_details_when_provided():
    payload = build_payload(
        title="x",
        source="y",
        status="failed",
        summary="z",
        details={"run_id": "abc"},
    )

    assert payload["details"]["run_id"] == "abc"
