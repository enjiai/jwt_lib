# Plan 04 — GitHub issue & pull request templates

## Agent identity

You add **task intake and PR templates** so agents and humans capture scope, token/API compatibility risk, verification, and handoff notes.  
Do **not** modify CI workflow behavior beyond leaving `.github/workflows/test.yml` intact. Do **not** edit library source, tests, or Wave A docs.

## Task

- **Task ID**: `jwt-ai-ready-04-github-templates`
- **Title**: Add issue + PR templates for compatibility-aware changes
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Process
- **Work mode**: Auto
- **Dependencies**: Wave A preferred complete; not strictly required for templates

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
test -d .git
uv run pytest -q
```

---

## Context

### Problem

Audit: no task intake / PR template → agents invent scope and skip compatibility and verification evidence.

### Goal

GitHub templates that force:

- Scope and non-goals
- API / token-compatibility impact
- Required tests + docs updates
- Verification commands run
- Handoff note pointer

### Non-goals

- Branch protection UI settings.
- CODEOWNERS (optional; skip unless already present).
- Rewriting CI.

### Constraints

- Keep templates short enough that agents fill them.
- This is an **authentication** library — compatibility checkbox is mandatory.
- Do not require proprietary tooling.

---

## Acceptance criteria

- [ ] AC-1: At least one issue template under `.github/ISSUE_TEMPLATE/` | verify: directory has markdown/yml
- [ ] AC-2: PR template at `.github/pull_request_template.md` (or `.github/PULL_REQUEST_TEMPLATE.md`) | verify: file exists
- [ ] AC-3: Templates include fields/checkboxes for: scope, token/API compatibility risk, tests, docs, verification command | verify: manual
- [ ] AC-4: Templates mention handoff/ADR when compatibility-sensitive | verify: `grep -ni handoff\|ADR\|compat` on templates
- [ ] AC-5: Existing `.github/workflows/test.yml` unchanged in behavior | verify: `git diff` / no unintended edits
- [ ] AC-6: Pytest still green | verify: `uv run pytest -q`

---

## Suggested content (adapt)

### `.github/ISSUE_TEMPLATE/change.md` (or `config.yml` + `task.md`)

Front matter optional. Body should include:

```markdown
## Summary
## Motivation
## Scope
- In:
- Out:
## Compatibility risk
- [ ] No token wire-format / AuthZ semantic change
- [ ] Token contract change (describe)
- [ ] AuthZ / permission matching change (describe)
- [ ] Packaging / public export change (describe)
## Proposed verification
- [ ] `uv run pytest -v`
## Docs / handoff
- [ ] README/API/AGENTS updated if needed
- [ ] `docs/handoff.md` / ADR if compatibility-sensitive
```

### `.github/pull_request_template.md`

```markdown
## Summary
## Compatibility checklist
- [ ] No change to token `enc` contract
- [ ] No change to permission allow/deny precedence
- [ ] No change to `stakeholder` role bypass (or ADR linked)
- [ ] Public exports unchanged (or changelog noted)
## Verification
- [ ] `uv sync --all-extras`
- [ ] `uv run pytest -v`
## Docs
- [ ] README/API/AGENTS updated as needed
- [ ] Handoff/ADR updated if required
## Notes for reviewers
```

---

## Implementation plan

### Files you may create/modify

**Allowed:**

- `.github/ISSUE_TEMPLATE/**`
- `.github/pull_request_template.md` (or GitHub’s alternate path)
- Optionally `.github/ISSUE_TEMPLATE/config.yml` if using multiple templates

**Forbidden:**

- `.github/workflows/**` changes
- `src/**`, `tests/**`, README/API, AGENTS, CONTRIBUTING/SECURITY/CHANGELOG, decisions/handoff

### Step-by-step

1. Create issue template(s).
2. Create PR template.
3. Confirm CI workflow file untouched.
4. Run pytest.

### Exit criteria

- AC met.

---

## Done report (for parent orchestrator)

Report paths created + confirmation CI workflow hash/diff empty for workflows.
