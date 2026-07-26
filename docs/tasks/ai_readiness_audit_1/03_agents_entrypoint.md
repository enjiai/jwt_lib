# Plan 03 — Tool-agnostic agent entrypoint (`AGENTS.md`)

## Agent identity

You add a root **`AGENTS.md`** so any coding agent (Cursor, Codex, Claude, Copilot, …) gets the same setup, verification, boundaries, and handoff rules for this library.  
Do **not** edit Wave A-owned docs beyond reading them. Do **not** add GitHub templates / CONTRIBUTING / SECURITY / CHANGELOG / decisions (other Wave B plans).

## Task

- **Task ID**: `jwt-ai-ready-03-agents-md`
- **Title**: Add tool-agnostic `AGENTS.md` for enjilib-jwt-auth
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Agent DevEx
- **Work mode**: Auto
- **Dependencies (filesystem)**: Wave A complete enough that token docs and packaging match reality

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -q
test -f README.md
test -f API.md
# Wave A signals (prefer present; if missing, document drift in AGENTS and still write accurate code-based guidance)
test -f src/enjilib_jwt/py.typed || echo "WARN: py.typed missing — note in AGENTS known gaps"
grep -n 'enc' README.md API.md || echo "WARN: docs may still lack enc — cite authenticator.py as source of truth"
```

If pytest is red, STOP.

---

## Context

### Problem

Audit score for cross-agent / skills / working-process was near floor: no shared entrypoint. Every agent re-discovers setup, token `enc` contract, packaging quirks, and safe-change boundaries.

### Goal

A single root `AGENTS.md` that an agent can open first and act from, without vendor lock-in (no Cursor-only or Claude-only required files).

### Non-goals

- Porting monorepo `AGENTS.md` / skills system into this nested repo.
- Creating slash-command skill packs.
- Changing library code.

### Constraints

- Tool-agnostic English.
- Prefer pointers to existing files (`README.md`, `API.md`, `tests/`, `docs/handoff.md`) over duplicating long API reference.
- Explicitly mark **forbidden** changes for casual agents (crypto, token wire format, AuthZ precedence, `stakeholder` bypass) without maintainer/ADR approval.
- Nested git: remind agents that commits belong in this directory’s `.git` (`enjiai/jwt_lib`), not the parent monorepo.

---

## Acceptance criteria

- [ ] AC-1: Root `AGENTS.md` exists | verify: `test -f AGENTS.md`
- [ ] AC-2: Names source roots (`src/enjilib_jwt/`), public exports (`JWTAuthenticator`, `JWTClaims`), and docs entrypoints | verify: manual
- [ ] AC-3: Documents setup + verification commands that match README/dev reality (`uv sync --all-extras`, `uv run pytest -v`, coverage if configured) | verify: commands work when run
- [ ] AC-4: Documents token contract: required `enc`, decrypt-then-claims; points to tests for golden behavior | verify: `grep -n enc AGENTS.md`
- [ ] AC-5: States safe-change boundaries / do-not-break list (crypto constants, AuthZ precedence, stakeholder bypass, public exports) | verify: manual
- [ ] AC-6: States handoff expectation (update `docs/handoff.md` / ADR when compatibility-sensitive) even if plan 06 lands in parallel | verify: `grep -ni handoff AGENTS.md`
- [ ] AC-7: Notes nested-repo / remote `enjiai/jwt_lib` | verify: manual
- [ ] AC-8: Pytest still green | verify: `uv run pytest -q`

---

## Suggested `AGENTS.md` outline (adapt, do not invent false commands)

```markdown
# AGENTS.md — enjilib-jwt-auth

## What this repo is
JWT verify + claims + role/permission helpers for Enji microservices.
Import package: `enjilib_jwt`. Distribution name: `enjilib-jwt-auth`.
Remote: https://github.com/enjiai/jwt_lib

## Read first
- README.md — install & usage
- API.md — API reference
- This file — agent boundaries
- docs/handoff.md — latest session notes (if present)
- docs/decisions/ — compatibility ADRs (if present)

## Source map
- src/enjilib_jwt/authenticator.py — verify_and_extract + AuthZ
- src/enjilib_jwt/cipher.py — decrypt_payload only (AES-GCM + HKDF + zlib)
- src/enjilib_jwt/claims.py — JWTClaims
- tests/helpers/token_factory.py — test-only encrypt + mint

## Token contract (critical)
Wire JWT must include `enc`. Flat claim tokens → verify_and_extract returns None.
Sensitive claims live inside encrypted `enc`. See API.md + tests/test_verify_extract.py.

## Setup & verify
uv sync --all-extras
uv run pytest -v
# coverage gate is configured in pyproject — do not lower casually

## Safe change rules
Allowed without special process: docs clarity, tests that pin existing behavior, packaging hygiene.
Requires maintainer + ADR: crypto pipeline, token wire shape, permission match semantics,
disallow precedence, stakeholder role bypass, public export renames, secret handling.

## Known footguns (pinned by tests — do not "fix" casually)
- stakeholder role short-circuit in role helpers
- permission patterns use re.match; non-/ patterns are still regex
- verify_and_extract maps almost all failures to None

## Handoff
After compatibility-sensitive work: update docs/handoff.md and add docs/decisions/* if behavior/policy changed.
```

Fill gaps from actual Wave A docs; if Wave A files still drift, **code + tests win** — say so explicitly in AGENTS.md.

---

## Implementation plan

### Files you may create/modify

**Allowed:**

- `AGENTS.md` (create)

**Forbidden:**

- Everything else (including README/API “drive-by” fixes — report drift to orchestrator instead)

### Step-by-step

1. Read `README.md`, `API.md`, `pyproject.toml` test commands, and skim authenticator/cipher.
2. Write `AGENTS.md` per outline, grounded in files that exist.
3. Run pytest smoke.
4. Stop.

### Exit criteria

- AC met; no unrelated file churn.

---

## Done report (for parent orchestrator)

Report:

1. Path created
2. Commands run
3. Any Wave A drift you had to override with code-as-truth
4. Confirmation no other files touched
