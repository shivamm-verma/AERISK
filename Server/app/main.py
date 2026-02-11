from __future__ import annotations

import io
import numpy as np
from pathlib import Path
from typing import Any, Dict, List
import logging

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .engine_maintenance_loader import EngineMaintenanceLoader
from .landing_gear_fault_loader import LandingGearFaultLoader
from .landing_gear_rul_loader import LandingGearRULLoader
from .durability_loader import DurabilityLoader
from .remaining_useful_life_loader import RemainingUsefulLifeLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = (BASE_DIR.parent / "Model").resolve()

app = FastAPI(title="AAI Risk Analysis API", version="1.0.0")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:5000",
    "https://risk-analysis-fault-prediction.vercel.app",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model loaders
models = {}

def initialize_loaders() -> None:
    """Initialize all model loaders."""
    global models
    models.clear()
    
    # Engine Maintenance Model
    try:
        engine_path = MODEL_DIR / "engine_maintenance_pipeline.pkl"
        if engine_path.exists():
            loader = EngineMaintenanceLoader(engine_path)
            loader.load()
            models["engine_maintenance"] = loader
            logger.info("✅ Engine Maintenance model initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Engine Maintenance model: {e}")
    
    # Landing Gear Fault Model
    try:
        fault_path = MODEL_DIR / "LandingGearFaultPrediction.pkl"
        if fault_path.exists():
            loader = LandingGearFaultLoader(fault_path)
            loader.load()
            models["landing_gear_fault"] = loader
            logger.info("✅ Landing Gear Fault model initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Landing Gear Fault model: {e}")
    
    # Landing Gear RUL Model
    try:
        rul_path = MODEL_DIR / "LandingGearRUL.pkl"
        if rul_path.exists():
            loader = LandingGearRULLoader(rul_path)
            loader.load()
            models["landing_gear_rul"] = loader
            logger.info("✅ Landing Gear RUL model initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Landing Gear RUL model: {e}")
    
    # Durability Model
    try:
        durability_path = MODEL_DIR / "durability.pkl"
        if durability_path.exists():
            loader = DurabilityLoader(durability_path)
            loader.load()
            models["durability"] = loader
            logger.info("✅ Durability model initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Durability model: {e}")
    
    # Remaining Useful Life LSTM Model
    try:
        lstm_path = MODEL_DIR / "remainingUsefulLife_lstm.keras"
        if lstm_path.exists():
            loader = RemainingUsefulLifeLoader(lstm_path)
            loader.load()
            models["remaining_useful_life"] = loader
            logger.info("✅ Remaining Useful Life LSTM model initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Remaining Useful Life model: {e}")
    
    logger.info(f"📊 Total models loaded: {len(models)}")


class PredictionResponse(BaseModel):
    model: str
    rows: int
    prediction: List[Any]
    summary: str
    risk_level: str | None = None


@app.on_event("startup")
def load_models() -> None:
    initialize_loaders()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/models")
def list_models() -> Dict[str, List[str]]:
    return {"models": sorted(models.keys())}


def compute_risk_level(preds: List[int]) -> str:
    if not preds:
        return "Unknown"

    avg_code = sum(preds) / len(preds)

    from collections import Counter
    most_common_code, _ = Counter(preds).most_common(1)[0]

    # You can tune thresholds based on domain meaning
    if most_common_code == 0 and avg_code < 0.5:
        return "Low Risk"
    elif avg_code < 2:
        return "Medium Risk"
    else:
        return "High Risk"


@app.post("/predict/{model_name}", response_model=PredictionResponse)
async def predict(model_name: str, file: UploadFile = File(...)) -> PredictionResponse:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    # Get the loader
    loader = models.get(model_name)
    if loader is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")

    # Read CSV
    df = pd.read_csv(io.BytesIO(await file.read()))

    try:
        # Call predict based on model type
        result = loader.predict(df)
        
        # Handle different response formats based on model type
        if model_name == "engine_maintenance":
            # Engine maintenance returns single prediction with label
            preds_list = [result["prediction"]]
            summary = f"Prediction: {result['label']}"
            results = [{
                "fault_code": result["prediction"],
                "fault_name": result["label"]
            }]
            risk_level = compute_risk_level(preds_list)
        
        elif model_name in ["landing_gear_fault", "durability"]:
            # These return multiple predictions
            preds_list = result["predictions"]
            results = [
                {
                    "fault_code": code,
                    "fault_name": f"Fault Code {code}"
                }
                for code in preds_list
            ]
            summary = f"Generated {len(results)} predictions using '{model_name}'."
            risk_level = compute_risk_level(preds_list)
        
        elif model_name in ["landing_gear_rul", "remaining_useful_life"]:
            # These return numeric RUL predictions
            preds_list = [int(p) for p in result["predictions"]]
            results = [
                {
                    "rul": float(p),
                    "unit": result.get("unit", "cycles")
                }
                for p in result["predictions"]
            ]
            summary = f"Generated {len(results)} RUL predictions using '{model_name}'."
            risk_level = None  # RUL doesn't have risk levels
        
        else:
            raise ValueError(f"Unknown model type: {model_name}")
        
        return PredictionResponse(
            model=model_name,
            rows=len(df),
            prediction=results,
            summary=summary,
            risk_level=risk_level,
        )
    
    except Exception as e:
        logger.error(f"❌ Prediction failed for {model_name}: {e}")
        raise HTTPException(status_code=422, detail=f"Prediction failed: {str(e)}")
