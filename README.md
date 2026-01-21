# Next Planner - Auth Prototype

This workspace contains a minimal prototype for the Sign In / Sign Up flow:

- `backend/` - FastAPI app implementing signup, signin, refresh, verify-email, forgot/reset flows (dev-only behavior: prints links to console).
 - `frontend/` - Next.js app with simple pages (`/` (signup), `/signin`, `/verify-email`, `/forgot-password`).
- `.devops/docker-compose.yml` - PostgreSQL service for local dev.

Quick start (Linux / macOS / Windows with WSL or Docker Desktop):

1. Start PostgreSQL (optional - app can run with SQLite):

```bash
docker compose -f ./.devops/docker-compose.yml up -d
```

2. Backend:

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate   # Windows
pip install -r requirements.txt
# copy .env.example to .env and set JWT_SECRET and DATABASE_URL if needed
uvicorn app.main:app --reload --port 8000
```

3. Frontend:

```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

Notes:
- This is a minimal demo. Replace printed email links with a real email provider.
- For production: enable HTTPS, secure cookie flags, proper JWT secrets, and stronger Argon2 parameters.
 - For production: enable HTTPS, secure cookie flags, proper JWT secrets, and stronger Argon2 parameters.
 - To enable Redis-backed rate limiting, set `REDIS_URL` and start the Redis service in docker-compose (the provided compose file includes Redis).
 - Cookie security: set `ENV=production` in your environment to ensure refresh cookies are set with `Secure` flag. For local development you can set `ENV=development`.
