from __future__ import annotations

import argparse
import asyncio
import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import delete, func, select

DEMO_EMAIL_DOMAIN = "example.local"
DEMO_EMAIL_PATTERN = f"demo.%@{DEMO_EMAIL_DOMAIN}"
DEFAULT_PASSWORD = "DemoPass123!"
MONEY_QUANTIZER = Decimal("0.01")

AsyncSessionLocal: Any = None
Expense: Any = None
Goal: Any = None
User: Any = None
engine: Any = None
hash_password: Any = None
settings: Any = None


@dataclass(frozen=True)
class CategoryRule:
    category: str
    descriptions: tuple[str, ...]
    min_amount: int
    max_amount: int


@dataclass(frozen=True)
class BehaviorProfile:
    code: str
    display_name: str
    weekday_spend_chance: float
    weekend_spend_chance: float
    extra_expense_chance: float
    amount_multiplier: Decimal
    category_weights: dict[str, int]
    recurring_habits: tuple[str, ...]
    goal_progress_ratio: Decimal


CATEGORY_RULES: dict[str, CategoryRule] = {
    "Coffee": CategoryRule(
        category="Coffee",
        descriptions=("Morning coffee", "Office coffee", "Cafe stop"),
        min_amount=60,
        max_amount=180,
    ),
    "Snacks": CategoryRule(
        category="Snacks",
        descriptions=("Evening snack", "Quick snack", "Tea and snacks"),
        min_amount=35,
        max_amount=160,
    ),
    "Transport": CategoryRule(
        category="Transport",
        descriptions=("Short ride", "Auto ride", "Cab share", "Metro recharge"),
        min_amount=50,
        max_amount=450,
    ),
    "Food Delivery": CategoryRule(
        category="Food Delivery",
        descriptions=("Dinner delivery", "Lunch order", "Late-night food"),
        min_amount=180,
        max_amount=750,
    ),
    "Groceries": CategoryRule(
        category="Groceries",
        descriptions=("Weekly groceries", "Home essentials", "Fresh produce"),
        min_amount=450,
        max_amount=2200,
    ),
    "Subscriptions": CategoryRule(
        category="Subscriptions",
        descriptions=("Streaming subscription", "App subscription", "Cloud storage"),
        min_amount=99,
        max_amount=899,
    ),
    "Entertainment": CategoryRule(
        category="Entertainment",
        descriptions=("Movie night", "Weekend outing", "Game night"),
        min_amount=250,
        max_amount=1800,
    ),
    "Shopping": CategoryRule(
        category="Shopping",
        descriptions=("Impulse purchase", "Clothing", "Online shopping"),
        min_amount=300,
        max_amount=3200,
    ),
    "Health": CategoryRule(
        category="Health",
        descriptions=("Pharmacy", "Clinic visit", "Wellness purchase"),
        min_amount=150,
        max_amount=1200,
    ),
    "Utilities": CategoryRule(
        category="Utilities",
        descriptions=("Phone recharge", "Electricity bill", "Internet bill"),
        min_amount=250,
        max_amount=2400,
    ),
}

PROFILES: tuple[BehaviorProfile, ...] = (
    BehaviorProfile(
        code="saver",
        display_name="Saver",
        weekday_spend_chance=0.48,
        weekend_spend_chance=0.58,
        extra_expense_chance=0.12,
        amount_multiplier=Decimal("0.82"),
        category_weights={
            "Coffee": 7,
            "Snacks": 5,
            "Transport": 18,
            "Food Delivery": 5,
            "Groceries": 26,
            "Subscriptions": 4,
            "Entertainment": 5,
            "Shopping": 5,
            "Health": 8,
            "Utilities": 17,
        },
        recurring_habits=("Transport",),
        goal_progress_ratio=Decimal("0.74"),
    ),
    BehaviorProfile(
        code="neutral",
        display_name="Neutral",
        weekday_spend_chance=0.68,
        weekend_spend_chance=0.82,
        extra_expense_chance=0.28,
        amount_multiplier=Decimal("1.00"),
        category_weights={
            "Coffee": 12,
            "Snacks": 10,
            "Transport": 17,
            "Food Delivery": 12,
            "Groceries": 18,
            "Subscriptions": 5,
            "Entertainment": 9,
            "Shopping": 8,
            "Health": 4,
            "Utilities": 5,
        },
        recurring_habits=("Coffee", "Transport"),
        goal_progress_ratio=Decimal("0.46"),
    ),
    BehaviorProfile(
        code="spender",
        display_name="Spender",
        weekday_spend_chance=0.88,
        weekend_spend_chance=0.96,
        extra_expense_chance=0.48,
        amount_multiplier=Decimal("1.38"),
        category_weights={
            "Coffee": 14,
            "Snacks": 12,
            "Transport": 12,
            "Food Delivery": 18,
            "Groceries": 8,
            "Subscriptions": 7,
            "Entertainment": 12,
            "Shopping": 13,
            "Health": 2,
            "Utilities": 2,
        },
        recurring_habits=("Coffee", "Snacks", "Food Delivery"),
        goal_progress_ratio=Decimal("0.22"),
    ),
    BehaviorProfile(
        code="weekend",
        display_name="Weekend Spender",
        weekday_spend_chance=0.46,
        weekend_spend_chance=0.98,
        extra_expense_chance=0.4,
        amount_multiplier=Decimal("1.18"),
        category_weights={
            "Coffee": 7,
            "Snacks": 6,
            "Transport": 13,
            "Food Delivery": 17,
            "Groceries": 12,
            "Subscriptions": 4,
            "Entertainment": 19,
            "Shopping": 15,
            "Health": 2,
            "Utilities": 5,
        },
        recurring_habits=("Entertainment", "Food Delivery"),
        goal_progress_ratio=Decimal("0.34"),
    ),
    BehaviorProfile(
        code="micro",
        display_name="Micro-Spender",
        weekday_spend_chance=0.94,
        weekend_spend_chance=0.92,
        extra_expense_chance=0.55,
        amount_multiplier=Decimal("0.92"),
        category_weights={
            "Coffee": 24,
            "Snacks": 22,
            "Transport": 18,
            "Food Delivery": 10,
            "Groceries": 7,
            "Subscriptions": 5,
            "Entertainment": 5,
            "Shopping": 5,
            "Health": 2,
            "Utilities": 2,
        },
        recurring_habits=("Coffee", "Snacks", "Transport"),
        goal_progress_ratio=Decimal("0.31"),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed realistic synthetic demo data for ML and product testing."
    )
    parser.add_argument("--users", type=int, default=10, help="Number of demo users to create.")
    parser.add_argument("--days", type=int, default=90, help="Number of past days to seed.")
    parser.add_argument(
        "--password",
        default=DEFAULT_PASSWORD,
        help="Password assigned to every generated demo user.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260513,
        help="Random seed for reproducible demo datasets.",
    )
    parser.add_argument(
        "--reset-demo-data",
        action="store_true",
        help="Delete existing demo.*@example.local users before seeding.",
    )
    parser.add_argument(
        "--allow-production",
        action="store_true",
        help="Allow running when APP_ENV=production. Use carefully.",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    load_app_dependencies()
    validate_args(args)
    rng = random.Random(args.seed)

    async with AsyncSessionLocal() as session:
        existing_demo_user_count = await count_existing_demo_users(session)
        if existing_demo_user_count and not args.reset_demo_data:
            raise SystemExit(
                f"Found {existing_demo_user_count} existing demo users. "
                "Run again with --reset-demo-data to replace them."
            )

        if args.reset_demo_data:
            deleted_count = await delete_demo_users(session)
            print(f"Deleted {deleted_count} existing demo users.")

        users_created = 0
        expenses_created = 0
        goals_created = 0

        for index in range(args.users):
            profile = PROFILES[index % len(PROFILES)]
            user = create_demo_user(index=index, profile=profile, password=args.password)
            session.add(user)
            await session.flush()

            user_expenses = build_expenses(
                user_id=user.id,
                profile=profile,
                days=args.days,
                rng=rng,
            )
            user_goals = build_goals(user_id=user.id, profile=profile, rng=rng)

            session.add_all(user_expenses)
            session.add_all(user_goals)

            users_created += 1
            expenses_created += len(user_expenses)
            goals_created += len(user_goals)

        await session.commit()

    await engine.dispose()

    print("Synthetic demo data seeded successfully.")
    print(f"Users created: {users_created}")
    print(f"Expenses created: {expenses_created}")
    print(f"Goals created: {goals_created}")
    print(f"Demo password: {args.password}")
    print("Demo emails follow this pattern: demo.<profile>.<number>@example.local")


def load_app_dependencies() -> None:
    global AsyncSessionLocal, Expense, Goal, User, engine, hash_password, settings

    try:
        from app.core.config import settings as loaded_settings
        from app.core.security import hash_password as loaded_hash_password
        from app.db.session import AsyncSessionLocal as loaded_session_local
        from app.db.session import engine as loaded_engine
        from app.models.expense import Expense as loaded_expense
        from app.models.goal import Goal as loaded_goal
        from app.models.user import User as loaded_user
    except Exception as exc:
        raise SystemExit(
            "Could not load backend configuration. From the backend folder, create .env "
            "from .env.example and set DATABASE_URL plus JWT_SECRET_KEY before seeding."
        ) from exc

    AsyncSessionLocal = loaded_session_local
    Expense = loaded_expense
    Goal = loaded_goal
    User = loaded_user
    engine = loaded_engine
    hash_password = loaded_hash_password
    settings = loaded_settings


def validate_args(args: argparse.Namespace) -> None:
    if args.users < 1:
        raise SystemExit("--users must be at least 1.")
    if args.days < 14:
        raise SystemExit("--days must be at least 14 so behavior patterns are meaningful.")
    if len(args.password) < 8:
        raise SystemExit("--password must be at least 8 characters.")
    if settings.app_env == "production" and not args.allow_production:
        raise SystemExit(
            "Refusing to seed demo data while APP_ENV=production. "
            "Pass --allow-production only if you intentionally want demo users there."
        )


async def count_existing_demo_users(session) -> int:
    result = await session.execute(
        select(func.count()).select_from(User).where(User.email.like(DEMO_EMAIL_PATTERN))
    )
    return int(result.scalar_one())


async def delete_demo_users(session) -> int:
    result = await session.execute(delete(User).where(User.email.like(DEMO_EMAIL_PATTERN)))
    await session.commit()
    return int(result.rowcount or 0)


def create_demo_user(*, index: int, profile: BehaviorProfile, password: str) -> User:
    user_number = index + 1
    return User(
        email=f"demo.{profile.code}.{user_number:02d}@{DEMO_EMAIL_DOMAIN}",
        hashed_password=hash_password(password),
        full_name=f"Demo {profile.display_name} {user_number:02d}",
        is_active=True,
        is_verified=True,
    )


def build_expenses(
    *,
    user_id: UUID,
    profile: BehaviorProfile,
    days: int,
    rng: random.Random,
) -> list[Expense]:
    today = datetime.now(UTC).date()
    start_date = today - timedelta(days=days - 1)
    expenses: list[Expense] = []

    for day_offset in range(days):
        spent_on = start_date + timedelta(days=day_offset)
        is_weekend = spent_on.weekday() >= 5
        spend_chance = profile.weekend_spend_chance if is_weekend else profile.weekday_spend_chance

        add_recurring_habit_expenses(
            expenses=expenses,
            user_id=user_id,
            profile=profile,
            spent_on=spent_on,
            rng=rng,
        )

        if is_subscription_day(spent_on):
            expenses.append(
                create_expense(
                    user_id=user_id,
                    rule=CATEGORY_RULES["Subscriptions"],
                    profile=profile,
                    spent_on=spent_on,
                    rng=rng,
                    hour_range=(9, 12),
                )
            )

        if rng.random() > spend_chance:
            continue

        expense_count = 1
        while rng.random() < profile.extra_expense_chance and expense_count < 4:
            expense_count += 1

        for _ in range(expense_count):
            category_name = choose_weighted_category(profile.category_weights, rng)
            hour_range = (18, 23) if is_weekend else (8, 22)
            expenses.append(
                create_expense(
                    user_id=user_id,
                    rule=CATEGORY_RULES[category_name],
                    profile=profile,
                    spent_on=spent_on,
                    rng=rng,
                    hour_range=hour_range,
                )
            )

    return expenses


def add_recurring_habit_expenses(
    *,
    expenses: list[Expense],
    user_id: UUID,
    profile: BehaviorProfile,
    spent_on: date,
    rng: random.Random,
) -> None:
    if spent_on.weekday() >= 5 and profile.code != "weekend":
        habit_chance = 0.35
    else:
        habit_chance = 0.64 if profile.code in {"micro", "spender"} else 0.42

    for category_name in profile.recurring_habits:
        if rng.random() <= habit_chance:
            expenses.append(
                create_expense(
                    user_id=user_id,
                    rule=CATEGORY_RULES[category_name],
                    profile=profile,
                    spent_on=spent_on,
                    rng=rng,
                    hour_range=(8, 11) if category_name == "Coffee" else (17, 21),
                    force_first_description=True,
                )
            )


def create_expense(
    *,
    user_id: UUID,
    rule: CategoryRule,
    profile: BehaviorProfile,
    spent_on: date,
    rng: random.Random,
    hour_range: tuple[int, int],
    force_first_description: bool = False,
) -> Expense:
    description = rule.descriptions[0] if force_first_description else rng.choice(rule.descriptions)
    return Expense(
        user_id=user_id,
        amount=random_money(
            min_amount=rule.min_amount,
            max_amount=rule.max_amount,
            multiplier=profile.amount_multiplier,
            rng=rng,
        ),
        category=rule.category,
        description=description,
        spent_at=random_datetime_on(spent_on=spent_on, hour_range=hour_range, rng=rng),
    )


def random_money(
    *,
    min_amount: int,
    max_amount: int,
    multiplier: Decimal,
    rng: random.Random,
) -> Decimal:
    rounded_rupees = rng.randrange(min_amount, max_amount + 1, 5)
    amount = Decimal(rounded_rupees) * multiplier
    return amount.quantize(MONEY_QUANTIZER, rounding=ROUND_HALF_UP)


def random_datetime_on(
    *,
    spent_on: date,
    hour_range: tuple[int, int],
    rng: random.Random,
) -> datetime:
    hour = rng.randint(hour_range[0], hour_range[1])
    minute = rng.choice((0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55))
    return datetime.combine(spent_on, time(hour=hour, minute=minute), tzinfo=UTC)


def is_subscription_day(spent_on: date) -> bool:
    return spent_on.day in {5, 17}


def choose_weighted_category(weights: dict[str, int], rng: random.Random) -> str:
    return rng.choices(
        population=list(weights.keys()),
        weights=list(weights.values()),
        k=1,
    )[0]


def build_goals(*, user_id: UUID, profile: BehaviorProfile, rng: random.Random) -> list[Goal]:
    target_amount = random_money(
        min_amount=15_000,
        max_amount=80_000,
        multiplier=Decimal("1.00"),
        rng=rng,
    )
    current_amount = (target_amount * profile.goal_progress_ratio).quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )
    secondary_target = random_money(
        min_amount=5_000,
        max_amount=25_000,
        multiplier=Decimal("1.00"),
        rng=rng,
    )
    secondary_current = (secondary_target * Decimal(rng.choice(("0.15", "0.25", "0.40")))).quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )

    return [
        Goal(
            user_id=user_id,
            name=f"{profile.display_name} emergency fund",
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=datetime.now(UTC).date() + timedelta(days=rng.randint(45, 180)),
            is_completed=current_amount >= target_amount,
        ),
        Goal(
            user_id=user_id,
            name="Monthly savings challenge",
            target_amount=secondary_target,
            current_amount=secondary_current,
            target_date=datetime.now(UTC).date() + timedelta(days=rng.randint(20, 60)),
            is_completed=secondary_current >= secondary_target,
        ),
    ]


if __name__ == "__main__":
    asyncio.run(main())
