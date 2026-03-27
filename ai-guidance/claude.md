# claude.md — AI Agent Guidance for Habit Tracker

This file constrains how AI agents (Claude, Copilot, etc.) should contribute to this
codebase. It exists to protect system integrity, maintain architecture boundaries, and
ensure generated code is verifiable and reviewable.

---

## Project Overview

**Streaks** is a habit-tracking API + React SPA.

- Backend: Python 3.12 + Flask 3, SQLAlchemy 2, Marshmallow, pytest
- Frontend: React 18, React Router 6, Axios
- Database: MySQL (prod), SQLite in-memory (tests)

---

## Architecture Rules — NEVER Violate These

### Backend layering

```
Route  →  Schema (validate)  →  Service (logic)  →  Model (data)
```

- **Routes** are thin. They: parse JSON, call a schema, call a service, return JSON.
  They do NOT contain SQL, business logic, or direct model access.
- **Schemas** (Marshmallow) validate ALL incoming data before it reaches the service.
  Never bypass schema validation.
- **Services** (`HabitService`) own all business rules: streak logic, duplicate
  prevention, cascade behaviour. Keep services as static methods on a class — no
  global state.
- **Models** hold domain helpers (`is_completed_on`, `current_streak`, `to_dict`).
  Models do NOT call services.

### Forbidden patterns

```python
# ❌ Never put business logic in a route
@habits_bp.route("/<int:id>", methods=["DELETE"])
def delete(id):
    Habit.query.filter_by(id=id).delete()   # wrong — bypasses service + cascade
    db.session.commit()

# ✅ Always delegate to the service
def delete(id):
    HabitService.delete_habit(id)           # correct
```

```python
# ❌ Never skip validation
data = request.get_json()
habit = Habit(**data)                       # untrusted input → model

# ✅ Always validate first
data = HabitCreateSchema().load(request.get_json() or {})
```

---

## Database Constraints

- The `UNIQUE(habit_id, completed_on)` constraint on `completions` is intentional.
  It is the authoritative guard against duplicate completions. Do not remove it.
- Always handle `IntegrityError` in `HabitService.log_completion` and raise
  `DuplicateCompletionError` — never let SQLAlchemy errors leak to routes.
- Use `db.session.get(Model, pk)` not `Model.query.get(pk)` (SQLAlchemy 2.x style).

---

## Test Requirements

- Every new service method needs at least one happy-path and one error-path test.
- Every new route needs a test for: success, 404, and invalid input (422).
- Tests use SQLite in-memory via the `testing` config. Do NOT require MySQL for tests.
- Never mock the database in unit tests — use the in-memory DB and real queries.
- Fixtures live in `tests/conftest.py`. Do not duplicate fixture logic.

---

## Error Handling Contract

| Situation                     | HTTP Status | Body shape                        |
|-------------------------------|-------------|-----------------------------------|
| Validation failure            | 422         | `{ "errors": { field: [msgs] } }` |
| Resource not found            | 404         | `{ "error": "..." }`              |
| Duplicate completion          | 409         | `{ "error": "..." }`              |
| Unhandled server error        | 500         | `{ "error": "..." }`              |

All errors must use one of these shapes. Never return a bare string or HTML error.

---

## Frontend Rules

- `src/api/index.js` is the **only** file that calls `axios`. Components use hooks.
- `src/hooks/useHabits.js` is the **only** file that calls API functions. Pages use
  the hook.
- Components receive data and callbacks via props — they do not fetch data directly.
- All user-facing error messages come from the API error normaliser in `api/index.js`.
- Do not add client-side routing beyond what exists. Keep it a single-page app.

---

## What AI Should NOT Do

- Do not introduce new dependencies without noting them in the README.
- Do not change the DB schema without creating a migration (`flask db migrate`).
- Do not add authentication/sessions — out of scope for this version.
- Do not use `any` types or skip prop validation.
- Do not silently catch errors — always surface them to the user or log them.
- Do not add environment-specific logic outside of `app/config.py`.
- Do not commit `.env` files or hardcode credentials.

---

## Extending This System

When adding a new feature (e.g. habit categories):

1. Add the DB column + migration.
2. Add a field to `HabitCreateSchema` / `HabitUpdateSchema` with validation.
3. Add the logic to `HabitService` with a test.
4. Add/update the route — keep it thin.
5. Update `Habit.to_dict()` to include the new field.
6. Update the frontend `api/index.js` if the payload changes.
7. Add/update the React component.

No step should require modifying more than 2 layers simultaneously.
