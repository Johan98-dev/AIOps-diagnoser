from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.routes import health, diagnose
from app.core.config import settings
from app.infrastructure.telemetry.otel import setup_telemetry

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic (e.g., database connection, telemetry init)
    print(f"Starting {settings.app_name} v{settings.version}...")
    yield
    # Shutdown logic (e.g., close connections)
    print(f"Shutting down {settings.app_name}...")
    from app.infrastructure.telemetry.otel import shutdown_telemetry
    shutdown_telemetry()


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan
)

# Setup OpenTelemetry instrumentation
setup_telemetry(app)

# Include routers

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(diagnose.router, prefix="/api/v1", tags=["Diagnose"])


# Root redirect or simple message
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name} API. Visit /docs for documentation."}
