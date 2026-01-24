# Next Planner — Copilot Instructions

## Project Overview

Next Planner is an authentication prototype used by a Next.js frontend and a FastAPI backend. It implements email/password sign-up and sign-in flows, CSRF-protected refresh token rotation, session management, password resets, email verification, and a short trial access flow.

## Features

- Sign up / Sign in with email and password.
- Email verification via one-time token.
- Password reset via one-time token.
- Access tokens (JWT) + HttpOnly refresh cookies (rotating refresh tokens).
- CSRF double-submit protection for cookie-based refresh/logout flows.
- Session listing and revocation (per-session and revoke-all).
- 24-hour trial access for unverified users within first day.
- Rate limiting with pluggable Redis or in-memory backends.
- SMTP-based email sending (with dev fallback printing link).
- Security headers middleware (CSP, HSTS, X-Frame-Options, etc.).

## Folder Structure (high-level)

- backend/
  - app/
    - main.py              — FastAPI app, middleware, router registration
    - auth.py              — All authentication routes and flows
    - database.py          — SQLAlchemy engine and session
    - models.py            — ORM models (User, RefreshToken, OneTimeToken)
    - schemas.py           — Pydantic request/response models
    - utils.py             — crypto helpers, JWT, password hashing
    - rate_limiter.py      — In-memory and Redis-backed rate limiter
    - emailer.py           — SMTP email sending with dev fallback
- frontend/
  - pages/                 — Next.js pages (signup, signin, sessions, etc.)
  - styles/                — CSS assets
- tests/
  - test_rate_limit_and_csrf.py  — automated tests covering limit and CSRF checks

Files to inspect for details: [backend/app/auth.py](backend/app/auth.py), [backend/app/utils.py](backend/app/utils.py), [frontend/pages](frontend/pages)

## Backend: Routes and Behaviors

- Root: `GET /` — health check.
- Auth router prefix: `/api/auth` (see [backend/app/auth.py](backend/app/auth.py)).

Key endpoints (behavior summary):
- `POST /api/auth/signup` — creates user, stores password hash (Argon2), creates email verification one-time token, sends verification link.
- `POST /api/auth/signin` — verifies credentials, ensures email verified, issues short-lived access token (JWT) and creates a server-side refresh token record. Sets `refresh_token` HttpOnly cookie and a non-HttpOnly `csrf_token` cookie (double-submit).
- `POST /api/auth/refresh` — requires `x-csrf` header matching `csrf_token` cookie. Rotates refresh tokens: marks old token revoked, issues new refresh token cookie and same-origin CSRF cookie, and returns a fresh access token.
- `POST /api/auth/logout` — requires CSRF check, revokes refresh token record and clears cookies.
- `POST /api/auth/verify-email` — validate one-time token (hashed in DB), marks user as verified.
- `POST /api/auth/forgot-password` — creates password reset one-time token and prints/sends link; response is always generic to avoid email enumeration.
- `POST /api/auth/reset-password` — validate token and set new password; revokes existing refresh tokens.
- `GET /api/auth/sessions` — returns session info from refresh tokens for current user (requires Bearer JWT access token).
- `POST /api/auth/sessions/revoke` — revoke a single session (requires access token + CSRF header when using cookie flows where applicable).
- `POST /api/auth/sessions/revoke-all` — revoke all sessions for current user.
- `POST /api/auth/trial` — 24h JWT access if user exists and is within 1 day of signup and email not verified.

## Data Models

See [backend/app/models.py](backend/app/models.py):
- `User` — id (UUID string), email, email_verified flag, password_hash, status enum (active/suspended/deleted), timestamps.
- `RefreshToken` — server-side token record with hashed token, device_info, expiry, revoked flag, created_at.
- `OneTimeToken` — hashed token, type enum (email_verification, password_reset, ...), expiry, used flag.

## Crypto, Tokens, and Algorithms

- Password hashing: Argon2 via `argon2.PasswordHasher` (parameters: time_cost=3, memory_cost=65536, parallelism=2).
- Random tokens: uses `secrets.token_urlsafe()` for opaque token generation.
- Token hashing: HMAC-SHA256 using `JWT_SECRET` to store hashed tokens safely in DB (`utils.hash_token`).
- Access tokens: JWT (`HS256`) signed with `JWT_SECRET`, `sub` claim holds user id, `exp` for expiry. Created with `utils.create_access_token` and validated via `utils.decode_access_token`.
- Refresh token rotation: plaintext token stored in cookie, hashed copy stored in DB; on refresh the old DB token is marked revoked and a new hashed record is created (rotating strategy).
- CSRF protection: double-submit model — non-HttpOnly `csrf_token` cookie is set alongside `refresh_token` cookie; refresh and logout endpoints expect `x-csrf` header matching cookie.

## Rate Limiting

Implemented in [backend/app/rate_limiter.py](backend/app/rate_limiter.py):
- Two backends: `InMemoryLimiter` (deque per key) and `RedisLimiter`.
- Configured via `REDIS_URL` env var; when available `RedisLimiter` is used.
- Two limiters:
  - `ip_limiter`: default 100 requests per minute per IP.
  - `auth_limiter`: default 10 requests per minute for auth-sensitive keys.
- Fail-open behavior: if Redis errors, logs a warning and allows requests.

## Security & Design Rules

- CORS: configured in `main.py` to only allow `FRONTEND_URL` origin with credentials.
- Security headers: middleware sets HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, and a minimal CSP.
- Cookies:
  - `refresh_token`: HttpOnly, Secure (in `production`), `samesite='lax'`, duration 14 days.
  - `csrf_token`: Non-HttpOnly so JS can read and double-submit; same flags as above except HttpOnly=False.
- Token expiry policy:
  - Access token: short-lived (default 15 minutes).
  - Refresh token: 14 days.
  - One-time tokens: email verification 30 minutes, password reset 1 hour.
- Password reset and other flows avoid user enumeration by returning generic success messages.
- Error handling: endpoints return appropriate HTTP status codes (401/403/400/429/etc.).

## Memory Management & Resource Handling

- Database sessions: `get_db()` yields a session and ensures `db.close()` in `finally` to avoid leaks.
- In-memory rate limiter: stores timestamps in deques keyed by IP or key; this increases memory proportional to unique keys in the window. Prefer Redis in production to avoid memory growth in multi-process deployments.
- Redis usage: optional via `REDIS_URL` — recommended for horizontal scaling.
- JWT secret, SMTP, DB connections are read from environment variables; secrets should be rotated and stored securely (Vault or cloud secret manager).

## Frontend: Pages and UI Flow

Frontend pages are simple Next.js React components under `frontend/pages` implementing forms and client logic.

Pages summary:
- `/` — Sign Up (`frontend/pages/index.js`): collects first name, last name, email, password; posts to `/api/auth/signup`. Shows dev fallback links printed by backend if SMTP not configured.
- `/signin` — Sign In (`frontend/pages/signin.js`): posts to `/api/auth/signin` with `credentials: 'include'` to receive cookies. Stores `access_token` in `localStorage` and redirects.
- `/verify-email` — reads `?token=` query param and posts to `/api/auth/verify-email`.
- `/forgot-password` — posts email to `/api/auth/forgot-password`.
- `/trial` — requests trial access; on success stores `access_token` in `localStorage`.
- `/sessions` — lists active sessions by calling `/api/auth/sessions` with `Authorization: Bearer <access_token>` and allows revocation via `sessions/revoke` and `revoke-all`. Uses CSRF token from cookie when calling endpoints that require it.

UI design rules:
- Minimal, accessible forms.
- Buttons show loading state text.
- Social OAuth links present but backend OAuth endpoints are placeholders in frontend (matching expected backend paths).

## Tests and Test Parameters

Automated tests exist in `tests/test_rate_limit_and_csrf.py`. Key test areas to cover manually and via automated scripts:

Test parameters (defaults and examples):
- `JWT_SECRET`: dev-secret by default; set a strong secret for real testing.
- `DATABASE_URL`: defaults to `sqlite:///./dev.db` for local tests; use PostgreSQL for integration tests.
- `REDIS_URL`: optional — provide a test Redis instance to validate RedisLimiter behavior.
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`: optional for sending real emails — otherwise backend prints links to stdout.
- Rate-limit thresholds: IP=100/min, auth key=10/min (adjust env or constants in `rate_limiter.py` for aggressive testing).

Testing matrix (what to validate):
- Auth correctness: signup, email verification, signin, refresh token rotation, logout, forgot/reset password, trial flow.
- Security: CSRF enforcement on refresh and logout endpoints, cookie flags set correctly, CORS restricted origin behavior.
- Rate limiting: IP-based and key-based limiting, both with in-memory and Redis backends.
- Session management: listing sessions, revoking single session, revoke-all.
- Token expiry behavior: expired one-time tokens rejected, expired refresh tokens rejected.
- Failure modes: Redis unavailable (rate limiter falls back), SMTP misconfigured (dev fallback prints links), DB unavailable (appropriate exceptions).

## Step-by-step Manual Testing Instructions

Prerequisites:
- Python 3.10+ and dependencies from `backend/requirements.txt`.
- Node.js + npm for frontend, or run frontend via `next`.
- Optional: Redis and PostgreSQL for full integration.

Start backend locally (example):

```powershell
cd backend
# create virtual env and install deps if needed
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --port 9003 --reload
```

Start frontend locally:

```bash
cd frontend
npm install
npm run dev
# By default Next.js runs on http://localhost:3000
```

Manual test steps:
1. Sign-up flow
   - Open frontend sign-up page `/`.
   - Submit valid email and password.
   - Backend prints verification link in console if SMTP not configured; copy link.
   - Visit `/verify-email?token=<token>` or use frontend's verify page to POST token.
   - Confirm response: "Email verified".

2. Sign-in and token lifecycle
   - Sign in on `/signin` with verified account.
   - Confirm `refresh_token` cookie and `csrf_token` cookie are set (use browser dev tools). `refresh_token` should be HttpOnly.
   - Confirm `access_token` stored in `localStorage` and authenticated pages load.
   - Manually call `POST /api/auth/refresh` with header `x-csrf` set to value of `csrf_token` cookie and cookie `refresh_token` present; expect a new `access_token` and rotated `refresh_token` cookie.
   - Attempt refresh without `x-csrf` or with mismatched cookie; expect 403.

3. Session management
   - Visit `/sessions` while signed in; confirm sessions listing contains device info and created/expiry.
   - Revoke a session and confirm it disappears or shows revoked=true.
   - Revoke all sessions and ensure subsequent refresh attempts fail (client must re-login).

4. Password reset
   - Use `/forgot-password` with an existing user; backend prints reset link.
   - Use `/reset-password` endpoint with token and new password; confirm password updated and old refresh tokens revoked.

5. Rate limiting
   - Rapidly call signin/signup endpoints from same IP > auth limiter threshold (10/min) and confirm 429 responses.
   - Configure Redis (`REDIS_URL`) and repeat to ensure RedisLimiter path used.

6. Edge cases and hardening
   - Try expired or reused one-time tokens; expect 400 errors.
   - Suspend a user by modifying DB status to `suspended`, test forbidden responses.

Automated testing (example):
- Run `pytest -q` in repo root (ensure `tests/` is discoverable and dependencies installed).

## Recommended Environment Variables

- `DATABASE_URL` (e.g., postgres://... or sqlite:///./dev.db)
- `JWT_SECRET` (strong secret)
- `FRONTEND_URL` (for CORS/callbacks)
- `ENV` (set to `production` to enable secure cookie flags)
- `REDIS_URL` (optional)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL` (for email delivery)

## Maintenance Notes

- Rotate `JWT_SECRET` carefully; rotation invalidates existing access tokens.
- Use Redis for rate limiting in production for cross-process consistency.
- Consider storing device/user agent and IP at refresh token creation to assist session auditing.
- Add stricter CSP and CSRF SameSite policies for stricter security.

## Where to Look in Code

- App entry / middleware: [backend/app/main.py](backend/app/main.py)
- Auth flows and routes: [backend/app/auth.py](backend/app/auth.py)
- Models: [backend/app/models.py](backend/app/models.py)
- Utilities & crypto: [backend/app/utils.py](backend/app/utils.py)
- Rate limiter: [backend/app/rate_limiter.py](backend/app/rate_limiter.py)
- Emailer: [backend/app/emailer.py](backend/app/emailer.py)
- Frontend UIs: [frontend/pages](frontend/pages)

---

If you want, I can now:
- Add more detailed sequence diagrams for the auth lifecycle.
- Convert the manual test steps into runnable integration tests (pytest + httpx).
- Add CI workflow templates for automated testing.

