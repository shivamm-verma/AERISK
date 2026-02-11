"""
Engine Maintenance Model Loader
Handles loading and inference for the engine maintenance pipeline model.
Uses custom feature extraction from raw CSV sensor data.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, List
import logging

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin

logger = logging.getLogger(__name__)


class CustomUnpickler(pickle.Unpickler):
    """Custom unpickler that remaps module paths for classes created in __main__."""
    
    def find_class(self, module: str, name: str):
        """Remap __main__ module references to engine_maintenance_loader."""
        # Remap CSVFeatureExtractor from __main__ to engine_maintenance_loader
        if module == "__main__" and name == "CSVFeatureExtractor":
            module = "app.engine_maintenance_loader"
        return super().find_class(module, name)

# Configuration
WINDOW_SIZE = 30
SENSORS = [
    's2', 's3', 's4', 's7', 's8', 's9',
    's11', 's12', 's13', 's14', 's15', 's16'
]


class CSVFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    Custom feature extractor for engine maintenance model.
    Extracts features from a sliding window of sensor data.
    """
    
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """
        Transform raw CSV data into feature vectors.
        X must be a pandas DataFrame with sensor columns.
        """
        if len(X) < WINDOW_SIZE:
            raise ValueError(f"CSV must contain at least {WINDOW_SIZE} rows")

        window = X.iloc[-WINDOW_SIZE:]
        features = []

        for s in SENSORS:
            if s not in X.columns:
                raise ValueError(f"Missing sensor: {s}")
            v = window[s].values
            features.extend([v.mean(), v.std(), v[-1] - v[0]])

        return np.array(features).reshape(1, -1)


class EngineMaintenanceLoader:
    """Loader for engine maintenance prediction model."""
    
    def __init__(self, model_path: str | Path):
        self.model_path = Path(model_path)
        self.pipeline = None
        self.feature_extractor = None
        self.scaler = None
        self.model = None
        self.label_map = None
        
    def load(self) -> None:
        """Load the engine maintenance pipeline."""
        try:
            # Use custom unpickler to remap __main__ module references
            with open(self.model_path, "rb") as f:
                unpickler = CustomUnpickler(f)
                self.pipeline = unpickler.load()
            
            self.feature_extractor = self.pipeline.get("feature_extractor")
            self.scaler = self.pipeline.get("scaler")
            self.model = self.pipeline.get("model")
            self.label_map = self.pipeline.get("label_map", {
                0: "HEALTHY", 
                1: "MAINTENANCE", 
                2: "REPLACE"
            })
            logger.info(f"✅ Loaded engine maintenance model from {self.model_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load engine maintenance model: {e}")
            raise
    
    def prepare_data(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepare CSV data for prediction.
        Applies custom feature extraction and scaling.
        """
        try:
            # Extract features using the custom extractor
            if self.feature_extractor is None:
                raise ValueError("Feature extractor not loaded")
            
            X_features = self.feature_extractor.transform(df)
            
            # Scale the features
            if self.scaler is None:
                raise ValueError("Scaler not loaded")
            
            X_scaled = self.scaler.transform(X_features)
            return X_scaled
        except Exception as e:
            logger.error(f"❌ Data preparation failed: {e}")
            raise
    
    def predict(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Make predictions on the provided data.
        
        Returns:
            Dict with predictions and metadata
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        X_scaled = self.prepare_data(df)
        
        try:
            # Get class predictions
            pred_class = self.model.predict(X_scaled)[0]
            
            # Get probabilities if available
            try:
                probabilities = self.model.predict_proba(X_scaled)[0]
            except:
                probabilities = None
            
            result = {
                "prediction": int(pred_class),
                "label": self.label_map.get(int(pred_class), "Unknown"),
                "probabilities": probabilities.tolist() if probabilities is not None else None
            }
            return result
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if model is properly loaded."""
        return self.model is not None and self.scaler is not None and self.feature_extractor is not None
