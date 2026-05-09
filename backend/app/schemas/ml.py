from typing import Literal

from pydantic import BaseModel

MLProblemType = Literal["clustering", "classification", "forecasting"]


class MLCapability(BaseModel):
    problem_type: MLProblemType
    status: Literal["planned", "available"]
    description: str
    required_feature_groups: list[str]


class MLReadinessResponse(BaseModel):
    ml_enabled: bool
    model_execution_available: bool
    capabilities: list[MLCapability]
