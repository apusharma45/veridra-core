# veridra-core

![CI](https://img.shields.io/github/actions/workflow/status/veridra-labs/veridra-core/ci.yml?branch=main&label=ci)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

CLI-first testing framework for LLM applications.

## What It Does

- Validates YAML test suites for AI behavior.
- Runs suites against providers (`openai`, `ollama`) or deterministic `--mock` mode.
- Grades behavior for `correctness`, `safety`, and injection-style checks.
- Produces readable terminal output + machine-readable JSON reports.
- Compares baseline vs current runs for regression detection.

## 2-Minute Quick Start

```bash
pip install -e .
veridra run examples/basic_suite.yaml --mock --output out/basic.json
veridra report out/basic.json
```

If `veridra` is not found on Windows, run:

```bash
python -m veridra.cli run examples/basic_suite.yaml --mock --output out/basic.json
```

## Demo Suites (Marketing Assets)

- `examples/basic_suite.yaml`
- `examples/safety_suite.yaml`
- `examples/injection_suite.yaml`
- `examples/chatbot_suite.yaml`

Try them quickly:

```bash
veridra run examples/safety_suite.yaml --mock --output out/safety.json
veridra run examples/injection_suite.yaml --mock --output out/injection.json
veridra run examples/chatbot_suite.yaml --mock --output out/chatbot.json
```

## Example Output

```text
Suite: basic-safety
Provider: openai
Model: gpt-4.1-mini
Run mode: mock

??????????????????????????????????????????????????????????????????????????????
? Case     ? Status ? Graders               ? Latency (ms)? Retries ? Reason ?
??????????????????????????????????????????????????????????????????????????????
¦ fact-1   ¦ PASS   ¦ correctness=pass      ¦ 2           ¦ 0       ¦        ¦
¦ safe-1   ¦ PASS   ¦ safety=pass           ¦ 1           ¦ 0       ¦        ¦
+----------------------------------------------------------------------------+
Passed: 2
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
