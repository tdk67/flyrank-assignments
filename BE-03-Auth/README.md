# BE-03-Auth · Secure API with Supabase Auth

A FastAPI backend that implements user authentication using **Supabase** as the Identity Provider.
Users can sign up, log in, and log out. Protected routes verify JSON Web Tokens (JWTs) via a
reusable middleware dependency. The API is documented with Swagger UI (built into FastAPI).

> FlyRank Internship · Backend Track · Week 4 · Assignment A4

---

## How it works

Authentication follows a **trust triangle**:

```
1. CLIENT → SUPABASE   : sends email + password → gets back a JWT (access token)
2. CLIENT → YOUR API   : sends JWT in Authorization header on every protected request
3. YOUR API → SUPABASE : verifies the JWT → opens or refuses the door
```

Your server **never stores passwords**. Supabase handles all cryptography.

---

## Endpoints

| Method | Route | Auth required | Description |
|--------|-------|:---:|---|
| POST | `/auth/signup` | ❌ | Create a new user account |
| POST | `/auth/login` | ❌ | Log in and receive a JWT |
| POST | `/auth/logout` | ✅ Bearer | End the user session |
| GET | `/public/info` | ❌ | Open endpoint, no token needed |
| GET | `/protected/profile` | ✅ Bearer | Returns current user details |

Status codes: `201` signup · `200` login/read · `204` logout · `400` missing input · `401` bad/missing token

---

## Setup

### 1. Prerequisites
- Python 3.10+
- A free [Supabase](https://supabase.com) account with a project created

### 2. Get your Supabase credentials

1. Open [supabase.com](https://supabase.com) → your project
2. Go to **Project Settings → API** (left sidebar)
3. Copy:
   - **Project URL** → looks like `https://xxxxxxxxxxxx.supabase.co`
   - **anon / public key** → a long JWT string under "Project API keys"
4. ⚠️ **Never use the `service_role` key** here — it bypasses all security

### 3. One-time Supabase setting (important for dev!)

In your Supabase Dashboard:
- Go to **Authentication → Sign In / Providers → Email**
- Turn **"Confirm email" OFF**
- This lets you test signup → login immediately without checking your inbox
- *(In production, you'd leave this ON)*

### 4. Create your `.env` file

```bash
cp .env.example .env
# Then fill in your real SUPABASE_URL and SUPABASE_KEY
```

### 5. Activate virtual environment & install dependencies

```bash
# Windows
.venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 6. Run the server

```bash
uvicorn main:app --reload --port 8000
```

Server runs at: http://localhost:8000  
Swagger UI at: http://localhost:8000/docs

---

## API reference — quick test with curl

```bash
# Sign up
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Log in (copy the access_token from the response)
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Access protected route (paste your token)
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"

# Public route (no token needed)
curl -i http://localhost:8000/public/info
```

---

## Progress — Stage Checklist

### Stage 0 — Setup server & Supabase client
- [ ] Supabase project created
- [ ] Project URL and anon key copied from dashboard
- [ ] `.env` created (and is in `.gitignore`)
- [ ] `.env.example` committed with placeholder values
- [ ] Dependencies installed from `requirements.txt`
- [ ] `main.py` created — server starts, Supabase client initialised
- [ ] **Checkpoint**: `uvicorn main:app --reload` logs no errors
- [ ] **Commit**: `Stage 0: setup server and supabase client`

### Stage 1 — Signup & Login routes
- [ ] `POST /auth/signup` calls `supabase.auth.sign_up()`
- [ ] Returns `400` if email or password missing
- [ ] Returns `201` with user object on success
- [ ] `POST /auth/login` calls `supabase.auth.sign_in_with_password()`
- [ ] Returns `400` on missing fields, `401` on wrong credentials
- [ ] Returns `200` with `access_token` and `refresh_token` on success
- [ ] **Checkpoint**: signup → 201, login → 200 with token, empty body → 400
- [ ] **Commit**: `Stage 1: signup and login routes working`

### Stage 2 — Public & unverified protected route
- [ ] `GET /public/info` returns `200` with welcome message (no auth)
- [ ] `GET /protected/profile` checks Authorization header is present
- [ ] Returns `401` if header missing or malformed (no real verification yet)
- [ ] **Checkpoint**: `/public/info` → 200, `/protected/profile` with no token → 401
- [ ] **Commit**: `Stage 2: public route and unverified protected route`

### Stage 3 — Real token verification
- [ ] `/protected/profile` calls `supabase.auth.get_user(token)` to verify JWT
- [ ] Returns `401` if token is expired or tampered
- [ ] Returns `200` with user id, email, created_at on success
- [ ] **Checkpoint**: valid token → 200, tampered token (change one char) → 401
- [ ] **Commit**: `Stage 3: profile route token verification`

### Stage 4 — Auth middleware & logout
- [ ] Token verification extracted into a reusable FastAPI `Depends()` function
- [ ] `GET /protected/profile` uses the dependency (no copy-paste of auth logic)
- [ ] `GET /protected/dashboard` added — uses same dependency, zero new auth code
- [ ] `POST /auth/logout` created — calls `supabase.auth.sign_out()`, returns `204`
- [ ] **Checkpoint**: second protected route works; bad token → 401 on both
- [ ] **Commit**: `Stage 4: auth middleware and logout endpoint`

### Stage 5 — Swagger UI with bearer auth
- [ ] FastAPI `HTTPBearer` security scheme configured
- [ ] Lock icon appears on protected routes in `/docs`
- [ ] Authorize with a token → Try it out on `/protected/profile` → 200
- [ ] Screenshot of Swagger taken for README
- [ ] **Commit**: `Stage 5: Swagger UI documentation with bearer auth`

### Stage 6 — Publish to GitHub
- [ ] Public GitHub repo created
- [ ] `.env` confirmed absent from all commits (`git log --all -- .env`)
- [ ] `.env.example` committed with placeholder values
- [ ] README complete: setup, run command, endpoint table, Swagger screenshot
- [ ] ≥6 commits (one per stage)
- [ ] **Checkpoint**: peer can clone → fill `.env` → run → authenticated API works
- [ ] **Commit**: `Stage 6: publish to GitHub and write README`

### Stretch goals (optional)
- [ ] `403` case — authenticated user who isn't admin
- [ ] Refresh token endpoint
- [ ] Rate-limit `POST /login`, return `429` after N failures
- [ ] Stage 7 — AI rematch (build in `ai-version/` folder, compare, document)

---

## Swagger screenshot

*(Add screenshot here after completing Stage 5)*

---

## Security notes

- The **anon key** is safe to use from your app — it respects Supabase Row Level Security
- The **service_role key** bypasses all security — never use it here, never commit it
- JWTs are short-lived (1 hour default) — that is intentional
