from fastapi import FastAPI
import auth_routes

# ---------------------------------------------------------------------------
# 3. Create the FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="FlyRank Auth API",
    description="Secure API with Supabase Auth — signup, login, logout, protected routes.",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Register routers
# include_router() mounts all routes from auth_routes under their /auth prefix
# ---------------------------------------------------------------------------
app.include_router(auth_routes.router)


@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase ✅"}
