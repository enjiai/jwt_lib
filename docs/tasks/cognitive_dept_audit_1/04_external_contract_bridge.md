# Plan 04 — External contract bridge (enji-auth + collector)

## Agent identity

You add a **repository-side bridge** to external systems named by this library so maintainers/agents know what to verify before changing shared token behavior.  
Own **`docs/EXTERNAL_CONTRACTS.md`**. You may add **one-line links** from `README.md` and/or `API.md` **only if** those files already contain an “External systems” / “Related” heading after Wave A — otherwise add a single “See also” bullet without rewriting token sections (plan 01 owns token prose). Prefer not fighting plan 01: if README is mid-edit, put the link only inside `EXTERNAL_CONTRACTS.md` and note “plan 05 / orchestrator may deep-link”.

Safest ownership for parallel Wave B: **create `docs/EXTERNAL_CONTRACTS.md` only**; optional link from `docs/decisions/001_token_contract_structure.md` Related section is allowed; **do not edit `AGENTS.md` / `docs/handoff.md`** (plan 05 will link this file).

## Task

- **Task ID**: `jwt-cogdebt-04-external-bridge`
- **Title**: Document enji-auth issuer + collector employee_id access paths
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Docs bridge
- **Work mode**: Auto
- **Dependencies**: None beyond pytest green; monorepo paths below are for **pointers**, not for editing those repos in this task

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -q
test -f src/enjilib_jwt/cipher.py
# Monorepo issuer should be readable when this nested repo sits inside agent_enji:
test -f ../../../services/enji-auth/app/auth/authentication/cipher.py \
  || test -f /Users/13910n/work/projects/enji/agent_enji/be/services/enji-auth/app/auth/authentication/cipher.py \
  || echo "WARN: issuer path not found from this machine — still write bridge with best-known relative paths"
```

---

## Context

### Problem

Cognitive debt audit: enji-auth and collector-db are named but not linked to owner/contract/access path. Agents cannot tell who mints `enc` or what `employee_id` means without guessing.

### Goal

One short bridge doc: where the issuer encrypts, which claims are plaintext vs sensitive, where employee IDs come from, and what must stay compatible with this library’s decrypt path.

### Non-goals

- Copying enji-auth source into this repo.
- Changing issuer or collector code.
- Embedding secrets, env values, or private schemas dumps.

### Constraints

- Point to paths / docs; do not paste large code blocks from issuer (small illustrative snippets OK if attributed).
- State clearly: **this library verifies; enji-auth issues**.

---

## Acceptance criteria

- [ ] AC-1: `docs/EXTERNAL_CONTRACTS.md` exists | verify: file_exists
- [ ] AC-2: Doc names **issuer** path for encrypt + token mint | verify: `rg -n 'enji-auth|encrypt_payload|_create_jwt_token|cipher\.py' docs/EXTERNAL_CONTRACTS.md`
- [ ] AC-3: Doc states plaintext claim set for issuer (`exp`, `type` only) vs everything else inside `enc` | verify: `rg -n 'PLAINTEXT|plaintext|exp|type' docs/EXTERNAL_CONTRACTS.md`
- [ ] AC-4: Doc names HKDF info string `enji-jwt-payload-encryption` as shared compatibility key material domain | verify: `rg -n 'enji-jwt-payload-encryption' docs/EXTERNAL_CONTRACTS.md`
- [ ] AC-5: Doc explains `employee_id` comes from collector via enji-auth lookup (not `user_id`) and points to issuer helper usage | verify: `rg -ni 'employee_id|collector' docs/EXTERNAL_CONTRACTS.md`
- [ ] AC-6: Doc lists “before changing shared token behavior, verify …” checklist | verify: section present
- [ ] AC-7: Link from `docs/decisions/001_token_contract_structure.md` Related Decisions/section to `../EXTERNAL_CONTRACTS.md` (or equivalent relative link) | verify: `rg -n 'EXTERNAL_CONTRACTS' docs/decisions/001_token_contract_structure.md`
- [ ] AC-8: Pytest still green | verify: `uv run pytest -q`

---

## Authoritative pointers (verified 2026-07-26 in monorepo)

Use these relative paths from monorepo root `agent_enji/` (also note nested-lib-relative equivalents in the doc):

| Concern | Path |
|---|---|
| Encrypt / decrypt (issuer) | `be/services/enji-auth/app/auth/authentication/cipher.py` (`encrypt_payload`, HKDF info `b"enji-jwt-payload-encryption"`) |
| Mint access token with `enc` | `be/services/enji-auth/app/auth/authentication/core.py` (`_create_jwt_token`, `_PLAINTEXT_CLAIMS = frozenset({"exp", "type"})`) |
| Employee id at issue time | same `core.py` — `get_employee_id_by_email` / collector lookup when generating tokens |
| Consumer decrypt (this lib) | `src/enjilib_jwt/cipher.py` (`decrypt_payload` only) |
| Test mint mirror | `tests/helpers/token_factory.py` |

Owner note for the bridge doc (adjust if README/CODEOWNERS say otherwise):

- Token wire format / secret: **enji-auth** maintainers + this library maintainers must agree.
- `employee_id` semantics: **collector DB** identity as resolved by enji-auth at issue time; this library only transports the claim.

---

## Suggested outline for `docs/EXTERNAL_CONTRACTS.md`

1. Purpose of this file  
2. Systems map (issuer → token → this lib → services)  
3. Shared crypto contract (HKDF info, AES-GCM, nonce, zlib, base64url)  
4. Claim placement (`exp`/`type` public; sensitive inside `enc`)  
5. Identity fields (`user_id` vs `employee_id`)  
6. Compatibility checklist before changes  
7. What this repo will not host (private schemas, secrets)

---

## Done report (required)

- File created + 001 link updated
- AC evidence
- Whether issuer paths were readable from the agent environment

## Out of scope

- Editing enji-auth or collector
- Rewriting AGENTS (plan 05 will cite this file)
