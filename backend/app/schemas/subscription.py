from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SubscriptionCandidate(BaseModel):
    category: str
    description: str | None
    occurrence_count: int
    average_amount: Decimal
    estimated_monthly_cost: Decimal
    first_seen_at: datetime
    latest_seen_at: datetime
    confidence: str


class SubscriptionDetectionResponse(BaseModel):
    candidates: list[SubscriptionCandidate]
