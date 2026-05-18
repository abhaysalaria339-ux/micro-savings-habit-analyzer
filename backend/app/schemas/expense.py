from datetime import datetime
from decimal import Decimal
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.pagination import MAX_PAGE_LIMIT, MAX_PAGE_OFFSET


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=255)
    spent_at: datetime


class ExpenseUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=255)
    spent_at: datetime | None = None

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one expense field must be provided.")

        return self


class ExpenseRead(BaseModel):
    id: UUID
    user_id: UUID
    amount: Decimal
    category: str
    description: str | None
    spent_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseListResponse(BaseModel):
    items: list[ExpenseRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=MAX_PAGE_LIMIT)
    offset: int = Field(ge=0, le=MAX_PAGE_OFFSET)
    has_more: bool


class ExpenseImportRequest(BaseModel):
    csv_content: str = Field(min_length=1, max_length=500_000)


class ExpensePdfImportRequest(BaseModel):
    pdf_base64: str = Field(min_length=1, max_length=2_000_000)


class ExpenseImportRowResult(BaseModel):
    row_number: int
    status: Literal["imported", "failed", "skipped_duplicate", "skipped_credit"]
    error: str | None = None
    expense: ExpenseRead | None = None


class ExpenseImportResponse(BaseModel):
    imported_count: int
    failed_count: int
    skipped_count: int = 0
    results: list[ExpenseImportRowResult]


class ExpenseDuplicateCheckResponse(BaseModel):
    has_duplicates: bool
    matches: list[ExpenseRead]
