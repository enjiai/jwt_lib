# AI readiness audit remediation — orchestration

## Audit review (vs local code, 2026-07-26)

Source audit: [`enjiai-jwt_lib-audit-ai-readiness-2026-07-15.md`](./enjiai-jwt_lib-audit-ai-readiness-2026-07-15.md) against commit `93d861b`.

| Audit claim | Local verification | Verdict |
|---|---|---|
| Score 21/100 — agents can orient but cannot ship safely | Still accurate for **agent process / docs / handoff**; machine checks improved | Partially outdated |
| Empty `tests/` behind documented `pytest` | **Superseded**: suite from `docs/tasks/test_audit_1/` — **74 passed**, coverage gate 100%, CI workflow present (uncommitted as of review) | Was correct; treat Urgent item as **done / out of scope** here |
| Token docs omit required `enc` | Confirmed: `README.md` + `API.md` still show flat claims; `verify_and_extract` requires `enc` | Still correct |
| Install docs point to `your-org/enji-agent` | Confirmed; remote is `enjiai/jwt_lib` | Still correct |
| `py.typed` declared in `pyproject.toml` but missing on disk | Confirmed: no `src/enjilib_jwt/py.typed` | Still correct |
| Dual packaging / egg-info drift | `cryptography` now in `setup.py` + egg-info requires; egg-info still committed; no `.gitignore` | Partially fixed |
| No `AGENTS.md` / skills / handoff | Confirmed | Still correct |
| No issue/PR templates, CONTRIBUTING/SECURITY/CHANGELOG, decisions | Confirmed (only `.github/workflows/test.yml`) | Still correct |

### Extra findings from code review (include in plans)

1. **`stakeholder` role bypass** — `has_role` / `has_any_role` / `has_all_roles` short-circuit to `True` when checking `stakeholder`; undocumented in README/API (tests already pin it).
2. **`API.md` Common Patterns** still labels `user_id` as “Employee ID” while the claims table says the opposite.
3. **Permission matching** uses `re.match` (prefix) and treats non-`/` strings as regex — security-sensitive contract; document as-is, do **not** “fix” in this remediation unless a separate security task says so.
4. **Bare `except Exception`** in `verify_and_extract` → any decrypt/claims failure becomes `None`; document in AGENTS as intentional contract locked by tests.
5. **Nested repo**: commits/PRs belong in `be/shared/enjilib-jwt-auth/.git` (`enjiai/jwt_lib`), not monorepo root.

### Audit quality note

The audit was **right for its snapshot** (read-only, empty tests, no agent entrypoint). Priority order is still sound. Re-score after this remediation: expect a large jump on machine checks / quality gates (already from test work) and on context/cross-agent once Wave A–B land; planning/memory will move from 0 only after templates + handoff exist.

## Goal

Close remaining AI-readiness gaps so an agent can change this auth library with: one entrypoint, one token/packaging contract, process templates, and durable handoff — **without** redoing the test suite.

## Parallel execution model

```
Prerequisite (human/orchestrator, not a code agent)
  └── Confirm test_audit_1 green: `uv run pytest -v` exits 0 (≈74 tests)
      If red → finish docs/tasks/test_audit_1/ first; do not start these plans.

Wave A (up to 2 agents, PARALLEL — disjoint file ownership)
  ├── 01_docs_token_contract.md
  └── 02_packaging_hygiene.md

Wave B (up to 4 agents, PARALLEL — after Wave A green)
  ├── 03_agents_entrypoint.md
  ├── 04_github_templates.md
  ├── 05_process_docs.md
  └── 06_memory_handoff.md
```

**Why this split:** Wave A removes doc/packaging drift that AGENTS and process docs must cite. Wave B files never share ownership, so four agents can run without merge conflicts.

## How to launch subagents

1. Orchestrator verifies pytest green (and preferably commits/finishes `test_audit_1` work first).
2. Launch **two** agents in parallel on Wave A (`01`, `02`).
3. After both report done, launch **four** agents in parallel on Wave B (`03`–`06`).
4. Each agent gets **only one** plan file path. Plans are self-contained; prerequisites are filesystem/command checks, not “read plan N”.

## Working directory

```
be/shared/enjilib-jwt-auth/
```

## Validation baseline (all waves)

```bash
cd be/shared/enjilib-jwt-auth
uv sync --all-extras
uv run pytest -v
```

Do not lower coverage fail-under or delete authz/crypto assertions to make docs green.

## Plan index

| File | Wave | Owns | Parallel? |
|---|---|---|---|
| [01_docs_token_contract.md](./01_docs_token_contract.md) | A | `README.md`, `API.md` | Yes (with 02) |
| [02_packaging_hygiene.md](./02_packaging_hygiene.md) | A | `py.typed`, `.gitignore`, egg-info policy, packaging metadata | Yes (with 01) |
| [03_agents_entrypoint.md](./03_agents_entrypoint.md) | B | `AGENTS.md` | Yes |
| [04_github_templates.md](./04_github_templates.md) | B | `.github/ISSUE_TEMPLATE/`, PR template | Yes |
| [05_process_docs.md](./05_process_docs.md) | B | `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` | Yes |
| [06_memory_handoff.md](./06_memory_handoff.md) | B | `docs/decisions/`, `docs/handoff.md` | Yes |

## Out of scope (do not reopen here)

- Rewriting the behavioral test suite (`docs/tasks/test_audit_1/`).
- Changing production AuthN/AuthZ semantics (`stakeholder` bypass, `re.match` behavior, bare `except`).
- Publishing a new package version / PyPI.
- Monorepo-root agent skills (this nested library keeps its own `AGENTS.md`).
