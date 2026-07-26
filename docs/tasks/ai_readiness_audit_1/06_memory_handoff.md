# Plan 06 — Decision records & handoff memory

## Agent identity

You add **lightweight durable memory** so the next agent does not rediscover token-contract and packaging decisions.  
Do **not** rewrite library code. Do **not** own README/API/`AGENTS.md`/templates/process root docs (other plans).

## Task

- **Task ID**: `jwt-ai-ready-06-memory-handoff`
- **Title**: Add ADR format + initial decisions + handoff note
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Agent memory
- **Work mode**: Auto
- **Dependencies**: Wave A preferred (docs/packaging truth); can proceed from code if docs lag

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -q
test -f src/enjilib_jwt/authenticator.py
test -f src/enjilib_jwt/cipher.py
```

---

## Context

### Problem

Audit memory/handoff score was 0: no ADRs, changelog linkage, or resume notes. For a security-sensitive JWT library, compatibility choices must outlive a single chat.

### Goal

1. `docs/decisions/README.md` — how to write a short ADR
2. At least **three** initial ADRs capturing current (not aspirational) contracts
3. `docs/handoff.md` — living “resume here” note for agents

### Non-goals

- Full architecture wiki.
- Migrating monorepo Conport/memory-bank here.
- Changing code to match docs.

### Constraints

- ADRs describe **current pinned behavior** from code/tests, including footguns.
- Keep each ADR to ~1 screen.
- Handoff file must be safe to update frequently (no secrets).

---

## Acceptance criteria

- [ ] AC-1: `docs/decisions/README.md` exists with ADR template (Context / Decision / Consequences) | verify: file
- [ ] AC-2: ADR for encrypted `enc` token wire format | verify: file under `docs/decisions/`
- [ ] AC-3: ADR for permission matching + disallow precedence | verify: file
- [ ] AC-4: ADR for `stakeholder` role bypass (current behavior) | verify: file
- [ ] AC-5: Optional but recommended: ADR for packaging source of truth (`pyproject.toml` primary, setup.py mirrored, egg-info generated) | verify: file or explicit skip note in done report
- [ ] AC-6: `docs/handoff.md` exists with status, verify commands, open risks, next actions | verify: file
- [ ] AC-7: Pytest still green | verify: `uv run pytest -q`

---

## Required decision content (ground in code)

### ADR: Encrypted payload (`enc`)

- Decision: Access tokens verified by this library **must** carry `enc`; sensitive claims decrypted via HKDF+AES-GCM+zlib (`cipher.decrypt_payload`).
- Consequence: Flat JWTs fail closed (`None`). Docs/tests must mint with `enc`.

### ADR: Permission allow/deny

- Decision: `disallows` checked first; then `permissions`; patterns may be regex; leading `/` strips and treats remainder as regex; `re.match` (prefix) semantics.
- Consequence: Changing to fullmatch/glob is breaking; needs new ADR + major caution.

### ADR: Stakeholder bypass

- Decision: Requesting role check for `stakeholder` (alone or in any/all lists) currently returns `True` unconditionally.
- Consequence: Documented footgun; do not remove without product approval + migration.

### ADR (recommended): Packaging truth

- Decision: `pyproject.toml` is canonical for deps/tooling; `setup.py` must mirror runtime deps; `*.egg-info` is generated and gitignored; `py.typed` ships with package.

---

## Suggested `docs/handoff.md` starter

```markdown
# Handoff

## Current status
- Tests: `uv run pytest -v` (expect green; coverage gate configured)
- AI-readiness remediation: see docs/tasks/ai_readiness_audit_1/

## Verify
```bash
uv sync --all-extras
uv run pytest -v
```

## Open risks / do not casually change
- Token `enc` contract
- Permission match / disallow precedence
- stakeholder bypass
- Crypto info string `enji-jwt-payload-encryption`

## Last agent note
- <date>: created initial ADRs + this handoff file
```

---

## Implementation plan

### Files you may create/modify

**Allowed:**

- `docs/decisions/README.md`
- `docs/decisions/NNNN-short-title.md` (use `0001`, `0002`, …)
- `docs/handoff.md`

**Forbidden:**

- `src/**`, `tests/**`, root process/docs owned by other plans (`AGENTS.md`, CONTRIBUTING, SECURITY, CHANGELOG, README, API, `.github/**`, packaging)

### Step-by-step

1. Skim authenticator/cipher + authz tests for accurate wording.
2. Write decisions README + ADRs.
3. Write handoff.
4. Run pytest.
5. Stop.

### Exit criteria

- AC met; no secrets in handoff.

---

## Done report (for parent orchestrator)

Report:

1. ADR paths + one-line each
2. Handoff path
3. Any behavior you documented that still contradicts README/API (list for orchestrator; do not fix those files here)
