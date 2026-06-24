# AIOps Diagnoser

AIOps Diagnoser is an automated infrastructure diagnostics system built with FastAPI. It leverages **OpenTelemetry** and **Dynatrace** to capture comprehensive system telemetry (logs, metrics, and spans) and utilizes Large Language Models (LLMs) to automatically detect root causes, calculate impact, and generate remediation steps for system errors.

## Key Features
- **Structured Infrastructure Diagnostics**: Coordinates telemetric inputs to analyze anomalies across distributed microservices.
- **LLM-Powered Root Cause Analysis (RCA)**: Integrates with open-source LLMs (via Groq/OpenAI-compatible APIs) to generate precise diagnoses.
- **OpenTelemetry-Native**: Standardized instrumentation for metrics, logs, and span exporting.
- **Dynatrace Observability**: Seamless telemetry ingestion from production environments.
- **Chaos Engineering**: Built-in fault injection mechanisms to simulate production anomalies and validate diagnostics.
- **Clean Architecture**: High separation of concerns between domain logic, HTTP APIs, and infrastructure clients.

## Tech Stack
- **Language**: Python 3.12.10 (FastAPI, Pydantic v2, Pydantic Settings)
- **Observability**: OpenTelemetry SDK/API, OTLP Exporter
- **AI/LLM**: OpenAI client SDK (compatible with Groq / Ollama / local models)
- **Deployment**: Docker & Docker Compose

## Project Structure
```text
├── app/
│   ├── api/             # API routes & controller endpoints
│   ├── core/            # Environment configurations & application setup
│   ├── domain/          # Core business entities & service interfaces
│   │   ├── models/      # Pydantic schemas (diagnostic report, telemetry context)
│   │   └── services/    # Business rules, orchestrator & prompt building logic
│   └── infrastructure/  # Concrete adapters (LLM client, telemetry collectors)
├── chaos/               # Fault injection scripts & environment config
├── tests/               # Automated unit & integration tests
├── docker-compose.yml   # Multi-service local setup
├── requirements.txt     # Python project dependencies
└── .env.example         # Template for environment configuration
```

## Getting Started

### Prerequisites
- Python 3.12+
- Docker & Docker Compose (optional)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Johan98-dev/AIOps-diagnoser.git
   cd aiops-diagnoser
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1
   # Linux/macOS
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template and set your API key:
   ```bash
   cp .env.example .env
   ```

### Running the Application
Start the development server with:
```bash
uvicorn app.main:app --reload
```
Once running, the interactive API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Running Tests
To run the automated tests:
```bash
pytest
```
