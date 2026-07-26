# Architectural Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for `enjilib-jwt-auth`. Each ADR documents a significant design choice, its rationale, consequences, and guidance for future maintainers and contributors.

## Format

Each ADR follows this structure:

```markdown
# Decision NNN: <Title>

**Date**: YYYY-MM-DD
**Status**: One of: Proposed | Accepted | Deprecated | Superseded

## Decision
[1-2 sentence summary of what was decided]

## Context
[Why this decision was needed; background and constraints]

## Consequences
[What happened as a result; positive and negative impacts]

## Alternatives Considered
[What else was considered and why it was rejected]

## Related Decisions
[Links to related ADRs]

## For Agents: Before You Change
[Specific guidance for future implementers]
```

### Status Legend

- **Proposed**: Decision has been made but not yet implemented
- **Accepted**: Decision is implemented and current production behavior
- **Deprecated**: Decision was once accepted but is no longer in effect (superceded by a newer decision)
- **Superseded**: This decision was replaced by a newer ADR

---

## Decisions

| # | Title | Date | Status | Summary |
|---|-------|------|--------|---------|
| [001](./001_token_contract_structure.md) | Token Payload Contract — Required `enc` Field | 2026-07-26 | ✅ Accepted | Token payload **must** include encrypted `enc` field with sensitive claims; flat-claim tokens are rejected |
| [002](./002_packaging_source_of_truth.md) | Packaging Source of Truth — `pyproject.toml` as Canonical | 2026-07-26 | 🔄 Proposed | `pyproject.toml` is the authoritative source for package metadata; `setup.py` is a compatibility shim |
| [003](./003_stakeholder_role_bypass.md) | Stakeholder Role Bypass — Unconditional Access for Internal Use | 2026-07-26 | ✅ Accepted | Role `"stakeholder"` grants access unconditionally in all role-checking methods (footgun: bypass mechanism) |
| [004](./004_permission_matching_semantics.md) | Permission Matching Semantics — Regex Prefix Matching with Disallow Precedence | 2026-07-26 | ✅ Accepted | Permissions use `re.match` prefix matching (not full); slash-prefixed patterns are regex; disallow overrides allow |

---

## Quick Reference for Developers

### Adding a New Decision

1. Pick the next free number (e.g., 005)
2. Copy the template above into `00N_title_with_underscores.md`
3. Fill in all sections
4. Add a row to the table above
5. If it affects production code, create a test case that validates the decision (see each ADR's evidence section)

### Related Topics

- **Token verification**: See [Decision 001](./001_token_contract_structure.md)
- **Role checking and stakeholder bypass**: See [Decision 003](./003_stakeholder_role_bypass.md)
- **Permission checking and pattern matching**: See [Decision 004](./004_permission_matching_semantics.md)
- **Package metadata and releases**: See [Decision 002](./002_packaging_source_of_truth.md)

### Common Questions

**Q: Can I change how permissions are matched?**  
A: Not without a breaking change. See [Decision 004](./004_permission_matching_semantics.md) "If you want to change matching semantics" section.

**Q: What does "stakeholder" do?**  
A: It's a special role that always grants access. See [Decision 003](./003_stakeholder_role_bypass.md). Use with caution.

**Q: Which file should I edit for package metadata?**  
A: `pyproject.toml`. See [Decision 002](./002_packaging_source_of_truth.md).

**Q: Can a permission match multiple patterns?**  
A: Yes. Disallow patterns are checked first; if any match, access is denied. Otherwise, allow patterns are checked. See [Decision 004](./004_permission_matching_semantics.md).

---

## History

- **2026-07-26**: Wave B cognitive debt remediation — added ADRs 003 and 004, created this index
- **2026-07-26**: Wave A documentation update — ADRs 001 and 002 finalized
- **2026-07-15**: AI readiness audit discovered decision rationale gaps

---

## Next Steps

After reviewing these ADRs:

1. **Understand the current decisions** by reading each one
2. **Link these in handoff documentation** (plan 05 will update `docs/handoff.md`)
3. **If you discover a new decision needed**, create a new ADR and add it to the table above
4. **Before changing any of these decisions**, create a **new** ADR documenting the change and why, then get explicit approval

---

For questions or discussions about these decisions, see [docs/EXTERNAL_CONTRACTS.md](../EXTERNAL_CONTRACTS.md) for maintainer contact info.
