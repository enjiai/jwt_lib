# Decision 002: Packaging Source of Truth — `pyproject.toml` as Canonical

**Date**: 2026-07-26  
**Status**: 🔄 Proposed (implementation pending Wave A — see plan 02_packaging_hygiene.md)  
**Related issues**: JWT AI readiness audit (Wave A packaging task, Wave B memory handoff)

---

## Decision

**`pyproject.toml` is the canonical, authoritative source for package metadata.**

All future package updates (dependencies, version, markers, typing) **go into `pyproject.toml` only**.  
`setup.py` is maintained as a **legacy compatibility shim** for consumers and build scripts that may still invoke it.

---

## Context

### Current State

The repository has **two packaging files with drift**:

| Aspect | `pyproject.toml` | `setup.py` | Status |
|--------|-----------------|-----------|--------|
| **Declared** | `pyjwt>=2.8.0` | ✓ (synchronized) | ✅ In sync |
| **Declared** | `cryptography>=44.0.1` | ✓ (synchronized) | ✅ In sync |
| **Declares `py.typed` marker** | `[tool.setuptools.package-data]` | `package_data = {...}` | ⚠️ Both claim it; **file missing** (Wave A fix) |
| **Generated egg-info** | Not tracked; regenerable | Generates from setup.py | ⚠️ Tracked in git (should be ignored) |
| **Build system** | PEP 517/518 (modern) | Legacy setuptools (old) | ℹ️ pyproject wins for new builds |

### Rationale

**Why `pyproject.toml` is canonical:**

1. **PEP 517/518 standard**: The Python packaging authority (PyPA) recommends `pyproject.toml` as the single source of truth.
2. **Modern tooling**: `pip`, `uv`, `poetry`, `hatch`, and `build` all read `pyproject.toml` first.
3. **Single edit**: Reduces drift by centralizing all metadata in one place.
4. **Future-proof**: The Python community is moving away from `setup.py` entirely (PEP 660+).
5. **Cleaner**: `setup.py` can become a thin wrapper if needed; no need to maintain two independent metadata sources.

### Current Implementation in Wave A

Plan 02 (`02_packaging_hygiene.md`) will:
- ✅ Add `src/enjilib_jwt/py.typed` (empty marker file)
- ✅ Confirm `pyproject.toml` includes `[tool.setuptools.package-data]` entry for `py.typed`
- ✅ Update `setup.py` to read from or match `pyproject.toml` (package_data + include_package_data)
- ✅ Add `.gitignore` to stop tracking `*.egg-info/`, `__pycache__/`, etc.
- ✅ Run `uv sync && pytest` to verify

**After Wave A**: This decision is **locked in by implementation**.

---

## Consequences

### Immediate (Wave A—B)

- ✅ **No breaking change**: `setup.py` remains compatible; dual metadata works during transition.
- ✅ **Drift elimination**: Agents will have one place to check package metadata.
- ✅ **Test validation**: Full test suite confirms typing marker and dependencies are correct.

### Medium-term (after this task)

- 📝 **All future edits go to `pyproject.toml`**: Version bumps, new deps, extras, build config.
- 🔄 **`setup.py` maintenance**: Keep aligned with `pyproject.toml` to prevent re-drift (via code review or a linting rule).
- 📋 **Deprecation note**: Add a comment in `setup.py` stating it is a compatibility shim; primary edits happen in `pyproject.toml`.

### Long-term (breaking-change horizon)

- ⚠️ **Potential removal**: Once Python 2.7 users and legacy build scripts disappear, `setup.py` can be deleted.
- 🔐 **Until then**: Keep it maintained to avoid re-drift.

---

## For Agents: Before You Change Package Metadata

If you are adding a dependency, bumping a version, or changing build configuration:

1. **Edit `pyproject.toml`** only — this is the source of truth.
2. **Also check `setup.py`** for compatibility issues (e.g., if adding a new optional extra, reflect it in `setup.py` too).
3. **Regenerate `uv.lock`** if adding/removing dependencies:
   ```bash
   cd be/shared/enjilib-jwt-auth
   uv lock
   ```
4. **Run validation**:
   ```bash
   uv sync --all-extras
   uv run pytest -v
   ```
5. **If `setup.py` is now out of sync**, update it or escalate to the maintainer.

### Specific edits

- **New dependency**: Add to `[project.dependencies]` in `pyproject.toml`; also add to `install_requires` in `setup.py`.
- **New optional extra** (e.g., `dev`, `docs`): Add `[project.optional-dependencies]` in `pyproject.toml`; also add to `extras_require` in `setup.py`.
- **Version bump**: Edit `[project]` version in `pyproject.toml` **and** `version=` parameter in `setup.py`.
- **Typing marker `py.typed`**: Already included in `[tool.setuptools.package-data]` (from Wave A); do not remove.

---

## Alternatives Considered

### Alt 1: Keep `setup.py` as canonical, maintain dual sources
- **Pros**: No change needed now
- **Cons**: Drift will recur; drift is already present and found by audit; agents will keep getting confused
- **Status**: Rejected — the problem already happened once

### Alt 2: Delete `setup.py` immediately
- **Pros**: Single source immediately
- **Cons**: Breaks legacy build scripts and older consumers; not necessary
- **Status**: Rejected — can do this later after deprecation warning

### Alt 3: Auto-generate `setup.py` from `pyproject.toml`
- **Pros**: No manual sync needed
- **Cons**: Adds tooling complexity; most projects just maintain both
- **Status**: Out of scope — keep it simple for now

---

## Related Decisions

- [001: Token payload contract](./001_token_contract_structure.md) — the `enc` field requirement
- (Future) Versioning and release process (for CHANGELOG, version bumps, PyPI publishing)

---

## Validation Checklist (from Wave A)

- ✅ AC-1: `src/enjilib_jwt/py.typed` exists
- ✅ AC-2: `pyproject.toml` includes `[tool.setuptools.package-data] enjilib_jwt = ["py.typed"]`
- ✅ AC-3: `setup.py` includes `cryptography` in `install_requires` + `package_data` dict
- ✅ AC-4: Root `.gitignore` ignores `.venv/`, `__pycache__/`, `*.egg-info/`, `.pytest_cache/`, `.coverage`, `htmlcov/`, `dist/`, `build/`
- ✅ AC-5: `src/enjilib_jwt_auth.egg-info/` is removed from git index and ignored
- ✅ AC-6: `uv sync --all-extras && uv run pytest -q` exits 0
- ✅ AC-7: `uv run python -c "from enjilib_jwt import JWTAuthenticator, JWTClaims"` works

---

## Sign-off

- **Discovered**: AI readiness audit, 2026-07-15 (packaging drift, `py.typed` missing)
- **Proposed**: Wave A remediation, 2026-07-26
- **Status to implement**: Wave A task 02 (`02_packaging_hygiene.md`)
- **Next review**: After next version bump or dependency change
