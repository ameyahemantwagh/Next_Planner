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

Check Users in PostgreSQL - docker exec Next-Planner-PostgreSQL psql -U postgres -d next_planner -p 9001 -c "SELECT id,email,email_verified,created_at FROM users ORDER BY created_at DESC LIMIT 10;"


Verift Account - docker exec Next-Planner-PostgreSQL psql -U postgres -d next_planner -p 9001 -c "UPDATE users SET email_verified = true WHERE email='ameyahemantwagh@gmail.com'; SELECT id,email,email_verified,created_at FROM users WHERE email='ameyahemantwagh@gmail.com';"


Run Browser Like Sign In Flow - $s = New-Object Microsoft.PowerShell.Commands.WebRequestSession; try { $signin = Invoke-RestMethod -Uri 'http://localhost:9003/api/auth/signin' -Method Post -Body '{"email":"test+agent@example.com","password":"password123"}' -ContentType 'application/json' -WebSession $s -ErrorAction Stop; Write-Output 'SIGNIN_RESPONSE:'; $signin | ConvertTo-Json -Depth 5 } catch { Write-Output 'SIGNIN_FAILED:'; $_.Exception.Response | Select-Object -ExpandProperty Content | ForEach-Object { Write-Output $_ } }; $cookies = $s.Cookies.GetCookies('http://localhost:9003'); $csrf = ($cookies | Where-Object { $_.Name -eq 'csrf_token' }).Value; Write-Output "CSRF:$csrf"; try { $refresh = Invoke-RestMethod -Uri 'http://localhost:9003/api/auth/refresh' -Method Post -Headers @{ 'x-csrf' = $csrf } -WebSession $s -ErrorAction Stop; Write-Output 'REFRESH_RESPONSE:'; $refresh | ConvertTo-Json -Depth 5 } catch { Write-Output 'REFRESH_FAILED:'; $_.Exception.Response | Select-Object -ExpandProperty Content | ForEach-Object { Write-Output $_ } }


Testing of protected API call using the access_token - $signin = Invoke-RestMethod -Uri 'http://localhost:9003/api/auth/signin' -Method Post -Body '{"email":"test+agent@example.com","password":"password123"}' -ContentType 'application/json' -ErrorAction Stop; $token = $signin.access_token; Write-Output "ACCESS_TOKEN:$token"; Invoke-RestMethod -Uri 'http://localhost:9003/api/auth/sessions' -Method Get -Headers @{ Authorization = "Bearer $token" } -ErrorAction Stop | ConvertTo-Json -Depth 5   
ACCESS_TOKEN:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMjdjNzM0MS1mMzM3LTRkYzMtYmY5MC0yYmJkMDJhNmJkMjkiLCJleHAiOjE3NjkxMTM3MjMsImlhdCI6MTc2OTExMjgyM30.pQb44TZN1pz3klY3F3psAL907MnRQvXbnQlzqyLkW_8
