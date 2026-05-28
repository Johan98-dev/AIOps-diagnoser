from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.routes import health
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic (e.g., database connection, telemetry init)
    print(f"Starting {settings.app_name} v{settings.version}...")
    yield
    # Shutdown logic (e.g., close connections)
    print(f"Shutting down {settings.app_name}...")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])

# Root redirect or simple message
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name} API. Visit /docs for documentation."}
