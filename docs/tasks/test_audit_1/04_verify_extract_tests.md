# Plan 04 — `verify_and_extract` authentication tests

## Agent identity

You own **only** `tests/test_verify_extract.py` for `enjilib-jwt-auth`.  
These are the highest-value security tests: signed JWT + encrypted `enc` → `JWTClaims` or `None`. Do not edit harness, other Wave B modules, CI, or production code.

## Task

- **Task ID**: `jwt-test-audit-04-verify`
- **Title**: Behavior tests for `JWTAuthenticator.verify_and_extract`
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library tester
- **Work mode**: Auto
- **Dependencies (filesystem)**: Wave A harness with `make_access_token` / `mint_token` / `encrypt_payload`

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
test -f tests/helpers/token_factory.py
test -f tests/conftest.py
grep -q '^\[pytest\]' pytest.ini
uv run python -c "from tests.helpers.token_factory import make_access_token, encrypt_payload"
```

If helpers are missing or differently named, inspect `tests/conftest.py` and `tests/helpers/` **once**. Use existing names. If minting is impossible, STOP — do not duplicate a second encrypt implementation in this test file unless helpers are absent *and* parent orchestrator instructed you to proceed with an inline copy of the enji-auth recipe (last resort).

---

## Context

### Problem

`verify_and_extract` is the public AuthN entry point. It must:

1. Verify HS256 signature with the configured secret/algorithm.
2. Require `enc` claim.
3. Decrypt sensitive claims and merge over public claims.
4. Drop `enc` before building `JWTClaims`.
5. Return `None` on any failure (including bare `except Exception`).

Audit checklist item: valid, expired, malformed, missing `enc`, wrong-secret cases.

### Goal

Pytest coverage proving happy path and the main negative branches return `None` (not exceptions) for invalid tokens.

### Non-goals

- Unit-testing `_match_permission` (plan 03).
- Cipher-only vectors without JWT (plan 01) — you may use encrypt helper but assert through authenticator.
- CI/coverage config.

### Constraints

- Prefer fixtures `authenticator`, `jwt_secret`, `mint_token` from conftest.
- Do not assert on exception types from `verify_and_extract` — public contract is `Optional[JWTClaims]`.
- Time-dependent expiry tests: use `exp_delta=timedelta(seconds=-10)` (or freezegun **only if already a dependency** — do not add new deps).

---

## Code under test (self-contained summary)

File: `src/enjilib_jwt/authenticator.py`

```python
def verify_and_extract(self, token: str) -> Optional[JWTClaims]:
    try:
        public = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        if "enc" not in public:
            return None
        sensitive = decrypt_payload(public["enc"], self.secret_key)
        payload = {**public, **sensitive}
        payload.pop("enc", None)
        return JWTClaims.from_payload(payload)
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None
```

Token mint shape (must match):

```python
public = {"exp": <ts>, "type": "access", "enc": encrypt_payload(sensitive, secret)}
jwt.encode(public, secret, algorithm="HS256")
```

Sensitive typically includes `sub`, `user_id`, `roles`, `permissions`, `disallows`, `employee_id`, `rand_str`.

---

## Acceptance criteria

- [ ] AC-1: `tests/test_verify_extract.py` exists | verify: `file_exists: tests/test_verify_extract.py`
- [ ] AC-2: Valid token returns `JWTClaims` with expected email/user_id/roles/permissions/disallows/employee_id | verify: `test: test_verify_valid_*`
- [ ] AC-3: Expired token → `None` | verify: `test: test_verify_expired_*`
- [ ] AC-4: Malformed token string → `None` | verify: `test: test_verify_malformed_*`
- [ ] AC-5: Missing `enc` → `None` | verify: `test: test_verify_missing_enc_*`
- [ ] AC-6: Wrong secret authenticator → `None` | verify: `test: test_verify_wrong_secret_*`
- [ ] AC-7: Corrupt `enc` / decrypt failure → `None` | verify: `test: test_verify_bad_enc_*`
- [ ] AC-8: `uv run pytest -v tests/test_verify_extract.py` exits 0 | verify: `manual: run command`
- [ ] AC-9: No edits outside `tests/test_verify_extract.py` | verify: `manual: git status`

---

## Required scenarios

1. **`test_verify_valid_token_returns_claims`**
   - Mint with known roles/permissions/disallows/employee_id.
   - Assert mapped fields (`email` from `sub`).

2. **`test_verify_expired_token_returns_none`**
   - Negative `exp_delta`.

3. **`test_verify_malformed_token_returns_none`**
   - `"not-a-jwt"`, empty string.

4. **`test_verify_missing_enc_returns_none`**
   - Use helper `include_enc=False` if available; else manually `jwt.encode` flat claims with secret.

5. **`test_verify_wrong_secret_returns_none`**
   - Token minted with secret A; `JWTAuthenticator(secret_key=B)`.

6. **`test_verify_tampered_signature_returns_none`**
   - Flip last characters of token / replace payload segment.

7. **`test_verify_bad_enc_returns_none`**
   - Valid JWT structure where `enc` is garbage string still signed — decode succeeds, decrypt fails → `None`.

8. **Recommended:** algorithm mismatch / authenticator constructed with different algorithm if easy.

### Example happy path

```python
def test_verify_valid_token_returns_claims(authenticator, mint_token):
    token = mint_token(
        sub="user@example.com",
        user_id=5,
        roles=["admin"],
        permissions=["ff:access-copilot"],
        disallows=["danger:do-not"],
        employee_id=9,
    )
    claims = authenticator.verify_and_extract(token)
    assert claims is not None
    assert claims.email == "user@example.com"
    assert claims.user_id == 5
    assert claims.roles == ["admin"]
    assert claims.permissions == ["ff:access-copilot"]
    assert claims.disallows == ["danger:do-not"]
    assert claims.employee_id == 9
```

---

## Implementation notes

### Files allowed

- `tests/test_verify_extract.py` only

### Forbidden

- Changing `verify_and_extract` to raise instead of returning `None`
- Editing helpers/conftest (Wave A owned)
- Other test modules

### Validate

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -v tests/test_verify_extract.py
```

---

## Done report

1. Scenarios covered vs required list
2. pytest summary
3. Confirm isolation
