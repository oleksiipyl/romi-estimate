# Sources of Truth — CursorAgentRomeEstimate

> When agents disagree, check these files in order.  
> Coordinator resolves anything not covered here.

---

## Priority Order

| # | Topic | Canonical File | Owner |
|---|-------|----------------|-------|
| 1 | Glazing product rules | `docs/GLAZING_PRODUCT_LOGIC.md` | VICTOR |
| 2 | Product catalog structure | `backend/products.py` | VICTOR → BACKEND |
| 3 | Price calculation | `backend/calculator.py` | BACKEND |
| 4 | Database schema & seed | `backend/database.py` | BACKEND / SENYA |
| 5 | API endpoints | `backend/main.py` | BACKEND |
| 6 | Calculator UI | `frontend/index.html` | FRONTEND |
| 7 | Admin UI | `frontend/admin.html` | FRONTEND |
| 8 | Agent scopes | `docs/AGENT_REGISTRY.md` | COORDINATOR |
| 9 | Team prompts (dev) | `docs/AGENTS.md` | SENYA |
| 10 | Victor domain prompt | `docs/AGENT_GLAZING_EXPERT.md` | VICTOR |
| 11 | Market research | `docs/VICTOR_*.md` | VICTOR |
| 12 | Project status | `docs/PROJECT_STATUS.md` | COORDINATOR |

---

## Immutable Stack Rules

```
✓ Python 3 + FastAPI + SQLite
✓ HTML + Tailwind CDN + vanilla JavaScript
✓ Mobile-first, works on phone browsers
✓ Prices from SQLite — never hardcoded

✗ React, Vue, Next.js, or build pipelines
✗ PostgreSQL (SQLite is enough)
✗ AI in price calculation (v1)
✗ Auto glass products
```

---

## Pricing Formula (Backend)

```
area_sqft = (width_inches / 12) × (height_inches / 12)
base = area_sqft × service rate (min/max from DB)
+ modifiers from modifiers table
+ ZIP multiplier from zip_multipliers table
+ floor surcharge
× urgency multiplier (urgent 1.30, emergency 1.50)
```

---

## API Surface (v1)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/services` | Enabled services |
| GET | `/api/products` | Victor product structure |
| GET | `/api/modifiers` | Price modifiers |
| GET | `/api/zip/{zip}` | ZIP lookup |
| POST | `/api/calculate` | Price estimate |
| GET | `/api/admin/services` | Admin list (password) |
| PUT | `/api/admin/services/{id}` | Admin update (password) |

---

*Coordinator updates this file when canonical locations change.*
