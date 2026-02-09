from __future__ import annotations

import io
import numpy as np
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .model_registry import ModelRegistry


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

registry = ModelRegistry(MODEL_DIR)


class PredictionResponse(BaseModel):
    model: str
    rows: int
    prediction: List[Any]
    summary: str
    risk_level: str | None = None


@app.on_event("startup")
def load_models() -> None:
    registry.load_all()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/models")
def list_models() -> Dict[str, List[str]]:
    return {"models": registry.list_names()}


@app.post("/predict/{model_name}", response_model=PredictionResponse)
async def predict(model_name: str, file: UploadFile = File(...)) -> PredictionResponse:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    model = registry.get(model_name)
    if model is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")

    df = pd.read_csv(io.BytesIO(await file.read()))

    try:
        if hasattr(model, "predict"):
            preds = model.predict(df)
        else:
            preds = model(np.array(df))

    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Prediction failed: {e}")

    preds_list = preds.tolist() if hasattr(preds, "tolist") else list(preds)

    return PredictionResponse(
        model=model_name,
        rows=len(df),
        prediction=preds_list,
        summary=f"Generated {len(preds_list)} predictions using '{model_name}'.",
        risk_level=None,
    )
