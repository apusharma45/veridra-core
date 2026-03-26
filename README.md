# veridra-core
AI verification and evaluation engine for LLM applications

## Run Modes

- Real provider mode (default):
  - `python -m veridra.cli run examples/basic_suite.yaml`
  - Requires `OPENAI_API_KEY` for `provider: openai`

- Ollama provider mode (local, quota-free):
  - `python -m veridra.cli run examples/ollama_suite.yaml`
  - Optional env: `OLLAMA_BASE_URL` (default: `http://localhost:11434`)

- Mock mode (no API quota needed):
  - `python -m veridra.cli run examples/basic_suite.yaml --mock`
  - Uses deterministic local responses for development and demos

## Compare Reports

- Compare baseline and current results without rerunning models:
  - `python -m veridra.cli compare out/baseline.json out/current.json`
  - `python -m veridra.cli compare out/baseline.json out/current.json --verbose`

## First 5 Minutes

1. Create a starter suite:
   - `python -m veridra.cli init quickstart.yaml --template basic --provider openai`
2. Validate it:
   - `python -m veridra.cli validate quickstart.yaml --verbose`
3. Run in mock mode:
   - `python -m veridra.cli run quickstart.yaml --mock --output out/quickstart.json`
4. Render report later:
   - `python -m veridra.cli report out/quickstart.json --verbose`
5. Compare two runs:
   - `python -m veridra.cli compare out/baseline.json out/current.json`

## Discoverability Commands

- List built-in suite examples and copy-ready commands:
  - `python -m veridra.cli examples`

## Shell Completion

- Install completion for your current shell:
  - `python -m veridra.cli --install-completion`
- Show completion script manually:
  - `python -m veridra.cli --show-completion`

## Development Checks

Run these before opening a PR:

- `ruff check .`
- `ruff format --check .`
- `mypy src/veridra`
- `python -m pytest -q -p no:cacheprovider --basetemp=tests/.pytest_tmp`
- `python -m build`

## CI Quickstart (Mock-First)

- Validate suite:
  - `python -m veridra.cli validate examples/basic_suite.yaml`
- Generate baseline in mock mode:
  - `python -m veridra.cli run examples/basic_suite.yaml --mock --output out/baseline.json`
- Generate current run in mock mode:
  - `python -m veridra.cli run examples/basic_suite.yaml --mock --output out/current.json`
- Compare for regressions:
  - `python -m veridra.cli compare out/baseline.json out/current.json`

## Ollama Setup & Troubleshooting

- Start Ollama daemon before running suites:
  - `ollama serve`
- Pull the model used in suite YAML:
  - `ollama pull llama3.2`
- If Veridra cannot connect, verify base URL and daemon status:
  - `OLLAMA_BASE_URL=http://localhost:11434`
  - check if `/api/generate` is reachable from your machine
