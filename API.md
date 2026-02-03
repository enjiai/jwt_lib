# enjilib-jwt-auth API Reference

JWT authentication library for Enji microservices. Provides local token verification and claims extraction without external API calls.

## Token Structure

Tokens issued by enji-auth contain the following claims:

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
  "employee_id": 321
}
```

### Claim Fields

| Field         | Type      | Description                                                        |
| ------------- | --------- | ------------------------------------------------------------------ |
| `sub`         | string    | User email address                                                 |
| `user_id`     | int       | Unique user ID (NOT AN employee ID, DONT USE IT AS AN employee_id) |
| `type`        | string    | Token type (e.g., "access")                                        |
| `exp`         | int       | Unix timestamp of expiration                                       |
| `rand_str`    | string    | Random UUID for token uniqueness                                   |
| `roles`       | list[str] | User roles (e.g., ["admin", "editor"])                             |
| `permissions` | list[str] | User permissions (exact match or regex patterns)                   |
| `employee_id` | int       | Employee ID from collector db                                      |

## Core Classes

### JWTClaims

Data class holding extracted token claims.

```python
from enjilib_jwt import JWTClaims

@dataclass
class JWTClaims:
    user_id: int              # Special id from enji-auth (not employee_id)
    email: str                # User email (from "sub" claim)
    roles: list[str]          # User roles
    permissions: list[str]    # User permissions
    employee_id: int          # Employee id from collector db
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

**Returns:** `JWTClaims` if valid, `None` if invalid

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

**Example:**

```python
if JWTAuthenticator.has_role(claims, "admin"):
    # Grant admin access
```

### has_any_role(claims: JWTClaims, roles: list[str]) -> bool

Check if user has any of the specified roles.

**Example:**

```python
if JWTAuthenticator.has_any_role(claims, ["admin", "moderator"]):
    # Grant special access
```

### has_all_roles(claims: JWTClaims, roles: list[str]) -> bool

Check if user has all specified roles.

**Example:**

```python
if JWTAuthenticator.has_all_roles(claims, ["editor", "publisher"]):
    # Both roles required
```

### has_permission(claims: JWTClaims, permission: str) -> bool

Check if user has specific permission using regex pattern matching.

**Permission Format:**

- Exact match: `"service:action-resource"`
- Regex pattern: `/service:(action1|action2)-resource$/`
- Wildcard: `/.*`

**Example:**

```python
# Exact permission check
if JWTAuthenticator.has_permission(claims, "activity:read-activities"):
    # User can read activities

# JWT permissions can be patterns that match multiple permissions
# If JWT contains: "/activity:(read|write)-.*"
# Then this returns True:
if JWTAuthenticator.has_permission(claims, "activity:read-activities"):
    # Matches the regex pattern in JWT
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

1. **Token Verification is Local** - No HTTP calls to enji-auth needed
2. **Permission Matching** - Uses regex patterns; permissions in JWT can be patterns that match multiple specific permissions
3. **Claims Structure** - Always check that `verify_and_extract()` returns non-None before accessing claims
4. **Security** - Keep `secret_key` secure and never expose it

## Common Patterns

### Extract user info without permissions check

```python
claims = authenticator.verify_and_extract(token)
if claims:
    user_id = claims.user_id  # Employee ID
    email = claims.email
    roles = claims.roles
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
