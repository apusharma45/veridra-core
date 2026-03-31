# veridra-core

![CI](https://img.shields.io/github/actions/workflow/status/veridra-labs/veridra-core/ci.yml?branch=main&label=ci)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

CLI-first eval runner for LLM apps: validate suites, run tests, catch safety/regression issues.

What it is: A CLI tool to test LLM behavior from YAML suites.  
Why it matters: Replace manual prompt testing with repeatable checks in local dev and CI.  
Run now: `pip install -e .` then `veridra run examples/basic_suite.yaml --mock`

## 2-Minute Quick Start

Install from GitHub:

```bash
pip install "git+https://github.com/apusharma45/veridra-core.git"
```

Or for local development:

```bash
pip install -e .
veridra validate examples/basic_suite.yaml
veridra run examples/basic_suite.yaml --mock
veridra report veridra-results.json
```

If `veridra` is not found on Windows, use:

```bash
python -m veridra.cli run examples/basic_suite.yaml --mock
```

![Veridra run output](docs/assets/veridra-run-output.png)

## Why Use Veridra Core?

- Run deterministic, reusable eval suites instead of ad-hoc prompt checks.
- Catch failures in correctness, safety, and regression before deployment.
- Integrate eval checks into CI with machine-readable JSON reports.
- Keep evaluation workflows consistent across developers and releases.

## Who Is This For?

- LLM app developers building chatbots, assistants, and RAG features.
- QA and platform teams that need repeatable AI quality gates in CI.
- Security/safety teams validating refusal behavior and injection resistance.

## What It Does

- Validates YAML test suites for AI behavior.
- Runs suites against providers (`openai`, `ollama`) or deterministic `--mock` mode.
- Grades behavior for `correctness` and `safety`.
- Produces readable terminal output + machine-readable JSON reports.
- Compares baseline vs current runs for regression detection.

## What’s Included In v0.1.0

- Commands: `validate`, `run`, `report`, `compare`, `init`, `examples`.
- Run controls: `--mock`, `--model`, `--timeout-ms`, `--retries`, `--fail-fast`, `--verbose`.
- Providers: OpenAI, Ollama, and deterministic mock mode.
- Regression gate support with baseline comparison and drift reporting.
- JSON reports with schema versioning for reproducible workflows.

## Limitations / Current Scope

- Grading is heuristic and rule-based, not a semantic truth engine.
- Primary experience is CLI/local and CI-focused (no hosted dashboard).
- Provider support is currently limited to OpenAI, Ollama, and mock mode.
- Best fit today is small-to-medium eval suites.

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

## Better Than Manual Prompt Testing

Manual testing is slow, inconsistent, and hard to reproduce. Veridra Core uses deterministic suite definitions, repeatable automated runs, baseline regression checks, and machine-readable outputs so quality checks can run in CI like normal software tests.

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
