# Plan 00 — Test harness, lockfile, shared fixtures

## Agent identity

You are implementing **only** the test harness and shared fixtures for `enjilib-jwt-auth`.  
Do **not** write behavioral test modules (`test_cipher.py`, `test_claims.py`, `test_authz.py`, `test_verify_extract.py`). Do **not** add CI workflows or coverage thresholds (Wave C).

## Task

- **Task ID**: `jwt-test-audit-00-harness`
- **Title**: Fix pytest/packaging reproducibility and add shared token fixtures
- **Component**: `be/shared` (library package)
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / FastAPI consumers of `enjilib_jwt`
- **Work mode**: Auto
- **Dependencies**: None (Wave A — must finish before other test plans)

---

## Context

### Problem

The library declares pytest tooling but has no runnable suite. Packaging is inconsistent:

- `pytest.ini` uses section `[tool:pytest]` (setup.cfg style). For `pytest.ini` the section must be `[pytest]`.
- `pyproject.toml` depends on `cryptography>=44.0.1`, but `uv.lock` does **not** pin `cryptography`.
- `setup.py` `install_requires` lists only `pyjwt` — missing `cryptography`.
- `tests/` contains only `__init__.py`. Downstream Wave B agents need a shared way to mint Enji-style tokens with an `enc` claim.

### Goal

A clean checkout can `uv sync --all-extras` and `uv run pytest` (exit 0 even with a single smoke/placeholder or zero collected tests once config is valid — prefer a tiny smoke that imports the package). Shared fixtures/helpers exist so other agents can mint valid HS256 + AES-GCM tokens without re-implementing encryption.

### Non-goals

- Full behavioral coverage of authenticator/cipher/claims/authz (other plans).
- GitHub Actions / coverage gates (plan `05_coverage_and_ci.md`).
- Changing production crypto algorithms or public API semantics.
- Publishing a new package version.

### Constraints

- Keep Python `>=3.9` compatibility.
- Encrypt helper in tests must match enji-auth pipeline exactly (see recipe below).
- Do not add production `encrypt_payload` to the library unless absolutely required; prefer **test-only** helper.
- No new runtime dependencies beyond aligning lockfile with already-declared `cryptography`.
- Dev extras may add nothing beyond what Wave C will need later; optional: leave coverage deps to Wave C.

---

## Acceptance criteria

- [ ] AC-1: `pytest.ini` uses `[pytest]` (not `[tool:pytest]`) | verify: `grep: ^\[pytest\] pytest.ini`
- [ ] AC-2: `uv.lock` contains a `cryptography` package entry | verify: `grep: name = \"cryptography\" uv.lock`
- [ ] AC-3: `setup.py` `install_requires` includes `cryptography` | verify: `grep: cryptography setup.py`
- [ ] AC-4: `tests/helpers/token_factory.py` (or equivalent) provides `encrypt_payload` + `make_access_token` matching enji-auth | verify: `file_exists: tests/helpers/token_factory.py`
- [ ] AC-5: `tests/conftest.py` exposes fixtures `jwt_secret`, `authenticator`, and re-exports/helpers for minting tokens | verify: `file_exists: tests/conftest.py`
- [ ] AC-6: From service root, `uv sync --all-extras && uv run pytest -v` exits 0 | verify: `manual: run command`
- [ ] AC-7: Package imports: `uv run python -c "from enjilib_jwt import JWTAuthenticator, JWTClaims"` succeeds | verify: `manual: run command`

---

## Analysis

### Current state

| Path | Role |
|---|---|
| `src/enjilib_jwt/authenticator.py` | Verify JWT, decrypt `enc`, authz helpers |
| `src/enjilib_jwt/cipher.py` | `decrypt_payload` only (HKDF + AES-GCM + zlib) |
| `src/enjilib_jwt/claims.py` | `JWTClaims` dataclass + `from_payload` |
| `pyproject.toml` | Declares `pyjwt`, `cryptography`, pytest extras |
| `setup.py` | Incomplete deps |
| `pytest.ini` | Wrong section name |
| `uv.lock` | Missing `cryptography` |
| `tests/__init__.py` | Empty package marker |

Canonical encrypt (enji-auth): `be/services/enji-auth/app/auth/authentication/cipher.py`  
Reference consumer test mint: `be/services/copilot/tests/fixtures/scheduled_jwt.py`

Token shape used by `JWTAuthenticator.verify_and_extract`:

1. Plaintext JWT claims: at least `exp`, `type`, and required `enc`.
2. `enc` = base64url(nonce12 ‖ AESGCM(zlib(json(sensitive)))).
3. Sensitive typically: `sub`, `user_id`, `roles`, `permissions`, `disallows`, `employee_id`, `rand_str`, …
4. Signed with HS256 using the same secret used for HKDF.

### Proposed changes

1. Fix `pytest.ini` section to `[pytest]`.
2. Add `cryptography>=44.0.1` to `setup.py` `install_requires`.
3. Regenerate `uv.lock` with `uv lock` / `uv sync --all-extras` so `cryptography` is pinned.
4. Add test-only encrypt + token mint helpers.
5. Add `conftest.py` fixtures.
6. Optionally add `tests/test_smoke_import.py` with one assert that imports succeed — only if needed so pytest exit code is 0 when no other tests exist yet. Prefer documenting that empty collection may still exit 5 until Wave B lands; **better**: add a single smoke test so harness itself is green.

### Risks & mitigations

- Lockfile churn → run `uv lock` only inside this repo; commit `uv.lock`.
- Encrypt drift from enji-auth → copy algorithm constants exactly (`info=b"enji-jwt-payload-encryption"`, nonce 12, `Z_BEST_COMPRESSION`, urlsafe b64).
- Wave B conflicts on `conftest.py` → this plan owns conftest; Wave B must not edit it.

### Security / safety

- Use disposable secrets in tests (`"test-secret-key-do-not-use"`).
- Never commit real JWT secrets.
- Do not weaken production exception handling in this plan.

---

## Implementation plan

### Files you may create/modify

**Allowed:**

- `pytest.ini`
- `setup.py`
- `pyproject.toml` (only if needed for package discovery / pytest config move — prefer minimal)
- `uv.lock`
- `tests/conftest.py`
- `tests/helpers/__init__.py`
- `tests/helpers/token_factory.py`
- `tests/test_smoke_import.py` (optional one-liner smoke)

**Forbidden:**

- `src/**` production behavior changes (unless fixing an import crash)
- `tests/test_cipher.py`, `tests/test_claims.py`, `tests/test_authz.py`, `tests/test_verify_extract.py`
- `.github/**`

### Step-by-step

#### 1. Fix `pytest.ini`

Replace content with:

```ini
[pytest]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

Note: in classic `pytest.ini`, list values are usually space-separated without JSON arrays. Prefer:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

#### 2. Align `setup.py`

Ensure `install_requires` includes both:

```python
install_requires=[
    "pyjwt>=2.8.0",
    "cryptography>=44.0.1",
],
```

#### 3. Refresh lockfile

```bash
cd be/shared/enjilib-jwt-auth
uv lock
uv sync --all-extras
```

Confirm `cryptography` appears in `uv.lock`.

#### 4. Add token factory (test-only)

Create `tests/helpers/token_factory.py` with this contract (adapt style to match repo):

```python
"""Test-only helpers mirroring enji-auth encrypt + HS256 minting."""

from __future__ import annotations

import base64
import json
import os
import zlib
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

_NONCE_SIZE = 12


def derive_key(secret: str) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"enji-jwt-payload-encryption",
    ).derive(secret.encode())


def encrypt_payload(data: dict[str, Any], secret: str) -> str:
    nonce = os.urandom(_NONCE_SIZE)
    plaintext = zlib.compress(
        json.dumps(data, separators=(",", ":")).encode(),
        level=zlib.Z_BEST_COMPRESSION,
    )
    ciphertext = AESGCM(derive_key(secret)).encrypt(nonce, plaintext, None)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode()


def make_access_token(
    secret: str,
    *,
    sub: str = "user@example.com",
    user_id: int = 1,
    roles: list[str] | None = None,
    permissions: list[str] | None = None,
    disallows: list[str] | None = None,
    employee_id: int | None = 42,
    exp_delta: timedelta = timedelta(hours=1),
    algorithm: str = "HS256",
    extra_sensitive: dict[str, Any] | None = None,
    include_enc: bool = True,
) -> str:
    exp_ts = int((datetime.now(UTC) + exp_delta).timestamp())
    sensitive: dict[str, Any] = {
        "sub": sub,
        "user_id": user_id,
        "rand_str": "test-rand-str",
        "roles": roles or [],
        "permissions": permissions or [],
        "disallows": disallows or [],
        "employee_id": employee_id,
    }
    if extra_sensitive:
        sensitive.update(extra_sensitive)
    public: dict[str, Any] = {"exp": exp_ts, "type": "access"}
    if include_enc:
        public["enc"] = encrypt_payload(sensitive, secret)
    else:
        public.update(sensitive)
    return str(jwt.encode(public, secret, algorithm=algorithm))
```

#### 5. Add `tests/conftest.py`

Provide at least:

```python
import pytest
from enjilib_jwt import JWTAuthenticator
from tests.helpers.token_factory import encrypt_payload, make_access_token

TEST_SECRET = "test-secret-key-do-not-use"


@pytest.fixture
def jwt_secret() -> str:
    return TEST_SECRET


@pytest.fixture
def authenticator(jwt_secret: str) -> JWTAuthenticator:
    return JWTAuthenticator(secret_key=jwt_secret)


@pytest.fixture
def mint_token(jwt_secret: str):
    def _mint(**kwargs):
        return make_access_token(jwt_secret, **kwargs)
    return _mint
```

Export `encrypt_payload` for cipher tests via fixture or direct import from helpers.

#### 6. Optional smoke test

`tests/test_smoke_import.py`:

```python
def test_package_exports():
    from enjilib_jwt import JWTAuthenticator, JWTClaims
    assert JWTAuthenticator is not None
    assert JWTClaims is not None
```

#### 7. Validate

```bash
uv sync --all-extras
uv run pytest -v
uv run python -c "from enjilib_jwt import JWTAuthenticator, JWTClaims; print('ok')"
```

### Exit criteria

- All AC checked.
- Working tree ready for Wave B agents (fixtures importable).
- Do not start Wave B work yourself.

---

## Done report (for parent orchestrator)

Report:

1. Commands run + exit codes
2. Files changed
3. Confirmation that Wave B file paths do **not** exist yet (or exist only if already from parallel work — do not create them)
4. Any deviation from encrypt recipe
