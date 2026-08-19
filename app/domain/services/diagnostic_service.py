import uuid
from typing import Optional
from datetime import datetime, timezone

from ..models.diagnostic import DiagnosticRequest, DiagnosticResult, DiagnosticReport, TelemetryContext
from ..models.enums import DiagnosticStatus
from .prompt_builder import PromptBuilder
from app.infrastructure.llm.client import LlmClient
from app.infrastructure.telemetry.collector import TelemetryCollector

class DiagnosticService:
    """Service responsible for coordinating the diagnostic process."""

    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.telemetry_collector = TelemetryCollector()
        self.llm_client = LlmClient()

    async def run_diagnosis(self, request: DiagnosticRequest) -> DiagnosticReport:
        """
        Runs the diagnostic process for a given request by fetching telemetry and querying Groq LLM.
        """
        # 1. Gather active telemetry context (logs, traces, metrics)
        context = await self.telemetry_collector.get_telemetry_context(
            service_name=request.service_name,
            lookback_minutes=request.lookback_minutes
        )

        # 2. Build prompt and run LLM diagnosis
        system_instruction = self.prompt_builder.build_system_instruction()
        user_prompt = self.prompt_builder.build_user_prompt(context, request.error_message)

        raw_diagnosis = await self.llm_client.generate_diagnosis(user_prompt, system_instruction)

        # 3. Parse JSON response into DiagnosticResult
        diagnosis = DiagnosticResult(
            summary=raw_diagnosis.get("summary", "No summary generated."),
            root_cause=raw_diagnosis.get("root_cause", "No root cause identified."),
            impact_analysis=raw_diagnosis.get("impact_analysis", "No impact analysis generated."),
            suggested_actions=raw_diagnosis.get("suggested_actions", []),
            confidence_score=raw_diagnosis.get("confidence_score", 0.0)
        )

        # 4. Create and return report
        report = DiagnosticReport(
            report_id=str(uuid.uuid4()),
            status=DiagnosticStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
            context=context,
            diagnosis=diagnosis
        )

        return report
