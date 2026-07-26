# Plan 02 — JWTClaims unit tests

## Agent identity

You own **only** `tests/test_claims.py` for `enjilib-jwt-auth`.  
Pure unit tests — no JWT crypto required. Do not edit harness, other tests, CI, or production code.

## Task

- **Task ID**: `jwt-test-audit-02-claims`
- **Title**: Unit tests for `JWTClaims.from_payload`
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library tester
- **Work mode**: Auto
- **Dependencies (filesystem)**: pytest harness Wave A present (`[pytest]` in `pytest.ini`); crypto fixtures optional for this plan

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
grep -q '^\[pytest\]' pytest.ini
uv run python -c "from enjilib_jwt import JWTClaims"
```

If import fails due to missing `cryptography`, Wave A is incomplete — **stop**.

You do **not** need `token_factory` for this plan.

---

## Context

### Problem

`JWTClaims` is the public claims container. Mapping bugs (`sub` → email, defaults for lists, optional `employee_id`) silently break every consumer. No tests exist.

### Goal

Lock `from_payload` field mapping and defaults with pure unit tests (construct dicts, no tokens).

### Non-goals

- Permission/role helpers (plan 03).
- `verify_and_extract` (plan 04).
- Cipher (plan 01).
- Changing dataclass fields or adding validation (out of scope unless tests cannot express current behavior).

### Constraints

- Pin **current** behavior, including permissive `.get` usage (`user_id`/`email` may become `None` if missing — assert that if you cover missing keys).
- No network, no filesystem side effects.

---

## Code under test (self-contained summary)

File: `src/enjilib_jwt/claims.py`

```python
@dataclass
class JWTClaims:
    user_id: int
    email: str
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    disallows: list[str] = field(default_factory=list)
    employee_id: int | None = None

    @classmethod
    def from_payload(cls, payload: dict) -> "JWTClaims":
        return cls(
            user_id=payload.get("user_id"),
            email=payload.get("sub"),          # note: sub → email
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", []),
            disallows=payload.get("disallows", []),
            employee_id=payload.get("employee_id"),
        )
```

Important mappings:

| Payload key | Attribute |
|---|---|
| `user_id` | `user_id` |
| `sub` | `email` |
| `roles` | `roles` |
| `permissions` | `permissions` |
| `disallows` | `disallows` |
| `employee_id` | `employee_id` |

---

## Acceptance criteria

- [ ] AC-1: `tests/test_claims.py` exists | verify: `file_exists: tests/test_claims.py`
- [ ] AC-2: Full payload maps all fields including `sub`→`email` | verify: `test: test_from_payload_maps_*`
- [ ] AC-3: Missing optional lists default to `[]` | verify: `test: test_from_payload_defaults_*`
- [ ] AC-4: Missing `employee_id` yields `None` | verify: `test: test_from_payload_employee_id_optional*`
- [ ] AC-5: `uv run pytest -v tests/test_claims.py` exits 0 | verify: `manual: run command`
- [ ] AC-6: No edits outside `tests/test_claims.py` | verify: `manual: git status`

---

## Required scenarios

1. **`test_from_payload_maps_all_fields`**
   - Include `sub`, `user_id`, `roles`, `permissions`, `disallows`, `employee_id`.
   - Assert `email == payload["sub"]`.

2. **`test_from_payload_defaults_empty_lists`**
   - Payload only `user_id` + `sub`.
   - `roles`, `permissions`, `disallows` == `[]`.

3. **`test_from_payload_employee_id_optional`**
   - No `employee_id` key → `claims.employee_id is None`.

4. **`test_from_payload_ignores_unknown_keys`** (recommended)
   - Extra keys like `exp`, `type`, `rand_str` do not appear as attributes / do not break construction.

5. **`test_from_payload_missing_user_id_and_sub`** (recommended — pins current permissive behavior)
   - Document actual results (`None`s) without “fixing” the dataclass.

Use plain asserts; parametrize if helpful.

---

## Implementation notes

### Files allowed

- `tests/test_claims.py` only

### Forbidden

- `src/**`
- `tests/conftest.py`, helpers, other test modules
- CI / lockfile / packaging

### Example

```python
from enjilib_jwt import JWTClaims


def test_from_payload_maps_all_fields():
    payload = {
        "sub": "a@b.c",
        "user_id": 12,
        "roles": ["admin"],
        "permissions": ["x"],
        "disallows": ["y"],
        "employee_id": 34,
        "exp": 1,
        "type": "access",
    }
    claims = JWTClaims.from_payload(payload)
    assert claims.email == "a@b.c"
    assert claims.user_id == 12
    assert claims.roles == ["admin"]
    assert claims.permissions == ["x"]
    assert claims.disallows == ["y"]
    assert claims.employee_id == 34
```

### Validate

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -v tests/test_claims.py
```

---

## Done report

1. Test names
2. pytest summary for this file
3. Confirm isolation (no other file edits)
