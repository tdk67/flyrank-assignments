import os
from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import create_client, Client

# ---------------------------------------------------------------------------
# 1. Load environment variables from .env
#    load_dotenv() reads the .env file and puts its values into os.environ.
#    This must happen BEFORE we try to read SUPABASE_URL / SUPABASE_KEY.
# ---------------------------------------------------------------------------
load_dotenv()

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set in your .env file. "
        "See .env.example for reference."
    )

# ---------------------------------------------------------------------------
# 2. Create the Supabase client — once, at startup.
#    This object is reused across all routes (like a DB connection).
# ---------------------------------------------------------------------------
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------------------------
# 3. Create the FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="FlyRank Auth API",
    description="Secure API with Supabase Auth — signup, login, logout, protected routes.",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Stage 0 checkpoint route — confirms server + Supabase client are alive.
# We'll replace / expand this in later stages.
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase ✅"}
