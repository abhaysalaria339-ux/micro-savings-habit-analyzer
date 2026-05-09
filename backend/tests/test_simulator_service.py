from decimal import Decimal

from app.schemas.simulator import SavingsSimulationRequest
from app.services.simulator_service import SavingsSimulatorService


def test_savings_simulator_projects_monthly_and_yearly_savings() -> None:
    service = SavingsSimulatorService()
    request = SavingsSimulationRequest(
        current_monthly_amount=Decimal("3000.00"),
        reduction_percentage=Decimal("20.00"),
    )

    result = service.simulate_savings(request)

    assert result.reduced_monthly_amount == Decimal("2400.00")
    assert result.projected_monthly_savings == Decimal("600.00")
    assert result.projected_yearly_savings == Decimal("7200.00")
