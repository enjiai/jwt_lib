# Repository Readiness for AI Agents

## Executive Summary
- Agents can read and understand this small JWT library quickly, but they cannot yet make stable, reliable changes on their own: the documented test path is hollow, there are no agent instructions or handoff records, and several docs disagree with the code.
- Overall readiness is **21 / 100 — Needs groundwork**. In plain terms, an agent can find its way around the code but will usually need a maintainer to confirm token behavior, packaging, and "done" criteria before changing anything sensitive. Confidence in this conclusion is high; the gaps are clear and repeatable.
- The single most valuable first improvement is a real, meaningful test suite behind the documented `pytest` command, because this is an authentication library and today a passing test run proves almost nothing.

## Audit Target and Version
- Repository: `enjiai/jwt_lib`
- Default branch: [`main`](https://github.com/enjiai/jwt_lib/tree/main)
- Audited commit: [`93d861b22ac56871284f63e88020c72d4d8eb096`](https://github.com/enjiai/jwt_lib/commit/93d861b22ac56871284f63e88020c72d4d8eb096)
- Version confidence: The default branch and full commit were confirmed against remote metadata. History was cloned shallow, so long-term change patterns, branch protection, and release history could not be read from local history.

## What We Checked
- The full repository tree: the four source files under `src/enjilib_jwt` (`__init__.py`, `authenticator.py`, `claims.py`, `cipher.py`), the `tests/` folder, packaging files (`pyproject.toml`, `setup.py`, `pytest.ini`, `uv.lock`), and the `README.md` and `API.md` documentation.
- The audit was read-only; no dependencies were installed and no tests, build, or scanners were run.

## Main Answer
Audit question: how ready is the repository for an AI agent to make stable and reliable changes with minimal explanation from a human?

Agents cannot yet move this repository forward calmly on their own. The code is compact and the public API is documented, so orientation is easy. But autonomous delivery is fragile: the `pytest` verification path has no real tests behind it, there is no agent entrypoint, planning, review, release, or handoff guidance, and current docs drift from the implementation on token shape, install source, and package metadata. Because this is a security-sensitive authentication library, an agent would repeatedly need maintainer clarification before changing token compatibility, distribution metadata, or authorization behavior. The most important first fix is a meaningful test suite that actually exercises encrypted-token verification and permission logic.

- Human input still needed: **high** — with no meaningful tests, no acceptance criteria, and docs that contradict the code, an agent must ask a human to confirm intended behavior for most non-trivial changes.
- Conclusion confidence: **high** — the missing infrastructure and the documentation-versus-code mismatches are concrete and easy to reproduce; the only limits are shallow history and the absence of an executed test run.

## Key Findings

### Agent Context
| Context type | Score (0-10) | Status | What we found | Why it matters |
|--------------|---------------:|--------|---------------|----------------|
| Technical | 5 | ⚠️ partial | `README.md` and `API.md` document the API, but token examples omit the required `enc` payload and package metadata is split across files. | An agent can navigate the code but cannot safely infer the real token contract or packaging source of truth. |
| Product | 4 | ⚠️ partial | The purpose (JWT helpers for Enji microservices), the `enji-auth` claim vocabulary, roles, permissions, and a FastAPI example are documented. | Domain terms are discoverable, but there is no way to judge consumers, compatibility risk, or acceptable behavior changes. |
| Working process | 2 | ❌ weak | Basic install, `pytest`, and build commands are listed, but no real tests, review rules, release process, or handoff notes exist. | An agent cannot know task intake, acceptance criteria, review routing, or what evidence proves a change is done. |

Overall context depth: **3/10** — technical (5), product (4), and working-process (2) context weight to `5·0.40 + 4·0.30 + 2·0.30 = 3.8`, minus a 1-point penalty for moderate drift in token-shape docs, install docs, test claims, and package metadata, rounding to 3. Working-process context is the weakest type and pulls the whole score down.

### Context Consistency
- ⚠️ Several moderate desyncs were found where documentation drifts from the code:
  - Token shape: `README.md` and `API.md` show tokens with direct claims, but `verify_and_extract()` returns `None` unless the decoded payload carries an `enc` field, then decrypts sensitive claims from it. An agent could write examples, tests, or compatibility changes against the wrong token shape.
  - Install source: the `README.md` install examples point to `your-org/enji-agent` and a subdirectory rather than `enjiai/jwt_lib`, so the install instructions cannot be treated as canonical.
  - Verification claim: `README.md` and `pytest.ini` present `pytest` as the check, but `tests/` contains only `tests/__init__.py`, so passing it proves nothing.
- ⚠️ Minor mismatches also exist: `pyproject.toml` declares `cryptography` and a `py.typed` marker that `setup.py`, the committed egg-info, and the file tree do not match; and `API.md` warns `user_id` is not an employee ID but a later example labels it as one. These can propagate wrong dependency or identity semantics.

### Procedures for Stable Changes
| Step | Status | What it means for the agent |
|------|--------|-----------------------------|
| Understand the task | ⚠️ partial | Docs explain the API surface, but there is no task intake or scope source. |
| Find context | ⚠️ partial | The small tree and API docs help, but drift forces extra cross-checking. |
| Plan the change | ❌ none | No specs, templates, or acceptance criteria exist to plan against. |
| Find entry point and set up | ⚠️ partial | Editable install and entry points are documented; install source is unreliable. |
| Make the change | ⚠️ partial | Public API boundaries are visible, but forbidden-change rules are not stated. |
| Verify the result | ⚠️ partial | A command exists, but the empty test suite means it does not prove behavior. |
| Hand off the work | ❌ none | No decision records, changelog, or resume notes preserve what was done. |

### Methodologies, Frameworks, and Tools
- **No AI-development methodology declared**: none present.
  Type: none — no Spec Kit, OpenSpec, SDD, GSD, BMAD, Beads, Taskmaster, Aider, custom planning method, skill system, or prompt assets were found.
  Attributes: only ordinary project documentation (`README.md`, `API.md`) and a documented `pytest`/build command; task intake, planning, acceptance criteria, handoff memory, and agent entry points are all missing.
  Adherence: not applicable — no framework is declared, so no adherence penalty was applied.
  What it gives agents: basic orientation from standard docs only.
  Limitation: there is no durable planning, verification, handoff, or agent-entry artifact, so every agent starts from scratch.

### Cross-Agent Readiness
- The repository is **not** locked to a single agent runtime — there are no vendor-specific instruction files — so any coding agent (for example Codex, Claude, Cursor, or Copilot) can inspect the small Python tree and start working.
- The main portability blocker is the absence of any shared entrypoint: with no `AGENTS.md`, skills, or handoff convention, every agent must independently rediscover setup, verification, package drift, and safe-change boundaries.

### Agent Skills and Instructions
- No project-specific skills, prompts, slash commands, or agent procedures exist, so there is nothing tailored to guide specialized tasks.
- There are also no outdated or over-general agent instructions to clean up — the gap is that none exist yet, not that existing ones are stale.

### Category Scores
| Category | Score (0-10) | Status | What affected the score |
|----------|---------------:|--------|-------------------------|
| Stable changes | 3 | ❌ | Easy orientation, but no task intake, planning, real tests, review, release, or handoff; doc drift raises clarification needs. |
| Context depth | 3 | ❌ | Technical 5, product 4, working-process 2, with a penalty for moderate drift in token and packaging docs. |
| Planning | 0 | ❌ | No specs, task database, issue templates, acceptance criteria, roadmap, or ADRs were found. |
| Machine checks | 3 | ❌ | `pytest` and `python -m build` are documented, but the test tree is empty and there is no lint, type, or coverage check. |
| Cross-agent | 3 | ❌ | Not vendor-locked, but no shared entrypoint, skills, or handoff rules; every agent re-learns the same context. |
| Skills and instructions | 0 | ❌ | No project skills, prompts, slash commands, or agent procedures exist. |
| Memory and handoff | 0 | ❌ | No ADRs, changelog, release notes, task logs, or resume notes; history is shallow. |
| Quality gates | 1 | ❌ | The only local gate is a documented `pytest` with an empty suite; no review, release, lint, or type gate is documented. |
| Environment and secrets | 5 | ⚠️ | No env secret reads and placeholder keys in docs, but no `.env.example`, ignore rules, security policy, or handling steps. |

### Score Calculation
Score 21/100 because agents can orient quickly in a small, readable library, but nearly every safety net for autonomous work — real tests, planning, agent instructions, and handoff records — is missing, and docs drift from the code. In numbers: `3·0.15 + 3·0.20 + 0·0.14 + 3·0.14 + 3·0.10 + 0·0.09 + 0·0.07 + 1·0.06 + 5·0.05 = 2.08` out of 10, which becomes 21 out of 100.

## What the Conclusion Is Based On
- Source: `src/enjilib_jwt/authenticator.py` requires an `enc` claim before decrypting sensitive fields; `src/enjilib_jwt/cipher.py` implements AES-GCM decryption; `src/enjilib_jwt/__init__.py` exports the public surface.
- Tests: `tests/` holds only `tests/__init__.py`, so the documented `pytest` path exercises nothing.
- Docs and packaging: `README.md` and `API.md` describe the API but diverge on token shape and install source; `pyproject.toml`, `setup.py`, and committed egg-info disagree on runtime dependencies and typing markers.

## Limitations
- History was cloned shallow, so long-term churn, branch protection, and release history could not be assessed.
- No dependencies were installed and no tests, build, or scanners were run, so behavior was inferred from reading the code, not from execution.
- Note: the token-shape, install-source, dependency, and typing-marker mismatches were captured as concrete improvement steps below; they are drift to reconcile, not confirmed bugs, since no test run confirmed runtime behavior.

## Improvement Checklist
| Urgency | What to do | Where to start | Done when |
|---------|-----------|----------------|-----------|
| ❌ Urgent | Add a meaningful test suite behind the documented check, covering encrypted-token verification, invalid tokens, claims extraction, role helpers, and permission allow/disallow precedence. | `tests/`, `README.md`, `pytest.ini` | A one-command check names the required tests, and they cover valid/invalid encrypted tokens, role and permission logic, and malformed input. |
| ⚠️ High | Reconcile the token contract and package metadata so there is one source of truth. | `README.md`, `API.md`, `pyproject.toml`, `setup.py`, `src/enjilib_jwt_auth.egg-info/`, `py.typed` | Docs, packaging, and generated-file policy agree on token shape, canonical install source, runtime dependencies, and the typing marker. |
| ⚠️ High | Add a tool-agnostic root entrypoint so any agent starts with the same setup, checks, and boundaries. | `AGENTS.md` | A root `AGENTS.md` names source roots, API boundaries, setup and verification commands, known drift, and handoff rules. |
| ℹ️ Medium | Add task and pull-request templates with scope, compatibility risk, and verification fields. | `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md` | New tasks and PRs capture scope, API and token-compatibility impact, required tests and docs, and handoff notes. |
| ℹ️ Medium | Document review, release, and security process for this authentication library. | `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` | Process docs define review requirements, release steps, changelog expectations, vulnerability handling, and local secret hygiene. |
| ℹ️ Medium | Add lightweight decision and handoff records for compatibility-sensitive choices. | `docs/decisions/`, `docs/handoff.md` | A simple decision-record format and handoff note exist for token-contract, packaging, and verification decisions. |
