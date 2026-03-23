# veridra-core
AI verification and evaluation engine for LLM applications

## Run Modes

- Real provider mode (default):
  - `python -m veridra.cli run examples/basic_suite.yaml`
  - Requires `OPENAI_API_KEY` for `provider: openai`

- Mock mode (no API quota needed):
  - `python -m veridra.cli run examples/basic_suite.yaml --mock`
  - Uses deterministic local responses for development and demos
