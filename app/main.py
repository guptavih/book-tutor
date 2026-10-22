import logfire
from fastapi import FastAPI
from app.config import settings

# 1. Initialize Observability FIRST
logfire.configure(
    service_name=settings.project_name,
    token=settings.logfire_token if settings.logfire_token else None,
    console=logfire.ConsoleOptions(verbose=True)
)

# 2. Initialize FastAPI
app = FastAPI(title=settings.project_name)

# 3. Instrument FastAPI with Logfire
logfire.instrument_fastapi(app)

@app.get("/health")
async def health_check():
    """Basic health check for the application."""
    logfire.info("Health check endpoint hit")
    return {"status": "ok", "environment": settings.environment}