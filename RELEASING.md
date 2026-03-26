# Releasing veridra-core

This project uses GitHub tag-based releases.

## Pre-release Checklist

Run locally:

- `ruff check .`
- `ruff format --check .`
- `mypy src/veridra`
- `python -m pytest -q -p no:cacheprovider --basetemp=tests/.pytest_tmp`
- `python -m build`

## Create a Release

1. Update version in `pyproject.toml`.
2. Commit the version bump.
3. Create and push a semver tag:
   - `git tag vX.Y.Z`
   - `git push origin vX.Y.Z`

## What Happens Automatically

When a tag like `v1.2.3` is pushed:

- GitHub Actions runs quality checks.
- Build artifacts (`.whl`, `.tar.gz`) are produced.
- A GitHub Release is created with generated notes.
- Artifacts are attached to that release.

## Dry Run Recommendation

Before tagging production, test the workflow in a sandbox branch/repo with a temporary tag.
