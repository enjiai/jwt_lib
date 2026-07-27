# CI/CD audit remediation — orchestration

## Audit review (vs code + provider, 2026-07-27)

Source audit: [`enjiai-jwt_lib-audit-cicd-2026-07-27.md`](./enjiai-jwt_lib-audit-cicd-2026-07-27.md) against commit `94a9f50` (`origin/main` after merge of `fix_tests_ai_readability`).

| Audit claim | Local / provider verification | Verdict |
|---|---|---|
| Score **16/100**, severity bad — zero automated protection | Provider: workflows `total_count=0`, runs `0`, rulesets `[]`. Branch protection API: **404 Branch not protected** (stronger than audit’s 403). Local: untracked draft `.github/workflows/test.yml` only | **Correct for remote.** Local draft does not count until committed + green on GitHub |
| No CI config on default branch | `git show origin/main:.github/workflows/test.yml` fails; filesystem on main has no `.github/` | **Correct** |
| Useful local foundation (uv, pytest, coverage) | `uv run pytest -q` → **74 passed**, fail-under **100%** via `pyproject.toml` | **Correct / stronger than audit implied** (suite is real, not hollow) |
| Containerization / runtime deploy N/A | No Dockerfile / compose | **Correct** — keep out of scope |
| Release is manual (tag → build → twine) | `CHANGELOG.md` still documents manual `python -m build` + `twine upload` | **Correct** |
| CONTRIBUTING references missing Actions + PR template | CONTRIBUTING on main requires green Actions and links `.github/pull_request_template.md`; neither exists on `origin/main`. Templates exist only as **local untracked** files | **Correct for remote**; local WIP partially started |
| Next action: minimal PR/push workflow with uv + pytest | Draft `test.yml` already matches that shape locally | **Right priority**; extend in this track rather than rewrite from scratch |

### Audit quality notes

- **Methodology is sound** for a first CI baseline: filesystem scan + provider API + local command inventory + docs drift.
- **Score arithmetic is directionally fair**; the no-CI cap is appropriate for a shared auth library.
- **Weaknesses in the report itself** (fix in remediation, do not re-audit for vanity):
  1. Improvement checklist **duplicates** “add build + mypy” (rows appear twice).
  2. Audited “shallow history” limitation is fine; branch-protection finding should now be stated as **unprotected**, not merely “unreadable”.
  3. Audit did not distinguish **remote main** vs **local uncommitted** `.github/` — agents must treat untracked drafts as starting points, not “done”.
  4. `mypy --strict` is documented in `AGENTS.md` but **mypy is not a declared/installed dev dependency** — typecheck gate cannot be honest until packaging catches up.

### Extra findings from this review (include in plans)

1. **No Makefile / single local gate** — README/AGENTS/CONTRIBUTING list overlapping `uv`/`pytest`/`build` commands; no `make test` / `make check`.
2. **Draft CI is pytest-only** — no `uv build`, no mypy job; Python pinned to 3.11 only while package declares `>=3.9` (matrix optional, not blocking).
3. **README Development** still shows `python -m build` while AGENTS prefers `uv build`.
4. **`.gitignore` is local-untracked**; `origin/main` still ships `tests/**/__pycache__` — commit ignore rules when landing CI so artifacts stop landing in PRs.
5. **Nested repo**: commits/PRs belong in `be/shared/enjilib-jwt-auth/.git` (`enjiai/jwt_lib`), not monorepo root.
6. **Sibling overlap**: `docs/tasks/test_audit_1/05_coverage_and_ci.md` already sketched coverage+workflow (partially executed locally). This track **owns remaining CI/CD delivery** and must not reopen behavioral tests.

### Expected score movement (after this remediation)

| Criterion (audit) | Then | After these plans (expected) |
|---|---|---|
| CI presence / triggers | 0 | ~4–5 (PR + main push) |
| Gate composition | 0 | ~4 (pytest+cov, mypy, build) |
| Blocking behavior | 0 | ~4 after Wave C (required check) |
| Local/CI command parity | 4 | ~5 (`make check` == CI) |
| Observable health | 0 | ~4 (workflow runs exist) |
| Release process | 2 | ~4 (tag-triggered publish path) |

Rough re-score target: **~55–70/100** once Waves A–B land and required checks are enabled; full “good” needs Wave C + a real published release dry-run.

## Goal

Give `enjiai/jwt_lib` automated, reproducible gates on every PR/push to main, local/CI command parity, truthful contribution docs, and a tag-triggered release path — **without** changing AuthN/AuthZ semantics or reopening the behavioral suite.

## Parallel execution model

```
Prerequisite (orchestrator)
  └── cd be/shared/enjilib-jwt-auth
      uv sync --all-extras && uv run pytest -q
      Expect: 74 passed. If red → stop; do not “fix” CI by deleting assertions.

Wave A (up to 2 agents, PARALLEL — disjoint ownership)
  ├── 01_local_gate_makefile.md   → Makefile (+ minimal README/AGENTS command pointers)
  └── 02_ci_workflow_gates.md     → .github/workflows/test.yml, mypy as dev dep, uv.lock, .gitignore

Wave B (up to 2 agents, PARALLEL — after Wave A green on CI file + make check)
  ├── 03_docs_ci_parity.md        → CONTRIBUTING.md, README Development, AGENTS § verify/CI, CHANGELOG release notes (manual→CI)
  └── 04_release_automation.md    → .github/workflows/release.yml (+ trusted-publishing setup notes in CHANGELOG/SECURITY as owned)

Wave C (human / admin — after check names stable from Wave A)
  └── 05_branch_protection.md     → require CI check on main; no code changes
```

**Why this split:** Wave A creates the real gate (Makefile + Actions) without fighting over docs. Wave B docs and release automation both need stable job/check names and command strings from Wave A, but they own different files so two agents can run in parallel. Wave C cannot be done by a normal code agent (GitHub admin settings).

## How to launch subagents

1. Orchestrator verifies pytest green.
2. Launch **two** agents in parallel on Wave A (`01`, `02`), each with **only one** plan file path.
3. After both report AC-pass with evidence, launch **two** agents in parallel on Wave B (`03`, `04`).
4. Hand Wave C checklist to a human with admin rights; do not fake branch protection in-repo.
5. Prefer committing/pushing from the nested `enjilib-jwt-auth` repo so Actions actually run.

Each plan is self-contained. Prerequisites are filesystem/command checks, not “read sibling plan N”.

## Working directory

```
be/shared/enjilib-jwt-auth/
```

## Validation baseline (all waves)

```bash
cd be/shared/enjilib-jwt-auth
uv sync --frozen --all-extras
uv run pytest -q
# After Wave A:
make check   # or documented equivalent
```

Do not lower coverage fail-under or delete authz/crypto assertions to make CI green.

## Plan index

| File | Wave | Owns | Parallel? |
|---|---|---|---|
| [01_local_gate_makefile.md](./01_local_gate_makefile.md) | A | `Makefile`; small README/AGENTS command pointers only | Yes (with 02) |
| [02_ci_workflow_gates.md](./02_ci_workflow_gates.md) | A | `.github/workflows/test.yml`, `pyproject.toml`/`uv.lock` mypy, `.gitignore` | Yes (with 01) |
| [03_docs_ci_parity.md](./03_docs_ci_parity.md) | B | `CONTRIBUTING.md`, `README.md` Development/CI, `AGENTS.md` verify/CI bits | Yes (with 04) |
| [04_release_automation.md](./04_release_automation.md) | B | `.github/workflows/release.yml`, `CHANGELOG.md` publish section | Yes (with 03) |
| [05_branch_protection.md](./05_branch_protection.md) | C | Human admin checklist only | After A |

## Out of scope (do not reopen here)

- Rewriting behavioral tests (`docs/tasks/test_audit_1/`).
- Changing production AuthN/AuthZ / token contract.
- Monorepo-root CI wiring (this nested repo has its own `.git`).
- Container images / runtime deployment.
- Codecov or other third-party coverage uploads.
