import base64
import csv
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO, StringIO
from uuid import UUID

from app.core.pagination import DEFAULT_PAGE_LIMIT, validate_pagination
from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseDuplicateCheckResponse,
    ExpenseImportResponse,
    ExpenseImportRowResult,
    ExpenseListResponse,
    ExpenseRead,
    ExpenseUpdate,
)


class ExpenseNotFoundError(Exception):
    pass


class ExpenseImportFormatError(Exception):
    pass


class ExpenseService:
    def __init__(self, expense_repository: ExpenseRepository) -> None:
        self.expense_repository = expense_repository

    async def create_expense(
        self,
        *,
        user_id: UUID,
        expense_create: ExpenseCreate,
    ) -> Expense:
        return await self.expense_repository.create(
            user_id=user_id,
            amount=expense_create.amount,
            category=expense_create.category,
            description=expense_create.description,
            spent_at=expense_create.spent_at,
        )

    async def check_duplicates(
        self,
        *,
        user_id: UUID,
        expense_create: ExpenseCreate,
    ) -> ExpenseDuplicateCheckResponse:
        duplicates = await self.expense_repository.find_potential_duplicates(
            user_id=user_id,
            amount=expense_create.amount,
            category=expense_create.category,
            description=expense_create.description,
            spent_at=expense_create.spent_at,
        )
        matches = [ExpenseRead.model_validate(expense) for expense in duplicates]
        return ExpenseDuplicateCheckResponse(
            has_duplicates=bool(matches),
            matches=matches,
        )

    async def import_expenses_from_csv(
        self,
        *,
        user_id: UUID,
        csv_content: str,
    ) -> ExpenseImportResponse:
        reader = csv.DictReader(StringIO(csv_content.strip()))
        required_columns = {"amount", "category", "spent_at"}
        if reader.fieldnames is None:
            raise ExpenseImportFormatError("CSV must include a header row.")

        normalized_fieldnames = {
            self._normalize_import_key(field) for field in reader.fieldnames if field
        }
        missing_columns = required_columns - normalized_fieldnames
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ExpenseImportFormatError(f"CSV is missing required columns: {missing}.")

        results: list[ExpenseImportRowResult] = []
        imported_count = 0
        failed_count = 0
        skipped_count = 0

        for row_number, row in enumerate(reader, start=2):
            try:
                expense_create = self._expense_create_from_import_row(
                    self._normalize_import_row(row)
                )
                duplicates = await self.check_duplicates(
                    user_id=user_id,
                    expense_create=expense_create,
                )
                if duplicates.has_duplicates:
                    skipped_count += 1
                    results.append(
                        ExpenseImportRowResult(
                            row_number=row_number,
                            status="skipped_duplicate",
                            error="Potential duplicate expense already exists.",
                            expense=duplicates.matches[0],
                        )
                    )
                    continue

                expense = await self.create_expense(
                    user_id=user_id,
                    expense_create=expense_create,
                )
            except SkippedCreditTransaction as exc:
                skipped_count += 1
                results.append(
                    ExpenseImportRowResult(
                        row_number=row_number,
                        status="skipped_credit",
                        error=str(exc),
                    )
                )
            except (InvalidOperation, ValueError) as exc:
                failed_count += 1
                results.append(
                    ExpenseImportRowResult(
                        row_number=row_number,
                        status="failed",
                        error=str(exc),
                    )
                )
                continue

            imported_count += 1
            results.append(
                ExpenseImportRowResult(
                    row_number=row_number,
                    status="imported",
                    expense=ExpenseRead.model_validate(expense),
                )
            )

        return ExpenseImportResponse(
            imported_count=imported_count,
            failed_count=failed_count,
            skipped_count=skipped_count,
            results=results,
        )

    async def import_expenses_from_pdf(
        self,
        *,
        user_id: UUID,
        pdf_base64: str,
    ) -> ExpenseImportResponse:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ExpenseImportFormatError(
                "PDF import requires the pypdf package to be installed."
            ) from exc

        pdf_bytes = base64.b64decode(pdf_base64)
        reader = PdfReader(BytesIO(pdf_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        csv_content = self._extract_csv_like_rows_from_pdf_text(text)
        return await self.import_expenses_from_csv(user_id=user_id, csv_content=csv_content)

    async def list_expenses(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        category: str | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> list[Expense]:
        validate_pagination(limit=limit, offset=offset)

        return await self.expense_repository.list_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            limit=limit,
            offset=offset,
        )

    async def list_expense_page(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        category: str | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> ExpenseListResponse:
        validate_pagination(limit=limit, offset=offset)

        expenses = await self.list_expenses(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            limit=limit,
            offset=offset,
        )
        total = await self.expense_repository.count_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
        )

        items = [ExpenseRead.model_validate(expense) for expense in expenses]
        return ExpenseListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            has_more=offset + len(items) < total,
        )

    async def get_expense(
        self,
        *,
        expense_id: UUID,
        user_id: UUID,
    ) -> ExpenseRead:
        expense = await self.expense_repository.get_by_id_for_user(
            expense_id=expense_id,
            user_id=user_id,
        )
        if expense is None:
            raise ExpenseNotFoundError("Expense not found.")

        return ExpenseRead.model_validate(expense)

    async def update_expense(
        self,
        *,
        expense_id: UUID,
        user_id: UUID,
        expense_update: ExpenseUpdate,
    ) -> ExpenseRead:
        expense = await self.expense_repository.get_by_id_for_user(
            expense_id=expense_id,
            user_id=user_id,
        )
        if expense is None:
            raise ExpenseNotFoundError("Expense not found.")

        updated_expense = await self.expense_repository.update(
            expense=expense,
            values=expense_update.model_dump(exclude_unset=True),
        )
        return ExpenseRead.model_validate(updated_expense)

    async def delete_expense(
        self,
        *,
        expense_id: UUID,
        user_id: UUID,
    ) -> None:
        expense = await self.expense_repository.get_by_id_for_user(
            expense_id=expense_id,
            user_id=user_id,
        )
        if expense is None:
            raise ExpenseNotFoundError("Expense not found.")

        await self.expense_repository.delete(expense=expense)

    def _expense_create_from_import_row(self, row: dict[str, str | None]) -> ExpenseCreate:
        amount = self._parse_import_amount(row.get("amount"))
        category = (row.get("category") or "").strip()
        if not category:
            raise ValueError("Category is required.")

        spent_at = self._parse_import_datetime(row.get("spent_at"))
        description = (row.get("description") or "").strip() or None

        return ExpenseCreate(
            amount=amount,
            category=category,
            description=description,
            spent_at=spent_at,
        )

    def _normalize_import_row(self, row: dict[str, str | None]) -> dict[str, str | None]:
        normalized: dict[str, str | None] = {}
        for key, value in row.items():
            if key is None:
                continue
            normalized[self._normalize_import_key(key)] = value

        transaction_type = (normalized.get("transaction_type") or "").lower()
        credit_value = normalized.get("credit")
        if transaction_type in {"credit", "deposit", "income"}:
            raise SkippedCreditTransaction("Credit transaction skipped.")

        if not normalized.get("amount"):
            normalized["amount"] = normalized.get("debit") or normalized.get("withdrawal")
        elif credit_value and not normalized.get("debit"):
            raise SkippedCreditTransaction("Credit transaction skipped.")

        if not normalized.get("category"):
            normalized["category"] = normalized.get("merchant") or normalized.get("narration")

        if not normalized.get("description"):
            normalized["description"] = normalized.get("narration") or normalized.get("merchant")

        return normalized

    def _normalize_import_key(self, key: str) -> str:
        normalized = key.strip().lower().replace(" ", "_").replace("-", "_")
        aliases = {
            "date": "spent_at",
            "transaction_date": "spent_at",
            "txn_date": "spent_at",
            "time": "spent_at",
            "value": "amount",
            "transaction_amount": "amount",
            "debit_amount": "debit",
            "withdrawal_amount": "withdrawal",
            "paid": "debit",
            "remarks": "description",
            "note": "description",
            "details": "description",
            "payee": "merchant",
            "merchant_name": "merchant",
            "type": "transaction_type",
            "dr_cr": "transaction_type",
        }
        return aliases.get(normalized, normalized)

    def _parse_import_amount(self, value: str | None) -> Decimal:
        if value is None or not value.strip():
            raise ValueError("Amount is required.")

        amount = Decimal(value.strip())
        if amount <= Decimal("0"):
            raise ValueError("Amount must be greater than zero.")

        return amount

    def _parse_import_datetime(self, value: str | None) -> datetime:
        if value is None or not value.strip():
            raise ValueError("spent_at is required.")

        cleaned = value.strip().replace("Z", "+00:00")
        if len(cleaned) == 10 and cleaned[4] == "-" and cleaned[7] == "-":
            cleaned = f"{cleaned}T12:00:00+00:00"

        spent_at = datetime.fromisoformat(cleaned)
        if spent_at.tzinfo is None:
            return spent_at.replace(tzinfo=UTC)

        return spent_at

    def _extract_csv_like_rows_from_pdf_text(self, text: str) -> str:
        rows = ["spent_at,description,category,amount"]
        for line in text.splitlines():
            parts = [part.strip() for part in line.split() if part.strip()]
            if len(parts) < 3:
                continue

            date_value = parts[0]
            amount_value = parts[-1].replace(",", "")
            try:
                Decimal(amount_value)
                spent_at = self._parse_import_datetime(date_value)
            except (InvalidOperation, ValueError):
                continue

            description = " ".join(parts[1:-1])
            category = description.split()[0] if description else "Imported"
            rows.append(
                f"{spent_at.date().isoformat()},{description},{category},{amount_value}"
            )

        if len(rows) == 1:
            raise ExpenseImportFormatError("No expense-like rows were found in the PDF.")

        return "\n".join(rows)


class SkippedCreditTransaction(Exception):
    pass
