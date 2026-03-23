import json
from pathlib import Path

from typer.testing import CliRunner

from veridra.cli import app


runner = CliRunner()
TEST_TMP_DIR = Path("tests/.tmp")


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _valid_report_payload() -> dict:
    return {
        "suite": "demo-suite",
        "provider": "openai",
        "model": "gpt-4.1-mini",
        "run_mode": "mock",
        "fail_fast": False,
        "stopped_early": False,
        "started_at": "2026-03-23T00:00:00Z",
        "ended_at": "2026-03-23T00:00:01Z",
        "passed": 1,
        "failed": 0,
        "results": [
            {
                "id": "case-1",
                "input": "Who discovered gravity?",
                "output": "Isaac Newton discovered gravity.",
                "pass_": True,
                "grader_results": [
                    {
                        "grader": "correctness",
                        "pass": True,
                        "details": ["expected_contains['Newton']: passed"],
                    }
                ],
                "errors": [],
                "latency_ms": 12,
                "debug": {
                    "latency_ms": 12,
                    "grader_details": {
                        "correctness": ["expected_contains['Newton']: passed"]
                    },
                    "errors": [],
                },
            }
        ],
    }


def test_report_renders_valid_json() -> None:
    report_file = _write_json(TEST_TMP_DIR / "valid-report.json", _valid_report_payload())

    result = runner.invoke(app, ["report", str(report_file)])

    assert result.exit_code == 0
    assert "Suite:" in result.output
    assert "demo-suite" in result.output


def test_report_verbose_renders_debug_info() -> None:
    report_file = _write_json(TEST_TMP_DIR / "verbose-report.json", _valid_report_payload())

    result = runner.invoke(app, ["report", str(report_file), "--verbose"])

    assert result.exit_code == 0
    assert "latency_ms:" in result.output
    assert "correctness details:" in result.output


def test_report_missing_file_returns_exit_two() -> None:
    missing_file = TEST_TMP_DIR / "missing-report.json"

    result = runner.invoke(app, ["report", str(missing_file)])

    assert result.exit_code == 2
    assert "Validation failed:" in result.output
    assert "results file not found" in result.output


def test_report_malformed_json_returns_exit_two() -> None:
    malformed_file = TEST_TMP_DIR / "malformed-report.json"
    malformed_file.parent.mkdir(parents=True, exist_ok=True)
    malformed_file.write_text("{ bad json", encoding="utf-8")

    result = runner.invoke(app, ["report", str(malformed_file)])

    assert result.exit_code == 2
    assert "Validation failed:" in result.output
    assert "malformed JSON" in result.output


def test_report_invalid_schema_returns_exit_two() -> None:
    invalid_payload_file = _write_json(
        TEST_TMP_DIR / "invalid-schema-report.json",
        {"suite": "demo-only"},
    )

    result = runner.invoke(app, ["report", str(invalid_payload_file)])

    assert result.exit_code == 2
    assert "Validation failed:" in result.output
    assert "provider" in result.output
