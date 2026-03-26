# veridra-core
AI verification and evaluation engine for LLM applications

## Run Modes

- Real provider mode (default):
  - `python -m veridra.cli run examples/basic_suite.yaml`
  - Requires `OPENAI_API_KEY` for `provider: openai`

- Mock mode (no API quota needed):
  - `python -m veridra.cli run examples/basic_suite.yaml --mock`
  - Uses deterministic local responses for development and demos

## Compare Reports

- Compare baseline and current results without rerunning models:
  - `python -m veridra.cli compare out/baseline.json out/current.json`
  - `python -m veridra.cli compare out/baseline.json out/current.json --verbose`

## CI Quickstart (Mock-First)

- Validate suite:
  - `python -m veridra.cli validate examples/basic_suite.yaml`
- Generate baseline in mock mode:
  - `python -m veridra.cli run examples/basic_suite.yaml --mock --output out/baseline.json`
- Generate current run in mock mode:
  - `python -m veridra.cli run examples/basic_suite.yaml --mock --output out/current.json`
- Compare for regressions:
  - `python -m veridra.cli compare out/baseline.json out/current.json`
