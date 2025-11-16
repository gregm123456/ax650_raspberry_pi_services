"""Simple model manager to track model paths and basic load/unload operations.
This is intentionally lightweight for the MVP: it validates paths and surfaces metadata.
"""
from __future__ import annotations
import os
from typing import Dict, Optional


class ModelManager:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.loaded_model: Optional[str] = None

    def list_models(self) -> Dict[str, Dict[str, str]]:
        """List candidate model directories/files under base_path.

        Returns a dict mapping model_id -> metadata.
        """
        out: Dict[str, Dict[str, str]] = {}
        if not os.path.isdir(self.base_path):
            return out
        for name in sorted(os.listdir(self.base_path)):
            path = os.path.join(self.base_path, name)
            out[name] = {"path": path, "exists": str(os.path.exists(path))}
        return out

    def load_model(self, model_id: str) -> bool:
        path = os.path.join(self.base_path, model_id)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model path not found: {path}")
        # In MVP we only track "loaded" state; actual runtime loads model separately
        self.loaded_model = model_id
        return True

    def get_loaded(self) -> Optional[str]:
        return self.loaded_model

