# agents.md — Agentic Workflow Rules

Guidance for AI agents operating autonomously (e.g. Claude Code, Cursor, Copilot
Workspace) on this repository.

---

## Allowed Autonomous Actions

An agent may perform these without human confirmation:

- Run `python -m pytest` and read output
- Read any source file
- Add a new test to an existing test file
- Add a field to a schema with a corresponding test
- Fix a failing test caused by a typo or off-by-one error
- Install packages listed in `requirements.txt`

---

## Requires Human Confirmation Before Proceeding

An agent MUST pause and present a plan before:

- Modifying the database schema (`models/` or `migrations/`)
- Changing the HTTP contract (URL shape, status codes, response body shape)
- Adding a new dependency to `requirements.txt` or `package.json`
- Deleting any file
- Changing error handling behaviour in `app/errors.py`
- Any change that would break existing passing tests

---

## Verification Gate

After any code change, an agent MUST:

1. Run `python -m pytest tests/ -v` from `backend/`
2. Confirm all tests pass before reporting success
3. If tests fail, attempt to fix — do not report the task as done

An agent that reports success without a green test run is incorrect.

---

## Context an Agent Should Always Load First

Before making changes, read:

1. `ai-guidance/claude.md` — architecture rules and forbidden patterns
2. `backend/app/services/habit_service.py` — business logic source of truth
3. `backend/app/schemas/__init__.py` — validation contracts
4. The relevant test file for the area being changed

---

## Scope Boundaries

This project is intentionally small. Agents should resist scope creep.

**In scope:** habits CRUD, daily/weekly frequency, completions, streaks, archiving.

**Out of scope (do not implement unless explicitly asked):**
- User authentication or multi-tenancy
- Push notifications or reminders
- Third-party integrations (calendar sync, etc.)
- Admin dashboards
- Rate limiting or API keys

If a user request implies out-of-scope work, the agent should note the boundary and
ask for explicit confirmation before proceeding.

---

## Code Style

- Python: follow existing patterns (type hints on function signatures, docstrings on
  public methods, `snake_case` everywhere)
- React: functional components with hooks, inline styles matching the design system
  variables in `index.css`
- No linter is configured — use human judgment and match the existing style

---

## Security Reminders

- Validate ALL input through Marshmallow schemas before it reaches service/model layer
- Never expose raw SQLAlchemy exceptions to API responses
- Do not log request bodies (may contain user data)
- The `SECRET_KEY` must come from environment variables — never hardcode
