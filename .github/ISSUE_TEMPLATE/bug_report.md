---
name: Bug Report
about: Report a bug in enjilib-jwt-auth (authentication library)
title: "[BUG] "
labels: bug
assignees: ""
---

<!-- 
⚠️ IMPORTANT: This is an authentication library — token compatibility is critical.
Please take extra care to describe how this bug affects token shape, verification, or security.
-->

## Summary
<!-- Clear, concise description of the bug. -->

## Steps to Reproduce
1.
2.
3.

## Expected Behavior
<!-- What should happen? -->

## Actual Behavior
<!-- What actually happens? Include error messages or logs. -->

## Environment
- **Python version:** (e.g., 3.10, 3.11)
- **enjilib-jwt-auth version:** (e.g., 0.1.0)
- **Installation method:** (e.g., pip, git+https)
- **OS:** (e.g., macOS, Linux, Windows)

## Token Compatibility Impact ⚠️
**Does this bug affect token shape, encryption, decryption, or verification logic?**
- [ ] Yes — this bug breaks token verification or changes how tokens are structured/encrypted
- [ ] No — this bug does not affect the token contract
- [ ] Unknown — I'm not sure; please advise

<!-- If "Yes": describe the impact (e.g., "Tokens encrypted with the old code cannot be decrypted by the new code") -->

## Additional Context
<!-- Any other context, logs, or minimal reproducible example? -->

## Checklist
- [ ] I have read the API.md and understand the expected token shape with `enc` field
- [ ] I have reproduced this bug locally
- [ ] I have checked if this is a duplicate of an existing issue
