"""
FastAPI main application
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv
import os
import shutil
from datetime import datetime
from pathlib import Path

from app.models.schemas import (
    AnalysisRequest, AnalysisResponse, WaferData, ProcessParameters
)
from app.agents.supervisor import SupervisorAgent
from app.services.dataset_service import DatasetService

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Semiconductor Yield Prediction & Optimization API",
    description="Multi-Agent System for Yield Prediction and Process Optimization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3008", "http://localhost:5173", "http://localhost:8006", "http://127.0.0.1:3008"],  # Frontend servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize supervisor agent
hf_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
if not hf_api_key:
    print("Warning: HUGGINGFACE_API_KEY not found. System will use rule-based prediction.")
    hf_api_key = "dummy_key"  # Will trigger fallback to rule-based

supervisor = SupervisorAgent(hf_api_key)
dataset_service = DatasetService()

# Create uploads directory
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Semiconductor Yield Prediction & Optimization API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_yield(request: AnalysisRequest):
    """
    Main endpoint for yield analysis and optimization
    
    Processes wafer data, predicts yield, optimizes parameters, and generates recommendations.
    Note: For PDF reports, use /generate-report endpoint instead.
    """
    try:
        response = supervisor.analyze(
            wafer_data=request.wafer_data,
            current_parameters=request.current_parameters
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/predict")
async def predict_only(request: AnalysisRequest):
    """Predict yield without optimization"""
    try:
        from app.services.data_service import DataAgent
        from app.services.prediction_service import PredictionAgent
        
        data_agent = DataAgent()
        prediction_agent = PredictionAgent(hf_api_key)
        
        data_summary = data_agent.process_wafer_data(request.wafer_data)
        prediction = prediction_agent.predict_yield(
            data_summary,
            request.current_parameters
        )
        
        return {
            "prediction": prediction,
            "data_summary": data_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/generate-report")
async def generate_report(request: AnalysisRequest):
    """
    Generate PDF report from analysis results
    
    Performs full analysis and returns PDF report instead of JSON
    """
    try:
        # Run full analysis
        response = supervisor.analyze(
            wafer_data=request.wafer_data,
            current_parameters=request.current_parameters
        )
        
        # Generate PDF report
        pdf_buffer = supervisor.report_agent.generate_pdf_report(
            response,
            wafer_id=request.wafer_data.wafer_id
        )
        
        # Return PDF as response
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="yield_report_{request.wafer_data.wafer_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.get("/datasets")
async def list_datasets():
    """List all available datasets"""
    datasets = dataset_service.list_datasets()
    return {"datasets": datasets}


@app.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    """Get a specific dataset"""
    dataset_path = dataset_service.get_dataset_path(dataset_id)
    if not dataset_path or not dataset_path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    
    import json
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return {"id": dataset_id, "data": data}


@app.post("/datasets/{dataset_id}/convert")
async def convert_dataset_to_wafer_data(dataset_id: str):
    """Convert uploaded dataset to wafer data format for analysis"""
    try:
        dataset_path = dataset_service.get_dataset_path(dataset_id)
        if not dataset_path or not dataset_path.exists():
            raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
        
        import json
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset_data = json.load(f)
        
        # Convert dataset to wafer data format
        # Handle list of records - use first record
        if isinstance(dataset_data, list) and len(dataset_data) > 0:
            record = dataset_data[0]
        elif isinstance(dataset_data, dict):
            record = dataset_data
        else:
            raise HTTPException(status_code=400, detail="Dataset format not supported")
        
        # Extract or generate wafer data from dataset
        wafer_data = WaferData(
            wafer_id=record.get('wafer_id', f"WAFER_{dataset_id[:8]}"),
            wafer_map={
                "total_dies": record.get('total_dies', record.get('totalDies', 500)),
                "good_dies": record.get('good_dies', record.get('goodDies', 465)),
                "defect_density": record.get('defect_density', record.get('defectDensity', 0.07)),
                "spatial_distribution": record.get('spatial_distribution', {"center": 0.02, "edge": 0.12}),
                "edge_exclusion": record.get('edge_exclusion', 3)
            },
            metrology_data={
                "thickness": {
                    "mean": record.get('thickness_mean', record.get('thicknessMean', 1.2)),
                    "std": record.get('thickness_std', record.get('thicknessStd', 0.05)),
                    "uniformity": record.get('thickness_uniformity', 0.95)
                },
                "critical_dimensions": {
                    "target": record.get('cd_target', record.get('cdTarget', 0.1)),
                    "actual": record.get('cd_actual', record.get('cdActual', 0.102)),
                    "variation": record.get('cd_variation', 0.003)
                }
            },
            eda_logs=record.get('eda_logs', [])
        )
        
        # Extract or generate process parameters
        current_parameters = ProcessParameters(
            temperature=record.get('temperature', record.get('temp', 198.5)),
            etch_time=record.get('etch_time', record.get('etchTime', 46.2)),
            exposure_dose=record.get('exposure_dose', record.get('exposureDose', 51.5))
        )
        
        return {
            "wafer_data": wafer_data.model_dump(),
            "current_parameters": current_parameters.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.post("/datasets/download")
async def download_huggingface_dataset(
    dataset_name: str = Form(...),
    dataset_config: str = Form(None),
    split: str = Form("train")
):
    """Download a dataset from HuggingFace"""
    result = dataset_service.download_huggingface_dataset(
        dataset_name=dataset_name,
        dataset_config=dataset_config if dataset_config else None,
        split=split
    )
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error", "Download failed"))


@app.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None)
):
    """Upload a local dataset file (JSON or CSV)"""
    # Save uploaded file temporarily
    temp_file = UPLOAD_DIR / f"temp_{file.filename}"
    try:
        # Ensure upload directory exists
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate file extension
        file_ext = file.filename.lower()
        if not (file_ext.endswith('.json') or file_ext.endswith('.csv')):
            if temp_file.exists():
                temp_file.unlink()
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Only JSON (.json) and CSV (.csv) files are supported. You uploaded: {file.filename}"
            )
        
        # Auto-generate dataset name from filename if not provided or empty
        if not dataset_name or (isinstance(dataset_name, str) and dataset_name.strip() == ""):
            # Remove extension and clean up the filename
            filename_without_ext = Path(file.filename).stem
            # Replace underscores and hyphens with spaces, then title case
            dataset_name = filename_without_ext.replace('_', ' ').replace('-', ' ').title()
        elif isinstance(dataset_name, str):
            # Clean the provided name
            dataset_name = dataset_name.strip()
        else:
            # Fallback if None
            dataset_name = Path(file.filename).stem.replace('_', ' ').replace('-', ' ').title()
        
        # Upload to dataset service
        result = dataset_service.upload_local_dataset(
            file_path=str(temp_file),
            dataset_name=dataset_name
        )
        
        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()
        
        if result.get("success"):
            return result
        else:
            error_msg = result.get("error", "Upload failed")
            raise HTTPException(status_code=400, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        if temp_file.exists():
            temp_file.unlink()
        import traceback
        error_detail = str(e)
        print(f"Upload error: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Upload failed: {error_detail}")


@app.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset"""
    result = dataset_service.delete_dataset(dataset_id)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=404, detail=result.get("error", "Delete failed"))


@app.get("/datasets/search/huggingface")
async def search_huggingface_datasets(query: str = "", limit: int = 10):
    """Search for datasets on HuggingFace"""
    results = dataset_service.search_huggingface_datasets(query, limit)
    return {"datasets": results}


@app.post("/datasets/{dataset_id}/convert")
async def convert_dataset_to_wafer_data(dataset_id: str):
    """Convert uploaded dataset to wafer data format for analysis"""
    try:
        dataset_path = dataset_service.get_dataset_path(dataset_id)
        if not dataset_path or not dataset_path.exists():
            raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
        
        import json
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset_data = json.load(f)
        
        # Convert dataset to wafer data format
        # Handle list of records - use first record
        if isinstance(dataset_data, list) and len(dataset_data) > 0:
            record = dataset_data[0]
        elif isinstance(dataset_data, dict):
            record = dataset_data
        else:
            raise HTTPException(status_code=400, detail="Dataset format not supported")
        
        # Extract or generate wafer data from dataset
        wafer_data = WaferData(
            wafer_id=record.get('wafer_id', f"WAFER_{dataset_id[:8]}"),
            wafer_map={
                "total_dies": record.get('total_dies', record.get('totalDies', 500)),
                "good_dies": record.get('good_dies', record.get('goodDies', 465)),
                "defect_density": record.get('defect_density', record.get('defectDensity', 0.07)),
                "spatial_distribution": record.get('spatial_distribution', {"center": 0.02, "edge": 0.12}),
                "edge_exclusion": record.get('edge_exclusion', 3)
            },
            metrology_data={
                "thickness": {
                    "mean": record.get('thickness_mean', record.get('thicknessMean', 1.2)),
                    "std": record.get('thickness_std', record.get('thicknessStd', 0.05)),
                    "uniformity": record.get('thickness_uniformity', 0.95)
                },
                "critical_dimensions": {
                    "target": record.get('cd_target', record.get('cdTarget', 0.1)),
                    "actual": record.get('cd_actual', record.get('cdActual', 0.102)),
                    "variation": record.get('cd_variation', 0.003)
                }
            },
            eda_logs=record.get('eda_logs', [])
        )
        
        # Extract or generate process parameters
        current_parameters = ProcessParameters(
            temperature=record.get('temperature', record.get('temp', 198.5)),
            etch_time=record.get('etch_time', record.get('etchTime', 46.2)),
            exposure_dose=record.get('exposure_dose', record.get('exposureDose', 51.5))
        )
        
        return {
            "wafer_data": wafer_data.model_dump(),
            "current_parameters": current_parameters.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# Sample data endpoint removed - now using uploaded datasets via /datasets/{id}/convert


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

