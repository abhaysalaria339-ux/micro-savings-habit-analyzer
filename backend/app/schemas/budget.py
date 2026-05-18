from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    monthly_limit: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class BudgetUpdate(BaseModel):
    monthly_limit: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class BudgetRead(BaseModel):
    id: UUID
    user_id: UUID
    category: str
    monthly_limit: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    usage_percentage: Decimal
    status: Literal["safe", "watch", "over"]
    period_start: datetime
    period_end: datetime
    created_at: datetime
    updated_at: datetime
