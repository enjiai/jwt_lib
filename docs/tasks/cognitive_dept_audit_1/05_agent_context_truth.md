# Plan 05 — Agent context truth repair (`AGENTS.md` + handoff)

## Agent identity

You repair **false or stale agent memory** so cognitive debt “agent context” is actually usable.  
Own **`AGENTS.md`** and **`docs/handoff.md`**. Do **not** rewrite README/API token sections (plan 01). Do **not** create ADRs or EXTERNAL_CONTRACTS (plans 03–04) — only **link** them if present.

## Task

- **Task ID**: `jwt-cogdebt-05-agent-truth`
- **Title**: Make AGENTS.md / handoff match filesystem reality after Wave A–B siblings
- **Component**: `be/shared`
- **Service Root**: `be/shared/enjilib-jwt-auth`
- **Role**: Shared library / Agent DevEx
- **Work mode**: Auto
- **Dependencies**: **Wave A must be complete** (plan 01 + 02 AC greps pass). Prefer Wave B 03–04 present; if missing, link as “expected path” only after `test -f`.

---

## Prerequisite gate (STOP if unmet)

```bash
cd be/shared/enjilib-jwt-auth
uv run pytest -q

# Wave A truth — STOP if unmet (do not re-assert “docs fixed”)
rg -n '"enc"' README.md API.md
rg -n 'enjiai/jwt_lib' README.md
test -f src/enjilib_jwt/py.typed
test -f .gitignore

# Soft checks for Wave B siblings
test -f docs/EXTERNAL_CONTRACTS.md || echo "WARN: EXTERNAL_CONTRACTS missing — link as pending only if truly absent"
ls docs/decisions/ | head
```

If Wave A greps fail, STOP and report which AC from plans 01/02 is still red. **Do not** “fix” AGENTS by claiming docs are aligned while greps fail.

---

## Context

### Problem

Cognitive debt audit scored agent context 0 (no entrypoint). Later work added `AGENTS.md` and `docs/handoff.md`, but re-review found **new cognitive debt**:

- `AGENTS.md` §4 claims Wave A token docs / packaging are **completed / now fixed**.
- `docs/handoff.md` claims README+API mention stakeholder and packaging Wave A “in progress/done” inconsistently with files on disk (pre-Wave-A state had flat tokens, missing `py.typed`).

False completion claims are worse than missing docs: agents skip verification.

### Goal

Single truthful entrypoint: what is locked, what was fixed in which audit track, where to read contracts, how to verify, what not to change.

### Non-goals

- Replacing sibling ADRs’ content.
- Expanding into full monorepo AGENTS.
- Changing library code.

### Constraints

- Every “✅ done” claim must be backed by a filesystem/command check you ran in this session.
- Prefer linking `docs/tasks/cognitive_dept_audit_1/` and `docs/tasks/ai_readiness_audit_1/` as historical audits, not as proof of completion.
- Remove or rewrite absolute machine-specific paths if present (`/Users/...`) in favor of repo-relative instructions.

---

## Acceptance criteria

- [ ] AC-1: `AGENTS.md` no longer claims README/API token examples are fixed unless `rg '"enc"' README.md API.md` succeeds (already gated) | verify: `! rg -ni 'token examples now correctly|Wave A.*✅ Completed|now fixed' AGENTS.md` **or** equivalent status table that matches checks you ran
- [ ] AC-2: `AGENTS.md` points to README, API.md, `docs/decisions/`, `docs/EXTERNAL_CONTRACTS.md` (if exists), tests, and safe-change boundaries including stakeholder + enc | verify: `rg -n 'EXTERNAL_CONTRACTS|stakeholder|enc|docs/decisions' AGENTS.md`
- [ ] AC-3: `AGENTS.md` lists verify command `uv run pytest` and expected green suite / coverage gate | verify: `rg -n 'pytest' AGENTS.md`
- [ ] AC-4: `docs/handoff.md` “Current status” / packaging / stakeholder sections match reality (py.typed present; docs mention enc/stakeholder; open items only if truly open) | verify: manual skim + greps
- [ ] AC-5: Handoff does not claim stakeholder is documented in README+API unless `rg -ni stakeholder README.md API.md` hits | verify: consistent with grep
- [ ] AC-6: Root TXT “FIX_PLAN” files are labeled non-authoritative **or** removed from “source of truth” lists in AGENTS (prefer: “historical / do not trust status headers”) | verify: `rg -n 'TOKEN_CONTRACT_FIX_PLAN|PACKAGING_HYGIENE_FIX_PLAN' AGENTS.md` context is cautionary
- [ ] AC-7: Pytest still green | verify: `uv run pytest -q`

---

## Implementation steps

1. Run prerequisite greps; capture evidence in done report.
2. Rewrite `AGENTS.md` §4 (Known Drift) into a **status table** with columns: topic / status / evidence command / owner plan.
3. Ensure safe-change section names: mandatory `enc`, stakeholder bypass, disallow precedence, `re.match` prefix, bare `except` → `None`.
4. Add navigation to EXTERNAL_CONTRACTS + decisions index when files exist.
5. Update `docs/handoff.md` Critical Context / Known Quirks / Next actions to match.
6. Do not invent completed GitHub-template work; if those files exist under `.github/`, mention briefly; if not, leave out or mark open without expanding scope.

---

## Done report (required)

- Diff summary for AGENTS + handoff
- Paste of key greps proving no false “fixed” claims
- Remaining open cognitive-debt items (if any) listed honestly

## Out of scope

- Implementing missing docs/packaging (send back to Wave A)
- New ADRs (plan 03)
- Editing issuer services
