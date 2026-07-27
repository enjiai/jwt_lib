# Plan 01 — Local gate (Makefile)

## Agent identity

You add a **single reproducible local verification entrypoint** for `enjilib-jwt-auth` so humans and CI share the same command vocabulary.  
Do **not** create or edit GitHub Actions workflows (plan 02). Do **not** edit `CONTRIBUTING.md` / `CHANGELOG.md` (plans 03–04). Do **not** change AuthN/AuthZ production code or tests except if a Makefile path typo blocks collection (report; do not weaken assertions).

## Task

- **Task ID**: `jwt-cicd-01-local-gate`
- **Title**: Makefile wrapping uv sync / pytest / mypy / build
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / DevEx
- **Work mode**: Auto
- **Dependencies**: None (Wave A; parallel with 02)

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
test -f pyproject.toml
test -f uv.lock
uv sync --all-extras
uv run pytest -q
```

Expect pytest green (**≈74 passed**). If red → STOP and report; do not invent a green Makefile by dropping coverage.

---

## Context

### Problem

CI/CD audit: local quality commands exist but are scattered across README / AGENTS / CONTRIBUTING. There is no one command that developers and future CI can treat as the gate.

### Goal

A root `Makefile` with targets that wrap the **exact** uv-based commands used (or about to be used) in CI:

| Target | Behavior |
|---|---|
| `make sync` | `uv sync --frozen --all-extras` |
| `make test` | pytest with existing coverage fail-under (100%) |
| `make typecheck` | `uv run mypy src/enjilib_jwt --strict` (may fail until plan 02 adds mypy dep — see note) |
| `make build` | `uv build` |
| `make check` | `sync` + `test` + `typecheck` + `build` (full local gate) |

### Non-goals

- GitHub Actions YAML.
- Branch protection.
- Release / PyPI publishing.
- Installing mypy if missing — **prefer** calling `uv run mypy`; if mypy is absent, document that `make typecheck` / `make check` require plan 02’s dep, **or** add a tiny note in the Makefile comment. Do **not** expand `pyproject.toml` here (owned by 02) to avoid lockfile merge conflicts.

### Constraints

- Prefer `.PHONY` targets; no fancy Make macros.
- Use `uv run` / `uv sync --frozen` — do not invent pip-only paths as primary.
- Keep Makefile portable enough for macOS/Linux developer machines and ubuntu-latest.
- If you update README/AGENTS, change **only** the Development / Setup verification command lists to mention `make check` / `make test` — do not rewrite token docs.

### Parallel-safety (file ownership)

**Owns exclusively:**

- `Makefile`

**May touch lightly (command pointers only):**

- `README.md` — Development section: add `make test` / `make check` lines (keep existing uv commands).
- `AGENTS.md` — Setup and Verification: add `make check` as the preferred full gate (keep uv equivalents).

**Must not touch:**

- `.github/**`
- `pyproject.toml`, `uv.lock`
- `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`
- `src/**`, `tests/**`

---

## Acceptance criteria

- [ ] AC-1: `Makefile` exists at repo root | verify: `test -f Makefile`
- [ ] AC-2: `make test` runs the coverage-gated suite and exits 0 | verify: `make test`
- [ ] AC-3: `make sync` uses `--frozen --all-extras` | verify: `grep -n 'sync --frozen --all-extras' Makefile`
- [ ] AC-4: `make build` invokes `uv build` | verify: `grep -n 'uv build' Makefile`
- [ ] AC-5: `make check` depends on test (+ typecheck/build as designed) | verify: `grep -n '^check:' Makefile` and recipe contents
- [ ] AC-6: README or AGENTS documents `make check` (or `make test`) as the local gate | verify: `rg -n 'make (check|test)' README.md AGENTS.md`
- [ ] AC-7: Pytest still green without lowering fail-under | verify: `uv run pytest -q`

### Note on typecheck during Wave A parallel run

Plan 02 adds mypy to dev deps. Until 02 merges:

- `make typecheck` may fail with “mypy not found” — that is OK for AC if the target exists and the command string is correct.
- Prefer implementing `make check` so orchestrator can run full gate **after** both Wave A plans land.
- In the done report, state whether `make typecheck` passed or blocked on missing mypy.

---

## Implementation plan

### Step 1 — Create Makefile

Suggested shape (adapt, do not cargo-cult if repo conventions differ):

```makefile
.PHONY: sync test typecheck build check

sync:
	uv sync --frozen --all-extras

test: sync
	uv run pytest -v

typecheck: sync
	uv run mypy src/enjilib_jwt --strict

build: sync
	uv build

check: test typecheck build
```

Rely on `pyproject.toml` `[tool.pytest.ini_options]` / coverage `fail_under = 100` — do not duplicate conflicting `--cov-fail-under` unless already required by CI draft.

### Step 2 — Point docs at the gate

In README Development and/or AGENTS § Setup and Verification, add 2–4 lines:

```bash
make check   # preferred full local gate
make test    # pytest + coverage only
```

Do not delete existing `uv run pytest` examples.

### Step 3 — Validate

```bash
make test
# After plan 02: make check
```

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Merge conflict with 02 on README/AGENTS | Touch only command-list bullets; leave token/packaging sections alone |
| `make check` red without mypy | Expected until 02; report clearly |
| Windows Make | Out of scope; document uv fallbacks already present |

---

## Done report

1. Makefile targets list
2. `make test` output summary (pass count)
3. Whether `make typecheck` / `make check` ran or waited on mypy
4. Which doc files received command pointers
5. Files changed
