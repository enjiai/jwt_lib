# Changelog

All notable changes to enjilib-jwt-auth are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Versioning Notes

**Token Format Changes:** Major version bumps (e.g., 0.1.0 → 1.0.0) indicate a breaking change to the JWT token contract, verification logic, or claim structure. Consumers must re-evaluate their token generation/handling when updating.

**Security Fixes:** If a security vulnerability affects token verification, all versions prior to the fix are considered unsupported. See [SECURITY.md](./SECURITY.md) for supported versions.

## [Unreleased]

### Added
- Initial release structure and development tooling
- Support for local JWT token verification without external API calls
- `JWTAuthenticator` class for token verification and claims extraction
- `JWTClaims` dataclass for structured claim access
- Role-based access control (RBAC) helpers: `has_role()`, `has_any_role()`, `has_all_roles()`
- Permission-based access control (PBAC) helpers: `has_permission()`, `has_any_permission()`, `has_all_permissions()`
- Regex pattern support in permission and disallow lists
- Full async support via standard `async def` functions
- Type hints on all public APIs
- 100% test coverage (pytest with coverage enforcement)
- **CI/CD Gate**: GitHub Actions workflow (`.github/workflows/test.yml`) for automated testing, type checking, and package building

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- All token verification uses constant-time comparison (via PyJWT)
- HMAC keys enforced to be ≥32 bytes for SHA256
- No sensitive data (keys, tokens) logged by default

---

## Example Releases (Below)

These are example entries showing the changelog format. Remove or adapt as needed when cutting real releases.

---

## [1.0.0] - 2026-02-15 (HYPOTHETICAL EXAMPLE)

### Added
- New claim type `employee_id` for linking to Collector database employees
- FastAPI integration helpers in new `fastapi_helpers` module
- Docs: Token compatibility testing guide added to API.md

### Changed
- **BREAKING**: Token verification now rejects tokens missing the `exp` claim (previously silently accepted indefinite tokens)
- **BREAKING**: `JWTAuthenticator.verify()` renamed to `verify_and_extract()` for clarity
- Simplified permission regex matching: moved from `re.match()` to `re.search()` for better UX

### Security
- Fixed timing-attack vulnerability in role comparison (now uses `set` instead of list iteration with early exit)
- Upgraded `cryptography` to ≥44.0.1 for improved key derivation
- Added constant-time comparison for all claim verification

---

## [0.1.0] - 2026-01-15 (HYPOTHETICAL EXAMPLE)

### Added
- Initial release
- JWT token verification with PyJWT
- Claims extraction and type validation
- RBAC and PBAC helpers
- Full test suite with 100% coverage

### Security
- Enforces HMAC key length ≥32 bytes for SHA256
- All tokens require `exp` claim

---

## Release Process

### Automated Publishing (CI/CD)

The repository includes a **tag-triggered GitHub Actions workflow** (`.github/workflows/release.yml`) that automates testing and publishing to PyPI.

**How it works:**

1. Cut a release locally:
   - Update `[Unreleased]` section in `CHANGELOG.md` → `[X.Y.Z] - YYYY-MM-DD`
   - Update `version = "X.Y.Z"` in `pyproject.toml`
   - Commit: `git commit -am "Release X.Y.Z"`

2. Create and push a version tag:
   ```bash
   git tag -a vX.Y.Z -m "Release X.Y.Z"
   git push origin vX.Y.Z
   ```

3. GitHub Actions automatically:
   - Checks out the tag
   - Installs dependencies (`uv sync --frozen --all-extras`)
   - Runs full test suite (`pytest`)
   - Builds the package (`uv build`)
   - Publishes to PyPI using **trusted publishing (OIDC)**

**Trusted Publishing (OIDC):**

This workflow uses PyPI's trusted publishing feature, which allows GitHub Actions to authenticate without storing long-lived API tokens. The following one-time admin setup is required:

- Create a PyPI project for `enjiai/jwt_lib` (if not already exists)
- In PyPI project settings → Trusted publishers → add a new publisher:
  - **Publisher type**: GitHub Actions
  - **Repository**: `enjiai/jwt_lib`
  - **Workflow**: `.github/workflows/release.yml`
  - **Environment name**: `release`
- In the GitHub repository, create an `environment: release` and configure branch protection rules if desired

Once configured, releases are fully automated: **tag push → tests → publish**.

### Manual Publishing (Legacy)

If needed for troubleshooting or special cases:

```bash
uv build
twine upload dist/*
```

Requires `TWINE_USERNAME` and `TWINE_PASSWORD` (or `.pypirc`) to be configured locally.

---

## Unreleased Versioning Guide

When ready to release, follow these steps:

1. **Choose version number** based on changes:
   - Token format/verification change → **major** (0.x → 1.0)
   - New feature (backwards compatible) → **minor** (1.0 → 1.1)
   - Bugfix (backwards compatible) → **patch** (1.0.0 → 1.0.1)

2. **Update this file**:
   - Move `[Unreleased]` section to `[X.Y.Z] - YYYY-MM-DD`
   - Add new empty `[Unreleased]` section above

3. **Update version** in `pyproject.toml`:
   ```toml
   version = "X.Y.Z"
   ```

4. **Create git tag**:
   ```bash
   git tag -a vX.Y.Z -m "Release X.Y.Z"
   git push origin vX.Y.Z
   ```
   The release workflow will automatically build and publish to PyPI.

---

## Release History

- **2026-02-15**: Release 1.0.0 (hypothetical example with breaking changes)
- **2026-01-15**: Release 0.1.0 (hypothetical example, initial release)

