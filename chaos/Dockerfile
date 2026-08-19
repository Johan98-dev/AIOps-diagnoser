FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp requests

COPY monkey.py .

ENTRYPOINT ["python", "monkey.py"]
CMD ["--target-service", "payment-service", "--fault", "db_timeout", "--otel-endpoint", "signoz-otel-collector:4317"]
