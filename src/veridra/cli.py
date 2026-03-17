from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
import yaml
from pydantic import ValidationError
from rich import print

from veridra.schemas.suite import SuiteSchema

app = typer.Typer()


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
def run(file: str):
    """
    Run a Veridra evaluation suite.
    """
    print(f"[bold green]Running suite:[/bold green] {file}")

@app.command()
def validate(file: str):
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

def main():
    app()

if __name__ == "__main__":
    main()
