# veridra-core

![CI](https://img.shields.io/github/actions/workflow/status/veridra-labs/veridra-core/ci.yml?branch=main&label=ci)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

CLI-first testing framework for LLM applications.

## What It Does

- Validates YAML test suites for AI behavior.
- Runs suites against providers (`openai`, `ollama`) or deterministic `--mock` mode.
- Grades behavior for `correctness` and `safety`.
- Produces readable terminal output + machine-readable JSON reports.
- Compares baseline vs current runs for regression detection.

## 2-Minute Quick Start

```bash
pip install -e .
veridra run examples/basic_suite.yaml --mock --output out/basic.json
veridra report out/basic.json
```

If `veridra` is not found on Windows, use:

```bash
python -m veridra.cli run examples/basic_suite.yaml --mock --output out/basic.json
```

## Full Reference Suites (15 Cases Each)

- `examples/safety_suite.yaml` (safety refusal/normal behavior)
- `examples/injection_suite.yaml` (prompt-injection resistance)
- `examples/chatbot_suite.yaml` (mixed chatbot quality checks)

### Copy-Paste Commands

```bash
veridra validate examples/safety_suite.yaml
veridra run examples/safety_suite.yaml --mock --output out/safety.json
veridra report out/safety.json
veridra compare out/safety.json out/safety.json

veridra validate examples/injection_suite.yaml
veridra run examples/injection_suite.yaml --mock --output out/injection.json
veridra report out/injection.json
veridra compare out/injection.json out/injection.json

veridra validate examples/chatbot_suite.yaml
veridra run examples/chatbot_suite.yaml --mock --output out/chatbot.json
veridra report out/chatbot.json
veridra compare out/chatbot.json out/chatbot.json
```

## Example Output

```text
Suite: chatbot-suite
Provider: openai
Model: gpt-4.1-mini
Run mode: mock

Case                Status   Graders                          Latency  Retries  Reason
chat-correct-1      PASS     correctness=pass                     2       0
chat-safe-refuse-1  PASS     safety=pass                          1       0

Passed: 15
Failed: 0
Score: 100.0%
```

## Core Commands

- `veridra validate <suite.yaml>`
- `veridra run <suite.yaml> [--mock] [--model ...] [--output ...] [--verbose]`
- `veridra report <results.json> [--verbose]`
- `veridra compare <baseline.json> <current.json> [--verbose]`
- `veridra init <path> [--provider ...] [--template ...]`
- `veridra examples`

## Development Checks

```bash
ruff check src
ruff format --check src
mypy src/veridra
python -m pytest -q -p no:cacheprovider --basetemp=tests/.pytest_tmp
python -m build
```

## Contributing

See `CONTRIBUTING.md`.

## Releasing

See `RELEASING.md` and `RELEASE_CHECKLIST.md`.
