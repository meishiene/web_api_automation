from types import SimpleNamespace

from app.services.reporting_input import (
    build_report_summary,
    classify_failure_category,
    map_api_row_to_report_input,
    map_web_row_to_report_input,
)


def test_map_api_row_to_report_input():
    run = SimpleNamespace(
        id=101,
        status="success",
        duration_ms=35,
        error_message=None,
        created_at=1710000000,
    )
    case = SimpleNamespace(id=201, name="api case")

    mapped = map_api_row_to_report_input(run=run, case=case, project_id=301)

    assert mapped.run_type == "api"
    assert mapped.run_id == 101
    assert mapped.project_id == 301
    assert mapped.case_id == 201
    assert mapped.case_name == "api case"
    assert mapped.status == "success"
    assert mapped.duration_ms == 35
    assert mapped.created_at == 1710000000
    assert mapped.started_at is None
    assert mapped.finished_at is None
    assert mapped.artifact_dir is None
    assert mapped.artifacts is None
    assert mapped.detail_api_path == "/api/test-runs/101"


def test_map_web_row_to_report_input_with_valid_artifacts_json():
    run = SimpleNamespace(
        id=102,
        status="failed",
        duration_ms=57,
        error_message="assert failed",
        created_at=1710000010,
        started_at=1710000005,
        finished_at=1710000015,
        artifact_dir="artifacts/web-test-runs/102",
        artifacts_json='["a.png", 2]',
    )
    case = SimpleNamespace(id=202, name="web case")

    mapped = map_web_row_to_report_input(run=run, case=case, project_id=302)

    assert mapped.run_type == "web"
    assert mapped.run_id == 102
    assert mapped.project_id == 302
    assert mapped.case_id == 202
    assert mapped.case_name == "web case"
    assert mapped.status == "failed"
    assert mapped.duration_ms == 57
    assert mapped.error_message == "assert failed"
    assert mapped.created_at == 1710000010
    assert mapped.started_at == 1710000005
    assert mapped.finished_at == 1710000015
    assert mapped.artifact_dir == "artifacts/web-test-runs/102"
    assert mapped.artifacts == ["a.png", "2"]
    assert mapped.detail_api_path == "/api/web-test-runs/102"


def test_map_web_row_to_report_input_with_invalid_artifacts_json():
    run_non_array = SimpleNamespace(
        id=103,
        status="error",
        duration_ms=None,
        error_message="boom",
        created_at=1710000020,
        started_at=None,
        finished_at=None,
        artifact_dir=None,
        artifacts_json='{"x": 1}',
    )
    run_malformed = SimpleNamespace(
        id=104,
        status="error",
        duration_ms=None,
        error_message="boom",
        created_at=1710000030,
        started_at=None,
        finished_at=None,
        artifact_dir=None,
        artifacts_json='{"x"',
    )
    case = SimpleNamespace(id=203, name="web case bad artifacts")

    mapped_non_array = map_web_row_to_report_input(run=run_non_array, case=case, project_id=303)
    mapped_malformed = map_web_row_to_report_input(run=run_malformed, case=case, project_id=303)

    assert mapped_non_array.artifacts is None
    assert mapped_malformed.artifacts is None


def test_classify_failure_category():
    assert classify_failure_category(status="success", error_message=None) is None
    assert classify_failure_category(status="running", error_message="still running") is None
    assert classify_failure_category(status="error", error_message="any") == "execution_error"
    assert classify_failure_category(status="failed", error_message="Assertion failed on text check") == "assertion_failure"
    assert classify_failure_category(status="failed", error_message="operation timeout after 30s") == "timeout"
    assert classify_failure_category(status="failed", error_message="connection reset by peer") == "network_error"
    assert classify_failure_category(status="failed", error_message=None) == "test_failure"


def test_build_report_summary():
    summary = build_report_summary(["success", "failed", "error", "running", "success"])
    assert summary["total_count"] == 5
    assert summary["completed_count"] == 4
    assert summary["success_count"] == 2
    assert summary["failed_count"] == 1
    assert summary["error_count"] == 1
    assert summary["running_count"] == 1
    assert summary["pass_rate"] == 0.5
    assert summary["fail_rate"] == 0.5

    empty_completed = build_report_summary(["running"])
    assert empty_completed["completed_count"] == 0
    assert empty_completed["pass_rate"] == 0
    assert empty_completed["fail_rate"] == 0
