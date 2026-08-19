#!/usr/bin/env python3
"""
Chaos Monkey Fault Injection Script for AIOps Diagnoser.
Simulates production anomalies (DB timeouts, Memory Leaks, Downstream Failures, CPU Spikes)
and exports synthetic OpenTelemetry spans and logs to SigNoz / OTEL Collector.
"""

import argparse
import logging
import sys
import time
from typing import List, Dict, Any, Optional

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ChaosMonkey")


def setup_tracer(service_name: str, otel_endpoint: str) -> trace.Tracer:
    """Initializes OpenTelemetry tracer for the synthetic target service."""
    resource = Resource.create(attributes={"service.name": service_name, "environment": "chaos-test"})
    provider = TracerProvider(resource=resource)

    try:
        otlp_exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.info(f"Connected OTLP Exporter to {otel_endpoint} for service '{service_name}'")
    except Exception as e:
        logger.warning(f"Could not connect OTLP exporter to {otel_endpoint}: {e}. Falling back to console.")
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    return trace.get_tracer("chaos-monkey")


def inject_db_timeout(tracer: trace.Tracer, service_name: str, duration: int):
    """Simulates database query latency and pool exhaustion errors."""
    logger.info(f"🔥 Injecting 'db_timeout' fault into service '{service_name}'...")
    start_time = time.time()
    while time.time() - start_time < duration:
        with tracer.start_as_current_span("db.execute_query") as span:
            span.set_attribute("db.system", "postgresql")
            span.set_attribute("db.name", "orders_db")
            span.set_attribute("db.statement", "SELECT * FROM orders WHERE status = 'PENDING' FOR UPDATE")
            
            # Simulate DB delay
            time.sleep(1.5)
            
            # Record DB timeout error
            error_msg = "psycopg2.OperationalError: connection pool exhausted after 30000ms (max_connections=100 reached)"
            span.set_status(Status(StatusCode.ERROR, error_msg))
            span.record_exception(RuntimeError(error_msg))
            logger.error(f"[{service_name}] {error_msg}")
        time.sleep(0.5)


def inject_memory_leak(tracer: trace.Tracer, service_name: str, duration: int):
    """Simulates progressive memory allocation and OOM warning logs."""
    logger.info(f"🔥 Injecting 'memory_leak' fault into service '{service_name}'...")
    start_time = time.time()
    junk_data = []
    chunk_size = 10 * 1024 * 1024  # 10 MB chunks
    
    while time.time() - start_time < duration:
        with tracer.start_as_current_span("memory.allocation") as span:
            # Allocate dummy memory bytes
            junk_data.append(bytearray(chunk_size))
            allocated_mb = (len(junk_data) * chunk_size) // (1024 * 1024)
            
            span.set_attribute("memory.allocated_mb", allocated_mb)
            span.set_attribute("memory.threshold_percentage", 94.5)
            
            warning_msg = f"CRITICAL: Memory usage threshold exceeded! Allocated: {allocated_mb} MB. High risk of OOM-killer termination."
            span.set_status(Status(StatusCode.ERROR, warning_msg))
            logger.warning(f"[{service_name}] {warning_msg}")
        time.sleep(0.8)


def inject_downstream_failure(tracer: trace.Tracer, service_name: str, duration: int):
    """Simulates HTTP 503 Bad Gateway / Service Unavailable failures from downstream API."""
    logger.info(f"🔥 Injecting 'downstream_failure' fault into service '{service_name}'...")
    start_time = time.time()
    while time.time() - start_time < duration:
        with tracer.start_as_current_span("http.outbound_request") as span:
            span.set_attribute("http.method", "POST")
            span.set_attribute("http.url", "https://payment-gateway.internal/v1/charge")
            span.set_attribute("http.status_code", 503)
            
            error_msg = "httpx.HTTPStatusError: Server error '503 Service Unavailable' for url 'https://payment-gateway.internal/v1/charge'"
            span.set_status(Status(StatusCode.ERROR, error_msg))
            span.record_exception(RuntimeError(error_msg))
            logger.error(f"[{service_name}] {error_msg}")
        time.sleep(1.0)


def inject_cpu_spike(tracer: trace.Tracer, service_name: str, duration: int):
    """Simulates CPU saturation and main event loop blocking."""
    logger.info(f"🔥 Injecting 'cpu_spike' fault into service '{service_name}'...")
    start_time = time.time()
    while time.time() - start_time < duration:
        with tracer.start_as_current_span("cpu.heavy_computation") as span:
            span.set_attribute("cpu.utilization_percentage", 99.8)
            
            # Blocking CPU computation loop
            calc = 0
            for i in range(5_000_000):
                calc += i * i
            
            warning_msg = "WARNING: Main event loop blocked for 2450ms. High CPU saturation detected on core 0-3."
            span.set_status(Status(StatusCode.ERROR, warning_msg))
            logger.warning(f"[{service_name}] {warning_msg}")
        time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(description="Chaos Monkey Fault Injector for AIOps Diagnoser")
    parser.add_argument("-s", "--target-service", default="payment-service", help="Target service name to simulate (default: payment-service)")
    parser.add_argument("-f", "--fault", choices=["db_timeout", "memory_leak", "downstream_failure", "cpu_spike"], default="db_timeout", help="Fault type to inject")
    parser.add_argument("-e", "--otel-endpoint", default="localhost:4317", help="OTEL Collector gRPC endpoint (default: localhost:4317)")
    parser.add_argument("-d", "--duration", type=int, default=10, help="Duration of fault injection in seconds (default: 10)")

    args = parser.parse_args()

    tracer = setup_tracer(args.target_service, args.otel_endpoint)

    if args.fault == "db_timeout":
        inject_db_timeout(tracer, args.target_service, args.duration)
    elif args.fault == "memory_leak":
        inject_memory_leak(tracer, args.target_service, args.duration)
    elif args.fault == "downstream_failure":
        inject_downstream_failure(tracer, args.target_service, args.duration)
    elif args.fault == "cpu_spike":
        inject_cpu_spike(tracer, args.target_service, args.duration)

    # Flush spans before exiting
    provider = trace.get_tracer_provider()
    if hasattr(provider, "shutdown"):
        provider.shutdown()

    logger.info(f"✅ Chaos injection '{args.fault}' completed for service '{args.target_service}'.")


if __name__ == "__main__":
    main()
