# Plan 05 — Coverage measurement and CI

## Agent identity

You add **coverage tooling + CI** for `enjilib-jwt-auth` after the behavioral suite exists.  
Do not rewrite Wave B tests unless a trivial import path fix is required for collection. Do not change AuthN/AuthZ production semantics.

## Task

- **Task ID**: `jwt-test-audit-05-coverage-ci`
- **Title**: pytest-cov configuration and GitHub Actions test workflow
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / DevEx
- **Work mode**: Auto
- **Dependencies (filesystem)**: Wave A + Wave B test modules present and green

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
test -f tests/conftest.py
test -f tests/helpers/token_factory.py
test -f tests/test_cipher.py
test -f tests/test_claims.py
test -f tests/test_authz.py
test -f tests/test_verify_extract.py
uv run pytest -q
```

`uv run pytest -q` must exit 0 **before** you add coverage gates. If the suite is red, STOP and report failing tests — do not lower quality by deleting assertions.

---

## Context

### Problem

Audit found no coverage measurement and no CI. Even with local tests, merges are unprotected. After meaningful tests exist, add:

1. Coverage reporting for `src/enjilib_jwt`
2. An initial threshold (pragmatic, not vanity 100%)
3. GitHub Actions workflow on PRs/pushes that installs from lockfile and runs pytest

### Goal

- Developers run one documented coverage command.
- CI fails on test failure and on coverage below the agreed floor.
- README documents the commands accurately.

### Non-goals

- Branch protection settings in GitHub UI (cannot set from repo content alone).
- Expanding behavioral coverage beyond fixing collection issues.
- Publishing packages / version bumps.
- Monorepo-root CI integration (this nested repo has its own `.git`).

### Constraints

- Prefer `uv sync --frozen --all-extras` in CI for reproducibility.
- Add `pytest-cov` as a **dev** optional dependency only.
- Initial coverage fail-under: start at a level the **current** suite actually meets (measure first, then set). Suggested target once Wave B is complete: **≥85%** on `src/enjilib_jwt` if achievable; otherwise set the highest integer the suite currently clears and note the gap in the done report.
- Do not add Codecov/Third-party upload unless already standard for this nested repo (it is not — skip uploads; print term report + XML optional artifact).

---

## Acceptance criteria

- [ ] AC-1: `pytest-cov` declared in `[project.optional-dependencies] dev` (or equivalent) | verify: `grep: pytest-cov pyproject.toml`
- [ ] AC-2: Lockfile updated to include pytest-cov | verify: `grep: pytest-cov uv.lock` (or package name form used by uv)
- [ ] AC-3: Documented/configed coverage run targets `src/enjilib_jwt` | verify: `grep: enjilib_jwt` in pytest addopts / pyproject / README
- [ ] AC-4: Coverage fail-under configured and locally passing | verify: `manual: uv run pytest --cov=enjilib_jwt --cov-report=term-missing --cov-fail-under=<N>`
- [ ] AC-5: GitHub Actions workflow exists under `.github/workflows/` and runs pytest (with coverage) | verify: `file_exists: .github/workflows/test.yml` (name may vary)
- [ ] AC-6: README Development section documents install + pytest + coverage commands that work | verify: `manual: README commands`
- [ ] AC-7: Full suite still green | verify: `manual: uv run pytest -v`

---

## Implementation plan

### Step 1 — Measure baseline

```bash
cd be/shared/enjilib-jwt-auth
uv add --dev pytest-cov   # or edit pyproject + uv lock
uv sync --all-extras
uv run pytest --cov=enjilib_jwt --cov-report=term-missing -v
```

Record total coverage %. Choose `--cov-fail-under` ≤ measured total (prefer ≥85 if measured ≥85).

### Step 2 — Persist config

Prefer `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
  "pytest>=7.0",
  "pytest-asyncio>=0.21.0",
  "pytest-cov>=4.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
# If moving config from pytest.ini, delete duplicate conflicting pytest.ini settings
# or keep pytest.ini [pytest] addopts instead.

[tool.coverage.run]
source = ["enjilib_jwt"]
branch = true

[tool.coverage.report]
show_missing = true
skip_empty = true
fail_under = 85  # adjust to measured floor
```

Keep a single source of truth. If both `pytest.ini` and `[tool.pytest.ini_options]` exist, avoid contradictory keys.

Optional `addopts`:

```ini
addopts = --cov=enjilib_jwt --cov-report=term-missing --cov-fail-under=85
```

Only enable fail-under in default addopts if local DX remains acceptable; otherwise document an explicit `make test-cov` / README command and use fail-under in CI.

### Step 3 — CI workflow

Create `.github/workflows/test.yml` (adjust Python version to `>=3.9`, recommend 3.11):

```yaml
name: test

on:
  push:
    branches: [main, staging]
  pull_request:

jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install
        run: uv sync --frozen --all-extras
      - name: Test with coverage
        run: uv run pytest -v --cov=enjilib_jwt --cov-report=term-missing --cov-fail-under=85
```

Adjust `fail-under` to the chosen N. If `--frozen` fails due to lock drift you introduced, regenerate lock in this plan.

### Step 4 — README

Update Development section so documented commands match reality:

```bash
uv sync --all-extras
uv run pytest -v
uv run pytest --cov=enjilib_jwt --cov-report=term-missing
```

Remove or fix any stale `pip install -e ".[dev]"`-only story if uv is now canonical — you may keep pip as alternate if it still works.

### Step 5 — Validate

```bash
uv sync --frozen --all-extras
uv run pytest -v --cov=enjilib_jwt --cov-report=term-missing --cov-fail-under=<N>
```

### Files allowed

- `pyproject.toml`
- `uv.lock`
- `pytest.ini` (only to align with coverage addopts / avoid duplication)
- `.github/workflows/*.yml`
- `README.md`
- Optionally `Makefile` with `test` / `test-cov` targets if you want ergonomics — not required

### Forbidden

- Deleting or weakening Wave B assertions to hit coverage
- Production crypto/authz changes
- Unrelated monorepo root CI

---

## Risks & mitigations

- Threshold too high → set to measured floor, list uncovered lines in done report for a follow-up.
- `setup.py` vs pyproject drift → do not reintroduce missing cryptography; leave packaging consistent with Wave A.
- CI without uv cache → slower but fine; keep workflow simple.

---

## Done report

1. Measured coverage % and chosen `fail_under`
2. Workflow path + trigger branches
3. README commands updated (yes/no)
4. Final pytest+cov command output summary
5. Uncovered lines (if any) worth a follow-up — list briefly, do not expand scope
