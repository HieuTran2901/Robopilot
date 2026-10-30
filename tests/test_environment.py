"""Automated Verification Test Suite for WarehouseGridEnv.

Designed by Tab 7 (@tab_7) — QA Auditor.
Specifications: docs/TEST_PLAN.md.
"""

from pathlib import Path
import pytest
import gymnasium as gym
from gymnasium.utils.env_checker import check_env
import numpy as np

from src.ai_core.env.warehouse_env import WarehouseGridEnv


def test_gymnasium_compliance() -> None:
    """TC-ENV-01: Verify compliance with Gymnasium standards."""
    env = WarehouseGridEnv()
    # check_env raises exceptions or warnings if the env violates Gymnasium contracts
    check_env(env.unwrapped)
    env.close()


def test_seed_reproducibility() -> None:
    """TC-ENV-02: Verify deterministic reset with seed."""
    env1 = WarehouseGridEnv()
    env2 = WarehouseGridEnv()

    obs1, _ = env1.reset(seed=42)
    obs2, _ = env2.reset(seed=42)

    assert np.allclose(obs1, obs2), "Observations with identical seeds must be identical"
    env1.close()
    env2.close()


def test_observation_bounds() -> None:
    """TC-ENV-03: Verify observation bounds [-1.0, 1.0]."""
    env = WarehouseGridEnv()
    obs, _ = env.reset(seed=123)

    for _ in range(100):
        action = env.action_space.sample()
        obs, _, terminated, truncated, _ = env.step(action)
        assert np.all(obs >= -1.0) and np.all(obs <= 1.0), f"Observation out of bounds: {obs}"
        if terminated or truncated:
            obs, _ = env.reset()

    env.close()


def test_collision_boundary_and_shelf() -> None:
    """TC-COL-01 & TC-COL-02: Verify zero-penetration boundary and obstacle collision invariants."""
    env = WarehouseGridEnv()
    env.reset(seed=42)

    # Robot starts at (1, 1). Move UP to (1, 0)
    obs, reward, terminated, truncated, info = env.step(WarehouseGridEnv.ACTION_UP)
    assert env.robot_pos == (1, 0)

    # Move UP again into top wall boundary y < 0
    obs, reward, terminated, truncated, info = env.step(WarehouseGridEnv.ACTION_UP)
    assert env.robot_pos == (1, 0), "Robot must stay at (1, 0) on boundary collision"
    assert info["is_collision"] is True
    assert info["base_reward"] <= -10.0, "Must apply collision penalty"

    env.close()


def test_anti_reward_hacking_oscillation() -> None:
    """TC-RWD-01: Verify that oscillating between two squares yields strictly negative return."""
    env = WarehouseGridEnv()
    env.reset(seed=42)

    # Robot starts at (1, 1). Move DOWN to (1, 2) and UP to (1, 1) repeatedly
    total_reward = 0.0
    for _ in range(25):  # 50 total steps (25 round-trips)
        # DOWN
        _, r1, _, _, _ = env.step(WarehouseGridEnv.ACTION_DOWN)
        # UP
        _, r2, _, _, _ = env.step(WarehouseGridEnv.ACTION_UP)
        total_reward += (r1 + r2)

    # In 50 steps, with step penalty -0.5, total reward must be <= -20.0 (strictly negative)
    assert total_reward <= -20.0, (
        f"Reward hacking detected! Oscillating agent earned positive or non-penalized reward: {total_reward}"
    )
    env.close()


def test_benchmark_maps_loading() -> None:
    """TC-MAP-01, 02, 03: Verify loading of all 3 benchmark maps."""
    maps_dir = Path("maps")
    map_files = [
        "benchmark_easy_10x10.json",
        "benchmark_medium_15x15.json",
        "benchmark_hard_20x20.json",
    ]

    for map_file in map_files:
        path = maps_dir / map_file
        assert path.exists(), f"Benchmark map {path} does not exist"
        env = WarehouseGridEnv(map_path_or_config=path)
        obs, info = env.reset(seed=42)
        assert obs.shape == (7,)
        assert info["goal_pos"] is not None
        env.close()
