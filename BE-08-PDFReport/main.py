from fastapi import FastAPI

app = FastAPI(
    title="BE-08 PDF Report Generator API",
    description="Executive Analytics & PDF Report Generator with Immediate Streaming",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    """Minimal health check endpoint to verify server setup."""
    return {
        "status": "ok",
        "app": "BE-08 PDF Report Generator"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
