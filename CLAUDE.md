# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run

```bash
# Start everything
docker compose up -d --build

# Rebuild one service
docker compose up -d --build backend     # or: frontend

# View logs
docker compose logs backend -f
docker compose logs frontend -f

# Backend hot-reload (dev)
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend dev server (runs on 5173, proxies /api to localhost:8000)
cd frontend && npm run dev

# Backend runs on :8000, frontend on :5200 (production) or :5173 (dev)
```

## Architecture

**Stack**: Python 3.12 + FastAPI + SQLAlchemy 2.0 + PostgreSQL 15 | Vue 3 + Element Plus + Pinia + Vite | Docker Compose

### Backend (`backend/app/`)

6 routers, 12 models, 1 schemas file, 3 utility modules.

- **`models.py`** — All 12 SQLAlchemy models. `BaseModel` provides `created_at`/`updated_at` on every table.
- **`schemas.py`** — All Pydantic request/response schemas.
- **`routers/auth.py`** — Login (`/api/auth/login` returns `access_token` + `user`), logout, `/auth/me`
- **`routers/admin.py`** — User/department/category CRUD + audit log viewer (`/api/admin/*`)
- **`routers/instruments.py`** — Instrument CRUD, Excel import/export, clear-all (`/api/instruments/*`)
- **`routers/calibration.py`** — Calibration records CRUD, expiring warnings, agency management (`/api/calibration/*`)
- **`routers/contracts.py`** — Contracts + items + execution records + auto-reconciliation (`/api/contracts/*`)
- **`routers/supervision.py`** — Supervision executions (with embedded check_items JSONB), auto-NCR generation, NCR lifecycle (`/api/supervision/*`)
- **`utils/auth.py`** — Password hashing (bcrypt), JWT creation/verification, `get_current_user`, `require_role(roles)`, `apply_department_filter`, `require_module(name)`
- **`utils/audit.py`** — `log(db, user_id, action, target_type, ...)` writes to `audit_logs`

### Frontend (`frontend/src/`)

- **`api/`** — Axios functions grouped by domain. Base instance in `index.js` auto-attaches Bearer token and redirects to `/login` on 401.
- **`store/user.js`** — Pinia store: token, userInfo, `isAdmin`, `canAccessModule(name)`.
- **`router/index.js`** — Route guards check token existence and module permissions.
- **`views/`** — `Dashboard.vue`, `Login.vue`, plus folders: `instruments/`, `calibration/`, `contract/`, `supervision/`, `system/`, `layout/`.

## API Conventions

### Response format
Lists: `{ "data": [...], "meta": { "total": N, "page": N, "page_size": N } }`
Single: `{ "data": { ... } }`
Error: HTTP status + `{ "detail": "message" }`

Exception: `/api/auth/login` returns `{ "access_token": "...", "token_type": "bearer", "user": {...} }` directly (no `data` wrapper).

### Pagination
All list endpoints accept `?page=1&page_size=20`. Page size capped at 100.

## Database Design

PostgreSQL 15. Key decisions:

- **Unified JSONB `fields`** on instruments, calibration_records, calibration_contracts, contract_items, execution_records, non_conformities. All business attributes live here — no fixed columns beyond ids and foreign keys.
- **`department_id`** on every permission-relevant table enables simple `WHERE department_id = ?` filtering.
- **`audit_logs`** records every create/update/delete with user, target type/id, JSONB `changes`, and `summary`.

Instrument code format: `INS-{YYYYMMDD}-{6-hex}` (uses `uuid.uuid4().hex[:6]`).

## Permission System

**Roles**: `admin` (all), `system_manager` (view all + audit), `dept_measurer` (manage own dept), `dept_leader` (approve own dept), `readonly`

**Department isolation**: `apply_department_filter(query, model, user)` — admin/system_manager see everything; others see only their `department_id`. Exception: "工艺质量管理科" department sees all.

**Module permissions**: Stored in `users.module_permissions` JSONB array. `null` = all modules. Otherwise only listed modules. Frontend: `userStore.canAccessModule(name)`. Backend: `require_module(name)`.

## Seed Data

Run via `python seed.py` (called by entrypoint.sh):
- **admin / admin123** — system administrator
- **dage / dage123** — system manager in 工艺质量管理科

## Key Domain Patterns

- Instrument `fields` keys are Chinese labels (e.g., "仪器名称", "规格型号") — they come directly from Excel headers during import. Frontend dynamic columns are extracted by collecting all unique keys across loaded items.
- `SupervisionExecution.check_items` is a JSONB array of `[{item_name, standard, result}]` — no separate check_items table. Updating with `result: "fail"` auto-generates NonConformity records.
- Auto-reconciliation runs on every execution record creation — generates `ReconciliationDiff` rows for quantity/amount/missing mismatches.
- All write operations are logged to `audit_logs` with JSONB changes.
