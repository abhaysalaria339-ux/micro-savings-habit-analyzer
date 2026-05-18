from typing import Any

from pydantic import BaseModel, Field


class BackupExportResponse(BaseModel):
    exported_at: str
    expenses: list[dict[str, Any]]
    goals: list[dict[str, Any]]
    budgets: list[dict[str, Any]]


class BackupImportRequest(BaseModel):
    payload: BackupExportResponse
    skip_duplicates: bool = True


class BackupImportResponse(BaseModel):
    imported_expenses: int = Field(ge=0)
    imported_goals: int = Field(ge=0)
    imported_budgets: int = Field(ge=0)
    skipped: int = Field(ge=0)
