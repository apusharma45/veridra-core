from pathlib import Path

import veridra.engine.runner as runner_module
from typer.testing import CliRunner

from veridra.cli import app


runner = CliRunner()
TEST_TMP_DIR = Path("tests/.tmp")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_suite(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_init_creates_openai_basic_scaffold() -> None:
    out = TEST_TMP_DIR / "init-openai-basic.yaml"
    if out.exists():
        out.unlink()
    result = runner.invoke(
        app,
        ["init", str(out), "--provider", "openai", "--template", "basic"],
    )

    assert result.exit_code == 0
    assert out.exists()
    content = _read(out)
    assert "provider: openai" in content
    assert "model: gpt-4.1-mini" in content
    assert "expected_contains" in content


def test_init_creates_ollama_safety_scaffold() -> None:
    out = TEST_TMP_DIR / "init-ollama-safety.yaml"
    if out.exists():
        out.unlink()
    result = runner.invoke(
        app,
        ["init", str(out), "--provider", "ollama", "--template", "safety"],
    )

    assert result.exit_code == 0
    content = _read(out)
    assert "provider: ollama" in content
    assert "model: llama3.2" in content
    assert "expected_behavior: refuse_or_safe" in content


def test_init_refuses_overwrite_without_force() -> None:
    out = TEST_TMP_DIR / "init-overwrite.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("suite: existing\n", encoding="utf-8")

    result = runner.invoke(app, ["init", str(out)])

    assert result.exit_code == 2
    assert "file already exists" in result.output


def test_init_overwrites_with_force() -> None:
    out = TEST_TMP_DIR / "init-overwrite-force.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("suite: existing\n", encoding="utf-8")

    result = runner.invoke(app, ["init", str(out), "--force"])

    assert result.exit_code == 0
    assert "provider: openai" in _read(out)


def test_examples_lists_expected_entries() -> None:
    result = runner.invoke(app, ["examples"])

    assert result.exit_code == 0
    assert "examples/basic_suite.yaml" in result.output
    assert "examples/customer_support_suite.yaml" in result.output
    assert "Run (mock)" in result.output
    assert "Run (provider)" in result.output


def test_validate_verbose_shows_checklist_and_warning() -> None:
    suite_file = _write_suite(
        TEST_TMP_DIR / "validate-verbose-warning.yaml",
        """suite: weak-checks
provider: openai
model: gpt-4.1-mini
cases:
  - id: weak-1
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [ok]
""",
    )

    result = runner.invoke(app, ["validate", str(suite_file), "--verbose"])

    assert result.exit_code == 0
    assert "checklist:" in result.output
    assert "warnings:" in result.output


def test_run_dry_run_prints_plan_and_skips_output_and_provider(monkeypatch) -> None:
    def _raise_if_called(*args, **kwargs):
        raise RuntimeError("provider should not be called in dry-run")

    monkeypatch.setattr(runner_module, "generate_openai_response", _raise_if_called)
    suite_file = _write_suite(
        TEST_TMP_DIR / "dry-run-suite.yaml",
        """suite: dry-run-suite
provider: openai
model: gpt-4.1-mini
cases:
  - id: fact-1
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [Newton]
""",
    )

    output_file = TEST_TMP_DIR / "dry-run-output.json"
    if output_file.exists():
        output_file.unlink()

    result = runner.invoke(
        app,
        ["run", str(suite_file), "--dry-run", "--output", str(output_file)],
    )

    assert result.exit_code == 0
    assert "Dry Run Plan" in result.output
    assert "case_order:" in result.output
    assert not output_file.exists()


def test_run_dry_run_still_returns_two_for_invalid_suite() -> None:
    bad_suite = _write_suite(
        TEST_TMP_DIR / "dry-run-invalid.yaml",
        """suite: bad
provider: openai
model: gpt-4.1-mini
cases:
  - id: bad-1
    input: test
    graders: [correctness]
""",
    )

    result = runner.invoke(app, ["run", str(bad_suite), "--dry-run"])

    assert result.exit_code == 2
    assert "Validation failed:" in result.output


def test_init_creates_injection_template() -> None:
    out = TEST_TMP_DIR / "init-injection.yaml"
    if out.exists():
        out.unlink()
    result = runner.invoke(
        app,
        ["init", str(out), "--template", "injection"],
    )

    assert result.exit_code == 0
    content = _read(out)
    assert "forbidden_contains" in content
    assert "expected_behavior: answer_normally" in content

