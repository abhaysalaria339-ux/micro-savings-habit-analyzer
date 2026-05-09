from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.simulator import SavingsSimulationRequest, SavingsSimulationResponse
from app.services.simulator_service import SavingsSimulatorService

router = APIRouter()


@router.post(
    "/savings",
    response_model=SavingsSimulationResponse,
    summary="Simulate savings",
    description="Calculate monthly and yearly savings projections from a what-if scenario.",
)
async def simulate_savings(
    simulation_request: SavingsSimulationRequest,
    current_user: User = Depends(get_current_active_user),
) -> SavingsSimulationResponse:
    _ = current_user
    simulator_service = SavingsSimulatorService()
    return simulator_service.simulate_savings(simulation_request)
