# Plan 05 — Branch protection / required checks (human)

## Agent identity

This plan is for a **repository administrator** (or an agent that only prepares evidence and stops before UI changes).  
It does **not** modify library code. GitHub branch protection / rulesets generally cannot be fully applied from the nested repo filesystem alone.

## Task

- **Task ID**: `jwt-cicd-05-branch-protection`
- **Title**: Require CI checks on `main` for `enjiai/jwt_lib`
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Governance
- **Work mode**: Manual (admin)
- **Dependencies**: Wave A merged to default branch; at least one green workflow run on `main` or a PR so check names exist

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
test -f .github/workflows/test.yml
gh api repos/enjiai/jwt_lib/actions/workflows --jq '.total_count'
# Expect > 0 after Wave A is pushed
gh api repos/enjiai/jwt_lib/actions/runs --jq '.total_count'
# Expect > 0 with at least one successful run
```

If workflows are still `0` → finish Wave A push/merge first.

---

## Context

### Problem

CI/CD audit + 2026-07-27 re-check: **main is not protected** (`GET /branches/main/protection` → 404). Even after CI exists, merges can skip failing checks until required status checks or rulesets are enabled.

### Goal

Make the Wave A CI check(s) **mandatory** on `main` so unverified changes cannot merge.

### Non-goals

- Code changes in this repository.
- Requiring release workflow on every PR.
- Organization-wide rules outside `enjiai/jwt_lib`.

---

## Acceptance criteria

- [ ] AC-1: Branch protection rule or repository ruleset exists for `main` | verify: `gh api repos/enjiai/jwt_lib/branches/main/protection` **or** rulesets list non-empty targeting `main`
- [ ] AC-2: The CI check name(s) from `.github/workflows/test.yml` are required | verify: protection/ruleset payload includes those contexts
- [ ] AC-3: A PR with a deliberate failing check cannot be merged by a non-admin (or requires override that is audited) | verify: manual attempt or org policy confirmation
- [ ] AC-4: Admins documented any bypass actors / required review count | verify: short note in done report / handoff

---

## Implementation checklist (admin UI or API)

1. Open https://github.com/enjiai/jwt_lib/settings/branches (or Rulesets).
2. Add rule for `main`:
   - Require a pull request before merging (recommended for an auth library).
   - Require status checks to pass — select the exact check name(s) from Wave A done report (e.g. `test / quality`).
   - Require branches to be up to date (optional but useful).
3. Prefer **rulesets** over legacy branch protection if the org standard is rulesets.
4. Confirm with:

```bash
gh api repos/enjiai/jwt_lib/branches/main/protection
# or
gh api repos/enjiai/jwt_lib/rulesets
```

5. Optional: restrict who can push tags `v*.*.*` if release automation (plan 04) is live.

---

## Evidence to collect before enabling

From Wave A done report / Actions UI:

| Item | Value |
|---|---|
| Workflow file | `.github/workflows/test.yml` |
| Check name(s) to require | _fill after first green run_ |
| Sample green run URL | _fill_ |

Do **not** guess check names — copy from a real Actions run.

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Requiring a check that was renamed | Stabilize job `name:` in Wave A before enabling |
| Admin bypass left wide open | Limit bypass actors; keep emergency break-glass documented |
| Blocking hotfix path | Allow admin override with audit, not silent disable of CI |

---

## Done report

1. Protection mechanism used (legacy branch protection vs ruleset)
2. Exact required check names
3. PR review requirements (count, code owners if any)
4. Bypass actors
5. Command/API evidence snippets (redact secrets)
