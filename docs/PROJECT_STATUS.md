# Project Status — CursorAgentRomeEstimate

> Live board for all agents. Update when you start or finish work.  
> **Coordinator reads this before approving any publication.**

---

## Current Phase

**Phase 1 — Working calculator** (in progress)

- Backend: FastAPI + SQLite scaffold exists
- Frontend: `index.html` exists
- Victor: Product logic and research docs complete
- Admin panel: partial / in progress

---

## Active Work

| Agent | Task | Branch | Status |
|-------|------|--------|--------|
| COORDINATOR | Re-link Senya ↔ Coordinator | `cursor/senya-coordinator-link-1c4b` | In progress |
| SENYA | Orchestrator active | — | Active — see `docs/AGENT_SENYA.md` |

---

## Cross-Agent Notes

*No open conflicts.*

### 2026-06-11 — Senya Re-linked
- Создан `docs/AGENT_SENYA.md` — Senya знает где координатор
- Создан `docs/CURRENT_TASK.md` — общая SYNC-доска
- Cursor rule `.cursor/rules/02-senya.mdc`
- Senya → Coordinator протокол восстановлен

### 2026-06-11 — Coordinator Setup
- Established Main Cursor Coordinator role
- Registered SOAP and CLO as parallel agents (scope TBD with Alex)
- Added publication gate: coordinator reads before merge
- Added sources of truth and agent registry
- **Язык ответов Alex: всегда русский**

---

## Handoff Log

### COORDINATOR Handoff — 2026-06-11
**Task:** Initialize CursorAgentRomeEstimate coordination framework  
**Files changed:**
- `.cursor/rules/00-coordinator.mdc`
- `.cursor/rules/01-all-agents.mdc`
- `docs/COORDINATOR.md`
- `docs/AGENT_REGISTRY.md`
- `docs/AGENT_TEMPLATE.md`
- `docs/AGENT_SOAP.md`
- `docs/AGENT_CLO.md`
- `docs/SOURCES_OF_TRUTH.md`
- `docs/PROJECT_STATUS.md`
- `README.md`

**Scope respected:** Governance docs only; no application logic changed  
**Needs coordinator review:** Self-approved setup commit  
**Conflicts with other agents:** none

---

## Blocked / Waiting

| Item | Waiting On |
|------|------------|
| SOAP permanent role | Alex definition |
| CLO permanent role | Alex definition |

---

## Next Priorities (Coordinator View)

1. Complete calculator UI wired to `/api/calculate`
2. Admin panel (`admin.html`) for price management
3. QA test pass on mobile (375px)
4. Align `products.py` with frontend product selector

---

*Updated by: Main Cursor Coordinator*
