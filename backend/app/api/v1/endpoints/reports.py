import csv
from datetime import UTC, datetime
from io import StringIO

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get(
    "/monthly.csv",
    summary="Export monthly report",
    description="Download a CSV summary of current month spending.",
)
async def export_monthly_report(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    now = datetime.now(UTC)
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    analytics_service = AnalyticsService(ExpenseRepository(db_session))
    summary = await analytics_service.get_spending_summary(
        user_id=current_user.id,
        start_date=start_date,
        end_date=now,
    )

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Micro-Savings Habit Analyzer Monthly Report"])
    writer.writerow(["Period start", start_date.isoformat()])
    writer.writerow(["Period end", now.isoformat()])
    writer.writerow([])
    writer.writerow(["Total spend", summary.total_amount])
    writer.writerow(["Transactions", summary.transaction_count])
    writer.writerow(["Average transaction", summary.average_amount])
    writer.writerow([])
    writer.writerow(["Category", "Amount", "Transactions", "Percentage"])
    for category in summary.categories:
        writer.writerow(
            [
                category.category,
                category.total_amount,
                category.transaction_count,
                category.percentage_of_total,
            ]
        )

    filename = f"micro-savings-report-{now:%Y-%m}.csv"
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
