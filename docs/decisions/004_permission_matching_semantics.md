# Decision 004: Permission Matching Semantics — Regex Prefix Matching with Disallow Precedence

**Date**: 2026-07-26  
**Status**: ✅ Accepted (current implementation)  
**Related issues**: JWT AI readiness audit (Wave A: cognitive-debt-adrs)

---

## Decision

**Permission matching uses `re.match` prefix semantics with disallow list precedence.**

### Matching Logic

1. **Permission format**: Patterns can be exact matches (`"admin"`) or regex patterns prefixed with `/` (`"/admin.*"`)
2. **Slash handling**: A leading `/` is stripped before regex compilation, allowing clean regex syntax
3. **Matching method**: `re.match()` is used, which matches from the **start** of the string (prefix semantics)
4. **Non-slash patterns**: Still treated as regex (e.g., `"admin"` becomes the regex `admin`, matching `admin`, `admin.x`, `admin-y`)
5. **Disallow precedence**: If permission matches any pattern in `disallows`, return `False` immediately, even if it also matches an allow pattern

### Current Implementation

**File**: `src/enjilib_jwt/authenticator.py`, lines 62–195

```python
@staticmethod
def _match_permission(permission: str, pattern: str) -> bool:
    try:
        if pattern.startswith("/"):
            regex_pattern = pattern[1:]
        else:
            regex_pattern = pattern
        return bool(re.match(regex_pattern, permission))
    except re.error:
        return False

@staticmethod
def has_permission(claims: JWTClaims, permission: str) -> bool:
    # First check if permission is in disallows list
    if JWTAuthenticator._check_permission_list(permission, claims.disallows):
        return False

    # Then check if permission is in allowed list
    return JWTAuthenticator._check_permission_list(permission, claims.permissions)
```

---

## Context

### Problem It Solves

Authorization needs flexible pattern matching:

- **Exact service permissions**: `"admin:delete-users"` (one specific action)
- **Prefix/wildcard**: `"admin.*"` or `/admin:(read|write)-.*$` (multiple actions)
- **Exceptions**: Disallow specific dangerous actions while allowing a broader pattern

### Examples

**Scenario 1: Prefix match with re.match**

```
Pattern: "admin"
Permission checked: "admin.users"
Match: True (re.match("admin", "admin.users") succeeds)

Pattern: "admin"
Permission checked: "user.admin"
Match: False (re.match("admin", "user.admin") fails — doesn't start with "admin")
```

**Scenario 2: Regex with `/` prefix**

```
Pattern: "/admin:(read|write)-.*"
Permission checked: "admin:read-users"
Match: True

Pattern: "/admin:(read|write)-.*"
Permission checked: "admin:delete-users"
Match: False (not read/write)
```

**Scenario 3: Disallow precedence**

```
permissions = ["/.*"]  # Allow everything
disallows = ["admin:delete"]  # Except this

has_permission(claims, "admin:read"): True
has_permission(claims, "admin:delete"): False (disallow matched first)
```

### Evidence

1. **Code**:
   - `_match_permission()` method (lines 62–84): implements slash strip + `re.match`
   - `has_permission()` method (lines 160–195): checks disallows first, then allows
   - `_check_permission_list()` helper (lines 86–103): iterates patterns and calls `_match_permission`

2. **Tests** in `tests/test_authz.py`:
   - `test_has_permission_exact_allow_true` — exact matches work
   - `test_has_permission_regex_allows_matching_permission` — regex patterns with `/` work
   - `test_has_permission_prefix_matching_with_rematch` — `re.match` prefix semantics verified:
     - `"admin"` matches `"admin"`, `"admin.extra"`, `"admin-something"`
     - `"admin"` does NOT match `"not-admin"`
   - `test_has_permission_wildcard_allows_arbitrary` — `/.*` matches anything
   - `test_has_permission_disallow_blocks_even_when_allowed` — disallow takes precedence
   - `test_has_permission_disallow_regex_overrides_allow_regex` — both allow and disallow can be regex
   - `test_has_permission_invalid_regex_treated_as_non_match` — invalid regex does not raise exception

3. **Documentation**:
   - README.md: "All patterns are matched using `re.match`, which matches from the beginning of the string (prefix semantics)"
   - API.md: Detailed "Permission Resolution Logic" section explaining disallow precedence and matching

### Rationale

- **Prefix matching**: `re.match()` is simpler than `re.fullmatch()` for common patterns; enables shorthand like `"admin"` to match admin-scoped actions
- **Slash prefix**: Disambiguates regex from literal patterns (e.g., `/admin-\d+/` is regex; `"admin-123"` is literal/regex hybrid)
- **Disallow first**: Follows principle of "deny by default"; explicit denials override broad allows
- **Invalid regex resilience**: Silently ignores regex errors instead of raising exceptions, allowing safe partial pattern deployments

---

## Consequences

### Positive

- ✅ **Flexible**: Supports exact, prefix, regex, and wildcard patterns
- ✅ **Simple syntax**: No special DSL; standard regex notation with optional `/` prefix
- ✅ **Intuitive precedence**: Deny overrides allow (standard security principle)
- ✅ **Fault-tolerant**: Invalid regex doesn't crash; treated as non-match

### Negative

- ⚠️ **Surprising prefix semantics**: `"admin"` matches `"admin.users"`; not a full match. Can lead to overly permissive matches if not careful
- ⚠️ **Regex liability**: Users must understand regex; typos like `"admin-.*$"` (missing `/`) will not compile as regex
- ⚠️ **Non-intuitive escaping**: Dots in permission names need escaping in regex (e.g., `"/enji\\.db:.*"` if pattern needs to match literal dots)
- ⚠️ **Silent failures**: Invalid regex is silently ignored; may hide permission bugs in production

### Operational

- ✅ **No token structure change**: Patterns live in JWT claims; matching happens at check time
- ✅ **Backward compatible**: Existing patterns (all tests passing) continue to work
- ⚠️ **Audit complexity**: Auditing requires understanding regex; cannot just list permission strings

---

## Alternatives Considered

### Alt 1: Use `re.fullmatch()` instead of `re.match()`

- **Pros**: Full string match; no surprise prefix behavior; `"admin"` matches only `"admin"`, not `"admin.users"`
- **Cons**: Requires explicit `.*` for wildcards; changes semantics for all existing patterns
- **Status**: Rejected — breaking change; all existing tokens and patterns would behave differently

### Alt 2: Disallow separate list (Alt: combined allow/deny with markers)

- **Pros**: Single list; no precedence confusion
- **Cons**: More complex pattern format (e.g., `"+admin"` vs `"-admin"`); two-list model is clearer
- **Status**: Rejected — current model is standard (Unix file permissions, firewall rules, etc.)

### Alt 3: No regex support; only exact matching

- **Pros**: Simpler; no regex liability
- **Cons**: Explodes token size for users with many permissions; less flexible
- **Status**: Rejected — regex enables compact permission lists

### Alt 4: Glob patterns instead of regex

- **Pros**: Simpler for non-regex users (e.g., `"admin*"`)
- **Cons**: Still requires escaping; not standard in Python; adds library dependency
- **Status**: Out of scope — regex is already available

---

## For Agents: Before You Use or Add Permissions

If you are adding permissions to JWT claims or checking permissions in code:

### Writing Patterns

1. **Exact match**: Use plain string, e.g., `"activity:read-activities"`
2. **Prefix match**: Use plain string without `/`, e.g., `"admin"` (matches `admin`, `admin.x`, `admin-y`)
3. **Regex**: Use `/` prefix, e.g., `/activity:(read|write)-.*$/`
4. **Escape dots**: If pattern needs to match literal dots, escape them: `/enji\.db:.*/`

### Permission Checking

1. **Understand precedence**: Disallow is checked **before** allow
2. **Test broadly**: Include tests for edge cases (prefix matches, regex special chars)
3. **Document intent**: Add comments explaining why a pattern is needed

### Common Pitfalls

- ❌ **Forgot the `/`**: `"admin.*"` matches `"admin"`, not regex; use `"/admin.*/"`
- ❌ **Dot not escaped**: `/admin.users/` matches `admin`, `admindusers` (dot is wildcard); use `/admin\.users/`
- ❌ **Overly broad disallow**: `/.*` in disallows blocks everything; use specific patterns
- ❌ **Order matters (in tests)**: If you accidentally add to both allow and disallow, disallow wins

### If you want to change matching semantics:

1. **Understand the impact**: All existing JWT tokens use current semantics
2. **Create a new ADR**: Document the new matching rules
3. **Plan migration**: Tokens with old patterns must be re-issued or re-validated
4. **Test thoroughly**: Write tests for old and new behavior during transition period
5. **Get approval**: This is a breaking change for any service checking permissions

---

## Related Decisions

- [001: Token payload contract](./001_token_contract_structure.md) — how permissions are stored in JWT
- (Future) Permission versioning or schema migration (if matching semantics ever change)

---

## Sign-off

- **Discovered**: AI readiness audit, 2026-07-15 (semantics not explicitly documented)
- **Documented**: Wave B cognitive debt ADRs, 2026-07-26
- **Status**: Locked implementation; all existing patterns and permissions rely on current semantics
- **Next review**: If permission matching is added to new services, or if audit requirements mandate different semantics (e.g., no regex, glob-only)
