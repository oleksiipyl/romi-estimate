# CursorAgentRomeEstimate — ROMI Estimate

> **Project:** CursorAgentRomeEstimate  
> **Product:** ROMI Estimate — glass repair price calculator  
> **Coordination:** Main Cursor Coordinator + agent team (see `docs/COORDINATOR.md`)

Simple web calculator for glass repair estimates.
> Open in browser → enter dimensions → get price range.
> No AI required. Works from price database directly.

## What It Does

1. Technician or operator opens page in browser
2. Selects glass type (Single Pane, Double Pane, Tempered, etc.)
3. Enters dimensions (width × height with fractions)
4. Selects additional work (hardware, frame, screen, etc.)
5. Adds comments/difficulty notes
6. Gets price range instantly (min–max)

## Admin Panel

- View and adjust prices
- Enable/disable services
- Set markup multipliers
- No code changes needed

## Tech Stack

- Backend: Python + FastAPI
- Database: SQLite (simple, no server needed)
- Frontend: HTML + Tailwind CSS (no framework, just works)
- Hosting: Any static host or Mac Mini

## Status
🚧 In Development

---
Built by: Senya + Alex (American Glazier)
Started: 2026-06-10
