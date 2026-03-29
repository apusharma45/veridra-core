# v0.1.0 Release Candidate Checklist

Run from repository root.

## 1) Quality Gates

- [ ] `ruff check src`
- [ ] `ruff format --check src`
- [ ] `mypy src/veridra`
- [ ] `python -m pytest -q -p no:cacheprovider --basetemp=tests/.pytest_tmp`

## 2) Packaging

- [ ] `python -m build`
- [ ] `python -m pip install --force-reinstall dist/veridra_core-0.1.0-py3-none-any.whl`
- [ ] `python -m veridra.cli --help`

## 3) Mock Runtime Smoke

- [ ] `python -m veridra.cli validate examples/basic_suite.yaml`
- [ ] `python -m veridra.cli run examples/basic_suite.yaml --mock --output out/rc-current.json`
- [ ] `python -m veridra.cli report out/rc-current.json`
- [ ] `python -m veridra.cli compare out/rc-current.json out/rc-current.json`

## 4) Release Trigger

- [ ] `git tag v0.1.0`
- [ ] `git push origin v0.1.0`
- [ ] Verify GitHub Release contains `.whl` and `.tar.gz` artifacts

## Notes

- If local provider quotas are unavailable, use mock mode for smoke checks.
- Tag push and GitHub Release verification require remote repository access.
