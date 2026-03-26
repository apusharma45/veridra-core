import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from veridra.cli import app
import veridra.engine.runner as runner_module
from veridra.engine.runner import run_suite
from veridra.providers.openai import OpenAIProviderError
from veridra.schemas.case import CaseSchema
from veridra.schemas.suite import SuiteSchema


runner = CliRunner()
TEST_TMP_DIR = Path("tests/.tmp")
FIXTURE_DIR = Path("tests/fixtures")


def _write_suite(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _suite_with_two_cases() -> SuiteSchema:
    return SuiteSchema(
        suite="phase8-suite",
        provider="openai",
        model="gpt-4.1-mini",
        cases=[
            CaseSchema(
                id="case-1",
                input="Who discovered gravity?",
                graders=["correctness"],
                expected_contains=["newton"],
            ),
            CaseSchema(
                id="case-2",
                input="Who discovered gravity?",
                graders=["correctness"],
                expected_contains=["newton"],
            ),
        ],
    )


def test_run_writes_schema_version(monkeypatch) -> None:
    monkeypatch.setattr(
        runner_module,
        "generate_openai_response",
        lambda input_text, model: "Isaac Newton discovered gravity.",
    )

    suite_file = _write_suite(
        TEST_TMP_DIR / "phase8-schema-suite.yaml",
        """suite: phase8-schema-suite
provider: openai
model: gpt-4.1-mini
cases:
  - id: fact-1
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [Newton]
""",
    )
    output_file = TEST_TMP_DIR / "phase8-schema-result.json"

    result = runner.invoke(app, ["run", str(suite_file), "--mock", "--output", str(output_file)])

    assert result.exit_code == 0
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"


def test_report_rejects_unsupported_schema_version() -> None:
    report_file = _write_json(
        TEST_TMP_DIR / "phase8-bad-schema-report.json",
        {
            "schema_version": "2.0",
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
            "results": [],
        },
    )

    result = runner.invoke(app, ["report", str(report_file)])

    assert result.exit_code == 2
    assert "unsupported schema_version" in result.output


def test_compare_rejects_unsupported_schema_version() -> None:
    baseline = _write_json(
        TEST_TMP_DIR / "phase8-bad-schema-baseline.json",
        {
            "schema_version": "2.0",
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
            "results": [],
        },
    )
    current = _write_json(
        TEST_TMP_DIR / "phase8-good-schema-current.json",
        {
            "schema_version": "1.0",
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
            "results": [],
        },
    )

    result = runner.invoke(app, ["compare", str(baseline), str(current)])

    assert result.exit_code == 2
    assert "unsupported schema_version" in result.output


def test_runner_timeout_marks_case_failed_and_continues(monkeypatch) -> None:
    def _timeout(*args, **kwargs):
        raise OpenAIProviderError("OpenAI request failed: request timed out", transient=True, timeout=True)

    monkeypatch.setattr(runner_module, "generate_openai_response", _timeout)

    result = run_suite(_suite_with_two_cases(), timeout_ms=10)

    assert len(result.results) == 2
    assert result.failed == 2
    assert all(not case.pass_ for case in result.results)
    assert "timed out" in result.results[0].errors[0]


def test_runner_timeout_respects_fail_fast(monkeypatch) -> None:
    def _timeout(*args, **kwargs):
        raise OpenAIProviderError("OpenAI request failed: request timed out", transient=True, timeout=True)

    monkeypatch.setattr(runner_module, "generate_openai_response", _timeout)

    result = run_suite(_suite_with_two_cases(), timeout_ms=10, fail_fast=True)

    assert len(result.results) == 1
    assert result.stopped_early is True


def test_runner_retries_transient_then_passes(monkeypatch) -> None:
    state = {"calls": 0}

    def _flaky(*args, **kwargs):
        state["calls"] += 1
        if state["calls"] == 1:
            raise OpenAIProviderError("OpenAI request failed: 429", transient=True, timeout=False)
        return "Isaac Newton discovered gravity."

    monkeypatch.setattr(runner_module, "generate_openai_response", _flaky)

    suite = SuiteSchema(
        suite="retry-suite",
        provider="openai",
        model="gpt-4.1-mini",
        cases=[
            CaseSchema(
                id="case-1",
                input="Who discovered gravity?",
                graders=["correctness"],
                expected_contains=["newton"],
            )
        ],
    )

    result = run_suite(suite, retries=1)

    assert result.passed == 1
    assert result.results[0].retry_count == 1


def test_runner_non_transient_error_does_not_retry(monkeypatch) -> None:
    state = {"calls": 0}

    def _fatal(*args, **kwargs):
        state["calls"] += 1
        raise OpenAIProviderError("OpenAI request failed: invalid model", transient=False, timeout=False)

    monkeypatch.setattr(runner_module, "generate_openai_response", _fatal)

    with pytest.raises(OpenAIProviderError):
        run_suite(_suite_with_two_cases(), retries=3)

    assert state["calls"] == 1


def test_run_regression_fail_on_drift_returns_exit_one(monkeypatch) -> None:
    monkeypatch.setattr(
        runner_module,
        "generate_openai_response",
        lambda input_text, model: "Isaac Newton discovered gravity.",
    )

    suite_file = _write_suite(
        TEST_TMP_DIR / "phase8-drift-suite.yaml",
        """suite: phase8-drift-suite
provider: openai
model: gpt-4.1-mini
cases:
  - id: fact-1
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [Newton]
""",
    )
    baseline_file = _write_json(
        TEST_TMP_DIR / "phase8-drift-baseline.json",
        {
            "schema_version": "1.0",
            "suite": "phase8-drift-suite",
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
                    "id": "fact-1",
                    "input": "Who discovered gravity?",
                    "output": "Newton discovered gravity.",
                    "pass_": True,
                    "grader_results": [],
                    "errors": [],
                    "latency_ms": 1,
                    "retry_count": 0,
                }
            ],
        },
    )
    output_file = TEST_TMP_DIR / "phase8-drift-result.json"

    result = runner.invoke(
        app,
        [
            "run",
            str(suite_file),
            "--mock",
            "--baseline",
            str(baseline_file),
            "--regression-fail-on-drift",
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["regression"]["fail_on_drift"] is True
    assert payload["regression"]["regression_failed"] is True


def test_smoke_matrix_and_golden_json_snapshot(monkeypatch) -> None:
    monkeypatch.setattr(
        runner_module,
        "generate_openai_response",
        lambda input_text, model: "Isaac Newton discovered gravity.",
    )

    suite_file = _write_suite(
        TEST_TMP_DIR / "phase8-smoke-suite.yaml",
        """suite: phase8-smoke-suite
provider: openai
model: gpt-4.1-mini
cases:
  - id: fact-1
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [Newton]
""",
    )

    validate_result = runner.invoke(app, ["validate", str(suite_file)])
    assert validate_result.exit_code == 0

    current_output = TEST_TMP_DIR / "phase8-smoke-current.json"
    run_result = runner.invoke(app, ["run", str(suite_file), "--mock", "--output", str(current_output)])
    assert run_result.exit_code == 0

    report_result = runner.invoke(app, ["report", str(current_output)])
    assert report_result.exit_code == 0

    baseline_output = TEST_TMP_DIR / "phase8-smoke-baseline.json"
    baseline_output.write_text(current_output.read_text(encoding="utf-8"), encoding="utf-8")

    compare_result = runner.invoke(app, ["compare", str(baseline_output), str(current_output)])
    assert compare_result.exit_code == 0

    payload = json.loads(current_output.read_text(encoding="utf-8"))
    fixture = json.loads((FIXTURE_DIR / "golden_report_keys.json").read_text(encoding="utf-8"))

    assert sorted(payload.keys()) == sorted(fixture["top_level_keys"])
    assert sorted(payload["results"][0].keys()) == sorted(fixture["case_level_keys"])
