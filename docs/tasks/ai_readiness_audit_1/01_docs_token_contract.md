# Plan 01 — Docs: token contract & install source of truth

## Agent identity

You reconcile **human/agent-facing docs** with the real JWT contract and install source for `enjilib-jwt-auth`.  
Do **not** change production code under `src/`. Do **not** edit packaging files owned by plan 02 (`.gitignore`, `py.typed`, egg-info). Do **not** create `AGENTS.md` / process docs (Wave B).

## Task

- **Task ID**: `jwt-ai-ready-01-docs-contract`
- **Title**: Fix README/API token shape, install URLs, and identity/authz documentation drift
- **Component**: `be/shared` (library package)
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Docs
- **Work mode**: Auto
- **Dependencies**: Prerequisite — `uv run pytest -v` exits 0 (test suite from `test_audit_1`)

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -q
test -f src/enjilib_jwt/authenticator.py
```

If pytest is red, STOP and report — do not “fix” docs by inventing a different token contract.

---

## Context

### Problem

AI-readiness audit found moderate doc↔code drift:

1. `README.md` and `API.md` show flat JWT claims (`sub`, `user_id`, `roles`, …) but `JWTAuthenticator.verify_and_extract` returns `None` unless the decoded payload has an `enc` field, then decrypts sensitive claims from it.
2. Install examples use placeholder `your-org/enji-agent` + subdirectory. Canonical nested remote is `enjiai/jwt_lib` (`git@github.com:enjiai/jwt_lib.git`).
3. `API.md` warns `user_id` is **not** employee ID, then “Common Patterns” comments `# Employee ID` on `claims.user_id`.
4. Undocumented **`stakeholder` role bypass** (always allow when the checked role list involves `stakeholder`) — already locked by tests in `tests/test_authz.py`.

### Goal

One documented token contract and install path that match code + tests, so agents stop minting flat tokens or installing from a fake monorepo URL.

### Non-goals

- Adding `encrypt_payload` to production library.
- Changing AuthZ semantics.
- Writing `AGENTS.md`, CONTRIBUTING, SECURITY, CHANGELOG, GitHub templates, handoff files.
- Editing `pyproject.toml` / `setup.py` / egg-info / adding `py.typed` (plan 02).

### Constraints

- Document **current** behavior; do not propose breaking API changes in this plan.
- Keep examples copy-pasteable; use placeholder secrets only (`your-secret-key`).
- Prefer documenting both shapes clearly: **wire format** (public JWT + `enc`) vs **extracted `JWTClaims`** after decrypt.

---

## Acceptance criteria

- [ ] AC-1: `README.md` install examples use `enjiai/jwt_lib` (direct package repo), not `your-org/enji-agent` | verify: `grep -n your-org README.md` returns empty; `grep -n enjiai/jwt_lib README.md` hits install section
- [ ] AC-2: `README.md` “JWT Token Structure” (or equivalent) documents public claims + required `enc` encrypted blob | verify: `grep -n '"enc"' README.md` (or clear prose + JSON showing `enc`)
- [ ] AC-3: `API.md` Token Structure matches the same `enc` contract | verify: same as AC-2 for `API.md`
- [ ] AC-4: `API.md` Common Patterns no longer calls `user_id` an employee ID; `employee_id` is the collector employee field | verify: `grep -n "Employee ID" API.md` has no false label on `user_id`
- [ ] AC-5: Docs mention `stakeholder` bypass for role helpers (README and/or API) as current behavior | verify: `grep -ni stakeholder README.md API.md`
- [ ] AC-6: Docs note disallow-before-allow permission precedence (already partly in API — keep consistent in README if permission section exists) | verify: manual skim
- [ ] AC-7: Suite still green | verify: `uv run pytest -q`

---

## Analysis

### Canonical verify path (do not invent)

From `src/enjilib_jwt/authenticator.py`:

1. `jwt.decode` with secret + algorithm.
2. If `"enc" not in public` → `None`.
3. `decrypt_payload(public["enc"], secret)` → sensitive dict.
4. Merge public+sensitive, drop `enc`, build `JWTClaims.from_payload`.

Sensitive fields typically live **inside** `enc`: `sub`, `user_id`, `roles`, `permissions`, `disallows`, `employee_id`, `rand_str`, …  
Public JWT often carries `exp`, `type`, `enc`.

### Suggested README install snippets

```toml
dependencies = [
    "enjilib-jwt-auth @ git+https://github.com/enjiai/jwt_lib.git@main",
]
```

```bash
pip install git+https://github.com/enjiai/jwt_lib.git@main
```

Optional note: a monorepo subdirectory install is **not** the canonical path for this nested package repo.

### Suggested wire-format JSON (illustrative)

```json
{
  "exp": 1706569200,
  "type": "access",
  "enc": "<base64url(nonce || aesgcm(zlib(json(sensitive_claims))))>"
}
```

Plus a second block showing **decrypted logical claims** / `JWTClaims` fields (what callers see after `verify_and_extract`).

### Stakeholder wording (pin current code)

- `has_role(claims, "stakeholder")` → always `True`
- `has_any_role` / `has_all_roles` → if `"stakeholder"` is in the **requested** list → always `True`

State this is intentional current behavior; changing it is a breaking compatibility decision (see future ADRs in plan 06).

---

## Implementation plan

### Files you may create/modify

**Allowed:**

- `README.md`
- `API.md`

**Forbidden:**

- `src/**`
- `tests/**`
- `pyproject.toml`, `setup.py`, `uv.lock`, `pytest.ini`
- `.gitignore`, `src/enjilib_jwt/py.typed`, `src/enjilib_jwt_auth.egg-info/**`
- `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`
- `.github/**` (except you must not touch CI either)
- `docs/decisions/**`, `docs/handoff.md`

### Step-by-step

1. Fix install URLs in `README.md`.
2. Replace flat token example with wire format + extracted-claims explanation in `README.md` and `API.md`.
3. Fix `user_id` vs `employee_id` inconsistency in `API.md` Common Patterns.
4. Add short “Role notes” / Important Notes bullet for `stakeholder`.
5. Align permission disallow-precedence wording between README and API if README still oversimplifies.
6. Run `uv run pytest -q`.

### Exit criteria

- All AC checked.
- Do not start Wave B yourself.

---

## Done report (for parent orchestrator)

Report:

1. Commands run + exit codes
2. Files changed
3. Before/after note for install URL and token example
4. Exact stakeholder wording added
5. Any leftover placeholder URLs found elsewhere (list only; do not edit forbidden files)
