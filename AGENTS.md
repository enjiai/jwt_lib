# JWT Library (enjilib-jwt-auth) — AI Agent Entry Point

**Overview for AI Agents**

This is the entrypoint for AI agents working on `enjilib-jwt-auth`, a small but security-critical JWT authentication library for Enji microservices. This file provides everything an agent needs to orient, make safe changes, and hand off work cleanly.

**Read this file FIRST on every task** — before reading the API, planning changes, or writing code. If you are asked to implement a task here, follow the sections below in order.

---

## 1. What Is This Library?

**Purpose**: Token verification and claims extraction for Enji backend services.

**Scope**: JWT cryptography utilities (4 source modules + tests + packaging).

**Used by**: All Enji FastAPI microservices and the legacy backend (`be/legacy-services/backend/`) to verify tokens from `enji-auth` service.

**Key responsibility**: Locally verify JWT signatures and decrypt sensitive claims (encrypted in an `enc` field) without making API calls to `enji-auth`.

**Note**: This is a **shared library**, not a standalone service. Changes affect token verification everywhere in Enji. See **§5 Safe Change Boundaries** below.

---

## 2. Source Roots — Where to Find Everything

| What | Path | Purpose |
|------|------|---------|
| **Public API** | `src/enjilib_jwt/__init__.py` | Exports `JWTAuthenticator`, `JWTClaims` |
| **Authenticator** | `src/enjilib_jwt/authenticator.py` | `verify_and_extract()`, token verification logic |
| **Claims** | `src/enjilib_jwt/claims.py` | `JWTClaims` dataclass, role/permission helpers |
| **Cipher** | `src/enjilib_jwt/cipher.py` | AES-GCM encryption/decryption for `enc` field |
| **Tests** | `tests/` | Pytest suite (74 tests, 100% coverage) |
| **Config** | `pyproject.toml` | Dependencies, build config, pytest options |
| **Legacy config** | `setup.py` | Legacy build file (deprecated; pyproject.toml is canonical) |
| **API docs** | `API.md` | Token structure, claims, examples (⚠️ see Wave A issues below) |
| **README** | `README.md` | Installation, usage examples (⚠️ see Wave A issues below) |
| **Audit reports** | Wave A fix plans (see §4) | `01_TOKEN_CONTRACT_FIX_PLAN.txt`, `02_PACKAGING_HYGIENE_FIX_PLAN.txt` |

---

## 3. API Boundaries — What's Public, What's Internal

### Public API (exported from `__init__.py`)

```python
from enjilib_jwt import JWTAuthenticator, JWTClaims

# JWTAuthenticator(secret_key, algorithm="HS256")
#   .verify_and_extract(token: str) -> JWTClaims | None
#   .has_role(claims, role_name) -> bool
#   .has_permission(claims, permission) -> bool
#   .is_permission_disallowed(claims, permission) -> bool

# JWTClaims (dataclass)
#   .email, .user_id, .roles, .permissions, .disallows, .employee_id, etc.
```

**DO NOT change:**
- `JWTAuthenticator.__init__()` signature
- `verify_and_extract()` return type or behavior
- `JWTClaims` field names or types
- The meaning of roles, permissions, or disallows

**These are part of the token contract** and changing them breaks all microservices.

### Internal Modules

`cipher.py`, `claims.py` — can be refactored internally, but:
- `cipher.decrypt()` must continue decrypting AES-GCM `enc` fields
- `cipher.encrypt()` must continue to produce valid `enc` fields
- Claims processing must preserve field semantics (see API.md)

---

## 4. Known Drift & Wave A Fix Plans

The AI Readiness Audit (July 2026) identified **documentation and packaging misalignment**. Two fix plans were created; both are COMPLETE in this repository as fix-plan files.

| Wave A Task | File | Status | What agents need to know |
|-------------|------|--------|-------------------------|
| **01_TOKEN_CONTRACT_FIX** | `01_TOKEN_CONTRACT_FIX_PLAN.txt` | ✅ Completed | `README.md` and `API.md` showed tokens WITHOUT the required `enc` field. This is **now fixed**. Token examples now correctly show `"enc": "base64url-encrypted-payload"` in JWT, and decrypted payload inside. |
| **02_PACKAGING_HYGIENE_FIX** | `02_PACKAGING_HYGIENE_FIX_PLAN.txt` | ✅ Completed | `pyproject.toml` and `setup.py` had inconsistencies: missing `pytest-cov`, missing `py.typed` marker, missing classifiers. **Now fixed**: py.typed file created, pytest-cov added, classifiers synced. |

**Bottom line for agents**: Read these plans if you are changing token examples, packaging, or docs. The current code and docs are now aligned.

---

## 5. Safe Change Boundaries

### ✅ SAFE to change (low risk)

- **Internal cipher optimizations** — faster decryption, better error handling, new failure modes (if tests still pass)
- **Internal claims processing** — cleaner extraction logic, refactored helpers
- **Documentation improvements** — clarify existing behavior, add examples, fix typos
- **Packaging metadata** — dependencies (with review), classifiers, version bumps
- **Non-public methods** — helper functions, utility classes not in `__init__.py`
- **Test additions** — new tests, edge cases, coverage improvements

### ⚠️ REQUIRES REVIEW (medium risk)

- **Adding new public exports** — new classes, new helper functions exposed in `__init__.py`
- **New dependencies** — any new `dependencies = [...]` in pyproject.toml (check with maintainers first)
- **Algorithm changes** — new hash, new encryption scheme (even if backward-compatible)
- **Claims field additions** — new fields in JWTClaims (breaks consuming code)

### ❌ DO NOT CHANGE without explicit human approval

- **Token format** — changing what fields are in the JWT vs. the encrypted `enc` payload
- **`enc` field semantics** — the encryption scheme, key derivation, or decryption behavior
- **`verify_and_extract()` return type** — must always return `JWTClaims | None`
- **Role/permission authorization logic** — the semantics of `has_role()`, `has_permission()`, precedence of `disallows`
- **Package name or import path** — `enjilib-jwt-auth` distribution and `enjilib_jwt` import name are locked
- **Python version requirements** — currently requires >=3.9; changing this affects all consumers

**Why?** This is a shared, security-critical library. Token format changes break downstream services. All services must agree on token structure and verification.

---

## 6. Setup and Verification

### Install dependencies (required before any work)

Using **uv** (recommended, uses `uv.lock`):

```bash
cd /Users/13910n/work/projects/enji/agent_enji/be/shared/enjilib-jwt-auth
uv sync
```

Or using **pip** (editable install):

```bash
cd /Users/13910n/work/projects/enji/agent_enji/be/shared/enjilib-jwt-auth
pip install -e ".[dev]"
```

### Run tests (verify changes)

Using **uv** (recommended):

```bash
cd /Users/13910n/work/projects/enji/agent_enji/be/shared/enjilib-jwt-auth
uv run pytest tests/ -v
```

Or with **pip** (if uv is not available):

```bash
cd /Users/13910n/work/projects/enji/agent_enji/be/shared/enjilib-jwt-auth
pip install -e ".[dev]"
python -m pytest tests/ -v
```

**Expected output**: 74 tests pass, 100% coverage, all green. This command is your quality gate.

**Note**: If you see import errors, ensure you have Python ≥3.9 and cryptography + pyjwt installed (see setup above).

### Build package (before PR)

Using **uv**:

```bash
cd /Users/13910n/work/projects/enji/agent_enji/be/shared/enjilib-jwt-auth
uv build
```

Or using Python:

```bash
cd /Users/13910n/work/projects/enji/agent_enji/be/shared/enjilib-jwt-auth
python -m build
```

**Expected output**: `dist/enjilib_jwt_auth-0.1.0-py3-none-any.whl` and `enjilib_jwt_auth-0.1.0.tar.gz` created, no warnings.

### Type checking (optional but recommended)

```bash
cd /Users/13910n/work/projects/enji/agent_enji/be/shared/enjilib-jwt-auth
uv run mypy src/enjilib_jwt --strict
```

**Expected**: All type checks pass (the library is PEP 561 compliant with inline type hints).

---

## 7. Handoff Rules — What to Document When You're Done

When you complete a task, **before creating a PR**, document:

1. **Tests affected** (in PR description):
   - Which tests did you add or modify?
   - Coverage impact (should remain ≥ 100%)
   - Example: `Added 5 new tests for AES-GCM edge cases; coverage remains 100%`

2. **API changes** (if any):
   - Did you add/remove/change public exports (see `__init__.py`)?
   - New parameters? New return types?
   - Document as: `Added optional parameter X to verify_and_extract()`

3. **Token compatibility risk** (if changes touch token format, `enc`, or verification):
   - Is this backward-compatible with tokens issued by the current `enji-auth` service?
   - Can old tokens still be verified?
   - Document as: `Backward-compatible: old tokens with enc field still decrypt correctly`

4. **Dependency changes**:
   - Did you add any new `dependencies` to pyproject.toml?
   - Document as: `Added cryptography>=44.0.1 (for XYZ)`

5. **Known drift references** (if you touched docs or packaging):
   - Which Wave A fix plans did your changes relate to?
   - Document as: `Addressed token contract clarity (Wave A 01_TOKEN_CONTRACT_FIX)`

Example PR description template:

```markdown
## Changes
- Fixed cipher implementation for AES-GCM edge case

## Tests
- Added test_aes_gcm_empty_plaintext(), test_aes_gcm_max_payload()
- Coverage: 100% (unchanged)

## Token Compatibility
- Backward-compatible: old tokens verified with fix applied

## Handoff Notes
- Touches: src/enjilib_jwt/cipher.py only
- No API changes
- No dependency changes
```

---

## 8. Decision Tree — What to Do Next

```
What kind of work?
│
├── I'm implementing a planned task
│   └── Follow this workflow:
│       1. Read this file (you're here ✓)
│       2. Read the task plan from docs/ or the user
│       3. Review §3 (API Boundaries) — understand what can/cannot change
│       4. Review §5 (Safe Change Boundaries) — ensure your change is safe
│       5. Make your changes
│       6. Run tests: uv run pytest -v
│       7. Build package: uv build
│       8. Document per §7 (Handoff Rules)
│       9. Create PR
│
├── I'm fixing a bug
│   ├── Is it in token verification or cipher logic?
│   │   └── Follow the task workflow above (requires review for token changes)
│   └── Is it in documentation or tests?
│       └── Follow the task workflow above
│
├── I'm adding a feature or new export
│   ├── Is the new export token-related or authorization-related?
│   │   └── REQUIRES HUMAN REVIEW per §5 (⚠️ medium risk)
│   └── Is it a new helper or test?
│       └── Follow the task workflow above
│
├── I'm updating dependencies or packaging
│   └── Review §4 (Wave A plans) first to avoid drift
│       Then follow the task workflow above
│
└── I'm confused about token format or structure
    └── Read API.md first, then authenticator.py docstring
        See §4 (Known Drift) for Wave A documentation fixes
```

---

## 9. Context for Downstream Services

**Services using this library** include all Enji microservices (25+ services in `be/services/`) and the legacy backend. When you change:

- **Token verification logic** → affects token validity everywhere
- **Claims extraction** → affects authorization checks everywhere
- **Role/permission logic** → affects access control everywhere
- **Public API** → all consumers must adapt

**Do NOT assume a change is "local"** — this is a shared library. Always ask: "Will this break any of the 25+ services that depend on me?"

See `/Users/13910n/work/projects/enji/agent_enji/AGENTS.md` for the full service registry and `docs/SERVICES.md` for port, DB, and NATS details.

---

## 10. Conflict Resolution & Further Questions

**If you encounter a conflict** between this file, API.md, README.md, or the code:

1. **Check Wave A plans first** — the `01_*` and `02_*` fix plans document all known drift
2. **Trust the code over docs** — `authenticator.py` is the source of truth for verification logic
3. **Ask for clarification** — if something contradicts the plans or the code, ask the maintainer

**For questions not answered here**:
- **Token structure**: See API.md and authenticator.py docstrings
- **Installation**: See README.md (now fixed per Wave A 02)
- **Packaging**: See pyproject.toml and §4 (Wave A 02 fixes)
- **Test strategy**: See pytest.ini and tests/ folder
- **Enji architecture**: See `/Users/13910n/work/projects/enji/agent_enji/AGENTS.md`

---

## 11. Verification Checklist (Before PR)

Use this checklist before creating a pull request:

- [ ] **Tests pass**: `uv run pytest -v` exits with 0, shows 74 passed, 100% coverage
- [ ] **Package builds**: `uv build` creates valid wheel in `dist/`
- [ ] **No API breakage**: Public exports in `__init__.py` unchanged (unless explicitly added per design)
- [ ] **Token compatibility**: If you touched verification logic, tested with both old and new token formats
- [ ] **Dependencies synced**: If you modified pyproject.toml, it matches setup.py or is intentionally diverged (with reason)
- [ ] **Documentation updated**: README.md, API.md reflect any new public features or token changes
- [ ] **Handoff notes complete**: PR description includes tests, API changes, compatibility notes per §7
- [ ] **No sensitive data**: No secrets, keys, or credentials in code or docs
- [ ] **Wave A alignment**: Checked that docs and packaging remain aligned per Wave A plans

---

## End of AGENTS.md

**Last updated**: July 26, 2026 (Wave B - AGENTS.md creation)

For root project structure and other agent guidance, see:
- `/Users/13910n/work/projects/enji/agent_enji/AGENTS.md` (project-level navigation)
- `/Users/13910n/work/projects/enji/agent_enji/docs/AGENTS_COMMON.md` (common agent rules)
