from app.ml.capabilities import get_planned_ml_capabilities
from app.schemas.ml import MLReadinessResponse


class MLReadinessService:
    def get_readiness(self) -> MLReadinessResponse:
        return MLReadinessResponse(
            ml_enabled=False,
            model_execution_available=False,
            capabilities=get_planned_ml_capabilities(),
        )
