# Plan 01 — Docs: token contract, identity, API discoverability

## Agent identity

You reconcile **human-facing docs** with the real JWT contract so cognitive debt item “encrypted token + identity + API link” closes.  
Do **not** change production code under `src/`. Do **not** edit packaging / `AGENTS.md` / `docs/handoff.md` / `docs/decisions/` (other plans). Do **not** invent a different token shape than code+tests.

## Task

- **Task ID**: `jwt-cogdebt-01-docs-contract`
- **Title**: Align README/API with enc wire format, identity fields, stakeholder note, API link
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Docs
- **Work mode**: Auto
- **Dependencies**: Prerequisite — `uv run pytest -q` exits 0

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
uv sync --all-extras
uv run pytest -q
test -f src/enjilib_jwt/authenticator.py
test -f tests/helpers/token_factory.py
```

If pytest is red, STOP — do not “fix” docs by inventing behavior.

---

## Context

### Problem (from cognitive debt audit + 2026-07-26 re-review)

1. `README.md` and `API.md` still show **flat** JWT claims as current structure, while `JWTAuthenticator.verify_and_extract` returns `None` unless `"enc" in public`, then decrypts sensitive claims.
2. `README.md` does not link to `API.md` (discoverability gap).
3. Install examples still use `your-org/enji-agent` placeholder; canonical remote is `enjiai/jwt_lib`.
4. `API.md` claims table says `user_id` is **not** employee ID, then Common Patterns labels `claims.user_id  # Employee ID`.
5. Regex permission notation is inconsistent in examples (`/` strip semantics live in `_match_permission`).
6. `stakeholder` role shortcut exists in all role helpers and is locked by tests, but public docs omit it.

### Goal

One authoritative human path: README → API → current wire format + extracted claims semantics, matching code and tests.

### Non-goals

- Adding production `encrypt_payload` export.
- Changing AuthZ / cipher behavior.
- Writing ADRs, AGENTS, EXTERNAL_CONTRACTS, packaging files.
- Copying private issuer secrets or full enji-auth docs into this repo.

### Constraints

- Document **current** behavior only.
- Use placeholder secrets only (`your-secret-key`).
- Distinguish clearly:
  - **Wire format** (JWT public claims + required `enc` blob)
  - **Extracted `JWTClaims`** after decrypt (what callers see)

---

## Acceptance criteria

- [ ] AC-1: `README.md` install examples use `enjiai/jwt_lib` (or documented nested path that is real), not `your-org/enji-agent` | verify: `rg -n 'your-org/enji-agent' README.md` empty; `rg -n 'enjiai/jwt_lib' README.md` hits install
- [ ] AC-2: `README.md` links to `API.md` near the top or Development/Docs section | verify: `rg -n 'API\.md' README.md`
- [ ] AC-3: `README.md` JWT Token Structure documents public claims + required `enc` | verify: `rg -n '"enc"' README.md`
- [ ] AC-4: `API.md` Token Structure matches the same `enc` contract (not flat-only as current) | verify: `rg -n '"enc"' API.md`
- [ ] AC-5: `API.md` Common Patterns no longer calls `user_id` an employee ID; `employee_id` is the collector employee field | verify: `rg -n 'Employee ID' API.md` has no false label on `user_id`
- [ ] AC-6: Docs document one regex permission convention: leading `/` means “regex body after strip”; note `re.match` prefix semantics as current | verify: skim + `rg -n 're\.match|prefix|/' API.md`
- [ ] AC-7: Docs mention `stakeholder` bypass on role helpers as current behavior (README and/or API) | verify: `rg -ni 'stakeholder' README.md API.md`
- [ ] AC-8: Disallow-before-allow precedence remains documented consistently | verify: `rg -ni 'disallow' README.md API.md`
- [ ] AC-9: Suite still green | verify: `uv run pytest -q`

---

## Canonical behavior (do not invent)

From `src/enjilib_jwt/authenticator.py` `verify_and_extract`:

1. `jwt.decode(token, secret, algorithms=[algorithm])` → public dict
2. If `"enc" not in public` → `None`
3. `decrypt_payload(public["enc"], secret)` → sensitive dict
4. Merge `{**public, **sensitive}`, pop `enc`
5. `JWTClaims.from_payload(payload)`
6. Any `InvalidTokenError` or other `Exception` → `None`

Cipher (`cipher.py`): HKDF-SHA256 info `b"enji-jwt-payload-encryption"`, AES-GCM, 12-byte nonce, zlib decompress, base64url.

Role helpers: if checked role / role list involves `"stakeholder"` → `True` (see `has_role` / `has_any_role` / `has_all_roles`).

Permission helpers: disallows checked before allows; `_match_permission` uses `re.match` after optional leading `/` strip.

Minting for examples/tests: follow `tests/helpers/token_factory.py` (mirrors issuer encrypt).

Issuer plaintext set (verified in monorepo `enji-auth` `_PLAINTEXT_CLAIMS`): **only** `exp` and `type` are public JWT claims; everything else (including `sub` / `user_id` / roles / permissions / `employee_id`) is encrypted inside `enc`. Document that as current wire format:

```json
{
  "exp": 1706569200,
  "type": "access",
  "enc": "<base64url(nonce || aesgcm(zlib(json(sensitive_claims))))>"
}
```

After extract, callers see `JWTClaims` fields (`email` from `sub`, `user_id`, `roles`, `permissions`, `disallows`, `employee_id`, …) — not the raw `enc` blob. Deep issuer pointers belong in plan 04 (`docs/EXTERNAL_CONTRACTS.md`); do not copy enji-auth source here.

---

## Implementation steps

1. Read `authenticator.py`, `claims.py`, `cipher.py`, `tests/helpers/token_factory.py`, and existing `API.md` / `README.md`.
2. Rewrite README “JWT Token Structure” + install URLs; add API.md link; add short stakeholder + disallow notes where roles/permissions are shown.
3. Rewrite API.md Token Structure to match; fix Common Patterns `user_id` comment; unify regex guidance; document stakeholder.
4. Keep FastAPI usage examples valid (they already use extracted claims — no flat-token minting required in app code samples).
5. Run acceptance greps + pytest.

---

## Done report (required)

Return:

- Files changed
- AC-1…AC-9 pass/fail with command evidence
- Any ambiguity left (e.g. exact plaintext claim set) marked as “see plan 04 EXTERNAL_CONTRACTS” rather than guessed

## Out of scope

- `AGENTS.md` / handoff truth repair (plan 05)
- ADRs (plan 03)
- Packaging marker / gitignore (plan 02)
