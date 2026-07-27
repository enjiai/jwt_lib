# enjilib-jwt-auth

JWT authentication utilities for Enji microservices.

## Installation

### From GitHub (development)

Add to your `pyproject.toml`:

```toml
dependencies = [
    "enjilib-jwt-auth @ git+https://github.com/enjiai/jwt_lib.git@main",
]
```

Or with pip:

```bash
pip install git+https://github.com/enjiai/jwt_lib.git@main
```

## Usage

### Basic Example

```python
from enjilib_jwt import JWTAuthenticator, JWTClaims

# Initialize authenticator with secret key from enji-auth
authenticator = JWTAuthenticator(secret_key="your-secret-key")

# Verify token and extract claims
claims = authenticator.verify_and_extract(token)

if claims:
    print(f"User: {claims.email}")
    print(f"User ID: {claims.user_id}")
    print(f"Roles: {claims.roles}")
    print(f"Permissions: {claims.permissions}")
```

### With FastAPI

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from enjilib_jwt import JWTAuthenticator, JWTClaims

security = HTTPBearer()
authenticator = JWTAuthenticator(settings.jwt_secret_key)

async def get_jwt_claims(credentials = Depends(security)) -> JWTClaims:
    claims = authenticator.verify_and_extract(credentials.credentials)
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid token")
    return claims

@app.get("/me/")
async def get_current_user(claims: JWTClaims = Depends(get_jwt_claims)):
    return {
        "user_id": claims.user_id,
        "email": claims.email,
        "roles": claims.roles,
    }
```

### Permission Checks

```python
# Check single permission
if authenticator.has_permission(claims, "users.delete"):
    # Allow user deletion
    pass

# Check any permission
if authenticator.has_any_permission(claims, ["admin.users", "admin.config"]):
    # Grant admin access
    pass

# Check all permissions
if authenticator.has_all_permissions(claims, ["users.read", "users.write"]):
    # Allow full user management
    pass
```

### Role Checks

```python
# Check single role
if authenticator.has_role(claims, "admin"):
    # Admin only
    pass

# Check any role
if authenticator.has_any_role(claims, ["admin", "moderator"]):
    # Special access
    pass

# Check all roles
if authenticator.has_all_roles(claims, ["editor", "publisher"]):
    # Both roles required
    pass
```

### FastAPI Dependency Factory

```python
from fastapi import Depends

async def require_permission(permission: str):
    async def check(claims: JWTClaims = Depends(get_jwt_claims)) -> JWTClaims:
        if not authenticator.has_permission(claims, permission):
            raise HTTPException(status_code=403)
        return claims
    return check

@app.post("/files/delete/")
async def delete_file(
    file_id: int,
    claims: JWTClaims = Depends(require_permission("files.delete"))
):
    # User already has permission
    return {"deleted": file_id}
```

## JWT Token Structure

### Wire Format

Tokens from enji-auth are signed JWT with public claims and encrypted sensitive claims:

```json
{
  "exp": 1706569200,
  "type": "access",
  "enc": "<base64url(nonce || aesgcm(zlib(sensitive_claims)))>"
}
```

Only `exp` and `type` are publicly visible. The `enc` claim contains encrypted and compressed sensitive claims (user identity, roles, permissions).

### Extracted Claims

After `verify_and_extract()` decrypts and decompresses the `enc` blob, callers see these fields in `JWTClaims`:

```json
{
  "sub": "user@example.com",
  "user_id": 123,
  "email": "user@example.com",
  "type": "access",
  "exp": 1706569200,
  "rand_str": "uuid",
  "roles": ["admin", "editor"],
  "permissions": ["read", "write", "delete"],
  "disallows": [],
  "employee_id": 321
}
```

> **Note:** Identity fields (`sub`, `user_id`, `roles`, `permissions`, `disallows`, `employee_id`) are **encrypted in transit** and only available after successful decryption. See [API.md](API.md) for complete method signatures and permission matching semantics.

### Stakeholder Bypass

All role helpers (`has_role`, `has_any_role`, `has_all_roles`) recognize `"stakeholder"` as a special bypass role that grants access unconditionally, even if the user has no actual roles. This is an intentional escape hatch for internal use.

## External Contracts

For details on the token encryption contract with enji-auth issuer and Collector employee ID integration, see [EXTERNAL_CONTRACTS.md](docs/EXTERNAL_CONTRACTS.md).

## Development

### Quick start

Use the local gate **Makefile** for reproducible verification:

```bash
make check      # Full local gate: sync + test + typecheck + build
make test       # Run pytest with coverage (must be 100%)
make sync       # Sync dependencies with uv (frozen, CI-parity)
make build      # Build wheel and sdist
make typecheck  # Run mypy type checker
```

**What is CI testing?** The same `quality` job runs on every PR via `.github/workflows/test.yml`, executing these exact commands.

### Manual setup (without Makefile)

Install dependencies (frozen for CI parity):

```bash
uv sync --frozen --all-extras
```

### Run tests

```bash
uv run pytest -v
```

### Run tests with coverage

```bash
uv run pytest --cov=enjilib_jwt --cov-report=term-missing
```

### Build package

```bash
uv build
```

## License

MIT
