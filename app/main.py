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

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

# Setup OpenTelemetry instrumentation
setup_telemetry(app)

# Mount static files directory
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(diagnose.router, prefix="/api/v1", tags=["Diagnose"])


# Dashboard UI route
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    html_path = BASE_DIR / "templates" / "dashboard.html"
    return FileResponse(html_path)


# Root redirect to dashboard
@app.get("/")
async def root():
    html_path = BASE_DIR / "templates" / "dashboard.html"
    return FileResponse(html_path)
