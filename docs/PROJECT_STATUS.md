# Project Status — CursorAgentRomeEstimate

> Live board for all agents. Update when you start or finish work.  
> **Coordinator reads this before approving any publication.**

---

## 🔔 SYNC PING — 2026-06-11 01:57 PDT

**FROM: SENYA (OpenClaw Tech Lead)**

ALL AGENTS: Read this file. Confirm you are alive.

**COORDINATOR** — прочитай `docs/activeagreement.md`, подтверди что видишь Senya.
**SOAP** — прочитай `docs/AGENT_SOAP.md` и `docs/AGENT_REGISTRY.md`. Подтверди готовность.
**CLO** — прочитай `docs/AGENT_CLO.md` и `docs/AGENT_REGISTRY.md`. Подтверди готовность.

Обновите эту таблицу Active Work с вашим статусом.

---

## Current Phase

**Phase 1 — Working calculator** (in progress)

- Backend: FastAPI + SQLite — ✅ working on port 8000
- Frontend: `index.html` — ✅ working, hardware category added
- Victor: Product logic and research docs — ✅ complete
- Hardware pricing: ✅ updated (hinge, screens, locks, casement)
- Admin panel: partial / in progress

---

## Active Work

| Agent | Task | Branch | Status |
|-------|------|--------|--------|
| COORDINATOR | UI redesign v3 — mobile-first professional | `cursor/ui-redesign-v3` | In progress |
| COORDINATOR | Multi-agent framework setup | `cursor/coordinator-setup-1c4b` | ✅ Merged to main |
| SENYA | Hardware pricing + floor surcharge updates | `main` | ✅ Done |
| SENYA | Beacon `activeagreement.md` for romi-estimate | `senya/accept-cursor-protocol` | ✅ Pushed |
| COORDINATOR | **UI REDESIGN** — Redesign `frontend/index.html`: mobile-first 375px, professional look, clean sections, brand colors (blue #2563EB + white). Keep ALL JS logic intact. Only change HTML structure and Tailwind classes. Add company logo area. Fix visual hierarchy. | cursor/ui-redesign-v3 | **assigned** |
| SOAP | **ADMIN PANEL** — Create `frontend/admin.html`: password login (fastglass2026), table of all 51 services with inline price editing, settings editor, search/filter. Use existing API: GET /api/admin/services?password=X, PUT /api/admin/services/{id}?password=X, GET/PUT /api/admin/settings. Tailwind CSS. | cursor/admin-panel | **assigned** |
| CLO | **STANDBY** — Wait for Phase 5 assignment. | — | **standby** |

---

## Cross-Agent Notes

### 2026-06-11 01:57 PDT — Senya SYNC
- Senya (OpenClaw) is ONLINE and coordinating
- Hardware prices updated: Screen $150-180 (min $350), Hinge $300-350 (new), Casement $650
- 2nd floor surcharge: $200 (was $150)
- Removed auto-recommendation "2 technicians for 2nd floor"
- Calculator running on localhost:8000
- GHL import scheduled at 02:00 (5,012 contacts from HouseCallPro)

### 2026-06-11 — Coordinator Setup
- Established Main Cursor Coordinator role
- Registered SOAP and CLO as parallel agents (scope TBD with Alex)
- Added publication gate: coordinator reads before merge
- **Язык ответов Alex: всегда русский**

---

## Handoff Log

### SENYA Handoff — 2026-06-11 01:57 PDT
**Task:** Hardware pricing + floor surcharge + frontend qty selector
**Files changed:**
- `backend/products.py` — new prices, min_charge, hw_hinge added
- `backend/database.py` — 2nd floor $150→$200
- `backend/calculator.py` — removed "recommend 2 techs" note
- `backend/main.py` — API returns min_charge + category for hardware
- `frontend/index.html` — hwQty selector, no /sf for hardware, min_charge logic

**Scope respected:** Backend + Frontend (Senya scope as Tech Lead)
**Conflicts with other agents:** none

### COORDINATOR Handoff — 2026-06-11
**Task:** Initialize CursorAgentRomeEstimate coordination framework  
**Files changed:** `.cursor/rules/*`, `docs/COORDINATOR.md`, `docs/AGENT_REGISTRY.md`, `docs/AGENT_TEMPLATE.md`, `docs/AGENT_SOAP.md`, `docs/AGENT_CLO.md`, `docs/SOURCES_OF_TRUTH.md`, `docs/PROJECT_STATUS.md`, `README.md`
**Scope respected:** Governance docs only; no application logic changed

---

## Blocked / Waiting

| Item | Waiting On |
|------|------------|
| SOAP permanent role | Alex definition |
| CLO permanent role | Alex definition |

---

## Next Priorities (Senya View)

1. **COORDINATOR** — confirm SYNC, verify all agents alive
2. **SOAP/CLO** — Alex to define roles
3. Calculator UI polish — mobile QA at 375px
4. Admin panel (`admin.html`) for price management
5. GHL integration — contact import running at 02:00

---

*Updated by: Senya (OpenClaw Tech Lead) — 2026-06-11 01:57 PDT*
