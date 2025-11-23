"""
Dataset Service - Manages HuggingFace datasets and local dataset storage
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from datasets import load_dataset
from huggingface_hub import hf_hub_download

class DatasetService:
    """Service for managing HuggingFace datasets and local dataset storage"""
    
    def __init__(self):
        self.datasets_dir = Path("data/datasets")
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.datasets_dir / "metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load dataset metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"datasets": []}
            self._save_metadata()
    
    def _save_metadata(self):
        """Save dataset metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def download_huggingface_dataset(
        self, 
        dataset_name: str, 
        dataset_config: Optional[str] = None,
        split: str = "train"
    ) -> Dict:
        """Download a dataset from HuggingFace"""
        try:
            print(f"Downloading dataset: {dataset_name}...")
            
            # Load dataset from HuggingFace
            if dataset_config:
                dataset = load_dataset(dataset_name, dataset_config, split=split)
            else:
                dataset = load_dataset(dataset_name, split=split)
            
            # Convert to list of dictionaries
            dataset_list = [item for item in dataset]
            
            # Save to local file
            dataset_id = f"{dataset_name.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dataset_file = self.datasets_dir / f"{dataset_id}.json"
            
            with open(dataset_file, 'w') as f:
                json.dump(dataset_list, f, indent=2)
            
            # Update metadata
            dataset_info = {
                "id": dataset_id,
                "name": dataset_name,
                "config": dataset_config,
                "split": split,
                "file_path": str(dataset_file),
                "rows": len(dataset_list),
                "columns": list(dataset_list[0].keys()) if dataset_list else [],
                "downloaded_at": datetime.now().isoformat(),
                "source": "huggingface"
            }
            
            self.metadata["datasets"].append(dataset_info)
            self._save_metadata()
            
            return {
                "success": True,
                "dataset_id": dataset_id,
                "file_path": str(dataset_file),
                "rows": len(dataset_list),
                "columns": dataset_info["columns"],
                "message": f"Dataset downloaded successfully: {len(dataset_list)} rows"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to download dataset: {str(e)}"
            }
    
    def upload_local_dataset(self, file_path: str, dataset_name: str) -> Dict:
        """Upload a local dataset file"""
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            # Read the uploaded file
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    try:
                        data = json.load(f)
                        # Handle both list and single object
                        if not isinstance(data, list):
                            data = [data]
                    except json.JSONDecodeError as e:
                        return {
                            "success": False,
                            "error": f"Invalid JSON format: {str(e)}"
                        }
                elif file_path.endswith('.csv'):
                    try:
                        import pandas as pd
                        df = pd.read_csv(file_path)
                        data = df.to_dict('records')
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Error reading CSV: {str(e)}"
                        }
                else:
                    return {
                        "success": False,
                        "error": "Unsupported file format. Please use JSON or CSV."
                    }
            
            if not data or len(data) == 0:
                return {
                    "success": False,
                    "error": "Dataset is empty. Please upload a file with data."
                }
            
            # Clean dataset name for file system
            safe_name = "".join(c for c in dataset_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            
            # Save to datasets directory
            dataset_id = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dataset_file = self.datasets_dir / f"{dataset_id}.json"
            
            # Ensure directory exists
            self.datasets_dir.mkdir(parents=True, exist_ok=True)
            
            with open(dataset_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Update metadata
            dataset_info = {
                "id": dataset_id,
                "name": dataset_name,
                "file_path": str(dataset_file),
                "rows": len(data),
                "columns": list(data[0].keys()) if data else [],
                "uploaded_at": datetime.now().isoformat(),
                "source": "local_upload"
            }
            
            self.metadata["datasets"].append(dataset_info)
            self._save_metadata()
            
            return {
                "success": True,
                "dataset_id": dataset_id,
                "file_path": str(dataset_file),
                "rows": len(data),
                "columns": dataset_info["columns"],
                "message": f"Dataset uploaded successfully: {len(data)} rows"
            }
        except Exception as e:
            import traceback
            error_msg = str(e)
            print(f"Upload error in service: {error_msg}")
            print(traceback.format_exc())
            return {
                "success": False,
                "error": error_msg,
                "message": f"Failed to upload dataset: {error_msg}"
            }
    
    def list_datasets(self) -> List[Dict]:
        """List all available datasets"""
        return self.metadata.get("datasets", [])
    
    def get_dataset_path(self, dataset_id: str) -> Optional[Path]:
        """Get the file path for a dataset"""
        for dataset in self.metadata.get("datasets", []):
            if dataset["id"] == dataset_id:
                return Path(dataset["file_path"])
        return None
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Get a specific dataset"""
        for dataset in self.metadata.get("datasets", []):
            if dataset["id"] == dataset_id:
                # Load the actual data
                with open(dataset["file_path"], 'r') as f:
                    dataset["data"] = json.load(f)
                return dataset
        return None
    
    def delete_dataset(self, dataset_id: str) -> Dict:
        """Delete a dataset"""
        try:
            dataset = None
            for i, ds in enumerate(self.metadata.get("datasets", [])):
                if ds["id"] == dataset_id:
                    dataset = ds
                    # Delete file
                    if os.path.exists(ds["file_path"]):
                        os.remove(ds["file_path"])
                    # Remove from metadata
                    self.metadata["datasets"].pop(i)
                    break
            
            if dataset:
                self._save_metadata()
                return {
                    "success": True,
                    "message": f"Dataset {dataset_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Dataset {dataset_id} not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete dataset: {str(e)}"
            }
    
    def search_huggingface_datasets(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for datasets on HuggingFace (simplified - returns popular semiconductor datasets)"""
        # Popular semiconductor/manufacturing datasets on HuggingFace
        popular_datasets = [
            {
                "id": "semiconductor-yield",
                "name": "semiconductor-yield-dataset",
                "description": "Semiconductor wafer yield prediction dataset",
                "tags": ["semiconductor", "yield", "manufacturing"]
            },
            {
                "id": "manufacturing-quality",
                "name": "manufacturing-quality-control",
                "description": "Manufacturing quality control dataset",
                "tags": ["manufacturing", "quality", "control"]
            }
        ]
        
        # Filter by query
        if query:
            query_lower = query.lower()
            return [
                ds for ds in popular_datasets 
                if query_lower in ds["name"].lower() or 
                   query_lower in ds["description"].lower() or
                   any(query_lower in tag for tag in ds["tags"])
            ][:limit]
        
        return popular_datasets[:limit]

