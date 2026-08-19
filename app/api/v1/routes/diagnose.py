from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.models.diagnostic import DiagnosticRequest, DiagnosticReport
from app.domain.services.diagnostic_service import DiagnosticService

router = APIRouter()

def get_diagnostic_service() -> DiagnosticService:
    return DiagnosticService()

@router.post("/diagnose", response_model=DiagnosticReport, status_code=status.HTTP_200_OK)
async def create_diagnosis(
    request: DiagnosticRequest,
    service: DiagnosticService = Depends(get_diagnostic_service)
):
    try:
        report = await service.run_diagnosis(request)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running diagnosis: {str(e)}"
        )
