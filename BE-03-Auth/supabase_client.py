import os
from dotenv import load_dotenv
from supabase import create_client, Client

# ---------------------------------------------------------------------------
# Load .env once here so any module that imports this file gets the vars.
# ---------------------------------------------------------------------------
load_dotenv()

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set in your .env file. "
        "See .env.example for reference."
    )

# Single shared client — imported by main.py, auth_routes.py, and any future router.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
