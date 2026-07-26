# Cognitive debt audit remediation — orchestration

## Audit review (vs local code, 2026-07-26)

Source audit: [`enjiai-jwt_lib-audit-cognitive-debt-2026-07-15.md`](./enjiai-jwt_lib-audit-cognitive-debt-2026-07-15.md) against commit `93d861b`.

### Verdict on the audit itself

| Aspect | Assessment |
|---|---|
| Main answer / score 27/100 | **Fair for the audited snapshot.** Broad goal recoverable; current contract, proof, and rationale were not. |
| Methodology | **Sound.** Docs → code → tests → agent context → metadata → alignment scorecard is the right order for cognitive debt. |
| Highest-risk finding (`enc` vs plain docs) | **Correct and still open in human docs.** `verify_and_extract` still requires `enc`; `README.md` / `API.md` still show flat claims. |
| Stakeholder shortcut undocumented | **Correct and still open in public docs.** Code short-circuits all role helpers; tests pin it; README/API do not explain it; no dedicated ADR yet. |
| Empty tests / proven behavior = 2 | **Was correct; now superseded.** Suite from `docs/tasks/test_audit_1/` — **74 passed**, coverage fail-under 100% (verified `uv run pytest -q` on 2026-07-26). |
| No `AGENTS.md` / agent context = 0 | **Was correct; partially superseded, with new debt.** Root `AGENTS.md` + `docs/handoff.md` exist, but they **claim Wave A docs/packaging are fixed while README/API/`py.typed` still contradict that** — false completion claims are fresh cognitive debt. |
| Packaging / cryptography drift | **Mostly fixed for deps.** `pyproject.toml` and `setup.py` both declare `cryptography`. Residual: missing `src/enjilib_jwt/py.typed`, no `.gitignore`, `setup.py` `dev` extras omit `pytest-cov`. |
| External enji-auth / collector bridge | **Still open.** Issuer + cipher now locatable in the monorepo; this library still does not point maintainers/agents there. |
| Confidence = medium | **Appropriate then.** Still fair: external contracts were inferred; today we can raise confidence after linking issuer paths and aligning docs. |

### Extra findings from this review (not explicit in the audit checklist)

1. **Meta-drift in agent memory** — `AGENTS.md` §4 and parts of `docs/handoff.md` mark token-doc / packaging Wave A as done; filesystem evidence contradicts. Agents will trust the wrong source.
2. **Root fix-plan TXT artifacts** (`01_TOKEN_CONTRACT_FIX_PLAN.txt`, `02_PACKAGING_HYGIENE_FIX_PLAN.txt`) read as completed work while human docs remain stale — treat as non-authoritative; prefer these plans + code/tests.
3. **Permission ADR still missing** — AI-readiness plan 06 asked for stakeholder + permission ADRs; only `001_token_contract_structure.md` and `002_packaging_source_of_truth.md` exist.
4. **Issuer source of truth exists outside this repo** — `be/services/enji-auth/app/auth/authentication/cipher.py` + `core.py` (`_create_jwt_token`, `_PLAINTEXT_CLAIMS`). Cognitive debt item “external bridge” can now be closed with paths, not guesses.
5. **Nested git repo** — commits/PRs belong in `be/shared/enjilib-jwt-auth/.git` (`enjiai/jwt_lib`), not monorepo root.

### Overlap with sibling remediations

| Sibling | Relation |
|---|---|
| `docs/tasks/test_audit_1/` | **Done / out of scope here.** Checklist item “add pytest specs” is satisfied. |
| `docs/tasks/ai_readiness_audit_1/` | **Overlaps heavily** on docs, packaging, AGENTS, ADRs. Those plans were written but human-facing docs were not actually aligned. **This track reopens the still-false items** with cognitive-debt acceptance criteria and strict ownership so subagents do not re-claim “done” without grep/file proof. |

### Expected score movement (after this remediation)

| Criterion (audit) | Then | After these plans (expected) |
|---|---|---|
| Goals and constraints | 4 | ~8 (enc + stakeholder + identity documented) |
| Proven behavior | 2 | ~9 (already improved by tests; keep green) |
| Knowledge recovery | 4 | ~8 (API linked, ADRs, external bridge) |
| Agent context | 0 | ~7 (AGENTS truthful + handoff accurate) |
| Evidence alignment | 2 | ~8 (docs/code/tests/metadata agree) |

Rough re-score target: **~70+/100**, severity “acceptable / good”, if all waves land without new false claims.

## Goal

Close remaining cognitive-debt gaps so a future human or agent can recover **current** constraints, rationale, and proof **without guessing** — especially the encrypted-token contract, stakeholder shortcut, identity fields, and external issuer/collector boundaries.

## Parallel execution model

```
Prerequisite (orchestrator)
  └── Confirm: cd be/shared/enjilib-jwt-auth && uv sync --all-extras && uv run pytest -q
      Expect: 74 passed. If red → stop; do not “fix” docs by inventing behavior.

Wave A (up to 2 agents, PARALLEL — disjoint ownership)
  ├── 01_docs_token_contract.md     → README.md, API.md
  └── 02_packaging_residuals.md     → py.typed, .gitignore, setup.py extras sync

Wave B (up to 3 agents, PARALLEL — after Wave A green)
  ├── 03_decision_rationale.md      → docs/decisions/* (new ADRs + index)
  ├── 04_external_contract_bridge.md → docs/EXTERNAL_CONTRACTS.md (+ one-line links)
  └── 05_agent_context_truth.md     → AGENTS.md, docs/handoff.md (truth repair only)
```

**Why this split:** Wave A removes the doc/packaging lies that Wave B must cite. Wave B files do not share ownership, so three agents can run without merge conflicts. Do **not** launch Wave B until Wave A acceptance greps pass — otherwise `05` will re-encode stale “docs still wrong” as permanent known-drift.

## How to launch subagents

1. Orchestrator runs pytest green.
2. Launch **two** agents in parallel on Wave A (`01`, `02`), each with **only one** plan path.
3. After both report AC-pass with evidence, launch **three** agents in parallel on Wave B (`03`–`05`).
4. Orchestrator runs a final truth check (commands in §Validation) and updates nothing except a short note in chat / PR.

Each plan is self-contained. Prerequisites are filesystem/command checks, not “read sibling plan N”.

## Working directory

```
be/shared/enjilib-jwt-auth/
```

Nested repo: create commits/PRs here (`enjiai/jwt_lib`), not at monorepo root.

## Validation baseline (all waves)

```bash
cd be/shared/enjilib-jwt-auth
uv sync --all-extras
uv run pytest -q
```

Do not lower coverage fail-under. Do not change AuthN/AuthZ semantics (`stakeholder` bypass, `re.match` prefix matching, bare `except` → `None`) unless a separate security task says so — **document and ADR-lock** them.

### Final orchestrator truth check (after Wave B)

```bash
# Docs no longer present plain-only token as current
rg -n '"enc"' README.md API.md
# Install source not placeholder
! rg -n 'your-org/enji-agent' README.md
# Stakeholder explained somewhere public + ADR
rg -ni 'stakeholder' README.md API.md docs/decisions/
# Agent entrypoint does not claim unfinished Wave A as done
! rg -n 'now fixed|COMPLETED|Wave A.*done' AGENTS.md docs/handoff.md || true
# Prefer explicit status lines that match reality
test -f src/enjilib_jwt/py.typed
test -f docs/EXTERNAL_CONTRACTS.md
uv run pytest -q
```

## Plan index

| File | Wave | Owns | Parallel? |
|---|---|---|---|
| [01_docs_token_contract.md](./01_docs_token_contract.md) | A | `README.md`, `API.md` | Yes (with 02) |
| [02_packaging_residuals.md](./02_packaging_residuals.md) | A | `py.typed`, `.gitignore`, `setup.py` extras | Yes (with 01) |
| [03_decision_rationale.md](./03_decision_rationale.md) | B | `docs/decisions/` | Yes |
| [04_external_contract_bridge.md](./04_external_contract_bridge.md) | B | `docs/EXTERNAL_CONTRACTS.md` (+ minimal links) | Yes |
| [05_agent_context_truth.md](./05_agent_context_truth.md) | B | `AGENTS.md`, `docs/handoff.md` | Yes |

## Out of scope

- Rewriting the behavioral test suite (`docs/tasks/test_audit_1/`).
- Changing production AuthN/AuthZ / cipher semantics.
- Publishing a new package version / PyPI.
- Re-running the full AI-readiness checklist items already closed (GitHub templates, CONTRIBUTING/SECURITY/CHANGELOG) unless a Wave B agent discovers they block truth repair — prefer linking existing files.
- Monorepo-root agent skills.
