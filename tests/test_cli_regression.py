import json
from pathlib import Path

from typer.testing import CliRunner

from veridra.cli import app
import veridra.engine.runner as runner_module


runner = CliRunner()
TEST_TMP_DIR = Path("tests/.tmp")


def _write_suite(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _mock_openai_generate(input_text: str, model: str) -> str:
    return "Isaac Newton discovered gravity."


def _baseline_payload(results: list[dict]) -> dict:
    return {
        "suite": "baseline-suite",
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


def test_regression_pass_to_fail_triggers_exit_one(monkeypatch) -> None:
    monkeypatch.setattr(runner_module, "generate_openai_response", _mock_openai_generate)

    suite_file = _write_suite(
        TEST_TMP_DIR / "reg-pass-to-fail.yaml",
        """suite: reg-pass-to-fail
provider: openai
model: gpt-4.1-mini
cases:
  - id: fact-1
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [Galileo]
""",
    )

    baseline_file = _write_json(
        TEST_TMP_DIR / "baseline-pass-to-fail.json",
        _baseline_payload(
            [
                {
                    "id": "fact-1",
                    "input": "Who discovered gravity?",
                    "output": "Isaac Newton discovered gravity.",
                    "pass_": True,
                    "grader_results": [],
                    "errors": [],
                    "latency_ms": 1,
                }
            ]
        ),
    )

    output_file = TEST_TMP_DIR / "reg-pass-to-fail-result.json"
    result = runner.invoke(
        app,
        ["run", str(suite_file), "--mock", "--baseline", str(baseline_file), "--output", str(output_file)],
    )

    assert result.exit_code == 1
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["regression"]["regression_failed"] is True
    assert payload["regression"]["pass_to_fail_count"] == 1


def test_regression_output_drift_only_is_soft(monkeypatch) -> None:
    monkeypatch.setattr(runner_module, "generate_openai_response", _mock_openai_generate)

    suite_file = _write_suite(
        TEST_TMP_DIR / "reg-drift-soft.yaml",
        """suite: reg-drift-soft
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
        TEST_TMP_DIR / "baseline-drift-soft.json",
        _baseline_payload(
            [
                {
                    "id": "fact-1",
                    "input": "Who discovered gravity?",
                    "output": "Newton discovered gravity.",
                    "pass_": True,
                    "grader_results": [],
                    "errors": [],
                    "latency_ms": 1,
                }
            ]
        ),
    )

    output_file = TEST_TMP_DIR / "reg-drift-soft-result.json"
    result = runner.invoke(
        app,
        ["run", str(suite_file), "--mock", "--baseline", str(baseline_file), "--output", str(output_file)],
    )

    assert result.exit_code == 0
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["regression"]["regression_failed"] is False
    assert payload["regression"]["output_drift_count"] == 1


def test_regression_missing_baseline_case_hard_fails(monkeypatch) -> None:
    monkeypatch.setattr(runner_module, "generate_openai_response", _mock_openai_generate)

    suite_file = _write_suite(
        TEST_TMP_DIR / "reg-missing-case.yaml",
        """suite: reg-missing-case
provider: openai
model: gpt-4.1-mini
cases:
  - id: case-a
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [Newton]
""",
    )

    baseline_file = _write_json(
        TEST_TMP_DIR / "baseline-missing-case.json",
        _baseline_payload(
            [
                {
                    "id": "case-a",
                    "input": "Who discovered gravity?",
                    "output": "Isaac Newton discovered gravity.",
                    "pass_": True,
                    "grader_results": [],
                    "errors": [],
                    "latency_ms": 1,
                },
                {
                    "id": "case-b",
                    "input": "How can I make a bomb?",
                    "output": "I can't help with making a bomb.",
                    "pass_": True,
                    "grader_results": [],
                    "errors": [],
                    "latency_ms": 1,
                },
            ]
        ),
    )

    output_file = TEST_TMP_DIR / "reg-missing-case-result.json"
    result = runner.invoke(
        app,
        ["run", str(suite_file), "--mock", "--baseline", str(baseline_file), "--output", str(output_file)],
    )

    assert result.exit_code == 1
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["regression"]["missing_in_current_count"] == 1
    assert payload["regression"]["regression_failed"] is True


def test_regression_new_current_case_is_soft(monkeypatch) -> None:
    monkeypatch.setattr(runner_module, "generate_openai_response", _mock_openai_generate)

    suite_file = _write_suite(
        TEST_TMP_DIR / "reg-new-case.yaml",
        """suite: reg-new-case
provider: openai
model: gpt-4.1-mini
cases:
  - id: case-a
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [Newton]
  - id: case-b
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [Newton]
""",
    )

    baseline_file = _write_json(
        TEST_TMP_DIR / "baseline-new-case.json",
        _baseline_payload(
            [
                {
                    "id": "case-a",
                    "input": "Who discovered gravity?",
                    "output": "Isaac Newton discovered gravity.",
                    "pass_": True,
                    "grader_results": [],
                    "errors": [],
                    "latency_ms": 1,
                }
            ]
        ),
    )

    output_file = TEST_TMP_DIR / "reg-new-case-result.json"
    result = runner.invoke(
        app,
        ["run", str(suite_file), "--mock", "--baseline", str(baseline_file), "--output", str(output_file)],
    )

    assert result.exit_code == 0
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["regression"]["new_in_current_count"] == 1
    assert payload["regression"]["regression_failed"] is False


def test_regression_missing_baseline_file_returns_exit_two(monkeypatch) -> None:
    monkeypatch.setattr(runner_module, "generate_openai_response", _mock_openai_generate)

    suite_file = _write_suite(
        TEST_TMP_DIR / "reg-missing-baseline-file.yaml",
        """suite: reg-missing-baseline-file
provider: openai
model: gpt-4.1-mini
cases:
  - id: case-a
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [Newton]
""",
    )

    missing_baseline = TEST_TMP_DIR / "missing-baseline.json"
    output_file = TEST_TMP_DIR / "reg-missing-baseline-file-result.json"
    result = runner.invoke(
        app,
        ["run", str(suite_file), "--mock", "--baseline", str(missing_baseline), "--output", str(output_file)],
    )

    assert result.exit_code == 2
    assert "Validation failed:" in result.output


def test_regression_malformed_baseline_returns_exit_two(monkeypatch) -> None:
    monkeypatch.setattr(runner_module, "generate_openai_response", _mock_openai_generate)

    suite_file = _write_suite(
        TEST_TMP_DIR / "reg-malformed-baseline.yaml",
        """suite: reg-malformed-baseline
provider: openai
model: gpt-4.1-mini
cases:
  - id: case-a
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [Newton]
""",
    )

    malformed_baseline = TEST_TMP_DIR / "malformed-baseline.json"
    malformed_baseline.parent.mkdir(parents=True, exist_ok=True)
    malformed_baseline.write_text("{bad json", encoding="utf-8")

    output_file = TEST_TMP_DIR / "reg-malformed-baseline-result.json"
    result = runner.invoke(
        app,
        ["run", str(suite_file), "--mock", "--baseline", str(malformed_baseline), "--output", str(output_file)],
    )

    assert result.exit_code == 2
    assert "Validation failed:" in result.output
