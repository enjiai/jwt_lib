# Decision 001: Token Payload Contract — Required `enc` Field

**Date**: 2026-07-26  
**Status**: ✅ Accepted (current implementation)  
**Related issues**: JWT AI readiness audit (Wave A: docs-token-contract, Wave B: memory-handoff)

---

## Decision

**The token payload MUST include an `enc` field containing AES-GCM encrypted sensitive claims.**

Token structure (wire format):
```json
{
  "exp": 1706569200,
  "type": "access",
  "enc": "<base64url(nonce || aesgcm(zlib(json(sensitive_claims))))>"
}
```

After `verify_and_extract`, sensitive claims are decrypted and merged into the `JWTClaims` object returned to callers.

---

## Context

### Why Separate Public and Sensitive Claims?

1. **JWT visibility**: Some platforms or proxies decode JWT headers/public payload to inspect metadata (expiry, type, etc.) without decryption.
2. **Forward compatibility**: Allows adding encrypted claims without changing the public JWT shape.
3. **Selective key exposure**: Public/private claims can use different protection levels (though this implementation uses the same secret).

### Current Implementation

- **File**: `src/enjilib_jwt/authenticator.py`, `verify_and_extract()` method
- **Contract**:
  1. Call `jwt.decode(token, secret, algorithms=["HS256"])` → get public dict
  2. **If `"enc" not in public` → return `None`** (token rejected)
  3. Call `decrypt_payload(public["enc"], secret)` → get sensitive dict
  4. Merge: `payload = {**public, **sensitive}; payload.pop("enc", None)`
  5. Return `JWTClaims.from_payload(payload)`
- **Cipher**: `src/enjilib_jwt/cipher.py` implements AES-GCM decryption with zlib compression
- **Locked by tests**: `tests/test_verify_extract.py` (74-test suite, 100% coverage)

### Rationale

This design **separates concerns**:
- **Public JWT** carries expiry, token type, and the encrypted blob reference.
- **Sensitive claims** (user_id, roles, permissions) live **inside** `enc`, decrypted on-demand.

It is **current production behavior** and enforced by all authentication paths in enji services.

---

## Consequences

### Compatibility

- ✅ **Forward**: All tokens without `enc` are rejected as invalid.
- ⚠️ **Breaking**: If `enc` is removed, all existing tokens become unparseable.
- ✅ **Backward**: Older tokens with `enc` are still valid.

### Documentation

- All token examples (README, API docs, tests, integration guides) **must** show the `enc` field.
- Callers see the **decrypted claims** (JWTClaims), not the wire format.
- Integrations must provide `enc` when creating/minting tokens (typically via `enji-auth` service).

### Changes to This Contract

Removing or making `enc` optional would be a **breaking change** requiring:
1. Deprecation plan (version bump, dual-accept period)
2. Migration guide for all enji services
3. Test suite update
4. Decision record (ADR) documenting why

### Validation

When adding new features or tests:
- Always include `enc` in test tokens
- Verify that tokens **without** `enc` are rejected
- If modifying `cipher.py` or `authenticate.py`, ensure no edge case allows `enc` to be skipped

---

## Alternatives Considered

### Alt 1: All claims encrypted
- **Pros**: Simpler contract, no public/private split
- **Cons**: Makes token inspection (e.g., expiry before decryption) impossible; breaks JWT debugging
- **Status**: Rejected — current design is more compatible

### Alt 2: `enc` field optional
- **Pros**: Backward compatible with flat-claim tokens
- **Cons**: Adds ambiguity; two code paths; tests must verify both, then deprecate one
- **Status**: Rejected — contract is simpler when `enc` is mandatory

### Alt 3: Multiple encryption schemes
- **Pros**: Allows gradual migration to stronger ciphers
- **Cons**: Adds complexity and key versioning burden
- **Status**: Out of scope — use a single well-tested cipher per decision

---

## Related Decisions

- [002: Packaging source of truth](./002_packaging_source_of_truth.md) — `pyproject.toml` as canonical metadata
- [003: Stakeholder role bypass](./003_stakeholder_role_bypass.md) — why `"stakeholder"` role bypasses all checks
- [EXTERNAL_CONTRACTS.md](../EXTERNAL_CONTRACTS.md) — External systems boundaries (enji-auth issuer, Collector employee_id integration)


---

## For Agents: Before You Change

If you are modifying token verification, encryption, or decryption:

1. **Read this decision** and confirm it matches your change.
2. **Run the full test suite**: `uv run pytest -v` (expect ≥74 tests, ≥100% coverage on cryptographic paths).
3. **If the tests fail**, stop and report — do not "fix" the contract to match your intuition.
4. **If you want to change the contract**, create a new ADR, link it here, and get explicit approval.
5. **After your change**, confirm:
   - Tokens **with** `enc` still decrypt correctly
   - Tokens **without** `enc` still get rejected
   - All tests still pass

---

## Sign-off

- **Discovered**: AI readiness audit, 2026-07-15
- **Confirmed**: Wave A remediation (docs update), 2026-07-26
- **Next review**: After any token verification or cipher logic changes
