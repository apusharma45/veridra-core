# Releasing veridra-core

This project uses tag-triggered GitHub Releases (`v*.*.*`).

## Canonical Release Steps

1. Complete all items in `RELEASE_CHECKLIST.md`.
2. Bump version in `pyproject.toml`.
3. Commit the version bump.
4. Tag and push:
   - `git tag vX.Y.Z`
   - `git push origin vX.Y.Z`

## What the Release Workflow Does

- Runs quality gates (`ruff`, `mypy`, `pytest`).
- Builds wheel + sdist.
- Verifies artifacts exist before publish.
- Creates GitHub Release with generated notes.
- Uploads `dist/*.whl` and `dist/*.tar.gz`.

## Dry Run Recommendation

Use a sandbox branch/repo and temporary semver tag before production release.

## Windows Troubleshooting

- If `veridra` command is not found, run:
  - `python -m veridra.cli --help`
- If script entry points are not on PATH, add:
  - `%APPDATA%\Python\Python3xx\Scripts`
