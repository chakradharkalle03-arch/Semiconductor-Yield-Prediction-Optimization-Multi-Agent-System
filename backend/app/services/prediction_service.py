"""
Prediction Agent Service - Uses HuggingFace LLM to forecast yield
"""
import os
from typing import Dict, Any
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from app.models.schemas import YieldPrediction, ProcessParameters


class PredictionAgent:
    """Agent responsible for yield prediction using LLM"""
    
    def __init__(self, api_key: str):
        self.name = "Prediction Agent"
        self.api_key = api_key
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize HuggingFace LLM"""
        if not self.api_key or self.api_key == "dummy_key":
            self.llm = None
            return
            
        try:
            # Using HuggingFace Inference API
            # Set environment variable for API token
            import os
            os.environ["HUGGINGFACE_API_TOKEN"] = self.api_key
            
            # Try a smaller model that's more likely to work
            # Parameters should be passed directly, not in model_kwargs
            self.llm = HuggingFaceEndpoint(
                repo_id="mistralai/Mistral-7B-Instruct-v0.1",
                temperature=0.3,
                max_new_tokens=512,
                timeout=30
            )
            # Test the connection with a simple prompt
            _ = self.llm.invoke("test")
        except Exception as e:
            print(f"Warning: Could not initialize HuggingFace LLM: {e}")
            print("Falling back to rule-based prediction")
            self.llm = None
    
    def predict_yield(
        self, 
        data_summary: Dict[str, Any],
        parameters: ProcessParameters
    ) -> YieldPrediction:
        """Predict yield based on data and parameters"""
        
        if self.llm:
            return self._predict_with_llm(data_summary, parameters)
        else:
            return self._predict_rule_based(data_summary, parameters)
    
    def _predict_with_llm(
        self,
        data_summary: Dict[str, Any],
        parameters: ProcessParameters
    ) -> YieldPrediction:
        """Use LLM for yield prediction"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert semiconductor yield prediction system.
                Analyze the provided data and predict the die yield percentage.
                Consider:
                - Wafer map quality and defect density
                - Metrology measurements
                - Process parameters (temperature, etch time, exposure dose)
                - EDA log errors and warnings
                
                Respond with a JSON object containing:
                - predicted_yield: float (0-100)
                - confidence: float (0-1)
                - factors: list of key factors affecting yield
                """),
                ("human", """Data Summary:
                Wafer Map: {wafer_map_summary}
                Metrology: {metrology_summary}
                EDA Logs: {eda_summary}
                Quality Score: {quality_score}
                
                Process Parameters:
                Temperature: {temperature}°C
                Etch Time: {etch_time}s
                Exposure Dose: {exposure_dose}mJ/cm²
                
                Predict the yield percentage and explain key factors."""),
            ])
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            response = chain.run(
                wafer_map_summary=str(data_summary.get("wafer_map", {})),
                metrology_summary=str(data_summary.get("metrology", {})),
                eda_summary=str(data_summary.get("eda_logs", {})),
                quality_score=data_summary.get("quality_score", 0.5),
                temperature=parameters.temperature,
                etch_time=parameters.etch_time,
                exposure_dose=parameters.exposure_dose
            )
            
            # Parse LLM response (simplified - in production, use structured output)
            # For now, fall back to rule-based if parsing fails
            return self._parse_llm_response(response, data_summary, parameters)
            
        except Exception as e:
            print(f"LLM prediction failed: {e}, falling back to rule-based")
            return self._predict_rule_based(data_summary, parameters)
    
    def _parse_llm_response(
        self,
        response: str,
        data_summary: Dict[str, Any],
        parameters: ProcessParameters
    ) -> YieldPrediction:
        """Parse LLM response (simplified implementation)"""
        # Try to extract yield from response
        import re
        yield_match = re.search(r'(\d+\.?\d*)%', response)
        if yield_match:
            predicted_yield = float(yield_match.group(1))
        else:
            # Fallback to rule-based
            return self._predict_rule_based(data_summary, parameters)
        
        factors = []
        if "temperature" in response.lower():
            factors.append("Temperature optimization needed")
        if "etch" in response.lower():
            factors.append("Etch time adjustment")
        if "exposure" in response.lower():
            factors.append("Exposure dose tuning")
        
        return YieldPrediction(
            predicted_yield=min(100.0, max(0.0, predicted_yield)),
            confidence=0.75,
            factors=factors if factors else ["Process parameter optimization"]
        )
    
    def _predict_rule_based(
        self,
        data_summary: Dict[str, Any],
        parameters: ProcessParameters
    ) -> YieldPrediction:
        """Rule-based yield prediction (fallback)"""
        base_yield = 90.0
        factors = []
        
        # Adjust based on quality score
        quality_score = data_summary.get("quality_score", 0.5)
        base_yield *= quality_score
        
        # Adjust based on process parameters
        # Optimal ranges (example values)
        optimal_temp = 200.0
        optimal_etch = 45.0
        optimal_dose = 50.0
        
        temp_deviation = abs(parameters.temperature - optimal_temp) / optimal_temp
        etch_deviation = abs(parameters.etch_time - optimal_etch) / optimal_etch
        dose_deviation = abs(parameters.exposure_dose - optimal_dose) / optimal_dose
        
        # Penalize deviations
        base_yield -= temp_deviation * 10
        base_yield -= etch_deviation * 8
        base_yield -= dose_deviation * 12
        
        if temp_deviation > 0.1:
            factors.append("Temperature out of optimal range")
        if etch_deviation > 0.1:
            factors.append("Etch time needs adjustment")
        if dose_deviation > 0.1:
            factors.append("Exposure dose optimization required")
        
        # Adjust based on EDA errors
        eda_data = data_summary.get("eda_logs", {}).get("data", {})
        if eda_data:
            error_count = eda_data.get("errors", 0)
            base_yield -= error_count * 2
        
        # Adjust based on defect density
        wafer_map_data = data_summary.get("wafer_map", {}).get("data", {})
        if wafer_map_data:
            defect_density = wafer_map_data.get("defect_density", 0.0)
            base_yield -= defect_density * 5
        
        predicted_yield = max(0.0, min(100.0, base_yield))
        confidence = 0.7 if quality_score > 0.7 else 0.5
        
        return YieldPrediction(
            predicted_yield=predicted_yield,
            confidence=confidence,
            factors=factors if factors else ["Standard process parameters"]
        )

