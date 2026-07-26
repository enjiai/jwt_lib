# Agent Handoff and Memory Bank — `enjilib-jwt-auth`

**Last updated**: 2026-07-26  
**For**: AI agents working on the JWT authentication library  
**Repository**: `be/shared/enjilib-jwt-auth` (nested git repo: `enjiai/jwt_lib`)

---

## Purpose

This file documents **key decisions, known issues, and critical context** for any agent working on this authentication library. It is the **single source of truth** for what is locked down, what can change, and what needs human sign-off.

**Before you start any change**, read the relevant section below.  
**After you finish**, update the appropriate sections and run the validation suite.

---

## 🔒 Critical Context (Do Not Override)

### Token Contract: `enc` Field is Mandatory

- **Decision**: [001_token_contract_structure.md](./decisions/001_token_contract_structure.md)
- **What it means**:
  - All tokens **must include** an `enc` field containing AES-GCM encrypted sensitive claims
  - Tokens **without** `enc` are rejected immediately
  - Sensitive fields (user_id, roles, permissions) live **inside** `enc`, not in the public JWT
  - Wire format (see example in decision 001)

- **Locked by**: `tests/test_verify_extract.py` (74 tests, 100% coverage on crypto paths)
- **Current status**: ✅ All tests pass (as of test_audit_1)
- **If you want to change this**: Create a new Architecture Decision Record (ADR), link it here, and get explicit maintainer approval

### Package Metadata: `pyproject.toml` is Canonical

- **Decision**: [002_packaging_source_of_truth.md](./decisions/002_packaging_source_of_truth.md)
- **What it means**:
  - `pyproject.toml` is the source of truth for all metadata (deps, version, markers)
  - `setup.py` is a legacy compatibility shim; keep it aligned but do not edit independently
  - `src/enjilib_jwt/py.typed` marker exists on disk (Wave A completed)
  - Generated artifacts (`.egg-info/`, `__pycache__/`) are ignored (Wave A completed)

- **Locked by**: Code review + test validation
- **Current status**: ✅ Wave A tasks (01–02) completed by cognitive-debt-audit-1; verified on 2026-07-26
- **If you add a dependency**: Edit `pyproject.toml`; also update `setup.py` for compatibility

### Test Suite: 74 Tests, 100% Coverage on Critical Paths

- **Location**: `tests/` (from `docs/tasks/test_audit_1/`)
- **What it covers**:
  - Cipher (AES-GCM encrypt/decrypt)
  - Claims parsing and validation
  - Authorization helpers (`has_role`, `has_any_role`, `has_all_roles`, `has_permission`)
  - Token verification and decryption
  - Permission matching (regex + exact match)
  - Stakeholder role bypass (intentional, tested)
  
- **Run it**: `uv run pytest -v` (expect all green)
- **Coverage gate**: Enforced in `pyproject.toml` — do not lower
- **If tests fail**: Stop and investigate — likely indicates a breaking change or environment issue

### Known Quirks (Intentional, Not Bugs)

1. **Stakeholder role always returns `True`** — `has_role(claims, "stakeholder")` → `True` regardless of token content
   - Rationale: Superuser bypass (see tests)
   - Change process: Would require versioning + deprecation plan
   - Docs: Mentioned in README + API (Wave A task 01)

2. **Permission matching uses `re.match` (prefix)** — patterns that do not start with `/` are treated as regex
   - Rationale: Security-sensitive contract; allows flexible permission schemes
   - Change process: Would be a breaking change; requires new ADR
   - Docs: Documented in API.md

3. **Bare `except Exception` in `verify_and_extract`** — any decrypt or claims failure becomes `None`
   - Rationale: Fail-safe default for auth
   - Change process: Do not change without careful testing
   - Docs: Mentioned in API.md example

4. **Nested git repo** — commits/PRs belong in `be/shared/enjilib-jwt-auth/.git` (`enjiai/jwt_lib`), not monorepo root
   - Rationale: Library has independent release cycle
   - Change process: Follow nested repo conventions (link to AGENTS.md when created)
   - Docs: Will be in AGENTS.md (Wave B task 03)

---

## ✅ Validation Baseline

**Before you make changes** and **after you finish**, run:

```bash
cd be/shared/enjilib-jwt-auth

# Install + validate
uv sync --all-extras

# Run full test suite
uv run pytest -v

# Confirm imports work
uv run python -c "from enjilib_jwt import JWTAuthenticator, JWTClaims; print('✓ Imports OK')"
```

**Expected**: All tests green (≥74), no coverage regressions, imports clean.  
**If not**: Investigate and report before committing.

---

## 🚨 Known Issues and Fix Plans (From Wave A Audit)

### Issue A1: Token Examples in Docs Missing `enc` Field

- **Current status**: ✅ Fixed (Wave A task 01 completed by cognitive-debt-audit-1; verified 2026-07-26)
- **What was wrong**: `README.md` and `API.md` originally showed flat JWT claims without the `enc` field
- **Verification**: `rg '"enc"' README.md API.md` returns 3 matches (lines 137, 15, 96)
- **Evidence**: Examples now show both encrypted wire format and decrypted claims with `enc` field present
- **Tests**: `uv run pytest -q` → 74 passed (all green)

### Issue A2: Packaging Inconsistencies

- **Current status**: ✅ Fixed (Wave A task 02 completed by cognitive-debt-audit-1; verified 2026-07-26)
- **What was wrong**:
  - `src/enjilib_jwt/py.typed` marker was missing from disk
  - `.gitignore` was missing; generated artifacts (`.egg-info/`, `__pycache__/`) were untracked
- **Verification**: `test -f src/enjilib_jwt/py.typed` ✅ returns 0; `test -f .gitignore` ✅ returns 0
- **Evidence**: Files exist on disk; git status clean for artifacts
- **Tests**: `uv run pytest -q` → 74 passed; coverage ≥100% maintained

### Issue A3: No Agent Entrypoint (`AGENTS.md`)

- **Current status**: ✅ Resolved (AGENTS.md created as Wave B task 05; verified 2026-07-26)
- **What was missing**: No AGENTS.md entrypoint for agent handoff and setup guidance
- **Resolution**: AGENTS.md now exists with setup, API boundaries, safe-change rules, review routing
- **Next step**: This plan (05_agent_context_truth.md) is repairing false completion claims in AGENTS.md

### Issue A4: No Process Documentation (CONTRIBUTING, SECURITY, CHANGELOG)

- **Current status**: 🔄 Planned for Wave B task 05
- **Symptom**: No review, release, or security process documented
- **Impact**: Agents do not know who reviews, what versions mean, how to handle vulns
- **Fix plan**: Will create `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`
- **Done when**: Files exist with review routing, release steps, security contact

### Issue A5: No GitHub Templates (Issue/PR templates)

- **Current status**: 🔄 Planned for Wave B task 04
- **Symptom**: No structured intake for bugs, features, or PRs
- **Impact**: Agents do not know what to include in issues/PRs; reviews are unfocused
- **Fix plan**: Will create `.github/ISSUE_TEMPLATE/` and PR template with scope/risk/verification fields
- **Done when**: `.github/` templates exist

---

## 📋 Before You Change Something

### If you are modifying token verification or encryption:

1. ✅ Read [Decision 001](./decisions/001_token_contract_structure.md) — understand the `enc` field
2. ✅ Run baseline: `uv run pytest -v` (confirm green)
3. ✅ Make your change
4. ✅ Run again: `uv run pytest -v` (must still be green, no coverage regression)
5. ✅ If tests fail → stop, investigate, do not commit
6. ✅ If you want to change the token contract → create a new ADR, update decision 001, get approval

### If you are adding a dependency or changing package metadata:

1. ✅ Read [Decision 002](./decisions/002_packaging_source_of_truth.md) — `pyproject.toml` is canonical
2. ✅ Edit `pyproject.toml` (primary source)
3. ✅ Also check/update `setup.py` for compatibility
4. ✅ Run: `uv lock` (if adding/removing deps)
5. ✅ Run: `uv sync --all-extras && uv run pytest -v`
6. ✅ Commit together (do not let them drift)

### If you are fixing a doc or example:

1. ✅ Check [Issue A1](#issue-a1-token-examples-in-docs-missing-enc-field) — token examples must show `enc`
2. ✅ Check [Issue A2](#issue-a2-packaging-inconsistencies) — install URLs must use `enjiai/jwt_lib`
3. ✅ Run: `uv run pytest -v` (ensure no behavior changed)
4. ✅ Check: `grep -n enc README.md API.md` (confirm examples have `enc` field)

### If you are adding a new test:

1. ✅ Ensure it covers a real behavior (not just code paths)
2. ✅ Keep coverage ≥100% on crypto functions
3. ✅ Run: `uv run pytest -v --cov=enjilib_jwt --cov-fail-under=100`
4. ✅ If coverage drops → add more tests, do not lower the gate

### If you are fixing a reported issue:

1. ✅ Check [Known Issues](#-known-issues-and-fix-plans-from-wave-a-audit) above
2. ✅ If it is listed → follow the fix plan
3. ✅ If it is new → create a GitHub issue first (when templates exist), link it in a new ADR or this file

---

## 🔄 Decisions Log

**Key architectural / compatibility-sensitive decisions** are documented in `docs/decisions/` as Architecture Decision Records (ADRs).

| File | Status | Locked by | Change process |
|------|--------|-----------|-----------------|
| [001_token_contract_structure.md](./decisions/001_token_contract_structure.md) | ✅ Accepted | Tests (74 green) | New ADR + approval |
| [002_packaging_source_of_truth.md](./decisions/002_packaging_source_of_truth.md) | 🔄 Proposed | Wave A implementation | Implementation blocks breaking changes |

**To add a new decision**:
1. Create `docs/decisions/00N_<slug>.md` (3-digit prefix)
2. Follow the format in existing ADRs
3. Link it here
4. Update CHANGELOG.md (when it exists)

---

## 📝 When You Finish Your Task

### Checklist

- ✅ Run full validation: `uv sync --all-extras && uv run pytest -v`
- ✅ Confirm coverage ≥100% on modified code (or raise in handoff)
- ✅ Update any decision records if you changed the contract
- ✅ Add a bullet to this handoff.md under "Recent changes" (see section below)
- ✅ Update `CHANGELOG.md` (when it exists) with your changes
- ✅ Commit and push to a feature branch in the nested repo (`be/shared/enjilib-jwt-auth/.git`)
- ✅ Open a PR with:
  - Clear scope (what changed, why)
  - Link to this handoff.md (if you added findings)
  - Verification (test output, before/after, edge cases)
- ✅ Address review feedback or escalate

### Template: Update this handoff.md

If you discovered something important:

```markdown
## Recent Changes

### {Date} — {Agent name} — {Task/PR}

**What changed**: {One-line summary}  
**Why**: {Context}  
**Files**: `docs/decisions/00N_*.md` (new), `src/file.py` (modified)  
**Tests**: ✅ All green (74 tests, 100% coverage)  
**Known follow-ups**: {Any TODOs or questions for next agent}  
```

---

## 🔗 Related Documentation

### Agent entrypoint (will be created Wave B task 03)
- `AGENTS.md` — setup, boundaries, safe-change rules, review routing

### Process documentation (will be created Wave B task 05)
- `CONTRIBUTING.md` — contribution workflow
- `SECURITY.md` — vulnerability reporting
- `CHANGELOG.md` — release notes and change tracking

### GitHub templates (will be created Wave B task 04)
- `.github/ISSUE_TEMPLATE/bug.md`
- `.github/ISSUE_TEMPLATE/feature.md`
- `.github/pull_request_template.md`

### Repository docs
- [`README.md`](../../README.md) — package overview (updated by Wave A task 01)
- [`API.md`](../../API.md) — public API reference (updated by Wave A task 01)
- [`docs/tasks/test_audit_1/README.md`](../tasks/test_audit_1/README.md) — test suite overview
- [`docs/tasks/ai_readiness_audit_1/README.md`](../tasks/ai_readiness_audit_1/README.md) — audit orchestration

---

## ℹ️ Quick Reference

### Repository structure
```
be/shared/enjilib-jwt-auth/
├── src/enjilib_jwt/
│   ├── __init__.py              (public exports)
│   ├── authenticator.py         (JWTAuthenticator, token verify/extract)
│   ├── claims.py                (JWTClaims, AuthZ helpers)
│   ├── cipher.py                (AES-GCM encrypt/decrypt)
│   └── py.typed                 (typing marker — Wave A to add)
├── tests/                       (74-test suite from test_audit_1)
├── pyproject.toml               (canonical metadata)
├── setup.py                     (legacy compatibility, keep aligned)
├── pytest.ini                   (test config)
├── README.md                    (install, overview — Wave A updating)
├── API.md                       (public API reference — Wave A updating)
└── docs/
    ├── decisions/               (ADRs, starting with 001, 002)
    ├── handoff.md               (this file)
    └── tasks/
        ├── test_audit_1/        (74-test suite implementation)
        └── ai_readiness_audit_1/ (Wave A–B remediation plans)
```

### Commands

```bash
cd be/shared/enjilib-jwt-auth

# Setup
uv sync --all-extras

# Test
uv run pytest -v                 # All tests
uv run pytest -v tests/test_authz.py  # Specific file
uv run pytest -k "stakeholder"    # Specific test by name
uv run pytest --cov=enjilib_jwt --cov-fail-under=100  # With coverage

# Development
uv run python -m pytest tests/ -v
uv run python -c "from enjilib_jwt import ..."

# Build
python -m build                  # (after uv sync)
```

### Key files to understand

| File | Purpose | Agent checklist |
|------|---------|-----------------|
| `src/enjilib_jwt/authenticator.py` | Token verification, role/permission helpers | Understand `verify_and_extract()` contract (Decision 001) |
| `src/enjilib_jwt/cipher.py` | AES-GCM encryption, zlib compression | Do not change without test coverage review |
| `src/enjilib_jwt/claims.py` | `JWTClaims` model, role/permission helpers | Understand `stakeholder` bypass (documented quirk) |
| `tests/` | 74-test suite with 100% coverage | Run before/after changes; all must stay green |
| `docs/decisions/` | Architecture decisions (001, 002, …) | Read relevant decision before changing |
| `docs/handoff.md` | This file — agent memory | Update after you finish |

---

## 🆘 Support

### Questions?

1. **About token contract** → See [Decision 001](./decisions/001_token_contract_structure.md)
2. **About packaging** → See [Decision 002](./decisions/002_packaging_source_of_truth.md)
3. **About known issues** → See [Known Issues](#-known-issues-and-fix-plans-from-wave-a-audit) section
4. **About running tests** → See [Validation Baseline](#-validation-baseline)
5. **About the audit** → See `docs/tasks/ai_readiness_audit_1/enjiai-jwt_lib-audit-ai-readiness-2026-07-15.md`

### Something broke?

1. Run `uv run pytest -v` to see what failed
2. Check if your change is in the [critical context](#-critical-context-do-not-override) section
3. Revert, investigate, then retry
4. If still stuck, escalate to maintainer with:
   - Command that failed
   - Full error output
   - What you changed
   - When you made the change

---

## Document Metadata

- **Created**: 2026-07-26 (Wave B task 06 — memory handoff)
- **Last updated**: 2026-07-26
- **Owner**: Enji JWT library maintainers + AI agents
- **Audience**: Any AI agent working on `be/shared/enjilib-jwt-auth`
- **Related**: Decisions in `docs/decisions/`, audit in `docs/tasks/ai_readiness_audit_1/`, tests in `docs/tasks/test_audit_1/`
