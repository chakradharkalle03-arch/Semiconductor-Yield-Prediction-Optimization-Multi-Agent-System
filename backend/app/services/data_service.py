"""
Data Agent Service - Handles wafer maps, metrology data, and EDA logs
"""
import json
from typing import Dict, Any, List
from app.models.schemas import WaferData


class DataAgent:
    """Agent responsible for reading and processing semiconductor data"""
    
    def __init__(self):
        self.name = "Data Agent"
    
    def read_wafer_map(self, wafer_map: Dict[str, Any]) -> Dict[str, Any]:
        """Process wafer map data"""
        if not wafer_map:
            return {"status": "no_data", "message": "No wafer map provided"}
        
        # Extract key metrics from wafer map
        processed = {
            "total_dies": wafer_map.get("total_dies", 0),
            "good_dies": wafer_map.get("good_dies", 0),
            "defect_density": wafer_map.get("defect_density", 0.0),
            "spatial_distribution": wafer_map.get("spatial_distribution", {}),
            "edge_exclusion": wafer_map.get("edge_exclusion", 0)
        }
        
        return {
            "status": "success",
            "data": processed,
            "summary": f"Processed wafer map with {processed['total_dies']} dies"
        }
    
    def read_metrology_data(self, metrology_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process metrology data"""
        if not metrology_data:
            return {"status": "no_data", "message": "No metrology data provided"}
        
        processed = {
            "thickness": metrology_data.get("thickness", {}),
            "critical_dimensions": metrology_data.get("critical_dimensions", {}),
            "overlay": metrology_data.get("overlay", {}),
            "film_stress": metrology_data.get("film_stress", 0.0)
        }
        
        return {
            "status": "success",
            "data": processed,
            "summary": "Processed metrology measurements"
        }
    
    def read_eda_logs(self, eda_logs: List[str]) -> Dict[str, Any]:
        """Process EDA (Electronic Design Automation) logs"""
        if not eda_logs:
            return {"status": "no_data", "message": "No EDA logs provided"}
        
        # Analyze logs for errors, warnings, and key events
        errors = []
        warnings = []
        key_events = []
        
        for log in eda_logs:
            log_lower = log.lower()
            if "error" in log_lower:
                errors.append(log)
            elif "warning" in log_lower:
                warnings.append(log)
            elif any(keyword in log_lower for keyword in ["complete", "success", "finished"]):
                key_events.append(log)
        
        processed = {
            "total_logs": len(eda_logs),
            "errors": len(errors),
            "warnings": len(warnings),
            "key_events": len(key_events),
            "error_details": errors[:5],  # First 5 errors
            "warning_details": warnings[:5]  # First 5 warnings
        }
        
        return {
            "status": "success",
            "data": processed,
            "summary": f"Processed {len(eda_logs)} EDA logs: {len(errors)} errors, {len(warnings)} warnings"
        }
    
    def process_wafer_data(self, wafer_data: WaferData) -> Dict[str, Any]:
        """Main method to process all wafer data"""
        results = {
            "wafer_id": wafer_data.wafer_id,
            "wafer_map": self.read_wafer_map(wafer_data.wafer_map),
            "metrology": self.read_metrology_data(wafer_data.metrology_data),
            "eda_logs": self.read_eda_logs(wafer_data.eda_logs)
        }
        
        # Calculate overall data quality score
        quality_score = self._calculate_quality_score(results)
        results["quality_score"] = quality_score
        
        return results
    
    def _calculate_quality_score(self, results: Dict[str, Any]) -> float:
        """Calculate data quality score (0-1)"""
        score = 1.0
        
        # Deduct points for missing data
        if results["wafer_map"]["status"] == "no_data":
            score -= 0.3
        if results["metrology"]["status"] == "no_data":
            score -= 0.3
        if results["eda_logs"]["status"] == "no_data":
            score -= 0.2
        
        # Deduct points for errors
        if results["eda_logs"]["status"] == "success":
            error_count = results["eda_logs"]["data"]["errors"]
            score -= min(0.2, error_count * 0.05)
        
        return max(0.0, score)

