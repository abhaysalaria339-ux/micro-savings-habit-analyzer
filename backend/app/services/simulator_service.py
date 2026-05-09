from decimal import ROUND_HALF_UP, Decimal

from app.schemas.simulator import SavingsSimulationRequest, SavingsSimulationResponse


class SavingsSimulatorService:
    def simulate_savings(
        self,
        simulation_request: SavingsSimulationRequest,
    ) -> SavingsSimulationResponse:
        reduction_ratio = simulation_request.reduction_percentage / Decimal("100")
        projected_monthly_savings = (
            simulation_request.current_monthly_amount * reduction_ratio
        )
        reduced_monthly_amount = (
            simulation_request.current_monthly_amount - projected_monthly_savings
        )
        projected_yearly_savings = projected_monthly_savings * Decimal("12")

        return SavingsSimulationResponse(
            current_monthly_amount=self._quantize_money(
                simulation_request.current_monthly_amount
            ),
            reduction_percentage=simulation_request.reduction_percentage,
            reduced_monthly_amount=self._quantize_money(reduced_monthly_amount),
            projected_monthly_savings=self._quantize_money(projected_monthly_savings),
            projected_yearly_savings=self._quantize_money(projected_yearly_savings),
        )

    def _quantize_money(self, amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
