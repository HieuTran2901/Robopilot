"""Model Artifact Packaging, Validation and Loading (Technical Contract #6).

Designed by Tab 4 (@tab_4) — ML/RL Engineer & Training Architect.
Specification: docs/MODEL_LIFECYCLE.md.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch

from src.ai_core.algorithms.d3qn import D3QNAgent


class ModelArtifactManager:
    """Manages serialization, validation, and loading of RoboPilot Model Artifacts."""

    REQUIRED_METADATA_FIELDS = [
        "model_id",
        "algorithm",
        "framework",
        "version",
        "environment",
        "architecture",
        "training_config",
        "metrics",
    ]

    @classmethod
    def validate_metadata(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate metadata dictionary against Contract #6 schema.

        Returns:
            (is_valid, list_of_error_messages)
        """
        errors: List[str] = []
        for field in cls.REQUIRED_METADATA_FIELDS:
            if field not in metadata:
                errors.append(f"Missing required field: '{field}'")

        if "environment" in metadata:
            env_meta = metadata["environment"]
            if env_meta.get("observation_dim") != 7:
                errors.append(
                    f"Invalid observation_dim: expected 7, got {env_meta.get('observation_dim')}"
                )
            if env_meta.get("action_dim") != 4:
                errors.append(
                    f"Invalid action_dim: expected 4, got {env_meta.get('action_dim')}"
                )

        return (len(errors) == 0, errors)

    @classmethod
    def export_artifact(
        cls,
        target_dir: str | Path,
        agent: D3QNAgent,
        metadata_overrides: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Package and export model weights and metadata into a standardized bundle.

        Args:
            target_dir: Directory where model.pt and metadata.json will be saved.
            agent: The trained D3QNAgent instance.
            metadata_overrides: Custom metrics, training configs to inject into metadata.

        Returns:
            Path to exported directory.
        """
        out_path = Path(target_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        weights_file = out_path / "model.pt"
        meta_file = out_path / "metadata.json"

        # 1. Save weights
        agent.save_weights(weights_file)

        # 2. Build metadata conforming to Contract #6
        meta: Dict[str, Any] = {
            "model_id": out_path.name,
            "algorithm": "D3QN",
            "framework": "PyTorch",
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "environment": {
                "name": "WarehouseGridEnv-v0",
                "observation_mode": "proximity_raycast",
                "observation_dim": 7,
                "action_dim": 4,
                "actions": ["UP", "DOWN", "LEFT", "RIGHT"],
            },
            "architecture": {
                "model_class": "DuelingQNetwork",
                "input_dim": 7,
                "action_dim": 4,
                "hidden_layers": [128, 128],
                "activation": "ReLU",
            },
            "training_config": {
                "gamma": agent.gamma,
                "tau": agent.tau,
                "batch_size": agent.batch_size,
                "epsilon_min": agent.epsilon_min,
            },
            "metrics": {
                "success_rate": 0.0,
                "collision_rate": 0.0,
                "avg_episode_reward": 0.0,
                "avg_steps_to_goal": 0.0,
            },
        }

        if metadata_overrides:
            for k, v in metadata_overrides.items():
                if isinstance(v, dict) and k in meta and isinstance(meta[k], dict):
                    meta[k].update(v)
                else:
                    meta[k] = v

        # Validate before writing
        is_valid, errors = cls.validate_metadata(meta)
        if not is_valid:
            raise ValueError(f"Invalid metadata artifact: {errors}")

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        return out_path

    @classmethod
    def load_artifact(
        cls, artifact_dir: str | Path, device: Optional[str] = None
    ) -> Tuple[D3QNAgent, Dict[str, Any]]:
        """Load and validate an artifact package into memory.

        Returns:
            (loaded_agent, metadata_dict)
        """
        dir_path = Path(artifact_dir)
        meta_file = dir_path / "metadata.json"
        weights_file = dir_path / "model.pt"

        if not meta_file.exists():
            raise FileNotFoundError(f"Missing metadata.json in {dir_path}")
        if not weights_file.exists():
            raise FileNotFoundError(f"Missing model.pt in {dir_path}")

        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)

        is_valid, errors = cls.validate_metadata(meta)
        if not is_valid:
            raise ValueError(f"Corrupted or invalid metadata: {errors}")

        # Instantiate agent based on metadata
        env_meta = meta["environment"]
        agent = D3QNAgent(
            input_dim=env_meta["observation_dim"],
            action_dim=env_meta["action_dim"],
            device=device,
        )
        agent.load_weights(weights_file)
        return agent, meta
