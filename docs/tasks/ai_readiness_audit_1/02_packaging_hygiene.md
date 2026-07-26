# Plan 02 — Packaging hygiene & typing marker

## Agent identity

You make **packaging / typing / ignore policy** consistent for `enjilib-jwt-auth`.  
Do **not** rewrite README/API narrative content (plan 01). Do **not** add `AGENTS.md` or process docs (Wave B). Do **not** change AuthN/AuthZ production semantics.

## Task

- **Task ID**: `jwt-ai-ready-02-packaging`
- **Title**: Add `py.typed`, ignore generated artifacts, align packaging metadata
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Packaging
- **Work mode**: Auto
- **Dependencies**: Prerequisite — pytest green from `test_audit_1`

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -q
test -f pyproject.toml
test -f setup.py
```

---

## Context

### Problem

AI-readiness audit found packaging drift:

- `pyproject.toml` declares `[tool.setuptools.package-data] enjilib_jwt = ["py.typed"]` but **no** `src/enjilib_jwt/py.typed` exists.
- `setup.py` historically lagged `pyproject.toml` (cryptography may already be fixed — verify, do not regress).
- Committed `src/enjilib_jwt_auth.egg-info/` and no `.gitignore` → agents treat generated metadata as source of truth; local `__pycache__`, `.coverage`, `.venv` pollute status.
- Dual packaging (`pyproject.toml` + `setup.py`) remains; keep both aligned rather than deleting `setup.py` in this plan (consumers/scripts may still call it).

### Goal

One clear packaging policy: typed marker ships with the package; generated/local artifacts are ignored; runtime deps match across `pyproject.toml` and `setup.py`.

### Non-goals

- Changing package name/version.
- Removing `setup.py` entirely.
- Rewriting install docs (plan 01).
- Adding lint/typecheck CI jobs beyond what already exists (do not expand CI unless required for packaging — prefer leave `.github/workflows/test.yml` alone).

### Constraints

- Python `>=3.9`.
- Empty `py.typed` marker file is enough (PEP 561).
- If egg-info is currently tracked by git, stop tracking it and ignore it going forward (do not leave stale committed metadata as the “source of truth”).
- Do not weaken pytest coverage gates in `pyproject.toml`.

---

## Acceptance criteria

- [ ] AC-1: `src/enjilib_jwt/py.typed` exists (empty file OK) | verify: `test -f src/enjilib_jwt/py.typed`
- [ ] AC-2: `pyproject.toml` still includes package-data for `py.typed` | verify: `grep -n py.typed pyproject.toml`
- [ ] AC-3: `setup.py` includes `cryptography` in `install_requires` and includes `package_data` (or equivalent) so `py.typed` is installed | verify: `grep -n cryptography setup.py` and package_data / include_package_data
- [ ] AC-4: Root `.gitignore` ignores at least: `.venv/`, `__pycache__/`, `*.egg-info/`, `.pytest_cache/`, `.coverage`, `htmlcov/`, `dist/`, `build/` | verify: `file_exists: .gitignore` + grep
- [ ] AC-5: Egg-info is no longer treated as source — either untracked/removed from the index or clearly regenerable; working tree does not rely on committed egg-info as docs | verify: `git check-ignore -v src/enjilib_jwt_auth.egg-info` or `git status` shows it ignored/deleted from tracking
- [ ] AC-6: `uv sync --all-extras && uv run pytest -q` still exits 0 | verify: manual
- [ ] AC-7: Editable/local import still works: `uv run python -c "from enjilib_jwt import JWTAuthenticator, JWTClaims"` | verify: manual

---

## Analysis

### Current packaging facts (verify before editing)

- Project name: `enjilib-jwt-auth`
- Import package: `enjilib_jwt` under `src/`
- Runtime deps expected: `pyjwt>=2.8.0`, `cryptography>=44.0.1`
- Dev extras: pytest family + pytest-cov (do not remove)

### Recommended `.gitignore` (minimum)

```gitignore
.venv/
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
dist/
build/
.pytest_cache/
.coverage
coverage.xml
htmlcov/
.mypy_cache/
.ruff_cache/
*.egg
```

### `setup.py` package_data example

```python
package_data={"enjilib_jwt": ["py.typed"]},
include_package_data=True,
```

If you use `include_package_data=True`, ensure something actually includes `py.typed` (package_data is enough without MANIFEST.in for this single file).

### Git note for egg-info

If egg-info is tracked:

```bash
git rm -r --cached src/enjilib_jwt_auth.egg-info
```

Do **not** `git commit` unless the user/orchestrator explicitly asked for a commit in this session — prepare the tree; report status. If commit is required by orchestrator instructions in the launch prompt, follow that prompt.

---

## Implementation plan

### Files you may create/modify

**Allowed:**

- `src/enjilib_jwt/py.typed` (create)
- `.gitignore` (create/update)
- `setup.py` (align deps + package_data only)
- `pyproject.toml` (only if needed for package-data / discoverability — keep minimal)
- `uv.lock` only if a packaging change forces lock refresh (prefer avoid)
- Remove/untrack `src/enjilib_jwt_auth.egg-info/**` as generated

**Forbidden:**

- `README.md`, `API.md` narrative edits (plan 01)
- `src/enjilib_jwt/*.py` behavior changes
- `tests/**`
- `AGENTS.md`, CONTRIBUTING/SECURITY/CHANGELOG, `docs/decisions/**`, `docs/handoff.md`
- Expanding or rewriting `.github/workflows/` (leave CI alone)

### Step-by-step

1. Create empty `src/enjilib_jwt/py.typed`.
2. Align `setup.py` `install_requires` + `package_data`.
3. Confirm `pyproject.toml` package-data entry remains.
4. Add `.gitignore`.
5. Untrack egg-info if tracked; leave directory deletable/ignored.
6. Validate sync + pytest + import.

### Exit criteria

- All AC checked.
- Do not start Wave B yourself.

---

## Done report (for parent orchestrator)

Report:

1. Commands run + exit codes
2. Files created/changed/untracked
3. Whether egg-info was previously tracked and what you did
4. Confirmation you did not edit README/API
