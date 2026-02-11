"""
Landing Gear RUL (Remaining Useful Life) Model Loader
Handles loading and inference for the landing gear RUL model.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class LandingGearRULLoader:
    """Loader for landing gear RUL prediction model."""
    
    def __init__(self, model_path: str | Path):
        self.model_path = Path(model_path)
        self.pipeline = None
        self.model = None
        self.scaler = None
        self.feature_names = None
        
    def load(self) -> None:
        """Load the landing gear RUL model."""
        try:
            with open(self.model_path, "rb") as f:
                loaded = pickle.load(f)
            
            # Handle both pipeline dict and direct model
            if isinstance(loaded, dict):
                self.pipeline = loaded
                self.model = loaded.get("model")
                self.scaler = loaded.get("scaler")
                self.feature_names = loaded.get("feature_names")
            else:
                self.model = loaded
                self.pipeline = {"model": loaded}
            
            logger.info(f"✅ Loaded landing gear RUL model from {self.model_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load landing gear RUL model: {e}")
            raise
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare CSV data for prediction.
        Ensures correct feature order and types.
        """
        try:
            if self.feature_names:
                missing = set(self.feature_names) - set(df.columns)
                if missing:
                    raise ValueError(f"Missing columns: {sorted(missing)}")
                return df[self.feature_names]
            return df
        except Exception as e:
            logger.error(f"❌ Data preparation failed: {e}")
            raise
    
    def predict(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Make predictions on the provided data.
        Predicts remaining useful life in cycles/hours.
        
        Returns:
            Dict with RUL predictions and metadata
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        df_prepared = self.prepare_data(df)
        
        try:
            predictions = self.model.predict(df_prepared)
            
            result = {
                "predictions": [float(p) for p in predictions],
                "unit": "cycles"
            }
            return result
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if model is properly loaded."""
        return self.model is not None
