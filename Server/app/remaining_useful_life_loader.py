"""
Remaining Useful Life LSTM Model Loader
Handles loading and inference for the RUL LSTM TensorFlow model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

try:
    import tensorflow as tf
except ImportError:
    tf = None
    logger.warning("TensorFlow not installed")


class RemainingUsefulLifeLoader:
    """Loader for remaining useful life LSTM model."""
    
    def __init__(self, model_path: str | Path):
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = None
        self.sequence_length = 30  # Default sequence length for LSTM
        
    def load(self) -> None:
        """Load the RUL LSTM model from TensorFlow SavedModel format."""
        if tf is None:
            raise ImportError("TensorFlow is required for LSTM model but is not installed")
        
        try:
            # Try loading as directory (SavedModel format)
            if self.model_path.is_dir():
                self.model = tf.keras.models.load_model(str(self.model_path))
            # Try loading as .keras file
            elif self.model_path.suffix == ".keras":
                self.model = tf.keras.models.load_model(str(self.model_path))
            else:
                raise ValueError(f"Unsupported model format: {self.model_path.suffix}")
            
            logger.info(f"✅ Loaded LSTM RUL model from {self.model_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load LSTM RUL model: {e}")
            raise
    
    def prepare_data(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepare CSV data for sequence prediction.
        Creates sequences for LSTM input.
        """
        try:
            # Check minimum data points
            if len(df) < self.sequence_length:
                raise ValueError(f"Input must contain at least {self.sequence_length} rows for sequences")
            
            # Get numeric columns (sensor data)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise ValueError("No numeric columns found in data")
            
            data = df[numeric_cols].values.astype(np.float32)
            
            # Create sequences covering the entire data
            sequences = []
            for i in range(len(data) - self.sequence_length + 1):
                seq = data[i:i + self.sequence_length]
                sequences.append(seq)
            
            if len(sequences) == 0:
                raise ValueError("Could not create sequences from input data")
            
            return np.array(sequences)
        except Exception as e:
            logger.error(f"❌ Data preparation failed: {e}")
            raise
    
    def predict(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Make predictions on the provided data.
        Returns RUL predictions for the entire sequence.
        
        Returns:
            Dict with RUL predictions and metadata
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        try:
            X_sequences = self.prepare_data(df)
            
            # Make predictions
            predictions = self.model.predict(X_sequences, verbose=0)
            
            # Handle both direct output and wrapped output
            if isinstance(predictions, np.ndarray):
                pred_values = predictions.flatten().tolist()
            else:
                pred_values = predictions
            
            result = {
                "predictions": pred_values,
                "unit": "cycles",
                "sequences_used": len(X_sequences)
            }
            return result
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if model is properly loaded."""
        return self.model is not None
