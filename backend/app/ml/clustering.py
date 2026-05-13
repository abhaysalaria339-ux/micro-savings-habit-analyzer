from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.ml.contracts import MLModelContract
from app.ml.features import UserSpendingFeatureVector

RATIO_QUANTIZER = Decimal("0.0001")


@dataclass(frozen=True)
class SpendingProfilePrediction:
    cluster_id: str
    profile_label: str
    confidence: Decimal
    summary: str
    reasons: list[str]
    recommendations: list[str]


@dataclass(frozen=True)
class SpendingProfileCentroid:
    cluster_id: str
    label: str
    summary: str
    values: dict[str, Decimal]
    recommendations: list[str]


class SpendingProfileClusteringModel(
    MLModelContract[UserSpendingFeatureVector, SpendingProfilePrediction]
):
    def predict(self, features: UserSpendingFeatureVector) -> SpendingProfilePrediction:
        if features.transaction_count < 10:
            return SpendingProfilePrediction(
                cluster_id="insufficient_data",
                profile_label="Insufficient data",
                confidence=Decimal("0.0000"),
                summary="Add more expenses to generate a reliable spending profile.",
                reasons=["At least 10 expense records are needed for the first profile estimate."],
                recommendations=[
                    "Seed demo data or track expenses for a few weeks before relying on "
                    "ML profiles."
                ],
            )

        normalized_features = self._normalize_features(features)
        scored_profiles = sorted(
            (
                (
                    self._euclidean_distance(normalized_features, centroid.values),
                    centroid,
                )
                for centroid in PROFILE_CENTROIDS
            ),
            key=lambda item: item[0],
        )
        nearest_distance, nearest_centroid = scored_profiles[0]

        return SpendingProfilePrediction(
            cluster_id=nearest_centroid.cluster_id,
            profile_label=nearest_centroid.label,
            confidence=self._confidence_from_distance(nearest_distance),
            summary=nearest_centroid.summary,
            reasons=self._build_reasons(features),
            recommendations=nearest_centroid.recommendations,
        )

    def _normalize_features(
        self,
        features: UserSpendingFeatureVector,
    ) -> dict[str, Decimal]:
        return {
            "micro_expense_ratio": features.micro_expense_ratio,
            "weekend_spend_ratio": features.weekend_spend_ratio,
            "food_and_snack_spend_ratio": features.food_and_snack_spend_ratio,
            "subscription_spend_ratio": features.subscription_spend_ratio,
            "top_category_spend_ratio": features.top_category_spend_ratio,
            "spending_frequency_per_day": self._clamp_ratio(
                features.spending_frequency_per_day / Decimal("3.00")
            ),
            "average_transaction_amount": self._clamp_ratio(
                features.average_transaction_amount / Decimal("1500.00")
            ),
            "spend_trend_ratio": self._normalize_trend(features.spend_trend_ratio),
        }

    def _build_reasons(self, features: UserSpendingFeatureVector) -> list[str]:
        reasons: list[str] = []

        if features.micro_expense_ratio >= Decimal("0.45"):
            reasons.append("A high share of transactions are micro-expenses.")
        if features.weekend_spend_ratio >= Decimal("0.40"):
            reasons.append("Weekend spending contributes a large part of total spend.")
        if features.food_and_snack_spend_ratio >= Decimal("0.35"):
            reasons.append("Coffee, snacks, and food delivery are strong spending signals.")
        if features.top_category_spend_ratio >= Decimal("0.45"):
            reasons.append("Spending is concentrated in one dominant category.")
        if features.spend_trend_ratio > Decimal("0.1500"):
            reasons.append("Recent spending is trending upward compared with the earlier period.")

        if not reasons:
            reasons.append("Spending signals are balanced across frequency, category, and timing.")

        return reasons

    def _euclidean_distance(
        self,
        features: dict[str, Decimal],
        centroid: dict[str, Decimal],
    ) -> Decimal:
        squared_distance = sum(
            (features[name] - centroid[name]) ** 2
            for name in centroid
        )
        return Decimal(str(float(squared_distance) ** 0.5))

    def _confidence_from_distance(self, distance: Decimal) -> Decimal:
        confidence = Decimal("1.00") / (Decimal("1.00") + distance)
        return confidence.quantize(RATIO_QUANTIZER, rounding=ROUND_HALF_UP)

    def _normalize_trend(self, trend_ratio: Decimal) -> Decimal:
        clamped = max(Decimal("-1.00"), min(Decimal("1.00"), trend_ratio))
        return ((clamped + Decimal("1.00")) / Decimal("2.00")).quantize(
            RATIO_QUANTIZER,
            rounding=ROUND_HALF_UP,
        )

    def _clamp_ratio(self, value: Decimal) -> Decimal:
        return max(Decimal("0.0000"), min(Decimal("1.0000"), value)).quantize(
            RATIO_QUANTIZER,
            rounding=ROUND_HALF_UP,
        )


PROFILE_CENTROIDS = (
    SpendingProfileCentroid(
        cluster_id="saver",
        label="Saver",
        summary=(
            "Spending appears controlled, with lower frequency and fewer risky leakage signals."
        ),
        values={
            "micro_expense_ratio": Decimal("0.18"),
            "weekend_spend_ratio": Decimal("0.20"),
            "food_and_snack_spend_ratio": Decimal("0.16"),
            "subscription_spend_ratio": Decimal("0.08"),
            "top_category_spend_ratio": Decimal("0.32"),
            "spending_frequency_per_day": Decimal("0.18"),
            "average_transaction_amount": Decimal("0.24"),
            "spend_trend_ratio": Decimal("0.42"),
        },
        recommendations=[
            "Keep tracking consistently and move surplus into goals weekly.",
            "Watch subscriptions so low spending does not hide recurring leaks.",
        ],
    ),
    SpendingProfileCentroid(
        cluster_id="neutral",
        label="Neutral",
        summary="Spending is moderate and mixed, with no single severe leakage signal.",
        values={
            "micro_expense_ratio": Decimal("0.32"),
            "weekend_spend_ratio": Decimal("0.28"),
            "food_and_snack_spend_ratio": Decimal("0.27"),
            "subscription_spend_ratio": Decimal("0.08"),
            "top_category_spend_ratio": Decimal("0.36"),
            "spending_frequency_per_day": Decimal("0.36"),
            "average_transaction_amount": Decimal("0.34"),
            "spend_trend_ratio": Decimal("0.50"),
        },
        recommendations=[
            "Pick one category to reduce by 10 percent this month.",
            "Use the simulator before increasing recurring spending.",
        ],
    ),
    SpendingProfileCentroid(
        cluster_id="spender",
        label="Spender",
        summary="Spending shows frequent activity and stronger leakage risk across categories.",
        values={
            "micro_expense_ratio": Decimal("0.45"),
            "weekend_spend_ratio": Decimal("0.35"),
            "food_and_snack_spend_ratio": Decimal("0.45"),
            "subscription_spend_ratio": Decimal("0.05"),
            "top_category_spend_ratio": Decimal("0.45"),
            "spending_frequency_per_day": Decimal("0.75"),
            "average_transaction_amount": Decimal("0.60"),
            "spend_trend_ratio": Decimal("0.62"),
        },
        recommendations=[
            "Set a weekly discretionary spending cap.",
            "Skip one repeated purchase pattern and transfer that amount to a goal.",
        ],
    ),
    SpendingProfileCentroid(
        cluster_id="weekend_spender",
        label="Weekend Spender",
        summary="Spending is weighted toward weekends and leisure-style categories.",
        values={
            "micro_expense_ratio": Decimal("0.26"),
            "weekend_spend_ratio": Decimal("0.56"),
            "food_and_snack_spend_ratio": Decimal("0.34"),
            "subscription_spend_ratio": Decimal("0.05"),
            "top_category_spend_ratio": Decimal("0.44"),
            "spending_frequency_per_day": Decimal("0.45"),
            "average_transaction_amount": Decimal("0.62"),
            "spend_trend_ratio": Decimal("0.58"),
        },
        recommendations=[
            "Plan a weekend budget before Friday evening.",
            "Move planned savings before weekend spending starts.",
        ],
    ),
    SpendingProfileCentroid(
        cluster_id="micro_spender",
        label="Micro-Spender",
        summary="Many small purchases appear repeatedly and may become invisible money leaks.",
        values={
            "micro_expense_ratio": Decimal("0.70"),
            "weekend_spend_ratio": Decimal("0.25"),
            "food_and_snack_spend_ratio": Decimal("0.55"),
            "subscription_spend_ratio": Decimal("0.05"),
            "top_category_spend_ratio": Decimal("0.40"),
            "spending_frequency_per_day": Decimal("0.85"),
            "average_transaction_amount": Decimal("0.18"),
            "spend_trend_ratio": Decimal("0.55"),
        },
        recommendations=[
            "Bundle small purchases into a fixed daily allowance.",
            "Choose one repeated micro-expense to pause for seven days.",
        ],
    ),
)
