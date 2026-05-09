from app.schemas.ml import MLCapability


def get_planned_ml_capabilities() -> list[MLCapability]:
    return [
        MLCapability(
            problem_type="clustering",
            status="planned",
            description="Group users or spending patterns by behavior similarity.",
            required_feature_groups=[
                "category_spending",
                "micro_expense_patterns",
                "repeated_spending_patterns",
            ],
        ),
        MLCapability(
            problem_type="classification",
            status="planned",
            description="Predict behavior class after enough labeled training data exists.",
            required_feature_groups=[
                "behavior_score_factors",
                "spending_frequency",
                "money_leak_patterns",
            ],
        ),
        MLCapability(
            problem_type="forecasting",
            status="planned",
            description="Forecast future spending from time-series expense trends.",
            required_feature_groups=[
                "daily_spending_trends",
                "weekly_spending_trends",
                "monthly_spending_trends",
            ],
        ),
    ]
