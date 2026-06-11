# CURRENT TASK — SYNC Board

> **Для Senya:** ставь задачи здесь.  
> **Для Coordinator:** читай перед ревью PR.  
> **Для всех агентов:** проверяй перед началом работы.

**Репозиторий:** https://github.com/oleksiipyl/romi-estimate  
**Координатор:** `docs/COORDINATOR.md`  
**Senya (Orchestrator):** `docs/AGENT_SENYA.md`

---

## Active Tasks

| ID | From | To | Branch | Status |
|----|------|-----|--------|--------|
| T-001 | Coordinator | Senya | — | ✅ Senya re-linked to Coordinator |
| T-002 | Senya | FRONTEND | `cursor/design-fix-v4` | PR #4 open — compact UI v4 |
| T-003 | Senya | COORDINATOR | `cursor/senya-coordinator-link-1c4b` | In progress — restore agent links |

---

## TASK — 2026-06-11 — Senya ↔ Coordinator Link

**From:** Main Cursor Coordinator  
**To:** Senya (Orchestrator)  
**Priority:** high

### Что сделано
- Восстановлены docs координатора и реестр агентов
- Создан `docs/AGENT_SENYA.md` — Senya знает где координатор
- Создан `docs/CURRENT_TASK.md` — общая доска SYNC
- Cursor rules: `.cursor/rules/00-coordinator.mdc`, `01-all-agents.mdc`, `02-senya.mdc`

### Как Senya находит координатора
1. Открыть репозиторий `oleksiipyl/romi-estimate`
2. Прочитать `docs/COORDINATOR.md`
3. Задачи писать в `docs/CURRENT_TASK.md`
4. Статус — `docs/PROJECT_STATUS.md`

### Acceptance
- [x] AGENT_SENYA.md существует
- [x] CURRENT_TASK.md существует
- [x] Coordinator docs в main (via PR)
- [ ] Alex подтвердил что Senya видит задачи

---

## Next (Senya → команда)

_Добавляй новые задачи ниже:_

```markdown
## TASK — [дата] — [название]
**From:** Senya
**To:** [агент]
**Branch:** cursor/xxx-1c4b

### Что сделать
...

### Acceptance
- [ ] ...
```

---

*Обновляй этот файл при каждой новой задаче.*
