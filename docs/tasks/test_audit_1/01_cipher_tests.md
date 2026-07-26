# Plan 01 — Cipher unit tests

## Agent identity

You own **only** `tests/test_cipher.py` for `enjilib-jwt-auth`.  
Do not edit harness files, other test modules, CI, or production source unless a test reveals a crash that blocks collection — prefer reporting production bugs instead of “fixing” crypto.

## Task

- **Task ID**: `jwt-test-audit-01-cipher`
- **Title**: Unit/integration tests for AES-GCM payload decrypt
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library tester
- **Work mode**: Auto
- **Dependencies (filesystem, not other plan files)**: Wave A harness must already be present

---

## Prerequisite gate (STOP if unmet)

Before writing tests, verify all of the following. If any fail, **stop and report** — do not invent a parallel harness.

```bash
cd be/shared/enjilib-jwt-auth
test -f tests/helpers/token_factory.py
test -f tests/conftest.py
grep -q '^\[pytest\]' pytest.ini
grep -q 'name = "cryptography"' uv.lock
```

You need:

- `tests.helpers.token_factory.encrypt_payload` (or equivalent name documented in `conftest` / helpers)
- Ability to import `enjilib_jwt.cipher.decrypt_payload`

---

## Context

### Problem

`src/enjilib_jwt/cipher.py` implements decrypt-only AES-256-GCM + HKDF + zlib decompression. It is security-critical and currently untested. Invalid ciphertext, wrong secrets, and malformed blobs must fail loudly (exceptions), while valid round-trips must restore dicts.

### Goal

Pytest module that proves:

1. Round-trip: encrypt (test helper) → decrypt (library) restores payload.
2. Wrong secret fails.
3. Truncated / garbage / wrong-nonce blobs fail.
4. Nested structures and unicode survive round-trip.

### Non-goals

- JWT signing / `verify_and_extract` (plan 04).
- Authz / claims mapping (plans 02–03).
- Adding production `encrypt_payload` to the library.
- Coverage config / CI.

### Constraints

- Deterministic tests: do not assert exact ciphertext bytes (nonce is random); assert decrypt results.
- Use only disposable secrets from fixtures.
- Keep tests fast (<1s total).

---

## Code under test (self-contained summary)

File: `src/enjilib_jwt/cipher.py`

- `_derive_key(secret)` — HKDF-SHA256, length 32, `salt=None`, `info=b"enji-jwt-payload-encryption"`.
- `decrypt_payload(token: str, secret: str) -> dict`:
  1. `base64.urlsafe_b64decode(token)`
  2. split first 12 bytes as nonce
  3. AESGCM decrypt
  4. `zlib.decompress` → `json.loads`

There is **no** public encrypt in the library. Encrypt via `tests.helpers.token_factory.encrypt_payload`.

---

## Acceptance criteria

- [ ] AC-1: File `tests/test_cipher.py` exists | verify: `file_exists: tests/test_cipher.py`
- [ ] AC-2: Round-trip test for a realistic sensitive claims dict | verify: `test: test_decrypt_roundtrip_*`
- [ ] AC-3: Wrong secret raises (cryptography/`InvalidTag` or equivalent) | verify: `test: test_decrypt_wrong_secret_*`
- [ ] AC-4: Malformed input raises | verify: `test: test_decrypt_malformed_*`
- [ ] AC-5: `uv run pytest -v tests/test_cipher.py` exits 0 | verify: `manual: run command`
- [ ] AC-6: This agent did not modify `tests/conftest.py` or other Wave B test files | verify: `manual: git status`

---

## Required scenarios (implement at least these)

1. **`test_decrypt_roundtrip_sensitive_claims`**
   - Payload includes `sub`, `user_id`, `roles`, `permissions`, `disallows`, `employee_id`.
   - `encrypt_payload` → `decrypt_payload` → equal dict.

2. **`test_decrypt_roundtrip_unicode_and_nested`**
   - Non-ASCII email / nested list values if present in dict.

3. **`test_decrypt_wrong_secret_raises`**
   - Encrypt with secret A, decrypt with secret B → expect exception (do not swallow).

4. **`test_decrypt_truncated_raises`**
   - Empty string / not-base64 / too-short blob after decode.

5. **`test_decrypt_tampered_ciphertext_raises`**
   - Flip a byte in the ciphertext portion after decode+re-encode, or mutate the token string.

Use `pytest.raises` with a reasonably broad exception type if cryptography exceptions vary (`Exception` is acceptable only if you also assert it is **not** silently returning `{}`). Prefer the concrete exception from AESGCM (`cryptography.exceptions.InvalidTag`) when stable.

---

## Implementation notes

### Files you may create/modify

**Allowed:** `tests/test_cipher.py` only (plus local untracked scratch if needed — do not commit scratch).

**Forbidden:** `src/**`, `tests/conftest.py`, `tests/helpers/**` (unless a one-line export is missing — then ask/report; prefer importing existing helper), other `tests/test_*.py`, `.github/**`, lockfiles.

### Suggested structure

```python
import pytest
from enjilib_jwt.cipher import decrypt_payload
from tests.helpers.token_factory import encrypt_payload


def test_decrypt_roundtrip_sensitive_claims(jwt_secret):
    payload = {
        "sub": "user@example.com",
        "user_id": 7,
        "roles": ["admin"],
        "permissions": ["ff:access-copilot"],
        "disallows": [],
        "employee_id": 99,
    }
    token = encrypt_payload(payload, jwt_secret)
    assert decrypt_payload(token, jwt_secret) == payload
```

If `jwt_secret` fixture is missing, import `TEST_SECRET` from conftest/helpers only if already exported; otherwise STOP.

### Validate

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -v tests/test_cipher.py
```

Do not require the entire suite green if other Wave B agents have broken tests mid-flight — your file must pass in isolation.

---

## Done report

1. Test names added
2. pytest output summary for `tests/test_cipher.py`
3. Confirm no edits outside allowed files
