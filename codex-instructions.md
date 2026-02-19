# Codex Instructions - Next Planner

## Project Summary
Next Planner is a full-stack prototype with two major areas:
- Auth system (email/password, verification, reset, refresh token rotation, CSRF double-submit, sessions).
- Planner system (plans, buckets, tasks, comments, memberships) with event logging and optional Redis pub/sub for realtime.

Backend: FastAPI + SQLAlchemy + JWT + Argon2.
Frontend: Next.js pages with simple forms and a minimal planner board view.

## Repository Map
Top-level (excluding .git and node_modules):
- `backend/` FastAPI service
- `frontend/` Next.js client
- `docker-compose.yml` Dev stack (Postgres, Redis, backend, frontend)
- `README.md` Quick start notes
- `.env` Local environment values
- `.github/`, `.vscode/` Dev tooling

### File Tree (key files)
- `backend/Dockerfile`
- `backend/requirements.txt`
- `backend/requirements_test.txt`
- `backend/app/__init__.py`
- `backend/app/main.py`
- `backend/app/database.py`
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/utils.py`
- `backend/app/auth.py`
- `backend/app/planner_routes.py`
- `backend/app/planner_events.py`
- `backend/app/websockets.py`
- `backend/app/rate_limiter.py`
- `backend/app/emailer.py`
- `backend/tests/test_rate_limit_and_csrf.py`
- `frontend/Dockerfile`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/hooks/usePlan.js`
- `frontend/providers/AuthProvider.jsx`
- `frontend/providers/WebsocketProvider.jsx`
- `frontend/pages/_app.js`
- `frontend/pages/index.js`
- `frontend/pages/signin.js`
- `frontend/pages/signup.js`
- `frontend/pages/verify-email.js`
- `frontend/pages/forgot-password.js`
- `frontend/pages/trial.js`
- `frontend/pages/sessions.js`
- `frontend/pages/board/[id].js`
- `frontend/components/planner/PlannerBoard.jsx`
- `frontend/components/planner/BucketColumn.jsx`
- `frontend/components/planner/TaskCard.jsx`
- `frontend/components/planner/TaskDetailPane.jsx`
- `frontend/styles/globals.css`

## Backend Architecture
### App Entry
- `backend/app/main.py`
- Creates the FastAPI app, registers auth + planner routes, and adds security headers.
- On startup: creates DB tables and spawns a Redis subscriber task for websocket routing.
- CORS allows only `FRONTEND_URL` (default `http://localhost:9005`) with credentials.

### Auth Module
- `backend/app/auth.py`
- Routes are under `/api/auth`.
- Uses JWT access tokens and rotating refresh tokens stored server-side.

Auth flows:
- Signup: create user, hash password (Argon2), create one-time email verification token, send or print link.
- Signin: validate credentials, require verified email, issue access token and refresh cookie, set CSRF cookie.
- Refresh: CSRF double-submit check, verify refresh token in DB, revoke old token, issue new refresh token + access token.
- Logout: CSRF check, revoke refresh token, clear cookies.
- Verify email: validate token and mark user verified.
- Forgot password: generate one-time reset token, always return generic response to avoid enumeration.
- Reset password: validate token, set new hash, revoke all refresh tokens.
- Sessions: list sessions, revoke one or all.
- Trial: 24-hour access token for unverified users within 1 day of signup.

### Planner Module
- `backend/app/planner_routes.py`
- Routes are under `/api/planner` and require `get_current_user` auth.

Planner flows:
- Plans: create and snapshot a plan; creator becomes owner member.
- Buckets: create, update, delete; membership required.
- Tasks: create, patch, move; membership required.
- Comments: add comment to task.
- Members: owner can add members with role.

### Eventing and Realtime
- `backend/app/planner_events.py`
- `append_event` persists event rows and publishes to Redis (best effort).
- Event versioning: increments by reading last event for the aggregate.
- Redis channel for events: `{aggregate_type}:{aggregate_id}`.

- `backend/app/websockets.py`
- Websocket endpoint at `/ws`.
- Server expects an initial JSON message with `client_id` or `user_id`.
- Redis subscriber listens on `broadcast` channel and routes messages with `target_user` to a matching websocket connection.

### Rate Limiting
- `backend/app/rate_limiter.py`
- In-memory by default; Redis limiter when `REDIS_URL` is set.
- IP limiter: 100 requests/minute; auth limiter: 10 requests/minute.
- Redis errors fail open (allow request).

### Security and Crypto
- Password hashing: Argon2 (`argon2.PasswordHasher` with time_cost=3, memory_cost=65536, parallelism=2).
- Access tokens: JWT HS256 signed with `JWT_SECRET`.
- Refresh tokens: random opaque token in cookie, HMAC-SHA256 hash stored in DB.
- CSRF: double-submit with `csrf_token` cookie + `x-csrf` header on refresh/logout.
- Cookies: refresh token is HttpOnly, CSRF is readable; secure flag enabled when `ENV=production`.

### Data Models
- `backend/app/models.py`
- Auth: `User`, `RefreshToken`, `OneTimeToken`.
- Planner: `Plan`, `Membership`, `Bucket`, `Task`, `Checklist`, `Attachment`, `Comment`, `Event`, `Snapshot`.
- Planner ordering uses `order_hint` (epoch ms string) in buckets and tasks.
- Task changes increment `version`.

## Frontend Architecture
### Auth UI
- `frontend/pages/index.js` is the current sign-up form (root route).
- `frontend/pages/signin.js` for sign-in; stores access token in `localStorage`.
- `frontend/pages/verify-email.js` posts token from query string.
- `frontend/pages/forgot-password.js` posts email.
- `frontend/pages/trial.js` requests 24h trial access.
- `frontend/pages/sessions.js` lists sessions and allows revocation; uses CSRF cookie for state-changing calls.

### Planner UI
- `frontend/pages/board/[id].js` loads a plan snapshot using `usePlan` (SWR + axios).
- `frontend/components/planner/*` render buckets and tasks.

### Providers
- `frontend/providers/AuthProvider.jsx` manages access token and user state.
- `frontend/providers/WebsocketProvider.jsx` opens websocket and exposes send/connected state.

### Styling
- `frontend/styles/globals.css` sets a teal-themed palette and basic form styles.

## API Summary
### Auth (`/api/auth`)
- `POST /signup`
- `POST /signin`
- `POST /refresh`
- `POST /logout`
- `POST /verify-email`
- `POST /forgot-password`
- `POST /reset-password`
- `GET /sessions`
- `POST /sessions/revoke`
- `POST /sessions/revoke-all`
- `POST /trial`

### Planner (`/api/planner`)
- `POST /plans`
- `GET /plans/{plan_id}/snapshot`
- `POST /plans/{plan_id}/buckets`
- `PATCH /buckets/{bucket_id}`
- `DELETE /buckets/{bucket_id}`
- `POST /plans/{plan_id}/tasks`
- `PATCH /tasks/{task_id}`
- `PATCH /tasks/{task_id}/move`
- `POST /tasks/{task_id}/comments`
- `POST /plans/{plan_id}/members`

## Environment Variables
Common (from `.env` and docker-compose):
- `DATABASE_URL`
- `JWT_SECRET`
- `FRONTEND_URL`
- `BACKEND_URL`
- `BACKEND_PORT`
- `FRONTEND_PORT`
- `REDIS_URL`
- `ENV` (set to `production` to enable secure cookies)
- SMTP: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL`

## Running Locally
- Backend: `uvicorn app.main:app --port 9003 --reload`
- Frontend: `npm run dev` (default 3000 or use `FRONTEND_PORT` in docker)
- Docker: `docker compose up` uses `docker-compose.yml` for Postgres, Redis, backend, frontend.

## Tests
- `backend/tests/test_rate_limit_and_csrf.py` checks rate limiting and CSRF behavior.
- Run: `pytest -q` from repo root (backend deps installed).

## Implementation Notes and Gaps
- `frontend/hooks/usePlan.js` uses `swr` and `axios`, but `frontend/package.json` does not list them.
- `frontend/pages/board/[id].js` expects `plan.buckets`, but the backend snapshot returns `buckets` as a top-level field separate from `plan`.
- `frontend/pages/_app.js` does not wrap `AuthProvider` or `WebsocketProvider`, so `AuthContext` and websocket usage will be null unless added.

## Development Conventions
- Prefer writing new backend logic in `backend/app` and exposing through a router.
- Keep auth flows consistent with CSRF and refresh rotation patterns already used.
- When adding planner mutations, append events via `append_event` for auditability and realtime.
- Use SQLAlchemy models in `backend/app/models.py` and add Pydantic schemas in `backend/app/schemas.py` as needed.
