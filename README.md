# veridra-core
AI verification and evaluation engine for LLM applications.

## Run Modes

- Real provider mode (default):
  - `python -m veridra.cli run examples/basic_suite.yaml`
  - Requires `OPENAI_API_KEY` for `provider: openai`
- Ollama provider mode (local, quota-free):
  - `python -m veridra.cli run examples/ollama_suite.yaml`
  - Optional env: `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
- Mock mode (no API quota needed):
  - `python -m veridra.cli run examples/basic_suite.yaml --mock`

## Canonical Quickstart

1. Create suite:
   - `python -m veridra.cli init quickstart.yaml --template basic --provider openai`
2. Validate:
   - `python -m veridra.cli validate quickstart.yaml --verbose`
3. Run locally in mock mode:
   - `python -m veridra.cli run quickstart.yaml --mock --output out/quickstart.json`
4. Render report:
   - `python -m veridra.cli report out/quickstart.json --verbose`
5. Compare runs:
   - `python -m veridra.cli compare out/quickstart.json out/quickstart.json`

## Development Checks

Run these before opening a PR:

- `ruff check src`
- `ruff format --check src`
- `mypy src/veridra`
- `python -m pytest -q -p no:cacheprovider --basetemp=tests/.pytest_tmp`
- `python -m build`

## Release Steps

1. Run `RELEASE_CHECKLIST.md` commands locally.
2. Bump version in `pyproject.toml`.
3. Commit version bump.
4. Tag and push:
   - `git tag vX.Y.Z`
   - `git push origin vX.Y.Z`

## Windows Troubleshooting

- If `veridra` command is not found after install, run via module:
  - `python -m veridra.cli --help`
- If scripts are not on PATH, add:
  - `%APPDATA%\Python\Python3xx\Scripts`
- If build/install fails due permissions, run terminal as user with write access to temp and project folders.

## Discoverability

- Built-in examples:
  - `python -m veridra.cli examples`
- Shell completion:
  - `python -m veridra.cli --install-completion`
  - `python -m veridra.cli --show-completion`
