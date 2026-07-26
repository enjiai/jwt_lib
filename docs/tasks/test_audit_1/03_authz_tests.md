# Plan 03 — Authorization (roles & permissions) tests

## Agent identity

You own **only** `tests/test_authz.py` for `enjilib-jwt-auth`.  
Construct `JWTClaims` directly — no token minting required. Do not edit harness, other tests, CI, or production source.

## Task

- **Task ID**: `jwt-test-audit-03-authz`
- **Title**: Parameterized tests for role and permission allow/deny logic
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library tester
- **Work mode**: Auto
- **Dependencies (filesystem)**: Wave A pytest/config green enough to import `enjilib_jwt`

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
grep -q '^\[pytest\]' pytest.ini
uv run python -c "from enjilib_jwt import JWTAuthenticator, JWTClaims"
```

---

## Context

### Problem

Authorization helpers decide allow/deny for every microservice using this library. Logic includes regex patterns, deny-list precedence, invalid regex skipping, and an undocumented `stakeholder` always-allow role bypass. None of this is tested.

### Goal

Explicit allow/deny assertions for:

- roles (`has_role`, `has_any_role`, `has_all_roles`) including `stakeholder` bypass
- permissions (`has_permission`, `has_any_permission`, `has_all_permissions`, `is_permission_disallowed`)
- exact vs `/regex` patterns
- deny precedence over allow
- invalid regex patterns → no match (skipped)

### Non-goals

- JWT verify/decrypt (plans 01/04).
- Changing production authz semantics (pin current behavior, even if surprising).
- FastAPI dependency examples.

### Constraints

- Prefer `@pytest.mark.parametrize` for matrix cases.
- Build claims with `JWTClaims(...)` — do not go through tokens.
- Document surprising behaviors in test names/docstrings, do not “fix” them in this plan.

---

## Code under test (self-contained summary)

File: `src/enjilib_jwt/authenticator.py` (static methods)

### Roles

- `has_role(claims, role)`: if `role == "stakeholder"` → **always `True`**; else `role in claims.roles`.
- `has_any_role(claims, roles)`: if `"stakeholder" in roles` → **always `True`**; else any membership.
- `has_all_roles(claims, roles)`: if `"stakeholder" in roles` → **always `True`**; else all membership.

### Permission matching (`_match_permission`)

- If `pattern.startswith("/")`, strip leading `/` and `re.match` the remainder.
- Else `re.match(pattern, permission)` on the raw pattern (so `.` is a metacharacter; match is prefix-anchored only via `re.match`).
- On `re.error`, return `False`.

### Permission checks

- `has_permission`: if matches any `disallows` → `False`; else if matches any `permissions` → `True`; else `False`.
- `has_any_permission` / `has_all_permissions`: compose over `has_permission`.
- `is_permission_disallowed`: match against `disallows` only.

---

## Acceptance criteria

- [ ] AC-1: `tests/test_authz.py` exists | verify: `file_exists: tests/test_authz.py`
- [ ] AC-2: Role allow/deny + stakeholder bypass covered | verify: `test: test_*role*`
- [ ] AC-3: Exact permission allow and deny covered | verify: `test: test_*permission*`
- [ ] AC-4: Regex `/...` allow patterns covered | verify: `test: test_*regex*` or parametrized cases
- [ ] AC-5: Deny-list precedence over overlapping allow covered | verify: `test: test_*deny*precedence*` or equivalent
- [ ] AC-6: Invalid regex pattern does not match / does not raise | verify: `test: test_*invalid_regex*`
- [ ] AC-7: `uv run pytest -v tests/test_authz.py` exits 0 | verify: `manual: run command`
- [ ] AC-8: No edits outside `tests/test_authz.py` | verify: `manual: git status`

---

## Required scenarios

### Roles

1. User with `admin` → `has_role(..., "admin")` True; `has_role(..., "editor")` False.
2. `has_any_role` / `has_all_roles` happy and unhappy paths.
3. **Stakeholder bypass (must pin):**
   - Empty `claims.roles`, `has_role(claims, "stakeholder")` is True.
   - `has_any_role(claims, ["stakeholder"])` True even when user has no roles.
   - `has_all_roles(claims, ["admin", "stakeholder"])` True even when user lacks `admin` (current code short-circuits).

### Permissions — exact

4. Allow exact `ff:access-copilot`.
5. Unknown permission → False.
6. Disallow exact blocks even when also allowed.

### Permissions — regex

7. Pattern `/enji-db:(read|update)-roles$` allows `enji-db:read-roles`, denies non-match.
8. Wildcard `/.*` allows arbitrary permission unless disallowed.
9. Disallow regex overrides allow regex for the same permission string.

### Permissions — edge

10. Invalid regex in permissions list (e.g. `"/[unclosed"`) → treated as non-match, no exception from `has_permission`.
11. Recommended: prefix behavior — pattern `"admin"` matching `"admin.extra"` via `re.match` (pin current behavior in a clearly named test).
12. `has_any_permission` / `has_all_permissions` / `is_permission_disallowed` at least one positive and one negative each.

### Helper to build claims

```python
from enjilib_jwt import JWTClaims, JWTAuthenticator

def make_claims(*, roles=None, permissions=None, disallows=None):
    return JWTClaims(
        user_id=1,
        email="u@example.com",
        roles=roles or [],
        permissions=permissions or [],
        disallows=disallows or [],
    )
```

---

## Implementation notes

### Files allowed

- `tests/test_authz.py` only

### Forbidden

- Production `src/**` changes (including “fixing” stakeholder bypass)
- Other test files / harness / CI

### Validate

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -v tests/test_authz.py
```

---

## Done report

1. Parametrize matrices / test names
2. Explicit note that stakeholder bypass was tested as-is
3. pytest summary for this file
4. Confirm file isolation
