# Contributing to veridra-core

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -e .[dev]`

## Canonical Developer Checks

Run all checks before opening a PR:

- `ruff check src`
- `ruff format --check src`
- `mypy src/veridra`
- `python -m pytest -q -p no:cacheprovider --basetemp=tests/.pytest_tmp`
- `python -m build`

## Canonical Quickstart Smoke

- `python -m veridra.cli init quickstart.yaml --template basic --provider openai`
- `python -m veridra.cli validate quickstart.yaml --verbose`
- `python -m veridra.cli run quickstart.yaml --mock --output out/quickstart.json`
- `python -m veridra.cli report out/quickstart.json --verbose`
- `python -m veridra.cli compare out/quickstart.json out/quickstart.json`

## Pull Request Notes

- Keep changes focused and tested.
- Update docs when behavior changes.
- Never commit secrets or real `.env` values.
