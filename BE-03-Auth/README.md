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
| POST | `/auth/login` | ❌ | Log in and receive a JWT & refresh token |
| POST | `/auth/refresh` | ❌ | Exchange refresh token for new access token |
| POST | `/auth/logout` | ✅ Bearer | End the user session |
| GET | `/public/info` | ❌ | Open endpoint, no token needed |
| GET | `/protected/profile` | ✅ Bearer | Returns current user profile details |
| GET | `/protected/dashboard` | ✅ Bearer | Protected user dashboard stats |

Status codes: `201` signup · `200` login/read/refresh · `204` logout · `400` missing input · `401` bad/missing token

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

## Testing tips

### Password rules (enforced on signup)

Passwords must satisfy **all** of the following:

| Rule | Example |
|------|---------|
| Minimum 8 characters | `MyPass1!` ✅ |
| At least one uppercase letter (A–Z) | `mypass1!` ❌ |
| At least one lowercase letter (a–z) | `MYPASS1!` ❌ |
| At least one digit (0–9) | `MyPassword!` ❌ |
| At least one special character (`!@#$%^&*` …) | `MyPassword1` ❌ |

A valid test password: `Test1234!`

---

### Known gotchas

#### ❌ `500 Internal Server Error` — "Email address is invalid"

**Symptom:** signup returns 500 with `AuthApiError: Email address "test01@example.com" is invalid`  
**Cause:** `example.com` (and `example.net`, `example.org`) are **reserved domains** (RFC 2606) with no MX records. Supabase validates that the email domain can actually receive mail.  
**Fix:** Use a real domain — `@gmail.com`, `@hotmail.com`, etc. The inbox doesn't need to exist if "Confirm email" is OFF.

```bash
# ❌ Will fail — reserved domain, no MX records
{"email": "test@example.com", "password": "Test1234!"}

# ✅ Will work
{"email": "testuser@gmail.com", "password": "Test1234!"}
```

#### ❌ `400 Bad Request` — "email rate limit exceeded"

**Symptom:** signup returns `{"detail": "email rate limit exceeded"}`  
**Cause:** Supabase's free cloud tier allows only **3–4 auth emails per hour** on its shared SMTP. Even with "Confirm email" OFF, signup attempts count against this limit.  
**Fix options** (see SMTP setup guide below):
- Reuse the same test email (delete user → re-signup)
- Configure a custom SMTP provider (removes the limit)
- Use your self-hosted Supabase instance

---

### Deleting a test user so you can re-use the same email

When iterating on signup you'll hit `"Email may already be registered"`.  
Pick whichever method is fastest for you:

**Option A — Supabase Dashboard (recommended)**
1. [supabase.com](https://supabase.com) → your project → **Authentication → Users**
2. Find the email → click **⋯** → **Delete user**

**Option B — SQL Editor (good for bulk cleanup)**
1. Supabase Dashboard → **SQL Editor**
2. Run:
```sql
-- Delete one user
DELETE FROM auth.users WHERE email = 'testuser@gmail.com';

-- Delete ALL users (dev only!)
DELETE FROM auth.users;
```

**Option C — Admin REST API (scriptable)**
```bash
# Requires your service_role key (never put this in app code)
curl -X DELETE "https://YOUR_PROJECT_REF.supabase.co/auth/v1/admin/users/USER_UUID" \
  -H "apikey: YOUR_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer YOUR_SERVICE_ROLE_KEY"
```
Find the `USER_UUID` in the Dashboard → Authentication → Users table.

> ⚠️ The `service_role` key bypasses all Row Level Security. Use it only in your terminal during dev — never commit it or embed it in app code.

---

### SMTP setup — removing the rate limit

The 3–4 emails/hour limit only applies to Supabase's **built-in shared SMTP**. Once you plug in your own SMTP server, the limit disappears. You have two paths:

#### Path 1 — Custom SMTP on Supabase Cloud (free tier)

Use any free transactional email provider. **Resend** is the easiest:

1. Sign up at [resend.com](https://resend.com) (free: 3,000 emails/month, 100/day)
2. Create an API key
3. In Supabase Dashboard → **Project Settings → Auth → SMTP**:

| Field | Value |
|---|---|
| Host | `smtp.resend.com` |
| Port | `465` |
| Username | `resend` |
| Password | your Resend API key |
| Sender email | `noreply@yourdomain.com` (must be verified in Resend) |

Alternative providers: SendGrid, Mailjet, Brevo — all have free tiers and similar setup.

> ⚠️ If you don't own a domain, Resend provides a shared sending domain for testing — check their docs.

#### Path 2 — Self-hosted Supabase

If you already run a **self-hosted Supabase instance** (e.g. via Docker), configure SMTP in your `docker-compose.yml` or `supabase/config.toml`:

```toml
# supabase/config.toml (local dev)
[auth.email]
enable_confirmations = false   # set true for production

[auth.smtp]
host = "smtp.yourmailserver.com"
port = 587
user = "your-smtp-user"
pass = "env(SMTP_PASSWORD)"   # read from .env
admin_email = "admin@yourdomain.com"
sender_name = "FlyRank Auth"
```

Or in `docker-compose.yml`:
```yaml
environment:
  GOTRUE_SMTP_HOST: smtp.yourmailserver.com
  GOTRUE_SMTP_PORT: 587
  GOTRUE_SMTP_USER: your-smtp-user
  GOTRUE_SMTP_PASS: ${SMTP_PASSWORD}
  GOTRUE_SMTP_ADMIN_EMAIL: admin@yourdomain.com
  GOTRUE_MAILER_AUTOCONFIRM: "true"   # skip email confirmation entirely
```

Setting `GOTRUE_MAILER_AUTOCONFIRM: "true"` on self-hosted means **no emails are sent at all** — users are confirmed instantly. This is the most friction-free dev setup.

---

## Python & FastAPI Syntax Notes (Java Dev Cheat Sheet)

Key concepts for developers coming from languages like Java:

### 1. Type Hints vs. Default Values
In Python, method parameters follow `name: Type = DefaultValue`:
```python
credentials: HTTPAuthorizationCredentials | None = Depends(security)
```
- **Name:** `credentials`
- **Type:** `HTTPAuthorizationCredentials | None`
- **Default / Injector:** `= Depends(security)`

### 2. Union Types (`|`)
In Python 3.10+, `TypeA | TypeB` means **either TypeA or TypeB**.
- `HTTPAuthorizationCredentials | None` is equivalent to Java's `Optional<HTTPAuthorizationCredentials>`.

### 3. Square Brackets `[]` vs Parentheses `()`
- **Parentheses `()`**: Function call or object instantiation at runtime (`my_func()`).
- **Square Brackets `[]`**: Type parameterization / generics (equivalent to Java `<>` generics).
  - Java `List<String>` $\rightarrow$ Python `list[str]`
  - Java `Map<String, Integer>` $\rightarrow$ Python `dict[str, int]`
  - Java `Annotated<Type, Meta>` $\rightarrow$ Python `Annotated[Type, Meta]`

### 4. Why `Depends()` in parameters instead of Decorators?
FastAPI uses parameter dependency injection (`Depends()`) instead of decorators (`@require_auth`) because:
1. The injected value is passed directly as a function argument (no global thread-local state).
2. IDE autocompletion works out of the box (`credentials.credentials`).
3. FastAPI reads parameters to build Swagger UI documentation (`securitySchemes`) automatically.

---


## Progress — Stage Checklist

### Stage 0 — Setup server & Supabase client
- [x] Supabase project created
- [x] Project URL and anon key copied from dashboard
- [x] `.env` created (and is in `.gitignore`)
- [x] `.env.example` committed with placeholder values
- [x] Dependencies installed from `requirements.txt`
- [x] `main.py` created — server starts, Supabase client initialised
- [x] **Checkpoint**: `uvicorn main:app --reload` logs no errors
- [x] **Commit**: `Stage 0: setup server and supabase client`

### Stage 1 — Signup & Login routes
- [x] `POST /auth/signup` calls `supabase.auth.sign_up()`
- [x] Returns `400` if email or password missing
- [x] Returns `201` with user object on success
- [x] `POST /auth/login` calls `supabase.auth.sign_in_with_password()`
- [x] Returns `400` on missing fields, `401` on wrong credentials
- [x] Returns `200` with `access_token` and `refresh_token` on success
- [x] **Checkpoint**: signup → 201, login → 200 with token, empty body → 400
- [x] **Commit**: `Stage 1: signup and login routes working`

### Stage 2 — Public & unverified protected route
- [x] `GET /public/info` returns `200` with welcome message (no auth)
- [x] `GET /protected/profile` checks Authorization header is present
- [x] Returns `401` if header missing or malformed (no real verification yet)
- [x] **Checkpoint**: `/public/info` → 200, `/protected/profile` with no token → 401
- [x] **Commit**: `Stage 2: public route and unverified protected route`

### Stage 3 — Real token verification
- [x] `/protected/profile` calls `supabase.auth.get_user(token)` to verify JWT
- [x] Returns `401` if token is expired or tampered
- [x] Returns `200` with user id, email, created_at on success
- [x] **Checkpoint**: valid token → 200, tampered token (change one char) → 401
- [x] **Commit**: `Stage 3: profile route token verification`

### Stage 4 — Auth middleware & logout
- [x] Token verification extracted into a reusable FastAPI `Depends()` function
- [x] `GET /protected/profile` uses the dependency (no copy-paste of auth logic)
- [x] `GET /protected/dashboard` added — uses same dependency, zero new auth code
- [x] `POST /auth/logout` created — calls `supabase.auth.sign_out()`, returns `204`
- [x] **Checkpoint**: second protected route works; bad token → 401 on both
- [x] **Commit**: `Stage 4: auth middleware and logout endpoint`

### Stage 5 — Swagger UI with bearer auth
- [x] FastAPI `HTTPBearer` security scheme configured
- [x] Lock icon appears on protected routes in `/docs`
- [x] Authorize with a token → Try it out on `/protected/profile` → 200
- [x] Screenshot of Swagger taken for README
- [x] **Commit**: `Stage 5: Swagger UI documentation with bearer auth`

### Stage 6 — Publish & Finalize
- [x] `.env` confirmed absent from tracking (`.gitignore` protects `.env`)
- [x] `.env.example` committed with placeholder values
- [x] README complete: setup, run command, endpoint table, architecture, testing notes
- [x] All 6 stages completed and verified
- [x] **Checkpoint**: peer can clone → fill `.env` → run → authenticated API works
- [x] **Commit**: `Stage 6: finalize application structure and documentation`

### Stretch goals (optional)
- [ ] `403` case — authenticated user who isn't admin
- [x] Refresh token endpoint (`POST /auth/refresh`)
- [ ] Rate-limit `POST /login`, return `429` after N failures
- [ ] Stage 7 — AI rematch (build in `ai-version/` folder, compare, document)

---

## Swagger screenshot

![FlyRank Auth API Swagger UI Documentation](./swagger_ui.png)

---

## Security notes

- The **anon key** is safe to use from your app — it respects Supabase Row Level Security
- The **service_role key** bypasses all security — never use it here, never commit it
- JWTs are short-lived (1 hour default) — that is intentional
