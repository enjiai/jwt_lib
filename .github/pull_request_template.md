<!-- 
⚠️ IMPORTANT: This is an authentication library — token compatibility is critical.
Mandatory disclosure: token contract impact and package metadata changes.
-->

## Summary
<!-- Brief description of the changes in this PR. What problem does it solve or what feature does it add? -->

## Type of Change
<!-- Mark the relevant option(s) with an "x" -->
- [ ] Bugfix (backwards compatible)
- [ ] Feature (backwards compatible)
- [ ] Feature (breaking change)
- [ ] Refactor (no functional change)
- [ ] Documentation update
- [ ] Test improvement

## Token Contract Impact 🔐 (MANDATORY)
**Does this PR change token shape, encryption, decryption, verification logic, or authorization behavior?**
- [ ] **None** — this PR does not touch the token contract or verification logic
- [ ] **Minor** — this PR modifies non-critical fields or adds optional behavior (backwards compatible)
- [ ] **Breaking** — this PR changes how tokens are verified, encrypted, or structured (not backwards compatible)

<!-- If "Minor" or "Breaking": explain the impact below with examples -->

### Explanation (required if not "None"):
<!-- 
Describe:
- How the token contract changes (e.g., "Adds optional 'sub_claim' field to enc payload")
- Whether existing tokens can still be verified (e.g., "Existing tokens remain valid; new code is additive")
- Any migration path needed (e.g., "Clients must re-encrypt tokens after upgrade")
- Links to related issues or decision records
-->

## Package Metadata Changes 📦 (MANDATORY)
**Does this PR change package dependencies, `py.typed` marker, version numbers, or install source?**
- [ ] No — no package metadata changes
- [ ] Yes — see explanation below

### Explanation (required if "Yes"):
<!-- 
Describe:
- New/removed/updated dependencies and why
- Changes to pyproject.toml, setup.py, or py.typed marker
- Any implications for consumers (e.g., new minimum Python version)
-->

## Testing & Verification
<!-- How have you tested this change? -->
- [ ] Added or updated unit tests
- [ ] Tested encrypted-token verification (if applicable)
- [ ] Verified role and permission logic (if applicable)
- [ ] Ran `pytest tests/` locally — all tests pass
- [ ] Tested with example token from API.md documentation

## Documentation Updates
- [ ] Updated README.md if behavior changed
- [ ] Updated API.md with new or changed signatures
- [ ] Added docstrings to new functions/classes
- [ ] Updated CHANGELOG.md (if applicable)

## Checklist
- [ ] My code follows the project style guide
- [ ] I have performed a self-review of my own code
- [ ] I have commented complex logic, especially around token verification
- [ ] I have checked for security implications (e.g., encryption strength, key handling)
- [ ] I have verified backwards compatibility (or documented breaking changes)
- [ ] I have read and understood the Token Compatibility and Packaging sections above
