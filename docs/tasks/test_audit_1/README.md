# Test audit remediation — orchestration

## Audit verdict (reviewed against local code)

Source audit: `enjiai-jwt_lib-audit-tests-2026-07-15.md` against commit `93d861b`.

| Audit claim | Local verification | Verdict |
|---|---|---|
| Zero executable tests (`tests/` only `__init__.py`) | Confirmed | Correct |
| Score ~5/100, effective coverage 0% | Confirmed | Correct |
| Security-sensitive surface untested (verify, decrypt, authz) | Confirmed on `authenticator.py`, `cipher.py`, `claims.py` | Correct |
| `pytest.ini` misconfigured (`[tool:pytest]` instead of `[pytest]`) | Confirmed | Correct |
| `cryptography` in `pyproject.toml` but missing from `uv.lock` | Confirmed | Correct |
| No CI | No `.github/` | Correct |
| Highest impact: auth verify + allow/deny | Matches library API surface | Correct priority |

### Extra findings from code review (not in audit, included in plans)

1. **`setup.py` omits `cryptography`** while `pyproject.toml` declares it — dual packaging drift.
2. **`verify_and_extract` uses bare `except Exception`** — any decrypt/claims failure becomes `None`; tests must lock that contract.
3. **`stakeholder` role always returns `True`** in `has_role` / `has_any_role` / `has_all_roles` — undocumented security footgun; tests must pin current behavior.
4. **Permission matching uses `re.match` without full-string anchors** for non-`/` patterns — `"admin"` matches `"admin.x"`; dots are regex metacharacters. Tests must pin this.
5. **Library has decrypt-only cipher** — mint helpers must copy enji-auth `encrypt_payload` (same HKDF info `enji-jwt-payload-encryption`).
6. **API.md inconsistency** (`user_id` vs employee_id in “Common Patterns”) — out of scope for test work unless a plan says otherwise.

## Goal

Bring `enjilib-jwt-auth` from 0 executable tests to a deterministic pytest suite covering cipher, claims, authz, and token verification, plus harness/CI so merges cannot silently drop coverage.

## Parallel execution model

```
Wave A (1 agent, BLOCKING)
  └── 00_harness.md

Wave B (up to 4 agents, PARALLEL — after Wave A green)
  ├── 01_cipher_tests.md
  ├── 02_claims_tests.md
  ├── 03_authz_tests.md
  └── 04_verify_extract_tests.md

Wave C (1 agent, after Wave B merged/green)
  └── 05_coverage_and_ci.md
```

**Why this split:** Wave B agents each own a single disjoint `tests/test_*.py` file and must not edit harness/CI. That avoids merge conflicts and lets four agents run in parallel after fixtures exist.

## How to launch subagents

1. Run **one** agent on `00_harness.md` until its acceptance criteria pass.
2. Launch **four** agents in parallel, each with **only one** plan file path from Wave B.
3. After all four report done, run **one** agent on `05_coverage_and_ci.md`.

Each plan file is self-contained: an agent must **not** need to read sibling plans. Prerequisites are expressed as filesystem checks, not “read plan N”.

## Working directory

All work happens in the nested repo:

```
be/shared/enjilib-jwt-auth/
```

Commits/PRs for this library belong in that nested `.git`, not the monorepo root.

## Validation baseline (all waves)

```bash
cd be/shared/enjilib-jwt-auth
uv sync --all-extras
uv run pytest -v
```

## Plan index

| File | Wave | Owns | Parallel? |
|---|---|---|---|
| [00_harness.md](./00_harness.md) | A | tooling, lockfile, shared fixtures | Solo first |
| [01_cipher_tests.md](./01_cipher_tests.md) | B | `tests/test_cipher.py` | Yes |
| [02_claims_tests.md](./02_claims_tests.md) | B | `tests/test_claims.py` | Yes |
| [03_authz_tests.md](./03_authz_tests.md) | B | `tests/test_authz.py` | Yes |
| [04_verify_extract_tests.md](./04_verify_extract_tests.md) | B | `tests/test_verify_extract.py` | Yes |
| [05_coverage_and_ci.md](./05_coverage_and_ci.md) | C | coverage config + CI workflow | Solo last |
