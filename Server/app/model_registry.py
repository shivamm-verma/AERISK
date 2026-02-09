from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pickle
from typing import Any, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import joblib
except Exception:
    joblib = None
    logger.warning("joblib not available, falling back to pickle")

try:
    import tensorflow as tf
except Exception:
    tf = None
    logger.warning("TensorFlow not available, TensorFlow models cannot be loaded")

try:
    import torch
except Exception:
    torch = None
    logger.warning("PyTorch not available, PyTorch models cannot be loaded")


@dataclass
class ModelRegistry:
    model_dir: Path
    models: Dict[str, Any]
    model_metadata: Dict[str, Dict[str, str]]

    def __init__(self, model_dir: Path) -> None:
        self.model_dir = model_dir
        self.models = {}
        self.model_metadata = {}

    def load_all(self) -> None:
        self.models.clear()
        self.model_metadata.clear()

        if not self.model_dir.exists():
            logger.error(f"Model directory does not exist: {self.model_dir}")
            return

        # Load scikit-learn models (.pkl)
        for path in self.model_dir.glob("*.pkl"):
            name = path.stem
            try:
                self.models[name] = self._load_sklearn_model(path)
                self.model_metadata[name] = {"type": "sklearn", "path": str(path), "format": ".pkl"}
                logger.info(f"✅ Loaded scikit-learn model: {name}")
            except Exception as e:
                logger.error(f"❌ Failed to load {name}: {e}")

        # Load TensorFlow/Keras models (.keras)
        for path in self.model_dir.glob("*.keras"):
            name = path.stem
            try:
                self.models[name] = self._load_tensorflow_model(path)
                self.model_metadata[name] = {"type": "tensorflow", "path": str(path), "format": ".keras"}
                logger.info(f"✅ Loaded TensorFlow (.keras) model: {name}")
            except Exception as e:
                logger.error(f"❌ Failed to load TensorFlow model {name}: {e}")

        # Load PyTorch models (.pt/.pth)
        for ext in ["*.pt", "*.pth"]:
            for path in self.model_dir.glob(ext):
                name = path.stem
                try:
                    self.models[name] = self._load_pytorch_model(path)
                    self.model_metadata[name] = {"type": "pytorch", "path": str(path), "format": path.suffix}
                    logger.info(f"✅ Loaded PyTorch model: {name}")
                except Exception as e:
                    logger.error(f"❌ Failed to load PyTorch model {name}: {e}")

        logger.info(f"📊 Total models loaded: {len(self.models)}")

    def list_names(self) -> List[str]:
        return sorted(self.models.keys())

    def list_models_with_metadata(self) -> Dict[str, Dict[str, str]]:
        return self.model_metadata

    def get(self, name: str) -> Any:
        if name not in self.models:
            logger.warning(f"Model '{name}' not found in registry")
            return None
        return self.models[name]

    def get_model_type(self, name: str) -> str | None:
        return self.model_metadata.get(name, {}).get("type")

    def reload_model(self, name: str) -> bool:
        if name not in self.model_metadata:
            return False
        meta = self.model_metadata[name]
        path = Path(meta["path"])
        try:
            if meta["type"] == "sklearn":
                self.models[name] = self._load_sklearn_model(path)
            elif meta["type"] == "tensorflow":
                self.models[name] = self._load_tensorflow_model(path)
            elif meta["type"] == "pytorch":
                self.models[name] = self._load_pytorch_model(path)
            return True
        except Exception as e:
            logger.error(f"❌ Reload failed for {name}: {e}")
            return False

    def _load_sklearn_model(self, path: Path) -> Any:
        if joblib is not None:
            try:
                return joblib.load(path)
            except Exception:
                pass
        with path.open("rb") as f:
            return pickle.load(f)

    def _load_tensorflow_model(self, path: Path) -> Any:
        if tf is None:
            raise ImportError("TensorFlow not installed")
        return tf.keras.models.load_model(str(path))

    def _load_pytorch_model(self, path: Path) -> Any:
        if torch is None:
            raise ImportError("PyTorch not installed")
        model = torch.load(path, map_location="cpu")
        model.eval()
        return model
