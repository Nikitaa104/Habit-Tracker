# Streaks — Habit Tracker

A small, well-structured habit-tracking application built with Python/Flask, React, and MySQL.

> Built as an assessment submission for Better Software.
> <img width="1919" height="913" alt="image" src="https://github.com/user-attachments/assets/00bafe9c-6eb1-4064-90c8-613e5bcaa7a0" />

<img width="1919" height="978" alt="image" src="https://github.com/user-attachments/assets/c9f75820-3b2f-43d7-b877-891e93368e6d" />

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node 18+
- MySQL 8+

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your MySQL credentials

# Create the database
mysql -u root -p -e "CREATE DATABASE habit_tracker_dev;"

flask db upgrade
python run.py
# → http://localhost:5000/api/health
```

### Frontend

```bash
cd frontend
npm install
npm start
# → http://localhost:3000
```

### Run Tests

```bash
cd backend
python -m pytest tests/ -v
# 35 tests, no MySQL required (SQLite in-memory)
```

---
<img width="1910" height="785" alt="image" src="https://github.com/user-attachments/assets/f8ea884d-eb11-47a7-8ac7-b539020faede" />

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health + DB connectivity check |
| GET | `/api/habits` | List habits (`?archived=true` for archived) |
| POST | `/api/habits` | Create habit |
| GET | `/api/habits/:id` | Get single habit |
| PATCH | `/api/habits/:id` | Update habit (partial) |
| DELETE | `/api/habits/:id` | Delete habit + completions |
| GET | `/api/habits/:id/completions` | List completions |
| POST | `/api/habits/:id/completions` | Log completion |
| DELETE | `/api/habits/:id/completions/:date` | Undo completion |

---

## Architecture

```
backend/
├── app/
│   ├── __init__.py        # App factory (create_app)
│   ├── config.py          # Dev / Test / Prod configs
│   ├── errors.py          # Global error handlers
│   ├── models/
│   │   ├── habit.py       # Habit model + domain logic
│   │   └── completion.py  # Completion model
│   ├── schemas/
│   │   └── __init__.py    # Marshmallow input validation
│   ├── services/
│   │   └── habit_service.py  # All business logic
│   └── routes/
│       ├── habits.py      # Thin HTTP handlers
│       ├── completions.py
│       └── health.py
└── tests/
    ├── conftest.py         # SQLite fixtures, per-test rollback
    ├── test_habits.py      # Route tests
    ├── test_completions.py # Route tests
    ├── test_service.py     # Domain logic unit tests
    └── test_health.py

frontend/
└── src/
    ├── api/index.js        # All Axios calls, error normalisation
    ├── hooks/useHabits.js  # All data-fetching logic
    ├── components/
    │   ├── HabitCard.js
    │   ├── HabitModal.js
    │   └── StatsBar.js
    └── pages/
        └── Dashboard.js

ai-guidance/
├── claude.md              # Architecture rules for AI agents
└── agents.md              # Agentic workflow constraints
```

### Request flow

```
HTTP Request
  → Route (parse + validate via Schema)
    → Service (business rules, raises typed exceptions)
      → Model (DB operations via SQLAlchemy)
        → Route (serialize to_dict() → JSON response)
```

---

## Key Technical Decisions

### 1. Service layer as the single logic boundary

All business rules live in `HabitService`. Routes are deliberately thin — they parse
input, delegate to the service, and serialise output. This means:

- Logic is testable without HTTP overhead
- Routes can't accidentally bypass validation
- Adding a new interface (CLI, async worker) reuses the same service

**Trade-off:** Slightly more files than a flat route-heavy approach. Worth it for
correctness and testability.

### 2. Database constraint as authoritative duplicate guard

The `UNIQUE(habit_id, completed_on)` constraint lives in the database — not just in
application code. This means duplicate completions are impossible even under concurrent
requests. The service catches `IntegrityError` and converts it to a typed
`DuplicateCompletionError` so callers get meaningful error handling, not raw SQL errors.

**Trade-off:** SQLite and MySQL handle constraint violation errors slightly differently,
which is why the test suite explicitly tests the 409 path.

### 3. Marshmallow schemas as the validation boundary

All input is validated at the schema layer before touching the service. Schemas handle:
type coercion, length limits, enum membership, hex colour format, and future-date
rejection. This keeps the service layer free of defensive null checks and lets
validation errors return structured `422` responses with per-field messages.

### 4. SQLite in tests, MySQL in production

Tests run against an in-memory SQLite database — no external services needed. This
makes the test suite fast (~0.5s for 35 tests) and runnable in CI with no setup.
The `create_app("testing")` factory swaps the DB URI via config, so tests exercise
real SQL — not mocks.

**Known limitation:** SQLite does not enforce the `Enum` column constraint at the DB
level (it stores strings freely), so the enum is enforced by the Marshmallow schema
instead. This is safe but worth noting.

### 5. Streak computed at read time

`current_streak()` is a Python method on the `Habit` model, computed from the loaded
`completions` relationship. It is not stored in the database.

**Trade-off:** For a user with years of data this would be slow. For the current scope
(personal habit tracker, <1000 completions per habit) it is fast enough and avoids a
class of bugs where a stored streak value gets out of sync.

**Extension path:** When needed, add a `streak` column and a background job that
recomputes it nightly, falling back to the computed version while the column is
backfilling.

---

## Known Weaknesses & Extension Paths

| Weakness | Impact | Fix when needed |
|----------|--------|-----------------|
| No authentication | Single-user only | Add Flask-JWT-Extended; user_id FK on Habit |
| Streak computed at read time | Slow for large history | Cache in DB column, recompute on completion change |
| No pagination | Large habit lists load fully | Add `?page=` + `?limit=` to list endpoints |
| No rate limiting | API is open | Add Flask-Limiter |
| Frontend has no offline support | Fails without backend | Add React Query for caching |

---

## AI Usage

AI tools (Claude) were used throughout this project. Here is an honest accounting:

**Where AI was used:**
- Initial project scaffolding and file structure
- Boilerplate (config, error handlers, CORS setup)
- Test case generation — AI suggested edge cases I then reviewed and kept/modified
- CSS design system variables

**Where I critically reviewed and changed AI output:**
- Streak algorithm: initial version didn't handle the "today not yet logged" case
  correctly. Rewrote to check yesterday as the fallback cursor.
- SQLAlchemy 2.x style: AI initially generated `Model.query.get()` (legacy). Updated
  to `db.session.get(Model, pk)`.
- Test isolation: initial conftest used `session` scope for DB setup without per-test
  cleanup, causing test pollution. Rewrote with per-test rollback + truncation.
- Error contract: AI initially returned different error body shapes across routes.
  Standardised to `{ error }` / `{ errors }` contract documented in claude.md.

**AI guidance files** (`ai-guidance/`) exist to constrain future AI contributions to
this codebase — preventing scope creep, enforcing the layering contract, and requiring
test verification before reporting success.
