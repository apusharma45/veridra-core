# Contributing to veridra-core

Thanks for contributing to Veridra Core.

## Local Setup

1. Create and activate a virtual environment.
2. Install package + dev dependencies:
   - `pip install -e .[dev]`

## Required Checks Before PR

Run all of these locally:

- `ruff check .`
- `ruff format --check .`
- `mypy src/veridra`
- `python -m pytest -q -p no:cacheprovider --basetemp=tests/.pytest_tmp`
- `python -m build`

## CLI Smoke Check

- `python -m veridra.cli validate examples/basic_suite.yaml`
- `python -m veridra.cli run examples/basic_suite.yaml --mock --output out/local-smoke.json`
- `python -m veridra.cli report out/local-smoke.json`
- `python -m veridra.cli compare out/local-smoke.json out/local-smoke.json`

## Pull Request Notes

- Keep changes focused and test-backed.
- Update README/docs when behavior changes.
- Do not commit secrets or `.env` values.
