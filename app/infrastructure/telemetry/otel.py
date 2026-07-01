import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import FastAPI
from app.core.config import settings

def setup_telemetry(app: FastAPI) -> None:
    """
    Initializes OpenTelemetry tracing.
    Configures TracerProvider, sets up the span processor (OTLP or Console),
    and instruments the FastAPI application.
    """
    # Define system Resource attributes
    resource = Resource.create(
        attributes={
            "service.name": settings.app_name,
            "service.version": settings.version,
            "deployment.environment": os.getenv("APP_ENV", "development"),
        }
    )

    # Initialize TracerProvider
    provider = TracerProvider(resource=resource)

    # Determine backend exporter: standard OTLP (e.g. for Dynatrace) vs Console
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        # Connect to OTLP backend using gRPC exporter
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        span_processor = BatchSpanProcessor(exporter)
    else:
        # Fallback to stdout console logger in local/development mode
        exporter = ConsoleSpanExporter()
        span_processor = BatchSpanProcessor(exporter)

    provider.add_span_processor(span_processor)

    # Register TracerProvider globally
    trace.set_tracer_provider(provider)

    # Auto-instrument FastAPI routes and middleware
    FastAPIInstrumentor().instrument_app(app)

def shutdown_telemetry() -> None:
    """
    Shuts down the global TracerProvider, flushing and closing active span processors.
    """
    provider = trace.get_tracer_provider()
    if hasattr(provider, "shutdown"):
        provider.shutdown()

