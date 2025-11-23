"""
Optimization Agent Service - Performs parameter search for yield optimization
"""
from typing import Dict, Any, List, Tuple
import numpy as np
from app.models.schemas import ProcessParameters, OptimizationResult, YieldPrediction


class OptimizationAgent:
    """Agent responsible for optimizing process parameters"""
    
    def __init__(self):
        self.name = "Optimization Agent"
        # Optimal parameter ranges (based on semiconductor manufacturing best practices)
        self.optimal_ranges = {
            "temperature": (195.0, 205.0),  # °C
            "etch_time": (42.0, 48.0),      # seconds
            "exposure_dose": (48.0, 52.0)   # mJ/cm²
        }
    
    def optimize_parameters(
        self,
        current_parameters: ProcessParameters,
        current_yield: float,
        data_summary: Dict[str, Any]
    ) -> OptimizationResult:
        """Optimize process parameters to improve yield"""
        
        # Perform grid search around current parameters
        best_params = current_parameters
        best_yield = current_yield
        
        # Search space around current values
        temp_range = self._get_search_range(current_parameters.temperature, 5.0)
        etch_range = self._get_search_range(current_parameters.etch_time, 3.0)
        dose_range = self._get_search_range(current_parameters.exposure_dose, 2.0)
        
        # Grid search (simplified - in production, use more sophisticated optimization)
        search_points = self._generate_search_points(
            temp_range, etch_range, dose_range, n_points=27
        )
        
        for temp, etch, dose in search_points:
            # Check if within optimal ranges
            if not self._is_in_optimal_range(temp, etch, dose):
                continue
            
            # Estimate yield for these parameters
            test_params = ProcessParameters(
                temperature=temp,
                etch_time=etch,
                exposure_dose=dose
            )
            
            estimated_yield = self._estimate_yield(
                test_params, data_summary, current_yield
            )
            
            if estimated_yield > best_yield:
                best_yield = estimated_yield
                best_params = test_params
        
        improvement = ((best_yield - current_yield) / current_yield) * 100 if current_yield > 0 else 0
        
        return OptimizationResult(
            current_yield=current_yield,
            optimized_yield=best_yield,
            recommended_parameters=best_params,
            improvement_percentage=improvement
        )
    
    def _get_search_range(self, center: float, radius: float) -> Tuple[float, float]:
        """Get search range around a center value"""
        return (max(0, center - radius), center + radius)
    
    def _generate_search_points(
        self,
        temp_range: Tuple[float, float],
        etch_range: Tuple[float, float],
        dose_range: Tuple[float, float],
        n_points: int = 27
    ) -> List[Tuple[float, float, float]]:
        """Generate search points in parameter space"""
        points = []
        
        # Create a 3x3x3 grid
        n_per_dim = int(np.ceil(n_points ** (1/3)))
        
        temp_values = np.linspace(temp_range[0], temp_range[1], n_per_dim)
        etch_values = np.linspace(etch_range[0], etch_range[1], n_per_dim)
        dose_values = np.linspace(dose_range[0], dose_range[1], n_per_dim)
        
        for temp in temp_values:
            for etch in etch_values:
                for dose in dose_values:
                    points.append((float(temp), float(etch), float(dose)))
        
        return points[:n_points]
    
    def _is_in_optimal_range(self, temp: float, etch: float, dose: float) -> bool:
        """Check if parameters are within optimal manufacturing ranges"""
        temp_ok = self.optimal_ranges["temperature"][0] <= temp <= self.optimal_ranges["temperature"][1]
        etch_ok = self.optimal_ranges["etch_time"][0] <= etch <= self.optimal_ranges["etch_time"][1]
        dose_ok = self.optimal_ranges["exposure_dose"][0] <= dose <= self.optimal_ranges["exposure_dose"][1]
        return temp_ok and etch_ok and dose_ok
    
    def _estimate_yield(
        self,
        parameters: ProcessParameters,
        data_summary: Dict[str, Any],
        baseline_yield: float
    ) -> float:
        """Estimate yield for given parameters"""
        # Simplified yield estimation model
        # In production, this would use a trained ML model or physics-based simulation
        
        base_yield = baseline_yield
        
        # Optimal values (center of optimal ranges)
        optimal_temp = 200.0
        optimal_etch = 45.0
        optimal_dose = 50.0
        
        # Calculate deviations
        temp_dev = abs(parameters.temperature - optimal_temp) / optimal_temp
        etch_dev = abs(parameters.etch_time - optimal_etch) / optimal_etch
        dose_dev = abs(parameters.exposure_dose - optimal_dose) / optimal_dose
        
        # Yield improvement from moving closer to optimal
        temp_improvement = (1 - temp_dev) * 3.0
        etch_improvement = (1 - etch_dev) * 2.5
        dose_improvement = (1 - dose_dev) * 4.0
        
        estimated = base_yield + temp_improvement + etch_improvement + dose_improvement
        
        # Cap at 100%
        return min(100.0, max(0.0, estimated))
    
    def get_parameter_sensitivity(
        self,
        parameters: ProcessParameters,
        data_summary: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate sensitivity of yield to each parameter"""
        base_yield = self._estimate_yield(parameters, data_summary, 90.0)
        
        sensitivities = {}
        
        # Test temperature sensitivity
        temp_plus = ProcessParameters(
            temperature=parameters.temperature + 1.0,
            etch_time=parameters.etch_time,
            exposure_dose=parameters.exposure_dose
        )
        yield_temp_plus = self._estimate_yield(temp_plus, data_summary, 90.0)
        sensitivities["temperature"] = abs(yield_temp_plus - base_yield)
        
        # Test etch time sensitivity
        etch_plus = ProcessParameters(
            temperature=parameters.temperature,
            etch_time=parameters.etch_time + 0.5,
            exposure_dose=parameters.exposure_dose
        )
        yield_etch_plus = self._estimate_yield(etch_plus, data_summary, 90.0)
        sensitivities["etch_time"] = abs(yield_etch_plus - base_yield)
        
        # Test exposure dose sensitivity
        dose_plus = ProcessParameters(
            temperature=parameters.temperature,
            etch_time=parameters.etch_time,
            exposure_dose=parameters.exposure_dose + 0.5
        )
        yield_dose_plus = self._estimate_yield(dose_plus, data_summary, 90.0)
        sensitivities["exposure_dose"] = abs(yield_dose_plus - base_yield)
        
        return sensitivities

