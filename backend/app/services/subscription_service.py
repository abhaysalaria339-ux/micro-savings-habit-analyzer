from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from app.repositories.expense_repository import ExpenseRepository
from app.schemas.subscription import SubscriptionCandidate, SubscriptionDetectionResponse


class SubscriptionService:
    def __init__(self, expense_repository: ExpenseRepository) -> None:
        self.expense_repository = expense_repository

    async def detect_subscriptions(self, *, user_id: UUID) -> SubscriptionDetectionResponse:
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=180)
        patterns = await self.expense_repository.get_repeated_spending_patterns(
            user_id=user_id,
            min_occurrences=2,
            start_date=start_date,
            end_date=end_date,
        )
        candidates: list[SubscriptionCandidate] = []
        for (
            category,
            description,
            occurrence_count,
            _total_amount,
            average_amount,
            first_spent_at,
            latest_spent_at,
        ) in patterns:
            if occurrence_count < 2:
                continue

            elapsed_days = (latest_spent_at - first_spent_at).days
            average_gap = elapsed_days / max(occurrence_count - 1, 1)
            label = f"{category} {description or ''}".lower()
            looks_like_subscription = (
                24 <= average_gap <= 38
                or any(token in label for token in ("subscription", "netflix", "spotify", "prime"))
            )
            if not looks_like_subscription:
                continue

            candidates.append(
                SubscriptionCandidate(
                    category=category,
                    description=description,
                    occurrence_count=occurrence_count,
                    average_amount=self._money(average_amount),
                    estimated_monthly_cost=self._money(average_amount),
                    first_seen_at=first_spent_at,
                    latest_seen_at=latest_spent_at,
                    confidence="high" if 26 <= average_gap <= 34 else "medium",
                )
            )

        return SubscriptionDetectionResponse(candidates=candidates[:8])

    def _money(self, amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
