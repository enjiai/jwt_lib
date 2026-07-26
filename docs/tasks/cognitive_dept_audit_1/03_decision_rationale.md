# Plan 03 — Decision rationale (stakeholder + permissions ADRs)

## Agent identity

You record **why** security-sensitive authorization shortcuts exist, so cognitive debt “decision rationale missing” closes.  
Own **only** `docs/decisions/`. Do **not** edit README/API/`AGENTS.md`/`docs/handoff.md`/`docs/EXTERNAL_CONTRACTS.md`/packaging/src.

## Task

- **Task ID**: `jwt-cogdebt-03-adrs`
- **Title**: Add stakeholder + permission ADRs and decisions index
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Architecture memory
- **Work mode**: Auto
- **Dependencies**: Wave A preferred (docs should already mention stakeholder); ADRs must match **code/tests**, not aspirational docs

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -q
test -f src/enjilib_jwt/authenticator.py
test -f tests/test_authz.py
```

If pytest red, STOP.

---

## Context

### Problem

Cognitive debt audit: terse commits show disallows/stakeholder/cipher landed without trade-offs. AI-readiness plan 06 asked for stakeholder + permission ADRs; repo only has:

- `docs/decisions/001_token_contract_structure.md`
- `docs/decisions/002_packaging_source_of_truth.md`

`001` even says “(Future) ADR for stakeholder role bypass semantics”.

### Goal

Durable ADR set covering current locked AuthZ behavior + a short index so agents know how to add the next decision.

### Non-goals

- Changing code to remove stakeholder bypass or switch to `re.fullmatch`.
- Rewriting public API tutorials (plan 01).
- Full architecture wiki.

### Constraints

- ADRs describe **current pinned behavior** from code + tests.
- Keep each ADR ~1 screen.
- No secrets.

---

## Acceptance criteria

- [ ] AC-1: `docs/decisions/README.md` exists with short “how to write an ADR” + index of existing ADRs | verify: file_exists + lists 001–00N
- [ ] AC-2: ADR for `stakeholder` role bypass (all of `has_role` / `has_any_role` / `has_all_roles`) | verify: file under `docs/decisions/` + `rg -ni stakeholder docs/decisions/`
- [ ] AC-3: ADR for permission matching + disallow precedence (`disallows` first; `/` strip; `re.match` prefix; non-`/` still compiled as regex) | verify: file + `rg -n 'disallow|re\.match' docs/decisions/`
- [ ] AC-4: Existing `001` / `002` remain valid; update `001` “Future ADR” pointer to the new stakeholder ADR link | verify: `rg -n 'stakeholder' docs/decisions/001_token_contract_structure.md`
- [ ] AC-5: Pytest still green (no code changes expected) | verify: `uv run pytest -q`

---

## Required ADR content (ground in code)

### Stakeholder bypass

- **Decision**: Checking role `"stakeholder"` (or including it in any/all lists) returns `True` regardless of `claims.roles`.
- **Evidence**: `authenticator.py` lines around `has_role` / `has_any_role` / `has_all_roles`; tests in `tests/test_authz.py`.
- **Consequences**: Treating `stakeholder` as a normal role name in call sites is a footgun; removing bypass is a breaking / security-policy change needing human approval + new ADR.
- **Rationale status**: If product rationale is unknown, state explicitly: “Rationale not recorded in-repo; behavior locked by tests as intentional current contract (commit history mentions stakeholder full roles access).”

### Permission allow/deny

- **Decision**: `has_permission` checks disallows before allows; `_match_permission` strips one leading `/` then uses `re.match` (prefix); patterns without `/` are still regex.
- **Evidence**: `authenticator.py` `_match_permission` / `has_permission`; `tests/test_authz.py`.
- **Consequences**: `"admin"` matches `"admin.x"`; dots are metacharacters; switching to fullmatch/glob is breaking.

### Template skeleton

```markdown
# Decision 00N: <title>
**Date**: YYYY-MM-DD
**Status**: Accepted (current implementation)
## Decision
## Context / Evidence
## Consequences
## Alternatives considered
## For agents before you change
```

---

## Implementation steps

1. Read role/permission helpers + authz tests.
2. Add `docs/decisions/README.md` indexing 001, 002, and new ADRs.
3. Add stakeholder ADR and permission ADR (pick next free numbers, e.g. 003 / 004).
4. Patch `001` future-pointer to link the stakeholder ADR.
5. Do not touch handoff/AGENTS (plan 05 will link these).

---

## Done report (required)

- New/updated files
- AC evidence
- Explicit note if product “why stakeholder exists” remains unknown (acceptable if stated)

## Out of scope

- External issuer paths (plan 04)
- Claiming docs already document stakeholder in README (plan 01 owns that)
