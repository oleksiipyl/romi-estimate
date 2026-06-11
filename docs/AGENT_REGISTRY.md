# Agent Registry — CursorAgentRomeEstimate

> Single map of all agents, scopes, and boundaries.  
> **Coordinator maintains this file.** Agents read it; they do not redefine scopes without coordinator approval.

---

## Registry

| ID | Name | Type | Scope | Must NOT Touch | Doc |
|----|------|------|-------|----------------|-----|
| `COORDINATOR` | Main Cursor Coordinator | Governance | Reviews all work, resolves conflicts, adds agents, maintains status | Does not implement features unless unblocking | `docs/COORDINATOR.md` |
| `SOAP` | SOAP Agent | External / Parallel | *Assigned by coordinator per task* | Other agents' in-progress branches without handoff | `docs/AGENT_SOAP.md` |
| `CLO` | CLO Agent | External / Parallel | *Assigned by coordinator per task* | Other agents' in-progress branches without handoff | `docs/AGENT_CLO.md` |
| `SENYA` | Senya — Tech Lead | Development | Architecture, schema, task breakdown, code review | UX wireframes before approval; Victor pricing without review | `docs/AGENTS.md` |
| `BACKEND` | Backend Agent | Development | `backend/`, API, SQLite, calculator logic | `frontend/`, hardcoded prices | `docs/AGENTS.md` |
| `FRONTEND` | Frontend Agent | Development | `frontend/`, UI, fetch to API | `backend/`, hardcoded prices, frameworks | `docs/AGENTS.md` |
| `UX` | UX Designer Agent | Design | Wireframes, flows (markdown/ASCII) | Production code until Alex approves | `docs/AGENTS.md` |
| `QA` | QA Agent | Quality | Tests, checklists, verification reports | Changing product logic without Victor/Senya sign-off | `docs/AGENTS.md` |
| `VICTOR` | Victor — Glazing Expert | Domain | Glazing specs, market research, product logic docs | Application code (feeds specs to BACKEND) | `docs/AGENT_GLAZING_EXPERT.md` |

---

## Scope Rules (No Contradictions)

### Pricing
- **Owner:** BACKEND (implementation) + VICTOR (accuracy)
- **Source:** SQLite `services` table, seeded from approved price data
- **Rule:** Never hardcode prices in Python or HTML

### Product / Glass Logic
- **Owner:** VICTOR
- **Source:** `docs/GLAZING_PRODUCT_LOGIC.md`, `backend/products.py`
- **Rule:** Low-E/Solarban only in IGU; tempered where code requires; no auto glass

### UI / Calculator
- **Owner:** FRONTEND + UX
- **Rule:** Mobile-first, Tailwind CDN, vanilla JS, no build step

### API Contract
- **Owner:** SENYA + BACKEND
- **Source:** `backend/main.py` endpoints as documented in `SOURCES_OF_TRUTH.md`

### Publication
- **Owner:** COORDINATOR only
- **Rule:** All agents hand off via `PROJECT_STATUS.md`; coordinator reads before merge

---

## SOAP & CLO Integration

SOAP and CLO work **in parallel** with the development team. To avoid contradiction:

1. Coordinator assigns **explicit file/task scope** before they start
2. They post handoff in `docs/PROJECT_STATUS.md` when done
3. Coordinator reads both agents' output before any merge
4. If SOAP and CLO touch the same area, coordinator sequences work (one then the other)

*Scope details for SOAP and CLO will be expanded when Alex defines their roles.*

---

## Adding a New Agent

1. Coordinator copies `docs/AGENT_TEMPLATE.md` → `docs/AGENT_<NAME>.md`
2. Add row to this registry table
3. Update `docs/COORDINATOR.md` org chart if needed
4. Post announcement in `docs/PROJECT_STATUS.md`

---

*Last updated by: Main Cursor Coordinator*
