# Plan 04 — Release automation

## Agent identity

You add a **tag-triggered package release workflow** and update the changelog’s publish instructions so releases are no longer “build on a laptop + twine upload” as the only path.  
Do **not** edit the PR test workflow beyond reading it for patterns (02 owns it). Do **not** edit CONTRIBUTING/README/AGENTS (03). Do **not** change library runtime code.

## Task

- **Task ID**: `jwt-cicd-04-release`
- **Title**: Tag-triggered build + publish workflow (trusted publishing preferred)
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Release
- **Work mode**: Auto
- **Dependencies**: Wave A CI test workflow exists and locally mirrors install/build commands

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
test -f .github/workflows/test.yml
test -f CHANGELOG.md
test -f pyproject.toml
uv sync --frozen --all-extras
uv build
```

If `uv build` fails → STOP; do not add a release workflow on a broken build.

---

## Context

### Problem

CI/CD audit: releases are fully manual (`CHANGELOG.md` → version bump → git tag → `python -m build` → `twine upload`). No CI publishes artifacts. For a shared auth library, manual uploads are error-prone and unverified against clean runners.

### Goal

1. `.github/workflows/release.yml` triggered by version tags (`v*.*.*`) or `workflow_dispatch`.
2. Clean checkout → `uv sync --frozen --all-extras` → run tests → `uv build`.
3. Publish path via **PyPI trusted publishing (OIDC)** if credentials/environment can be documented without storing long-lived tokens in the repo.
4. CHANGELOG release section updated to describe the automated path and remaining human steps (version bump, changelog cut, tag push).

### Non-goals

- Actually publishing a real package version to PyPI as part of this task (no surprise 0.1.0 yank/upload unless a maintainer explicitly asks in-session).
- Semantic-release / commitizen / auto-bump bots.
- Docker images.
- Editing PR `test.yml` behavior.

### Constraints

- **Never** commit PyPI API tokens or `.pypirc`.
- Prefer GitHub `environment: release` + `permissions: id-token: write` for OIDC.
- If trusted publishing cannot be fully configured from the repo alone, ship the workflow **with publish step gated** (environment protection) and document the one-time PyPI/GitHub admin setup in CHANGELOG and the done report.
- Fallback acceptable for AC: workflow builds artifacts and uploads them as **GitHub Release assets** / `actions/upload-artifact`, with a clearly marked optional PyPI publish job that maintainers enable after OIDC is configured.
- Tag pattern must match project SemVer guidance in CHANGELOG.

### Parallel-safety (file ownership)

**Owns exclusively:**

- `.github/workflows/release.yml`
- `CHANGELOG.md` — **Unreleased Versioning Guide / Publish** sections only (keep historical/example entries unless they actively contradict the new process)

**May add** (optional, only if needed for OIDC docs hygiene):

- A short subsection in `SECURITY.md` under “release credentials” — **only if** you do not conflict with plan 03; prefer keeping secrets guidance inside CHANGELOG release section to avoid ownership clash. Default: **do not touch SECURITY.md**.

**Must not touch:**

- `.github/workflows/test.yml`
- `Makefile`, `CONTRIBUTING.md`, `README.md`, `AGENTS.md`
- `src/**`, `tests/**`, `pyproject.toml` version field (humans bump version when cutting a release)

---

## Acceptance criteria

- [ ] AC-1: `.github/workflows/release.yml` exists | verify: `test -f .github/workflows/release.yml`
- [ ] AC-2: Triggers on version tags (`v*.*.*` or documented equivalent) | verify: `on:` block
- [ ] AC-3: Release job builds on a clean runner with `uv sync --frozen --all-extras` and `uv build` | verify: workflow steps
- [ ] AC-4: Release job runs tests before publish/upload | verify: pytest step present before publish
- [ ] AC-5: No long-lived PyPI token appears in repo files | verify: `rg -n 'pypi-Ag|TWINE_PASSWORD|PYPI_API_TOKEN' .github/ CHANGELOG.md` returns nothing real
- [ ] AC-6: CHANGELOG publish instructions describe tag → Actions path (and any one-time trusted-publishing setup) | verify: `rg -n 'trusted publishing|release\.yml|git tag' CHANGELOG.md`
- [ ] AC-7: Local `uv build` still works | verify: `uv build`
- [ ] AC-8: Pytest still green | verify: `uv run pytest -q`

---

## Implementation plan

### Step 1 — Design trigger + permissions

Suggested sketch (adapt to current actions best practice; keep minimal):

```yaml
name: release

on:
  push:
    tags: ["v*.*.*"]
  workflow_dispatch:

permissions:
  contents: read
  id-token: write

jobs:
  release:
    runs-on: ubuntu-latest
    environment: release   # optional but recommended
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: uv sync --frozen --all-extras
      - run: uv run pytest -q
      - run: uv build
      # Publish: pypa/gh-action-pypi-publish@release/v1  (OIDC)
      # OR upload-artifact / softprops/action-gh-release for assets-only interim
```

Choose **one** primary publish strategy and document it:

- **Preferred:** `pypa/gh-action-pypi-publish` with trusted publishing.
- **Interim:** attach `dist/*` to a GitHub Release; leave PyPI as follow-up checkbox in done report.

### Step 2 — Update CHANGELOG release guide

Replace the manual-only twine instructions with:

1. Cut CHANGELOG section + bump `pyproject.toml` version (human).
2. `git tag -a vX.Y.Z && git push origin vX.Y.Z`
3. Actions `release` workflow builds, tests, publishes (or uploads assets).
4. One-time admin: configure PyPI trusted publisher for `enjiai/jwt_lib` + GitHub `release` environment.

Keep SemVer / token-breakage major-bump guidance.

### Step 3 — Validate locally

```bash
uv sync --frozen --all-extras
uv run pytest -q
uv build
# Do not push tags unless explicitly asked by the user
```

Optionally run `actionlint` if available; not required for AC.

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Accidental PyPI publish during implementation | Do not push tags; keep `environment: release` protection noted for admins |
| OIDC not yet configured | Ship workflow + docs; mark publish job needs admin; assets-only interim OK |
| Duplicate publish with old twine docs | Remove or clearly deprecate twine-as-primary path |

---

## Done report

1. Trigger pattern and workflow path
2. Publish strategy chosen (OIDC vs assets-only interim)
3. Admin follow-ups remaining (PyPI publisher, environment reviewers)
4. CHANGELOG sections updated
5. Files changed
6. Confirmation: no secrets committed
