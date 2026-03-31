from pathlib import Path

from typer.testing import CliRunner

from veridra.cli import app


runner = CliRunner()
SUITES = [
    "examples/basic_suite.yaml",
    "examples/safety_suite.yaml",
    "examples/injection_suite.yaml",
    "examples/chatbot_suite.yaml",
    "examples/ollama_suite.yaml",
]


def test_full_reference_suites_validate() -> None:
    for suite in SUITES:
        result = runner.invoke(app, ["validate", suite])
        assert result.exit_code == 0, f"validate failed for {suite}: {result.output}"


def test_full_reference_suites_mock_run_report_compare() -> None:
    out_dir = Path("tests/.tmp/full-suites")
    out_dir.mkdir(parents=True, exist_ok=True)

    for suite in SUITES:
        stem = Path(suite).stem
        output_file = out_dir / f"{stem}.json"

        run_result = runner.invoke(
            app,
            ["run", suite, "--mock", "--output", str(output_file)],
        )
        assert run_result.exit_code == 0, f"run failed for {suite}: {run_result.output}"
        assert output_file.exists()

        report_result = runner.invoke(app, ["report", str(output_file)])
        assert report_result.exit_code == 0, f"report failed for {suite}: {report_result.output}"

        compare_result = runner.invoke(app, ["compare", str(output_file), str(output_file)])
        assert compare_result.exit_code == 0, f"compare failed for {suite}: {compare_result.output}"
