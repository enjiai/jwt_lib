# Security Policy

### Disclosure Timeline

We follow a responsible disclosure policy:

1. **Initial acknowledgment**: Within 24 hours of report
2. **Assessment and fix development**: 7-14 days (depending on severity)
3. **CVE assignment** (if applicable): Coordinated with relevant authorities
4. **Public disclosure**: 30-90 days after initial report, or upon release of fix (whichever is earlier)

**High-severity vulnerabilities** may be expedited (fixed and released within 24-48 hours).

## Supported Versions

**Only the latest version receives security updates.**

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes (current) |
| < 0.1.0 | ❌ No |

Consumers are strongly encouraged to upgrade to the latest version promptly.

## Known Limitations & Security Assumptions

### Key Material Handling

- **Key material is held in memory** — the JWT secret key is not encrypted at rest within this library. Assume any Python process with access to the authenticator object has access to the secret key.
- **Recommendation**: Store secrets in secure vaults (e.g., HashiCorp Vault, AWS Secrets Manager) and load them into environment variables or configuration services at runtime.

### HMAC Key Strength

- **HMAC keys must be at least 32 bytes** (256 bits) when using SHA256 (the default algorithm).
- Shorter keys may provide insufficient entropy and weaken the authentication guarantee.
- **Recommendation**: Generate keys using `secrets.token_bytes(32)` or equivalent cryptographically secure random source.

### Token Expiration

- This library validates the `exp` (expiration) claim against the current system clock.
- **Clock skew**: Ensure your systems have synchronized clocks (NTP recommended).
- Tokens without an `exp` claim or with a missing `exp` claim will fail verification.

### Regular Expression in Permissions

- Permission checks support regex patterns (see API.md).
- **Be careful with regex complexity** — overly complex patterns may cause ReDoS (Regular Expression Denial of Service) attacks.
- **Recommendation**: Keep permission regex patterns simple and well-tested.

### No Rate Limiting in Library

- This library does not implement rate limiting.
- Rate limiting should be implemented at the service/API gateway level to prevent brute-force token verification attacks.

### No Audit Logging in Library

- This library does not log authentication events.
- Services using this library should implement their own audit logging for compliance and security monitoring.

## Testing Security

### Running Tests with Coverage

Ensure all token verification and cryptographic operations are covered:

```bash
pytest tests/ --cov=enjilib_jwt --cov-report=term-missing --cov-fail-under=100
```

The project enforces **100% code coverage**, meaning all code paths—including error cases and edge cases in encryption/decryption—are tested.

### Checking for Timing Attacks

Token verification operations should be constant-time to prevent timing-based attacks. This library uses PyJWT's secure comparison for signatures. Verify:

- [ ] All token verification uses `==` operator (never `!=` with early exit)
- [ ] Permission/role checks use `in` operator consistently
- [ ] No early returns based on sensitive data

### Test Existing Tokens

Always test with example tokens from [API.md](./API.md):

```python
from enjilib_jwt import JWTAuthenticator

authenticator = JWTAuthenticator(secret_key="your-secret-key")

# Example token (from API.md documentation)
token = "eyJ0eXAiOiJKV1QiLCJhbGc..."

claims = authenticator.verify_and_extract(token)
assert claims is not None
```

## Security Contact

For non-vulnerability security inquiries:
- Email: security@enjiai.org
- Check: https://enjiai.org/security (if applicable)

---

Last updated: 2026-07-26
