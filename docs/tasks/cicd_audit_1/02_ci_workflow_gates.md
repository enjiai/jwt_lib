# Plan 02 — CI workflow gates (pytest + mypy + build)

## Agent identity

You land the **first real GitHub Actions pipeline** for `enjilib-jwt-auth` and extend it with package build + strict mypy once pytest is wired.  
Do **not** create a release/publish workflow (plan 04). Do **not** create `Makefile` (plan 01). Do **not** rewrite CONTRIBUTING/CHANGELOG process prose (plan 03/04). Do **not** change AuthN/AuthZ semantics or weaken coverage.

## Task

- **Task ID**: `jwt-cicd-02-ci-gates`
- **Title**: GitHub Actions test workflow with coverage, mypy, and build
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / DevEx
- **Work mode**: Auto
- **Dependencies**: None (Wave A; parallel with 01). Prefer absorbing any existing local draft under `.github/workflows/test.yml`.

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
test -f uv.lock
uv sync --all-extras
uv run pytest -q
```

Expect **≈74 passed** with coverage fail-under 100%. If red → STOP.

---

## Context

### Problem

CI/CD audit (and provider re-check 2026-07-27): `origin/main` has **zero** workflows and **zero** runs. Local untracked draft `.github/workflows/test.yml` runs pytest only. `AGENTS.md` documents `mypy --strict` but mypy is **not** in dev dependencies. `.gitignore` is missing on remote while `__pycache__` is committed.

### Goal

1. Commit a CI workflow on `pull_request` + `push` to `main` (and `staging` if already in draft).
2. Install with `uv sync --frozen --all-extras`.
3. Gate on: **pytest+coverage**, **strict mypy**, **`uv build`**.
4. Declare `mypy` as a dev optional dependency and refresh `uv.lock`.
5. Commit a sensible `.gitignore` so CI/PRs do not keep adding caches/egg-info.

### Non-goals

- Required status checks in GitHub UI (plan 05 / human).
- PyPI trusted publishing / tag release workflow (plan 04).
- Codecov uploads.
- Multi-OS matrix (Linux only is enough).
- Changing production source to satisfy mypy by altering token behavior — only add annotations if strictly necessary and behavior-preserving; prefer fixing types without API changes.

### Constraints

- Prefer `astral-sh/setup-uv` + `actions/setup-python` (draft already does).
- Pin major action versions reasonably (`@v4` / `@v5` OK); do not use unpinned `@master`.
- Python: keep **3.11** as primary (matches draft). Optional matrix `3.9/3.11/3.12` is nice-to-have, not required for AC.
- CI must call the **same command strings** as the Makefile (plan 01), not necessarily `make` itself — either is fine; prefer explicit `uv …` in YAML for clearer logs.
- Job/check names must be stable and human-readable (Wave C will require them).

### Parallel-safety (file ownership)

**Owns exclusively:**

- `.github/workflows/test.yml` (create or replace draft)
- `pyproject.toml` — only to add `mypy` under `[project.optional-dependencies] dev` (and optional `[tool.mypy]` if needed)
- `uv.lock` — regenerate after mypy add
- `.gitignore` — create/commit if missing

**Must not touch:**

- `Makefile`
- `CONTRIBUTING.md`, `README.md`, `AGENTS.md`, `CHANGELOG.md` (docs parity is plan 03)
- `.github/workflows/release.yml`
- Issue/PR templates unless a trivial path fix is required to keep them valid — prefer leave templates as-is
- `src/enjilib_jwt/**` unless mypy forces a **non-behavioral** typing fix; if so, list every line in the done report and keep tests green

---

## Acceptance criteria

- [ ] AC-1: `.github/workflows/test.yml` exists and triggers on `pull_request` and push to `main` | verify: file + `on:` block
- [ ] AC-2: Install step uses `uv sync --frozen --all-extras` | verify: `grep -n 'uv sync --frozen --all-extras' .github/workflows/test.yml`
- [ ] AC-3: Pytest coverage gate runs in CI (fail-under 100%) | verify: workflow step + local `uv run pytest -q`
- [ ] AC-4: `mypy` is a declared dev dependency and locked | verify: `rg -n 'mypy' pyproject.toml uv.lock`
- [ ] AC-5: CI runs `uv run mypy src/enjilib_jwt --strict` (job or step) | verify: workflow grep
- [ ] AC-6: CI runs `uv build` (job or step) | verify: workflow grep
- [ ] AC-7: `.gitignore` excludes at least `__pycache__/`, `*.py[cod]`, `.venv/`, `dist/`, `*.egg-info/` | verify: file contents
- [ ] AC-8: Local mypy strict passes after dep install | verify: `uv sync --all-extras && uv run mypy src/enjilib_jwt --strict`
- [ ] AC-9: Local build passes | verify: `uv build`
- [ ] AC-10: Suite still green at 100% coverage | verify: `uv run pytest -q`

---

## Implementation plan

### Step 1 — Absorb or create workflow

If `.github/workflows/test.yml` already exists locally, **extend it** rather than delete history of the draft. Suggested jobs (one job with sequential steps is OK; separate jobs are nicer for required-check granularity):

```yaml
name: test

on:
  push:
    branches: [main, staging]
  pull_request:

jobs:
  quality:
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
        run: uv run pytest -v
      - name: Typecheck
        run: uv run mypy src/enjilib_jwt --strict
      - name: Build package
        run: uv build
```

If you split jobs (`pytest` / `typecheck` / `build`), give each a clear `name:` — Wave C may require one or all.

### Step 2 — Add mypy

```bash
uv add --dev mypy
# or edit pyproject.toml dev extras, then uv lock
uv sync --all-extras
uv run mypy src/enjilib_jwt --strict
```

Fix only typing issues that block `--strict`. Do not change runtime branches to silence mypy.

Optional minimal config in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.9"
strict = true
packages = ["enjilib_jwt"]
mypy_path = "src"
```

### Step 3 — `.gitignore`

Commit a root `.gitignore` covering Python caches, venv, build artifacts, coverage files, egg-info. Do **not** mass-delete already-tracked `__pycache__` unless trivial; at minimum stop new ones. If you untrack caches, keep the diff scoped.

### Step 4 — Validate locally (CI parity)

```bash
uv sync --frozen --all-extras
uv run pytest -v
uv run mypy src/enjilib_jwt --strict
uv build
```

### Step 5 — Done evidence

Record final **check/job names** as they will appear in GitHub (for plan 05), e.g. `test / quality` or `test / pytest`.

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| mypy strict fails on current code | Fix types only; if blocked on intentional dynamic patterns, use precise `typing`/`cast` — no `# type: ignore` without one-line justification in done report |
| Lockfile conflict with unrelated edits | Only touch lock for mypy |
| `--frozen` fails | Regenerate lock in this plan; never remove `--frozen` from CI |
| Templates already untracked under `.github/` | Leave issue/PR templates intact; only own `workflows/test.yml` |

---

## Done report

1. Workflow path + trigger summary
2. Job/step names (exact strings for required checks)
3. mypy version / whether any src typing edits were required (list files)
4. `uv build` artifact names produced locally
5. Confirmation pytest still 74/100% (or current count)
6. Files changed
