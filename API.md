# enjilib-jwt-auth API Reference

JWT authentication library for Enji microservices. Provides local token verification and claims extraction without external API calls.

## Token Structure

### Wire Format

Tokens issued by enji-auth are JWT with public claims and encrypted sensitive claims:

```json
{
  "exp": 1706569200,
  "type": "access",
  "enc": "<base64url(nonce || aesgcm(zlib(sensitive_claims)))>"
}
```

Only `exp` and `type` are directly readable in the JWT. The `enc` claim contains AES-GCM encrypted sensitive data (compressed with zlib, using HKDF-SHA256 key derivation with info `b"enji-jwt-payload-encryption"`).

### Extracted Claims Structure

After `verify_and_extract()` decrypts the `enc` blob, callers receive a `JWTClaims` object with:

```json
{
  "sub": "user@example.com",
  "user_id": 123,
  "type": "access",
  "exp": 1706569200,
  "rand_str": "uuid",
  "roles": ["admin", "editor"],
  "permissions": [
    "service:action-resource",
    "/service:(action1|action2)-resource$"
  ],
  "disallows": ["service:dangerous-action", "/service:(delete)-admin_only$"],
  "employee_id": 321
}
```

### Claim Fields

| Field         | Type      | Description                                                        |
| ------------- | --------- | ------------------------------------------------------------------ |
| `sub`         | string    | User email address (from encrypted payload)                         |
| `user_id`     | int       | Unique user ID from enji-auth (NOT the same as `employee_id`)      |
| `type`        | string    | Token type (e.g., "access"); public claim                          |
| `exp`         | int       | Unix timestamp of expiration; public claim                         |
| `rand_str`    | string    | Random UUID for token uniqueness (encrypted)                       |
| `roles`       | list[str] | User roles (e.g., ["admin", "editor"]; encrypted)                  |
| `permissions` | list[str] | User permissions (exact match or regex patterns; encrypted)        |
| `disallows`   | list[str] | Explicitly disallowed permissions (exact match or regex; encrypted) |
| `employee_id` | int       | Employee ID from collector database (encrypted)                    |

## Core Classes

### JWTClaims

Data class holding extracted token claims.

```python
from enjilib_jwt import JWTClaims

@dataclass
class JWTClaims:
    user_id: int              # Unique user ID from enji-auth (not employee_id)
    email: str                # User email (from "sub" claim)
    roles: list[str]          # User roles
    permissions: list[str]    # User permissions (allowed patterns)
    disallows: list[str]      # Explicitly disallowed permission patterns
    employee_id: int | None   # Employee ID from collector database
```

### JWTAuthenticator

Main class for JWT verification and authorization checks.

```python
from enjilib_jwt import JWTAuthenticator

authenticator = JWTAuthenticator(
    secret_key="your-secret-key",
    algorithm="HS256"  # default
)
```

## Methods

### verify_and_extract(token: str) -> JWTClaims | None

Verifies JWT signature and extracts claims.

**Behavior:**
1. Decodes JWT public claims (requires `exp` and `type`)
2. Returns `None` if `"enc"` is missing or invalid (no fallback to flat claims)
3. Decrypts sensitive payload from `enc` blob using HKDF-SHA256 derived key and AES-GCM
4. Merges public and sensitive claims, removes `enc` before returning
5. Returns `None` on any error (invalid signature, decryption failure, or JSON parse error)

**Returns:** `JWTClaims` if valid and successfully decrypted, `None` if invalid

**Example:**

```python
token = "eyJhbGc..."
claims = authenticator.verify_and_extract(token)

if claims:
    print(f"User: {claims.email}")
    print(f"ID: {claims.user_id}")
    print(f"Roles: {claims.roles}")
else:
    print("Invalid token")
```

### has_role(claims: JWTClaims, role: str) -> bool

Check if user has a specific role.

**Special Behavior:** If `role == "stakeholder"`, always returns `True` (bypass mechanism). This is an intentional escape hatch for internal use, regardless of the user's actual roles.

**Example:**

```python
if JWTAuthenticator.has_role(claims, "admin"):
    # Grant admin access

if JWTAuthenticator.has_role(claims, "stakeholder"):
    # Always True (bypass granted)
    pass
```

### has_any_role(claims: JWTClaims, roles: list[str]) -> bool

Check if user has any of the specified roles.

**Special Behavior:** If `"stakeholder"` is in the roles list, always returns `True` (bypass mechanism).

**Example:**

```python
if JWTAuthenticator.has_any_role(claims, ["admin", "moderator"]):
    # Grant special access

if JWTAuthenticator.has_any_role(claims, ["stakeholder", "editor"]):
    # Always True because stakeholder is in the list
    pass
```

### has_all_roles(claims: JWTClaims, roles: list[str]) -> bool

Check if user has all specified roles.

**Special Behavior:** If `"stakeholder"` is in the roles list, always returns `True` (bypass mechanism).

**Example:**

```python
if JWTAuthenticator.has_all_roles(claims, ["editor", "publisher"]):
    # Both roles required
    pass

if JWTAuthenticator.has_all_roles(claims, ["stakeholder", "anyone"]):
    # Always True because stakeholder is in the list
    pass
```

### has_permission(claims: JWTClaims, permission: str) -> bool

Check if user has specific permission using regex pattern matching.

The method checks both allowed permissions and disallowed permissions. **Disallows take precedence:** if a permission matches any pattern in `disallows`, it returns `False` even if it matches an allow pattern.

**Permission Format:**

- Exact match: `"service:action-resource"` (matched by `re.match`, so prefix match)
- Regex pattern: `/service:(action1|action2)-resource$/` (leading `/` stripped, then matched with `re.match`)
- Wildcard: `/.*` (matches any permission starting with any characters)

**Permission Resolution Logic:**

1. Check if permission matches any pattern in `disallows` → return `False` (blocked)
2. Check if permission matches any pattern in `permissions` → return `True` (allowed)
3. Otherwise → return `False`

Note: All patterns are matched using `re.match`, which matches from the beginning of the string (prefix semantics).

**Example:**

```python
# Exact permission check
if JWTAuthenticator.has_permission(claims, "activity:read-activities"):
    # User can read activities

# JWT permissions can be patterns that match multiple permissions
# If JWT contains: "permissions": ["/activity:(read|write)-.*"]
#            and: "disallows": ["activity:write-admin_settings"]
# Then:
if JWTAuthenticator.has_permission(claims, "activity:read-activities"):
    # True - matches allow pattern

if JWTAuthenticator.has_permission(claims, "activity:write-admin_settings"):
    # False - matches disallow pattern (disallow takes precedence)

if JWTAuthenticator.has_permission(claims, "activity:write-activities"):
    # True - matches allow pattern, not in disallows
```

### has_any_permission(claims: JWTClaims, permissions: list[str]) -> bool

Check if user has any of the specified permissions.

**Example:**

```python
if JWTAuthenticator.has_any_permission(claims, ["admin:all", "user:read"]):
    # Grant access if has any permission
```

### has_all_permissions(claims: JWTClaims, permissions: list[str]) -> bool

Check if user has all specified permissions.

**Example:**

```python
if JWTAuthenticator.has_all_permissions(claims, ["user:read", "user:write"]):
    # Allow full user management
```

### is_permission_disallowed(claims: JWTClaims, permission: str) -> bool

Check if a specific permission is explicitly disallowed.

**Example:**

```python
if JWTAuthenticator.is_permission_disallowed(claims, "admin:delete-users"):
    # Permission is explicitly blocked
    raise HTTPException(status_code=403, detail="This action is blocked")
```

## FastAPI Integration Example

```python
from enjilib_jwt import JWTAuthenticator, JWTClaims
from fastapi import Depends, HTTPException, FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()
security = HTTPBearer()
authenticator = JWTAuthenticator(secret_key="your-secret-key")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> JWTClaims:
    claims = authenticator.verify_and_extract(credentials.credentials)
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid token")
    return claims

@app.get("/me/")
async def get_user(claims: JWTClaims = Depends(get_current_user)):
    return {
        "email": claims.email,
        "user_id": claims.user_id,
        "roles": claims.roles,
    }

@app.post("/admin/")
async def admin_only(claims: JWTClaims = Depends(get_current_user)):
    if not JWTAuthenticator.has_role(claims, "admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    return {"message": "Admin access granted"}

def require_permission(permission: str):
    async def check(claims: JWTClaims = Depends(get_current_user)) -> JWTClaims:
        if not JWTAuthenticator.has_permission(claims, permission):
            raise HTTPException(status_code=403, detail="Permission denied")
        return claims
    return check

@app.post("/users/create/")
async def create_user(
    claims: JWTClaims = Depends(require_permission("admin:create-users"))
):
    return {"message": "User created"}
```

## Important Notes

1. **Token Verification is Local** - No HTTP calls to enji-auth needed. Decryption uses the same secret key that signed the JWT.
2. **Permission Matching** - Uses `re.match` for prefix-based regex matching. Permissions in JWT can be patterns that match multiple specific permissions.
3. **Claims Structure** - Always check that `verify_and_extract()` returns non-None before accessing claims.
4. **Security** - Keep `secret_key` secure and never expose it. The same key is used for both JWT signing and sensitive claim encryption.
5. **Disallow Precedence** - Disallow list takes precedence over allow list. A permission matching any disallow pattern will be denied even if it matches an allow pattern.

## Common Patterns

### Extract user info without permissions check

```python
claims = authenticator.verify_and_extract(token)
if claims:
    user_id = claims.user_id  # Unique user ID (not employee_id)
    email = claims.email
    roles = claims.roles
    employee_id = claims.employee_id  # Employee ID from collector database
```

### Check if user can access resource

```python
permission = "activity:read-activities"
if JWTAuthenticator.has_permission(claims, permission):
    # User has permission
```

### Create permission from components

```python
service = "activity-service"
action = "read"
resource = "activities"
permission = f"{service}:{action}-{resource}"

if JWTAuthenticator.has_permission(claims, permission):
    # Check passed
```

### Regex permission patterns

```python
# JWT can contain regex patterns for permissions and disallows.
# Pattern syntax: if pattern starts with /, it's a regex; otherwise exact match.
# Matching uses re.match (prefix matching from start of string).

# Example: JWT has permission "/enji-db:(read|write)-.*"
# This matches "enji-db:read-roles", "enji-db:write-users", etc.

# To check if a user can read from any table:
if JWTAuthenticator.has_permission(claims, "enji-db:read-users"):
    # True if JWT permissions include the above pattern
    pass
```

## See Also

For details on the external contract with enji-auth issuer and Collector employee ID integration, see [EXTERNAL_CONTRACTS.md](./docs/EXTERNAL_CONTRACTS.md).
