# Plan 05 — Process docs (CONTRIBUTING, SECURITY, CHANGELOG)

## Agent identity

You document **review, release, and security hygiene** for this authentication library.  
Do **not** invent a heavyweight release bureaucracy. Do **not** edit source/tests. Do **not** create `AGENTS.md` or GitHub templates (other plans).

## Task

- **Task ID**: `jwt-ai-ready-05-process-docs`
- **Title**: Add CONTRIBUTING.md, SECURITY.md, CHANGELOG.md
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Process
- **Work mode**: Auto
- **Dependencies**: Wave A preferred (accurate install/verify commands)

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -q
test -f README.md
```

---

## Context

### Problem

Audit: no review/release/security process docs → agents cannot tell what “done” means for shipping an auth-library change, or how to handle secret/vuln reports.

### Goal

Three lightweight root docs:

1. **CONTRIBUTING.md** — how to set up, test, review expectations, when ADR/handoff is required
2. **SECURITY.md** — how to report vulnerabilities; local secret hygiene; what not to commit
3. **CHANGELOG.md** — Keep a Changelog–style starting point for 0.1.0 + Unreleased

### Non-goals

- Legal review of MIT license text.
- Setting up private security mailing infrastructure (use GitHub Security Advisories / issues guidance).
- Full semantic-release automation.

### Constraints

- Match real commands from README/`pyproject.toml` (`uv sync --all-extras`, `uv run pytest -v`).
- Emphasize auth-library caution: token contract and AuthZ changes are high risk.
- No real secrets in examples.

---

## Acceptance criteria

- [ ] AC-1: `CONTRIBUTING.md` exists with setup, test, PR expectations, compatibility guidance | verify: `test -f CONTRIBUTING.md`
- [ ] AC-2: `SECURITY.md` exists with reporting path + secret hygiene | verify: `test -f SECURITY.md`
- [ ] AC-3: `CHANGELOG.md` exists with at least `[Unreleased]` and `0.1.0` baseline | verify: `test -f CHANGELOG.md`
- [ ] AC-4: CONTRIBUTING points to `AGENTS.md` and/or `docs/handoff.md` / `docs/decisions/` as optional-but-expected for agents | verify: grep
- [ ] AC-5: SECURITY states never commit real JWT secrets; use placeholders; rotate if leaked | verify: manual
- [ ] AC-6: Pytest still green | verify: `uv run pytest -q`

---

## Suggested doc contents (condensed)

### CONTRIBUTING.md

- Dev setup: `uv sync --all-extras`
- Tests: `uv run pytest -v` (coverage gate may fail the run if configured — do not lower casually)
- PR must say whether token/`enc`/AuthZ semantics change
- Reviewer focus: crypto helpers, permission matching, docs sync
- Prefer small PRs; nested repo `enjiai/jwt_lib`
- Link: README, API, AGENTS, SECURITY, CHANGELOG, docs/decisions

### SECURITY.md

- Report via GitHub Security Advisories on `enjiai/jwt_lib` (or private maintainer channel if advisories unavailable — state primary path clearly)
- Do not file public issues for exploitable auth bypasses with PoC against production
- Local hygiene: `.env` not used by this lib; never paste production secrets into tests/docs
- Supported versions: document current `0.1.0` as the only line unless more exist

### CHANGELOG.md

```markdown
# Changelog

## [Unreleased]

## [0.1.0] - YYYY-MM-DD
### Added
- Initial JWT verify, encrypted `enc` payload decrypt, claims, role/permission helpers.
```

Use a reasonable date (package history / today) without inventing fake release notes for unreleased AI-readiness work unless those changes are already on the branch and you are documenting them under Unreleased.

---

## Implementation plan

### Files you may create/modify

**Allowed:**

- `CONTRIBUTING.md`
- `SECURITY.md`
- `CHANGELOG.md`

**Forbidden:**

- `src/**`, `tests/**`, README/API drive-by rewrites, `AGENTS.md`, `.github/**`, `docs/decisions/**`, `docs/handoff.md`, packaging files

### Step-by-step

1. Read README Development section for accurate commands.
2. Write the three files.
3. Run pytest.
4. Stop.

### Exit criteria

- AC met.

---

## Done report (for parent orchestrator)

Report files created + any command mismatches you discovered in README (list only).
