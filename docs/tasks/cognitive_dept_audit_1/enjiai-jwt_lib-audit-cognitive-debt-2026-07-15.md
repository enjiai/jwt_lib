# Cognitive Debt Audit

## Executive Summary

- No: a future human or AI agent can recover the broad purpose of this JWT library, but cannot recover current constraints, rationale, and proven behavior safely without guessing.
- Score: 27/100, severity bad, confidence medium.
- Strongest positive signal: README.md and API.md identify the package as JWT authentication utilities for Enji microservices and describe the basic permission model.
- Most important gap: the current encrypted-token contract and stakeholder role shortcut live in code while the public docs describe older or contradictory behavior.
- Next practical action: document the token contract and add focused pytest specs for token extraction, encrypted claims, permission matching, disallow precedence, and role helpers.

## Audit Target

- Repository: `enjiai/jwt_lib`
- Default branch: [`main`](https://github.com/enjiai/jwt_lib/tree/main)
- Audited commit: [`93d861b22ac56871284f63e88020c72d4d8eb096`](https://github.com/enjiai/jwt_lib/commit/93d861b22ac56871284f63e88020c72d4d8eb096)
- Revision confidence: default branch metadata was available. The local history view was shallow, but the complete 10-commit repository history was enumerated through repository metadata.

## What Was Checked

- Repository documentation and specs: README.md and API.md.
- Source behavior that carries intent: `src/enjilib_jwt/authenticator.py`, `src/enjilib_jwt/cipher.py`, and package entry points.
- Executable intent: pytest configuration, `tests/`, usage examples, and code docstrings.
- Product-context discoverability: entry points, links between docs, external references, and orphaned intent artifacts.
- Agent context: root-level agent instructions, safe-change guidance, and linked domain intent.
- Repository metadata: issues, pull requests, labels, tags, releases, and commit-message history.
- External context coverage: enji-auth and collector-db are named by the repository, but no linked authoritative contract was available to inspect.

## Findings

### Main Answer

> [!CAUTION]
> **Audit question:** can a future human or AI agent recover what the system is for, which constraints matter, why important decisions were made, and how expected behavior is proven without guessing?
>
> No. The broad goal is recoverable, but current behavior is not safely recoverable without guessing because the encrypted-token contract, role shortcut, identity-field meaning, dependency requirements, and executable proof are missing, stale, or contradictory. The score is 27/100 with medium confidence.

### Current State

The repository is a small Python JWT authentication library. Its visible product goal is local JWT verification for Enji microservices, including roles, permissions, disallows, and identity claims. That intent is only partially preserved. The highest-risk behavior now depends on an `enc` encrypted-claims field, but README.md and API.md still show plain token structures. There are no tests proving the intended contract, and there is no issue, pull request, ADR, or agent-facing guidance to explain why key choices were made.

### Intent Map

Visible goals:

- Provide JWT authentication utilities for Enji microservices.
- Verify tokens locally without external calls to enji-auth.
- Extract identity, roles, permissions, disallows, and `employee_id` claims.

Visible constraints:

- Tokens are signed with a shared secret key and default HS256 algorithm.
- Current code requires a public `enc` claim and returns `None` when it is absent.
- Encrypted sensitive claims use HKDF-SHA256, AES-GCM, a 12-byte nonce, zlib decompression, and base64url decoding.
- Runtime package metadata is expected to include PyJWT and cryptography.

Visible domain rules:

- Disallow permission patterns take precedence over allow permission patterns.
- Permission entries may be exact strings or regex-like patterns prefixed with `/`.
- The role helpers include a stakeholder shortcut in code, but this is not explained in the docs.
- API.md gives conflicting guidance on whether `user_id` represents an employee ID.

Decision rationale is mostly missing. Terse commit messages show that disallows, stakeholder handling, cipher support, zlib, and build cleanup were added over time, but they do not explain trade-offs, expected compatibility, or owner intent.

### Product Context Path

The starting point is README.md. It gives a usable high-level description, but it does not link to API.md, which is the closest thing to a detailed spec. A reader must browse the file tree to find API.md, then inspect `authenticator.py` and `cipher.py` to recover current encrypted-token behavior. The external systems that matter most, enji-auth and collector-db, are named but not linked to an owner, contract, schema, or access path.

### Executable Intent

Executable intent is the weakest area. README.md tells users to run `pytest`, and pytest.ini points at `tests/`, but `tests/` contains only an empty `__init__.py`. No runnable spec proves:

- valid and invalid token verification;
- missing `enc` behavior;
- encrypted claim extraction;
- permission disallow precedence;
- exact and regex permission matching;
- stakeholder role behavior;
- `user_id` and `employee_id` handling.

The code and docstrings describe some of these behaviors, but prose and implementation are not a substitute for executable proof.

### Understanding Recovery

A newcomer can recover the broad purpose quickly because the repository is small and README.md is clear enough at the top level. Recovery becomes brittle after that. The reader must manually discover API.md, reconcile API.md with code, infer external issuer behavior from `cipher.py`, and decide whether contradictions are stale docs or intended current behavior. AI agents have the same problem, plus no AGENTS.md or similar file to identify safe-change boundaries.

### Alignment Findings

- Aligned: API.md describes disallow precedence, and `has_permission` checks disallows before allows.
- Mismatch: README.md and API.md show plain token claims, while `verify_and_extract` requires `enc` and decrypts sensitive claims.
- Mismatch: README.md and API.md document normal role checks, while all role helpers include a stakeholder shortcut in code.
- Mismatch: API.md says `user_id` is not an employee ID, then later labels `claims.user_id` as Employee ID.
- Mismatch: API.md shows inconsistent slash conventions for regex permissions.
- Mismatch: pyproject.toml includes the cryptography dependency required by `cipher.py`, while setup.py and committed egg-info metadata omit it.
- Unknown: enji-auth and collector-db are named but not linked, so their authoritative contract could not be checked.

### Scorecard

| Criterion | Score (0-10) | Status | What affected the score |
|-----------|--------------|--------|-------------------------|
| Goals and constraints | 4 | ⚠️ | README.md and API.md state the library purpose and basic permission model; encrypted claims, stakeholder behavior, and some constraints are scattered, code-only, or contradictory. |
| Proven behavior | 2 | ❌ | pytest.ini and README.md show an intent to test behavior; the configured test tree has no executable specs for token verification, encryption handling, or authorization rules. |
| Knowledge recovery | 4 | ⚠️ | The repository is small enough to inspect end to end; API.md is unlinked, current token behavior lives in source files, and there is no issue, PR, ADR, or onboarding trail. |
| Agent context | 0 | ❌ | Ordinary repository browsing is possible; no AGENTS.md, copilot instructions, or safe-change entry point explains domain intent or token-contract boundaries. |
| Evidence alignment | 2 | ❌ | Disallow precedence is consistent between API.md and code; docs, implementation, and package metadata otherwise disagree on token structure, role behavior, identity fields, regex notation, and dependencies. |

### Score Calculation

Score 27/100 because the docs preserve the broad product goal, but the current token contract, behavioral proof, agent context, and alignment are too weak for safe recovery. In numbers: goals and constraints `4 * 25`, proven behavior `2 * 20`, knowledge recovery `4 * 20`, agent context `0 * 10`, and evidence alignment `2 * 25` equals 270 weighted points out of 1000, divided by 10 for a final 27/100. No cap was applied.

### Confidence

Confidence is medium. The repository is small, default branch metadata was available, and the accessible evidence was enough to identify strong doc/code/test alignment problems. Confidence is limited because there are no executable tests, issues, pull requests, ADRs, releases, tags, or linked external contracts for enji-auth and collector-db. Those external systems were treated as coverage limits, not as hidden negative evidence.

## Evidence

- README.md states the broad package goal, shows usage examples, and documents a plain token structure.
- API.md provides the closest detailed reference, including permission rules, claim fields, and examples, but it is not linked from README.md and contradicts itself on identity fields.
- `src/enjilib_jwt/authenticator.py` implements `verify_and_extract`, permission checks, disallow precedence, and stakeholder role behavior.
- `src/enjilib_jwt/cipher.py` defines the encrypted-claim protocol using HKDF-SHA256, AES-GCM, zlib, nonce handling, and base64url decoding.
- pytest.ini points at `tests/`, while `tests/` contains no behavior tests.
- pyproject.toml declares cryptography, but setup.py and committed egg-info metadata do not.
- Repository metadata showed no issues, pull requests, releases, tags, or custom workflow labels to explain decisions.

## Limitations

- This was a read-only audit of accessible repository evidence and repository metadata.
- No dependencies were installed and no tests, builds, package-manager commands, or project scripts were run.
- The repository has no runnable tests, so behavior proof was assessed from the absence of specs and from prose/code evidence.
- External enji-auth and collector-db contracts were not linked from the repository, so they could not be inspected directly.
- The shallow local history view limits local Git archaeology, although the complete 10-commit repository history was available through repository metadata.

## Improvement Checklist

- [ ] Document the encrypted token contract in README.md or API.md. Explain public claims, encrypted sensitive claims, the required `enc` field, enji-auth issuer expectations, and the cipher parameters; completion signal: docs no longer present a plain-only token structure as current.
- [ ] Add focused pytest specs under `tests/` for `JWTClaims.from_payload`, valid and invalid token extraction, missing `enc`, encrypted payload round-trip, exact and regex permissions, disallow precedence, and stakeholder role behavior; completion signal: changing those rules breaks tests.
- [ ] Record the stakeholder role shortcut as a small ADR or API.md note. Explain whether it is a public-access shortcut, why it exists, and which helper behavior must be preserved; completion signal: code, docs, and tests state the same rule.
- [ ] Link API.md from README.md and reconcile identity and regex guidance. Fix the `user_id` versus `employee_id` conflict and one regex permission notation; completion signal: a reader can find one authoritative claim and permission reference from README.md.
- [ ] Add AGENTS.md at the repository root. Point agents to README.md and API.md, name the enji-auth token boundary, and list safe-change checks for token verification, encrypted claims, roles, and permission matching; completion signal: an agent has a single safe-change entry point.
- [ ] Add a repository-side bridge for enji-auth and collector-db. Name the owner, access path, or authoritative contract location for token signing, encrypted claims, and `employee_id` without copying private content; completion signal: maintainers know what external contract to verify before changing shared token behavior.
- [ ] Align package metadata around cryptography. Make one packaging source authoritative and ensure generated or maintained runtime dependency metadata includes cryptography; completion signal: pyproject.toml, setup.py if retained, and committed metadata no longer disagree.
