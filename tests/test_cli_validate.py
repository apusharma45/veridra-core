from pathlib import Path

from typer.testing import CliRunner

from veridra.cli import app


runner = CliRunner()
TEST_TMP_DIR = Path("tests/.tmp")


def _write_suite(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_validate_succeeds_for_valid_suite() -> None:
    suite_file = _write_suite(
        TEST_TMP_DIR / "valid-suite.yaml",
        """suite: basic-safety
provider: openai
model: gpt-4.1-mini
cases:
  - id: fact-1
    input: Who discovered gravity?
    graders: [correctness]
    expected_contains: [Newton]
""",
    )

    result = runner.invoke(app, ["validate", str(suite_file)])

    assert result.exit_code == 0
    assert "Suite is valid." in result.output
    assert "cases: 1" in result.output


def test_validate_fails_for_invalid_suite() -> None:
    suite_file = _write_suite(
        TEST_TMP_DIR / "invalid-suite.yaml",
        """suite: bad-suite
provider: openai
model: gpt-4.1-mini
cases:
  - id: bad-1
    input: test prompt
    graders: [correctness]
""",
    )

    result = runner.invoke(app, ["validate", str(suite_file)])

    assert result.exit_code == 2
    assert "Validation failed:" in result.output
    assert "correctness grader requires at least one of" in result.output


def test_validate_fails_for_missing_file() -> None:
    missing_file = TEST_TMP_DIR / "missing.yaml"

    result = runner.invoke(app, ["validate", str(missing_file)])

    assert result.exit_code == 2
    assert "Validation failed:" in result.output
    assert "suite file not found" in result.output
