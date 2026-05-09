from decimal import Decimal

from pydantic import BaseModel, Field


class SavingsSimulationRequest(BaseModel):
    current_monthly_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    reduction_percentage: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)


class SavingsSimulationResponse(BaseModel):
    current_monthly_amount: Decimal
    reduction_percentage: Decimal
    reduced_monthly_amount: Decimal
    projected_monthly_savings: Decimal
    projected_yearly_savings: Decimal
