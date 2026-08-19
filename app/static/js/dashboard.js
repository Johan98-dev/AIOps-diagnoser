document.addEventListener("DOMContentLoaded", () => {
    const diagnoseForm = document.getElementById("diagnoseForm");
    const runBtn = document.getElementById("runBtn");
    const btnText = document.getElementById("btnText");
    const btnSpinner = document.getElementById("btnSpinner");
    const resultsContainer = document.getElementById("resultsContainer");
    const emptyState = document.getElementById("emptyState");

    // Status dots
    const apiDot = document.getElementById("apiStatusDot");
    const apiText = document.getElementById("apiStatusText");

    // Initial Health Check
    checkSystemHealth();

    async function checkSystemHealth() {
        try {
            const res = await fetch("/api/v1/health");
            if (res.ok) {
                apiDot.className = "dot online";
                apiText.textContent = "API: Online";
            } else {
                apiDot.className = "dot warning";
                apiText.textContent = "API: Degraded";
            }
        } catch (e) {
            apiDot.className = "dot offline";
            apiText.textContent = "API: Offline";
        }
    }

    // Form Submission
    diagnoseForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const serviceName = document.getElementById("serviceName").value;
        const lookbackMinutes = parseInt(document.getElementById("lookbackMinutes").value, 10);
        const errorMessage = document.getElementById("errorMessage").value.trim();

        // UI Loading State
        btnText.textContent = "Analyzing Telemetry...";
        btnSpinner.style.display = "inline-block";
        runBtn.disabled = true;

        try {
            const response = await fetch("/api/v1/diagnose", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    service_name: serviceName,
                    lookback_minutes: lookbackMinutes,
                    error_message: errorMessage || null
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Failed to generate diagnosis");
            }

            const data = await response.json();
            renderReport(data);
        } catch (err) {
            alert(`Error running diagnosis: ${err.message}`);
        } finally {
            btnText.textContent = "Run AI Diagnosis";
            btnSpinner.style.display = "none";
            runBtn.disabled = false;
        }
    });

    function renderReport(report) {
        emptyState.style.display = "none";
        resultsContainer.style.display = "flex";

        const diagnosis = report.diagnosis;
        const context = report.context;
        const confidencePct = Math.round((diagnosis.confidence_score || 0) * 100);

        let confidenceColor = "#10b981"; // green
        if (confidencePct < 60) confidenceColor = "#ef4444"; // red
        else if (confidencePct < 85) confidenceColor = "#f59e0b"; // yellow

        const suggestedActionsHtml = (diagnosis.suggested_actions || [])
            .map(action => `<li>${escapeHtml(action)}</li>`)
            .join("");

        resultsContainer.innerHTML = `
            <div class="report-header">
                <div>
                    <span style="font-weight: 700; color: var(--accent-cyan);">Service: ${escapeHtml(context.service_name)}</span>
                    <div class="report-id">Report ID: ${escapeHtml(report.report_id)}</div>
                </div>
                <span class="status-badge" style="background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.3); color: #10b981;">
                    STATUS: ${escapeHtml(report.status)}
                </span>
            </div>

            <div class="section-box confidence-box">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                    <span>Diagnostic Confidence Score</span>
                    <strong style="color: ${confidenceColor};">${confidencePct}%</strong>
                </div>
                <div class="confidence-bar-bg">
                    <div class="confidence-bar-fill" style="width: ${confidencePct}%; background: ${confidenceColor};"></div>
                </div>
            </div>

            <div class="section-box">
                <h4>📝 Executive Summary</h4>
                <p style="font-size: 0.9rem; color: var(--text-primary); line-height: 1.5;">
                    ${escapeHtml(diagnosis.summary)}
                </p>
            </div>

            <div class="section-box" style="border-left: 4px solid var(--accent-red);">
                <h4>🔍 Identified Root Cause</h4>
                <p style="font-size: 0.9rem; color: #fca5a5; font-family: monospace; line-height: 1.5;">
                    ${escapeHtml(diagnosis.root_cause)}
                </p>
            </div>

            <div class="section-box">
                <h4>💥 Downstream & System Impact Analysis</h4>
                <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.5;">
                    ${escapeHtml(diagnosis.impact_analysis)}
                </p>
            </div>

            <div class="section-box">
                <h4>🛠️ Suggested Remediation Actions</h4>
                <ul class="action-list">
                    ${suggestedActionsHtml || "<li>No specific actions provided.</li>"}
                </ul>
            </div>
        `;
    }

    function escapeHtml(text) {
        if (!text) return "";
        return String(text)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
