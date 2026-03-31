# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [0.1.0] - 2026-03-31

### Added
- CLI commands: `validate`, `run`, `report`, `compare`, `init`, and `examples`.
- Mock execution mode for deterministic local development and CI.
- Provider support for OpenAI and Ollama.
- Built-in graders for correctness and safety.
- Regression comparison workflow using baseline/current JSON reports.
- Run controls: model override, retries, timeout, fail-fast, and verbose diagnostics.
- JSON report schema versioning (`schema_version: "1.0"`).
- Full reference suites (safety, injection, chatbot) for demos and onboarding.
- CI, release, contributing, and release checklist documentation.

