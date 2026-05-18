from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    target_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    current_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    target_date: date | None = None


class GoalProgressUpdate(BaseModel):
    current_amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class GoalRead(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    target_amount: Decimal
    current_amount: Decimal
    progress_percentage: Decimal
    target_date: date | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime


class GoalSuggestion(BaseModel):
    suggestion_type: Literal["money_leak", "micro_savings", "category_cap"]
    title: str
    message: str
    suggested_amount: Decimal
    confidence: Literal["low", "medium", "high"]


class GoalSuggestionsResponse(BaseModel):
    suggestions: list[GoalSuggestion]
