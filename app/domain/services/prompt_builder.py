from typing import Optional
from app.domain.models.diagnostic import TelemetryContext

class PromptBuilder:
    """Builder class for structuring diagnostic prompts and system instructions for the LLM."""

    def build_system_instruction(self) -> str:
        """
        Builds the system prompt instructing the LLM on its role, inputs, and response format.
        """
        return (
            "You are an elite Site Reliability Engineer (SRE) and AIOps automated diagnostic assistant.\n"
            "Your task is to analyze the telemetry context provided and identify the root cause of the service issue.\n\n"
            "You MUST respond with a single JSON object. The keys of the JSON object must be exactly:\n"
            "1. 'summary': (string) A concise executive summary of the issue.\n"
            "2. 'root_cause': (string) The technical root cause of the problem (e.g., database connection timeout, memory leak, unoptimized loop).\n"
            "3. 'impact_analysis': (string) How this issue impacts downstream services, users, and overall system health.\n"
            "4. 'suggested_actions': (list of strings) Actionable, precise steps to mitigate and fix the issue.\n"
            "5. 'confidence_score': (float) Your confidence in this diagnosis, between 0.0 (no confidence) and 1.0 (absolutely certain).\n\n"
            "Do not include any thinking block, markdown formatting wrapper (such as ```json), or extra text outside the JSON object itself. "
            "Ensure the output is valid JSON."
        )

    def build_user_prompt(self, context: TelemetryContext, error_message: Optional[str] = None) -> str:
        """
        Formats the logs, metrics, spans, and optional error message into a prompt.
        """
        symptom_section = f"Symptom / Error Message: {error_message}\n" if error_message else "Symptom / Error Message: None provided (routine scan)\n"
        
        # Format logs
        logs_str = ""
        if context.logs:
            for log in context.logs:
                timestamp_str = log.timestamp.isoformat() if hasattr(log.timestamp, "isoformat") else str(log.timestamp)
                logs_str += f"- [{timestamp_str}] [{log.level}] {log.message} (Service: {log.service_name or 'unknown'}, Trace: {log.trace_id or 'none'})\n"
        else:
            logs_str = "No logs captured in the lookback period.\n"

        # Format metrics
        metrics_str = ""
        if context.metrics:
            for metric in context.metrics:
                metrics_str += f"- {metric}\n"
        else:
            metrics_str = "No anomalous metrics captured.\n"

        # Format spans
        spans_str = ""
        if context.spans:
            for span in context.spans:
                spans_str += f"- {span}\n"
        else:
            spans_str = "No relevant trace spans captured.\n"

        return (
            f"Analyze the following telemetry data for service '{context.service_name}':\n\n"
            f"### Symptom\n"
            f"{symptom_section}\n"
            f"### Logs\n"
            f"{logs_str}\n"
            f"### Metrics\n"
            f"{metrics_str}\n"
            f"### Spans & Traces\n"
            f"{spans_str}\n"
            f"Based on this data, construct the JSON diagnostic report."
        )
