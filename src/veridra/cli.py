from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
import yaml
from dotenv import load_dotenv
from pydantic import ValidationError
from rich import print

from veridra.engine.runner import run_suite
from veridra.reporters.console import print_suite_report
from veridra.reporters.json import write_json_report
from veridra.schemas.suite import SuiteSchema

app = typer.Typer()
load_dotenv()


def _load_suite_from_yaml(path: Path) -> SuiteSchema:
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"suite file not found: {path}") from exc
    except OSError as exc:
        raise ValueError(f"unable to read suite file: {path} ({exc})") from exc

    try:
        raw_data: Any = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise ValueError(f"malformed YAML in {path}: {exc}") from exc

    if raw_data is None:
        raise ValueError(f"suite file is empty: {path}")
    if not isinstance(raw_data, dict):
        raise ValueError("suite YAML must be a top-level mapping/object")

    return SuiteSchema.model_validate(raw_data)


def _render_validation_errors(exc: ValidationError) -> None:
    print("[bold red]Validation failed:[/bold red]")
    for error in exc.errors():
        location = ".".join(str(item) for item in error.get("loc", []))
        message = error.get("msg", "invalid value")
        print(f"- [red]{location}[/red]: {message}")


@app.command()
def run(
    file: str,
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="Override suite model for this run.",
    ),
    mock: bool = typer.Option(
        False,
        "--mock",
        help="Use deterministic mock provider responses instead of live provider calls.",
    ),
    fail_fast: bool = typer.Option(
        False,
        "--fail-fast",
        help="Stop execution after first failed case.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed run diagnostics.",
    ),
    output: str = typer.Option(
        "veridra-results.json",
        "--output",
        "-o",
        help="Path for JSON result output.",
    ),
):
    """
    Run a Veridra evaluation suite.
    """
    path = Path(file)
    try:
        suite = _load_suite_from_yaml(path)
    except ValidationError as exc:
        _render_validation_errors(exc)
        raise typer.Exit(code=2)
    except ValueError as exc:
        print(f"[bold red]Validation failed:[/bold red] {exc}")
        raise typer.Exit(code=2)

    if model is not None:
        model_value = model.strip()
        if not model_value:
            print("[bold red]Validation failed:[/bold red] --model cannot be empty")
            raise typer.Exit(code=2)
        suite = suite.model_copy(update={"model": model_value})

    run_mode = "mock" if mock else "provider"

    try:
        result = run_suite(suite, run_mode=run_mode, fail_fast=fail_fast)
        output_path = Path(output)
        write_json_report(result, output_path, include_debug=verbose)
    except Exception as exc:
        print(f"[bold red]Runtime failure:[/bold red] {exc}")
        raise typer.Exit(code=3)

    print_suite_report(result, verbose=verbose)
    print(f"[bold]JSON report:[/bold] {output_path}")
    if result.failed > 0:
        raise typer.Exit(code=1)

@app.command()
def validate(
    file: str,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation output.",
    ),
):
    """
    Validate a test suite file.
    """
    path = Path(file)
    try:
        suite = _load_suite_from_yaml(path)
    except ValidationError as exc:
        _render_validation_errors(exc)
        raise typer.Exit(code=2)
    except ValueError as exc:
        print(f"[bold red]Validation failed:[/bold red] {exc}")
        raise typer.Exit(code=2)

    print("[bold green]Suite is valid.[/bold green]")
    print(f"- suite: {suite.suite}")
    print(f"- provider: {suite.provider}")
    print(f"- model: {suite.model}")
    print(f"- cases: {len(suite.cases)}")
    if verbose:
        for case in suite.cases:
            print(
                f"  - case={case.id} graders={','.join(case.graders)} "
                f"expected_behavior={case.expected_behavior or '-'}"
            )

def main():
    app()

if __name__ == "__main__":
    main()
