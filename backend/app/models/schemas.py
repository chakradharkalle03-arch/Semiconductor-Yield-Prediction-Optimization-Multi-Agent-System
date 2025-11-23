from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class WaferData(BaseModel):
    wafer_id: str
    wafer_map: Optional[Dict[str, Any]] = None
    metrology_data: Optional[Dict[str, Any]] = None
    eda_logs: Optional[List[str]] = None


class ProcessParameters(BaseModel):
    temperature: float
    etch_time: float
    exposure_dose: float


class YieldPrediction(BaseModel):
    predicted_yield: float
    confidence: float
    factors: List[str]


class OptimizationResult(BaseModel):
    current_yield: float
    optimized_yield: float
    recommended_parameters: ProcessParameters
    improvement_percentage: float


class Recommendation(BaseModel):
    action: str
    parameter: str
    current_value: float
    recommended_value: float
    improvement: float
    description: str


class AnalysisRequest(BaseModel):
    wafer_data: WaferData
    current_parameters: ProcessParameters


class AnalysisResponse(BaseModel):
    prediction: YieldPrediction
    optimization: OptimizationResult
    recommendations: List[Recommendation]
    current_parameters: ProcessParameters
    timestamp: datetime

