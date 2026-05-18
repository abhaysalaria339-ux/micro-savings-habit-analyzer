from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.schemas.expense import ExpenseImportRequest
from app.services.expense_service import ExpenseImportFormatError, ExpenseService


@dataclass
class FakeImportedExpense:
    id: UUID
    user_id: UUID
    amount: Decimal
    category: str
    description: str | None
    spent_at: datetime
    created_at: datetime
    updated_at: datetime


class FakeImportExpenseRepository:
    async def find_potential_duplicates(self, **kwargs):
        return []

    async def create(
        self,
        *,
        user_id: UUID,
        amount: Decimal,
        category: str,
        description: str | None,
        spent_at: datetime,
    ) -> FakeImportedExpense:
        now = datetime.now(UTC)
        return FakeImportedExpense(
            id=uuid4(),
            user_id=user_id,
            amount=amount,
            category=category,
            description=description,
            spent_at=spent_at,
            created_at=now,
            updated_at=now,
        )


@pytest.mark.asyncio
async def test_import_expenses_from_csv_imports_valid_rows_and_reports_failures() -> None:
    service = ExpenseService(FakeImportExpenseRepository())
    csv_content = "\n".join(
        [
            "amount,category,spent_at,description",
            "120.00,Transport,2026-05-17T09:30:00+00:00,Cab ride",
            "-5.00,Snacks,2026-05-17,Invalid amount",
        ]
    )

    result = await service.import_expenses_from_csv(
        user_id=uuid4(),
        csv_content=csv_content,
    )

    assert result.imported_count == 1
    assert result.failed_count == 1
    assert result.results[0].status == "imported"
    assert result.results[1].status == "failed"


@pytest.mark.asyncio
async def test_import_expenses_from_csv_rejects_missing_headers() -> None:
    service = ExpenseService(FakeImportExpenseRepository())

    with pytest.raises(ExpenseImportFormatError):
        await service.import_expenses_from_csv(
            user_id=uuid4(),
            csv_content="amount,category\n100.00,Food",
        )


def test_expense_import_request_accepts_csv_text() -> None:
    request = ExpenseImportRequest(
        csv_content="amount,category,spent_at\n100.00,Food,2026-05-17",
    )

    assert "amount" in request.csv_content
