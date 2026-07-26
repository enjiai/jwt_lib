# Decision 003: Stakeholder Role Bypass — Unconditional Access for Internal Use

**Date**: 2026-07-26  
**Status**: ✅ Accepted (current implementation)  
**Related issues**: JWT AI readiness audit (Wave A: cognitive-debt-adrs)

---

## Decision

**The role `"stakeholder"` grants access unconditionally, regardless of the user's actual roles.**

All three role-checking methods (`has_role`, `has_any_role`, `has_all_roles`) recognize `"stakeholder"` as a special bypass role:

- `has_role(claims, "stakeholder")` → always returns `True`
- `has_any_role(claims, [..., "stakeholder", ...])` → always returns `True`
- `has_all_roles(claims, [..., "stakeholder", ...])` → always returns `True`

This behavior is intentional and locked by tests.

---

## Context

### Current Implementation

**File**: `src/enjilib_jwt/authenticator.py`

```python
@staticmethod
def has_role(claims: JWTClaims, role: str) -> bool:
    if role == "stakeholder":
        return True
    return role in claims.roles

@staticmethod
def has_any_role(claims: JWTClaims, roles: list[str]) -> bool:
    if "stakeholder" in roles:
        return True
    return any(role in claims.roles for role in roles)

@staticmethod
def has_all_roles(claims: JWTClaims, roles: list[str]) -> bool:
    if "stakeholder" in roles:
        return True
    return all(role in claims.roles for role in roles)
```

### Evidence

1. **Code**: Three dedicated checks in `has_role`, `has_any_role`, `has_all_roles` methods (lines 121–159 in `authenticator.py`)
2. **Tests**: Comprehensive coverage in `tests/test_authz.py`:
   - `test_has_role_stakeholder_bypass_always_true` — bypass on any user with empty roles
   - `test_has_role_stakeholder_bypass_with_other_roles` — bypass even when user has roles
   - `test_has_any_role_stakeholder_bypass_always_true` — bypass when `"stakeholder"` is in the check list
   - `test_has_all_roles_stakeholder_bypass_always_true` — bypass when `"stakeholder"` is in the check list
   - `test_empty_claims_all_denied_except_stakeholder` — empty claims still grant stakeholder access

3. **Documentation**: README.md Section "Stakeholder Bypass" and API.md methods `has_role`, `has_any_role`, `has_all_roles` explicitly document this behavior.

### Rationale Status

**Product rationale unknown in-repo.** Behavior is locked by tests and appears intentional as an internal escape hatch. Commit history mentions "stakeholder full roles access" but does not explain the use case or security justification. The bypass is treated as a **current contract** that agents must respect, not a technical debt or bug.

### Use Cases (Inferred)

Based on test comments and implementation:

- **Internal stakeholder access**: Special admin or support roles that need full access without requiring explicit role assignment
- **Fallback access**: Shortcut for emergency internal access without modifying user claims
- **Testing**: Simplified test fixture for scenarios where authorization should pass

---

## Consequences

### Positive

- ✅ **Simple escape hatch**: One string match enables internal overrides without role engineering
- ✅ **Testable**: Easy to verify in unit tests with empty or arbitrary roles
- ✅ **No token modification**: Stakeholder access does not require changes to JWT claims

### Negative

- ⚠️ **Security footgun**: Callers who use `has_role(claims, "stakeholder")` or mix it with other roles in `has_any_role(claims, ["stakeholder", "..."])` may be surprised by the bypass behavior
- ⚠️ **Implicit authorization**: The bypass is not obvious from role names (unlike explicit role checks); reviewers must know the convention
- ⚠️ **No token evidence**: Checking role claims alone will not reveal who has stakeholder access; the check is code-level only

### Operational

- ✅ **No breaking**: Removing bypass would break any code that depends on it (unknown scope)
- ⚠️ **Audit gaps**: Standard role audits will not flag stakeholder access because it bypasses claims
- ✅ **Backward compatible**: Existing tokens remain valid; behavior applies at check time, not token time

---

## Alternatives Considered

### Alt 1: Remove bypass; require explicit role in claims

- **Pros**: More transparent; auditable role claims
- **Cons**: Breaking change; unknown impact on internal systems; requires finding all call sites and updating role assignments
- **Status**: Rejected — would need explicit approval and migration plan

### Alt 2: Stakeholder as a feature flag instead of hard-coded bypass

- **Pros**: Can be toggled per service; more visible
- **Cons**: Adds configuration complexity; loses simplicity
- **Status**: Out of scope — would be a separate decision

### Alt 3: Stakeholder in JWT claims but not checked in code

- **Pros**: Auditable in token; consistent with other roles
- **Cons**: Defeats the purpose of a bypass; just a normal role
- **Status**: Rejected — current implementation separates bypass logic from token data

---

## For Agents: Before You Use Stakeholder

If you are writing authorization checks or reviewing code that calls `has_role`, `has_any_role`, or `has_all_roles`:

1. **Be aware**: Checking for `"stakeholder"` will always succeed, even for users with empty roles.
2. **Document intent**: If you are checking stakeholder, add a comment explaining why (e.g., "allow internal support to override").
3. **Don't combine lightly**: Avoid mixing `"stakeholder"` in `has_any_role` or `has_all_roles` unless you specifically want the bypass; use a separate if-statement if the bypass is conditional.
4. **Test coverage**: Include a test case verifying that stakeholder access works even for users with no roles (or test for the specific scenario you need).

### If you want to change this decision:

1. **Open an issue or ADR**: Document why the change is needed and what the migration plan is
2. **Find all call sites**: Search for `has_role(.*stakeholder)` and `has_any_role.*stakeholder` to find dependent code
3. **Create a new ADR**: Link this decision and propose the replacement behavior
4. **Get approval**: This is a security-sensitive change and must be approved before implementation

---

## Related Decisions

- [001: Token payload contract](./001_token_contract_structure.md) — the `enc` field requirement
- (Future) Auditing and logging of stakeholder access

---

## Sign-off

- **Discovered**: AI readiness audit, 2026-07-15 (decision rationale missing)
- **Documented**: Wave B cognitive debt ADRs, 2026-07-26
- **Status**: Locked implementation; no change without new ADR
- **Next review**: If stakeholder bypass is used in new critical access paths, or if audit requirements change
