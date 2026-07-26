# Plan 02 — Packaging residuals (typing marker + ignore policy)

## Agent identity

You close **residual packaging cognitive debt** so metadata no longer contradicts the typed package claim.  
Do **not** rewrite README/API narrative (plan 01). Do **not** edit `AGENTS.md` / handoff / decisions / EXTERNAL_CONTRACTS. Do **not** change AuthN/AuthZ code.

## Task

- **Task ID**: `jwt-cogdebt-02-packaging`
- **Title**: Add `py.typed`, `.gitignore`, keep packaging deps aligned
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Packaging
- **Work mode**: Auto
- **Dependencies**: Prerequisite — pytest green

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
uv sync --all-extras
uv run pytest -q
test -f pyproject.toml
test -f setup.py
```

---

## Context

### Problem

Cognitive debt audit flagged dual packaging / missing cryptography in some metadata. Re-review finds:

- Runtime deps: **`cryptography` is now present** in both `pyproject.toml` and `setup.py` — do not regress.
- `pyproject.toml` still declares `[tool.setuptools.package-data] enjilib_jwt = ["py.typed"]` but **`src/enjilib_jwt/py.typed` is missing**.
- No `.gitignore` → `.coverage`, `__pycache__`, `.venv`, egg-info / dist noise pollute agent context.
- `setup.py` `extras_require.dev` omits `pytest-cov` while `pyproject.toml` optional-dev includes it.

### Goal

Typed marker on disk; generated/local artifacts ignored; setuptools extras mirror pyproject where retained.

### Non-goals

- Deleting `setup.py`.
- Publishing to PyPI.
- Changing package name/version/import path.
- Rewriting install prose in README (plan 01).

### Constraints

- `pyproject.toml` remains packaging source of truth (see existing `docs/decisions/002_packaging_source_of_truth.md` if present).
- Keep `setup.py` install_requires aligned with project.dependencies.

---

## Acceptance criteria

- [ ] AC-1: `src/enjilib_jwt/py.typed` exists (empty marker file OK) | verify: `test -f src/enjilib_jwt/py.typed`
- [ ] AC-2: `pyproject.toml` still lists `enjilib_jwt = ["py.typed"]` package-data | verify: `rg -n 'py\.typed' pyproject.toml`
- [ ] AC-3: `.gitignore` exists and ignores at least `.venv/`, `__pycache__/`, `.pytest_cache/`, `.coverage`, `dist/`, `*.egg-info/`, `build/` | verify: file + `rg -n` each pattern
- [ ] AC-4: `setup.py` `install_requires` still includes `cryptography` and `pyjwt` matching pyproject floors | verify: `rg -n 'cryptography|pyjwt' setup.py pyproject.toml`
- [ ] AC-5: `setup.py` `extras_require.dev` includes `pytest-cov` (aligned with pyproject) | verify: `rg -n 'pytest-cov' setup.py`
- [ ] AC-6: Pytest still green | verify: `uv run pytest -q`

---

## Implementation steps

1. Create empty `src/enjilib_jwt/py.typed`.
2. Add `.gitignore` with standard Python/packaging ignores for this repo (do not ignore `uv.lock` or source).
3. Align `setup.py` `extras_require.dev` with `pyproject.toml` `[project.optional-dependencies].dev`.
4. If a committed `*.egg-info/` directory exists in the tree and is tracked, stop short of mass `git rm` unless clearly untracked — prefer ignore + note in done report; do not fight git history beyond ignore policy unless egg-info is untracked local junk.
5. Run pytest.

---

## Done report (required)

- Files added/changed
- AC evidence
- Whether any egg-info was present/tracked (fact only)

## Out of scope

- README install URL fixes (plan 01)
- Claiming “packaging fully fixed” in AGENTS (plan 05 will do truth repair after this lands)
