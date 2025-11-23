"""
Recommendation Agent Service - Provides actionable improvement suggestions
"""
from typing import List
from app.models.schemas import (
    Recommendation,
    ProcessParameters,
    OptimizationResult,
    YieldPrediction
)


class RecommendationAgent:
    """Agent responsible for generating actionable recommendations"""
    
    def __init__(self):
        self.name = "Recommendation Agent"
    
    def generate_recommendations(
        self,
        current_parameters: ProcessParameters,
        optimization_result: OptimizationResult,
        prediction: YieldPrediction
    ) -> List[Recommendation]:
        """Generate actionable recommendations for yield improvement"""
        recommendations = []
        
        # Temperature recommendation
        temp_change = optimization_result.recommended_parameters.temperature - current_parameters.temperature
        if abs(temp_change) > 0.5:
            recommendations.append(
                Recommendation(
                    action="adjust" if temp_change > 0 else "reduce",
                    parameter="temperature",
                    current_value=current_parameters.temperature,
                    recommended_value=optimization_result.recommended_parameters.temperature,
                    improvement=optimization_result.improvement_percentage * 0.3,
                    description=f"{'Increase' if temp_change > 0 else 'Decrease'} process temperature to optimize thermal conditions"
                )
            )
        
        # Etch time recommendation
        etch_change = optimization_result.recommended_parameters.etch_time - current_parameters.etch_time
        if abs(etch_change) > 0.3:
            recommendations.append(
                Recommendation(
                    action="adjust" if etch_change > 0 else "reduce",
                    parameter="etch_time",
                    current_value=current_parameters.etch_time,
                    recommended_value=optimization_result.recommended_parameters.etch_time,
                    improvement=optimization_result.improvement_percentage * 0.25,
                    description=f"{'Increase' if etch_change > 0 else 'Decrease'} etch time to improve pattern transfer"
                )
            )
        
        # Exposure dose recommendation (most critical)
        dose_change = optimization_result.recommended_parameters.exposure_dose - current_parameters.exposure_dose
        if abs(dose_change) > 0.2:
            dose_change_pct = (dose_change / current_parameters.exposure_dose) * 100
            recommendations.append(
                Recommendation(
                    action="reduce" if dose_change < 0 else "increase",
                    parameter="exposure_dose",
                    current_value=current_parameters.exposure_dose,
                    recommended_value=optimization_result.recommended_parameters.exposure_dose,
                    improvement=optimization_result.improvement_percentage * 0.45,
                    description=f"{'Reduce' if dose_change < 0 else 'Increase'} stepper exposure dose by {abs(dose_change_pct):.1f}% to improve yield from {optimization_result.current_yield:.1f}% → {optimization_result.optimized_yield:.1f}%"
                )
            )
        
        # Sort by improvement impact (descending)
        recommendations.sort(key=lambda x: x.improvement, reverse=True)
        
        # Add general recommendations based on prediction factors
        if prediction.factors:
            for factor in prediction.factors[:2]:  # Top 2 factors
                if not any(rec.description.lower() in factor.lower() or factor.lower() in rec.description.lower() 
                          for rec in recommendations):
                    recommendations.append(
                        Recommendation(
                            action="review",
                            parameter="process",
                            current_value=0.0,
                            recommended_value=0.0,
                            improvement=optimization_result.improvement_percentage * 0.1,
                            description=f"Review and address: {factor}"
                        )
                    )
        
        return recommendations
    
    def format_recommendation_summary(self, recommendations: List[Recommendation]) -> str:
        """Format recommendations as a summary string"""
        if not recommendations:
            return "No specific recommendations at this time. Current parameters are near optimal."
        
        summary_parts = []
        for i, rec in enumerate(recommendations[:3], 1):  # Top 3 recommendations
            if rec.parameter == "exposure_dose" and rec.action in ["reduce", "increase"]:
                change_pct = abs((rec.recommended_value - rec.current_value) / rec.current_value) * 100
                summary_parts.append(
                    f"{rec.action.capitalize()} stepper exposure dose by {change_pct:.1f}% "
                    f"to improve yield from {rec.current_value:.1f} → {rec.recommended_value:.1f}."
                )
            else:
                summary_parts.append(
                    f"{rec.action.capitalize()} {rec.parameter.replace('_', ' ')} "
                    f"from {rec.current_value:.2f} to {rec.recommended_value:.2f}."
                )
        
        return " ".join(summary_parts)

