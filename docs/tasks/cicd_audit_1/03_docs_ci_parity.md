# Plan 03 — Docs CI parity

## Agent identity

You make **contribution and agent docs tell the truth** about CI and local gates after Wave A lands.  
Do **not** edit workflow YAML (02/04). Do **not** create Makefile (01). Do **not** change library source or tests. Do **not** invent branch-protection settings as if they already exist.

## Task

- **Task ID**: `jwt-cicd-03-docs-parity`
- **Title**: Align CONTRIBUTING / README / AGENTS with real CI + make gate
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Docs
- **Work mode**: Auto
- **Dependencies**: Wave A complete (`Makefile` + `.github/workflows/test.yml` present and locally green)

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
test -f Makefile
test -f .github/workflows/test.yml
test -f .github/pull_request_template.md
uv sync --frozen --all-extras
uv run pytest -q
grep -q 'uv sync --frozen --all-extras' .github/workflows/test.yml
```

If Wave A artifacts are missing → STOP and report; do not “fix” docs by claiming CI exists when YAML is absent.

---

## Context

### Problem

CI/CD audit: `CONTRIBUTING.md` requires green GitHub Actions and links a PR template that were missing on `origin/main`. After Wave A, automation exists, but docs still mix stale commands (`python -m build`, bare `pytest` without uv), and may still imply required checks that Wave C has not enabled yet.

### Goal

Docs that accurately describe:

1. How to run the **local** gate (`make check` / `make test` + uv equivalents).
2. What CI runs on PRs/pushes (pytest+coverage, mypy, build) — matching Wave A workflow.
3. That PR template path is real.
4. That **required** status checks may still need admin enablement (point to plan 05) — do not claim merges are blocked until that is done.

### Non-goals

- Rewriting SECURITY.md vulnerability process.
- Rewriting token contract / API.md.
- Implementing release automation docs beyond a one-line pointer to CHANGELOG / plan 04 ownership.
- Enabling GitHub branch protection.

### Constraints

- Prefer short edits; no new process bureaucracy.
- Keep authentication-library warnings (token compatibility) intact.
- Distinguish **“CI runs on PRs”** from **“CI is a required check”**.

### Parallel-safety (file ownership)

**Owns exclusively:**

- `CONTRIBUTING.md`
- `README.md` (Development / CI mentions only — do not reopen token-structure sections unless a single stale build command sits there)
- `AGENTS.md` (Setup/Verification / quality-gate bullets only)

**Must not touch:**

- `Makefile`
- `.github/workflows/**`
- `CHANGELOG.md` (release publish steps owned by 04 — you may leave a single “see CHANGELOG for release” link)
- `pyproject.toml`, `uv.lock`, `src/**`, `tests/**`

---

## Acceptance criteria

- [ ] AC-1: CONTRIBUTING no longer references nonexistent CI/template paths | verify: `test -f .github/pull_request_template.md` and CONTRIBUTING link resolves
- [ ] AC-2: CONTRIBUTING documents the real local gate (`make test` or `make check`, and/or `uv run pytest`) | verify: `rg -n 'make (check|test)|uv run pytest' CONTRIBUTING.md`
- [ ] AC-3: CONTRIBUTING describes what CI runs (tests/coverage; typecheck/build if present in workflow) without claiming required checks unless known true | verify: manual read
- [ ] AC-4: README Development build command matches project preference (`uv build` or `make build`) | verify: `rg -n 'uv build|make build|python -m build' README.md`
- [ ] AC-5: AGENTS verification section mentions CI workflow existence and local `make check` (or equivalent) consistently with Makefile | verify: `rg -n 'make check|GitHub Actions|\.github/workflows' AGENTS.md`
- [ ] AC-6: No doc claims “branch protection requires CI” as already enforced | verify: `rg -ni 'required check|branch protection|must show green' CONTRIBUTING.md AGENTS.md README.md` and wording is conditional/accurate
- [ ] AC-7: Pytest still green untouched | verify: `uv run pytest -q`

---

## Implementation plan

### Step 1 — Read Wave A reality

```bash
sed -n '1,120p' .github/workflows/test.yml
grep -E '^[a-z].*:|^	' Makefile | head -40
```

Mirror those commands in docs; do not invent extra gates.

### Step 2 — Patch CONTRIBUTING

Update:

- Development setup → `uv sync --all-extras` / frozen note for CI parity
- Running tests → `make test` / `uv run pytest`
- PR checklist → local gate + “CI workflow `test` must be green on the PR”
- Review criteria → replace absolute “GitHub Actions CI must show green” with accurate wording once workflow exists; if required checks are not enabled, say reviewers must wait for the workflow run **and** note that making it mandatory is an admin step

### Step 3 — Patch README Development

Replace stale `python -m build` with `uv build` or `make build`. Mention `make check` if Makefile provides it.

### Step 4 — Patch AGENTS § Setup and Verification

Align optional mypy / build bullets with CI. State that `.github/workflows/test.yml` is the automated gate.

### Step 5 — Validate

```bash
uv run pytest -q
# docs-only: spot-check links
test -f .github/pull_request_template.md
test -f .github/workflows/test.yml
```

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Race with plan 04 on CHANGELOG | Do not edit CHANGELOG |
| Over-claiming required checks | Explicit “admin must enable” sentence |
| Drift with Makefile target names | Copy target names from Makefile literally |

---

## Done report

1. Which claims were stale and how they were corrected
2. Exact local + CI commands now documented
3. Confirmation that required-check wording is not overstated
4. Files changed
