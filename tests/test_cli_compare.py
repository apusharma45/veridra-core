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


def _result_payload(results: list[dict]) -> dict:
    return {
        "suite": "suite-x",
        "provider": "openai",
        "model": "gpt-4.1-mini",
        "run_mode": "mock",
        "fail_fast": False,
        "stopped_early": False,
        "started_at": "2026-03-23T00:00:00Z",
        "ended_at": "2026-03-23T00:00:01Z",
        "passed": sum(1 for r in results if r["pass_"]),
        "failed": sum(1 for r in results if not r["pass_"]),
        "results": results,
    }


def test_compare_hard_regression_returns_exit_one() -> None:
    baseline = _write_json(
        TEST_TMP_DIR / "cmp-baseline-hard.json",
        _result_payload(
            [
                {
                    "id": "case-1",
                    "input": "q",
                    "output": "ok",
                    "pass_": True,
                    "grader_results": [],
                    "errors": [],
                    "latency_ms": 1,
                }
            ]
        ),
    )
    current = _write_json(
        TEST_TMP_DIR / "cmp-current-hard.json",
        _result_payload(
            [
                {
                    "id": "case-1",
                    "input": "q",
                    "output": "bad",
                    "pass_": False,
                    "grader_results": [],
                    "errors": ["failed"],
                    "latency_ms": 1,
                }
            ]
        ),
    )

    result = runner.invoke(app, ["compare", str(baseline), str(current)])

    assert result.exit_code == 1
    assert "Regression:" in result.output
    assert "FAILED" in result.output


def test_compare_soft_drift_returns_zero() -> None:
    baseline = _write_json(
        TEST_TMP_DIR / "cmp-baseline-soft.json",
        _result_payload(
            [
                {
                    "id": "case-1",
                    "input": "q",
                    "output": "old output",
                    "pass_": True,
                    "grader_results": [],
                    "errors": [],
                    "latency_ms": 1,
                }
            ]
        ),
    )
    current = _write_json(
        TEST_TMP_DIR / "cmp-current-soft.json",
        _result_payload(
            [
                {
                    "id": "case-1",
                    "input": "q",
                    "output": "new output",
                    "pass_": True,
                    "grader_results": [],
                    "errors": [],
                    "latency_ms": 1,
                }
            ]
        ),
    )

    result = runner.invoke(app, ["compare", str(baseline), str(current)])

    assert result.exit_code == 0
    assert "Regression:" in result.output
    assert "PASSED" in result.output


def test_compare_missing_file_returns_exit_two() -> None:
    baseline = TEST_TMP_DIR / "cmp-missing-a.json"
    current = TEST_TMP_DIR / "cmp-missing-b.json"

    result = runner.invoke(app, ["compare", str(baseline), str(current)])

    assert result.exit_code == 2
    assert "Validation failed:" in result.output


def test_compare_malformed_json_returns_exit_two() -> None:
    baseline = TEST_TMP_DIR / "cmp-malformed-a.json"
    current = TEST_TMP_DIR / "cmp-malformed-b.json"
    baseline.parent.mkdir(parents=True, exist_ok=True)
    baseline.write_text("{bad", encoding="utf-8")
    current.write_text("{bad", encoding="utf-8")

    result = runner.invoke(app, ["compare", str(baseline), str(current)])

    assert result.exit_code == 2
    assert "Validation failed:" in result.output


def test_compare_verbose_prints_findings() -> None:
    baseline = _write_json(
        TEST_TMP_DIR / "cmp-baseline-verbose.json",
        _result_payload(
            [
                {
                    "id": "case-1",
                    "input": "q",
                    "output": "old output",
                    "pass_": True,
                    "grader_results": [],
                    "errors": [],
                    "latency_ms": 1,
                }
            ]
        ),
    )
    current = _write_json(
        TEST_TMP_DIR / "cmp-current-verbose.json",
        _result_payload(
            [
                {
                    "id": "case-1",
                    "input": "q",
                    "output": "new output",
                    "pass_": True,
                    "grader_results": [],
                    "errors": [],
                    "latency_ms": 1,
                }
            ]
        ),
    )

    result = runner.invoke(app, ["compare", str(baseline), str(current), "--verbose"])

    assert result.exit_code == 0
    assert "findings:" in result.output
    assert "output_drift" in result.output
