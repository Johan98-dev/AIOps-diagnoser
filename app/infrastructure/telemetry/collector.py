import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import httpx

from app.core.config import settings
from app.domain.models.diagnostic import TelemetryContext, LogEntry
from app.domain.models.enums import LogLevel

logger = logging.getLogger(__name__)

class TelemetryCollector:
    """
    Adapter responsible for fetching active logs, metrics, and trace spans
    from the OpenTelemetry backend (SigNoz Query Service / OTLP backend).
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.signoz_api_url or "http://localhost:8080"

    async def get_telemetry_context(
        self,
        service_name: str,
        lookback_minutes: int = 15
    ) -> TelemetryContext:
        """
        Queries SigNoz for logs, traces, and metrics associated with `service_name`
        within the specified lookback window.
        """
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=lookback_minutes)
        start_ts_nano = int(start_time.timestamp() * 1e9)
        end_ts_nano = int(now.timestamp() * 1e9)

        logs: List[LogEntry] = []
        spans: List[Dict[str, Any]] = []
        metrics: List[Dict[str, Any]] = []
        collector_status = "connected"

        async with httpx.AsyncClient(timeout=3.0) as client:
            # 1. Fetch Logs
            try:
                logs_resp = await client.post(
                    f"{self.base_url}/api/v1/logs",
                    json={
                        "start": start_ts_nano,
                        "end": end_ts_nano,
                        "query": f"service.name = '{service_name}'",
                        "limit": 50
                    }
                )
                if logs_resp.status_code == 200:
                    raw_logs = logs_resp.json().get("logs", [])
                    for item in raw_logs:
                        logs.append(self._parse_log_entry(item))
            except Exception as e:
                logger.warning(f"Unable to fetch logs from SigNoz: {e}")
                collector_status = "offline_fallback"

            # 2. Fetch Traces / Spans
            try:
                traces_resp = await client.post(
                    f"{self.base_url}/api/v1/traces",
                    json={
                        "start": start_ts_nano,
                        "end": end_ts_nano,
                        "serviceName": service_name,
                        "limit": 20
                    }
                )
                if traces_resp.status_code == 200:
                    spans = traces_resp.json().get("result", [])
            except Exception as e:
                logger.warning(f"Unable to fetch traces from SigNoz: {e}")
                collector_status = "offline_fallback"

        return TelemetryContext(
            service_name=service_name,
            logs=logs,
            metrics=metrics,
            spans=spans,
            metadata={
                "status": collector_status,
                "lookback_minutes": lookback_minutes,
                "collected_at": now.isoformat()
            }
        )

    def _parse_log_entry(self, item: Dict[str, Any]) -> LogEntry:
        """Helper to parse SigNoz log payload into Pydantic LogEntry model."""
        ts_raw = item.get("timestamp")
        if isinstance(ts_raw, (int, float)):
            ts = datetime.fromtimestamp(ts_raw / 1e9, tz=timezone.utc)
        else:
            ts = datetime.now(timezone.utc)

        level_str = str(item.get("severity_text", "INFO")).upper()
        try:
            level = LogLevel[level_str]
        except KeyError:
            level = LogLevel.INFO

        return LogEntry(
            timestamp=ts,
            level=level,
            message=item.get("body", item.get("message", "")),
            service_name=item.get("service_name"),
            trace_id=item.get("trace_id"),
            span_id=item.get("span_id"),
            attributes=item.get("attributes", {})
        )
