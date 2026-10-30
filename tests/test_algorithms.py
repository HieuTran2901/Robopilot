"""Unit and Integration Tests for RoboPilot Core Algorithms.

Designed by Tab 7 (@tab_7) — QA & System Validation Auditor.
Specifications: docs/TEST_PLAN.md, docs/ACCEPTANCE_CRITERIA.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import torch

from src.ai_core.algorithms.artifact import ModelArtifactManager
from src.ai_core.algorithms.astar import AStarPlanner
from src.ai_core.algorithms.d3qn import D3QNAgent, DuelingQNetwork, ReplayBuffer
from src.ai_core.algorithms.q_learning import QLearningAgent
from src.ai_core.env.warehouse_env import WarehouseGridEnv


MAP_PATH = Path("maps/benchmark_easy_10x10.json")


class TestAStarPlanner:
    """Test suite for A* theoretical baseline pathfinding."""

    def test_astar_benchmark_easy_optimal_path(self) -> None:
        """A* must find optimal path of exactly 16 steps on benchmark_easy_10x10."""
        assert MAP_PATH.exists(), f"Map file {MAP_PATH} not found"
        env = WarehouseGridEnv(map_file=MAP_PATH)
        planner = AStarPlanner(env.grid_map)

        plan = planner.plan(env.start_pos, env.goal_pos)
        assert plan["found"] is True
        assert plan["length"] == 16, f"Expected 16 steps, got {plan['length']}"
        assert len(plan["actions"]) == 16
        assert len(plan["path"]) == 17  # start + 16 steps
        assert plan["path"][0] == env.start_pos
        assert plan["path"][-1] == env.goal_pos

        # Verify no obstacles along path
        for x, y in plan["path"]:
            assert env.grid_map[y, x] == 0, f"Path passes through obstacle at ({x}, {y})"

    def test_astar_unreachable_goal(self) -> None:
        """A* must return found=False when goal is fully enclosed by obstacles."""
        grid = np.zeros((5, 5), dtype=np.int32)
        # Enclose goal (4, 4)
        grid[3, 4] = 1
        grid[4, 3] = 1
        planner = AStarPlanner(grid)
        plan = planner.plan((0, 0), (4, 4))
        assert plan["found"] is False
        assert plan["length"] == 0
        assert plan["path"] == []


class TestQLearningAgent:
    """Test suite for Tabular Q-Learning baseline."""

    def test_q_learning_initialization_and_encode(self) -> None:
        """Test state encoding and Q-table initialization."""
        agent = QLearningAgent(grid_width=10, grid_height=10, seed=42)
        assert agent.q_table.shape == (100, 4)
        assert np.all(agent.q_table == 0.0)

        # (x=3, y=2) in 10-wide grid -> 2*10 + 3 = 23
        assert agent.encode_state((3, 2)) == 23

    def test_q_learning_bellman_update(self) -> None:
        """Test TD(0) update alters Q-value towards reward."""
        agent = QLearningAgent(grid_width=5, grid_height=5, learning_rate=0.5, gamma=0.9, seed=42)
        pos = (0, 0)
        action = 3  # RIGHT
        reward = 10.0
        next_pos = (1, 0)

        # Before update Q(s, a) == 0
        td_error = agent.update(pos, action, reward, next_pos, done=True)
        # target = 10.0, prev = 0.0, td_error = 10.0, new_Q = 0 + 0.5 * 10 = 5.0
        assert td_error == 10.0
        s = agent.encode_state(pos)
        assert agent.q_table[s, action] == 5.0

    def test_q_learning_epsilon_decay(self) -> None:
        """Test exploration rate decay and minimum boundary."""
        agent = QLearningAgent(grid_width=5, grid_height=5, epsilon_start=1.0, epsilon_min=0.1, epsilon_decay=0.5)
        agent.decay_epsilon()
        assert agent.epsilon == 0.5
        agent.decay_epsilon()
        assert agent.epsilon == 0.25
        agent.decay_epsilon()
        assert agent.epsilon == 0.125
        agent.decay_epsilon()
        assert agent.epsilon == 0.1  # Clamped to min

    def test_q_learning_save_and_load(self, tmp_path: Path) -> None:
        """Test serialization and deserialization of Q-table."""
        agent = QLearningAgent(grid_width=4, grid_height=4, seed=123)
        agent.q_table[5, 2] = 42.5
        save_file = tmp_path / "q_table.pkl"
        agent.save(save_file)

        agent2 = QLearningAgent(grid_width=4, grid_height=4)
        agent2.load(save_file)
        np.testing.assert_array_equal(agent.q_table, agent2.q_table)


class TestD3QNAgent:
    """Test suite for Dueling Double Deep Q-Network."""

    def test_dueling_network_forward_and_identifiability(self) -> None:
        """Test Dueling architecture forward pass and mean advantage subtraction."""
        net = DuelingQNetwork(input_dim=7, action_dim=4)
        net.eval()

        dummy_obs = torch.randn(8, 7)
        with torch.no_grad():
            q_values = net(dummy_obs)
            features = net.feature_backbone(dummy_obs)
            v = net.value_stream(features)
            a = net.advantage_stream(features)
            expected_q = v + (a - a.mean(dim=-1, keepdim=True))

        assert q_values.shape == (8, 4)
        torch.testing.assert_close(q_values, expected_q)

    def test_replay_buffer_operations(self) -> None:
        """Test circular push, size tracking, and uniform sampling."""
        buffer = ReplayBuffer(capacity=5, obs_dim=7)
        assert buffer.size == 0

        for i in range(7):  # Push 7 items to test wrap-around
            obs = np.full(7, fill_value=i, dtype=np.float32)
            buffer.add(obs, action=i % 4, reward=float(i), next_obs=obs + 0.1, done=False)

        assert buffer.size == 5
        device = torch.device("cpu")
        b_obs, b_actions, b_rewards, b_next_obs, b_dones = buffer.sample(batch_size=3, device=device)
        assert b_obs.shape == (3, 7)
        assert b_actions.shape == (3, 1)
        assert b_rewards.shape == (3, 1)
        assert b_next_obs.shape == (3, 7)
        assert b_dones.shape == (3, 1)

    def test_d3qn_agent_train_step_and_soft_update(self) -> None:
        """Test D3QN training iteration updates policy net and moves target net."""
        agent = D3QNAgent(
            obs_dim=7,
            action_dim=4,
            learning_rate=1e-3,
            batch_size=4,
            buffer_capacity=100,
            tau=0.1,  # Large tau for measurable parameter shift
            device="cpu",
            seed=42,
        )

        # Populate buffer above batch_size
        for _ in range(10):
            obs = np.random.randn(7).astype(np.float32)
            next_obs = np.random.randn(7).astype(np.float32)
            agent.store_transition(obs, action=1, reward=1.0, next_obs=next_obs, done=False)

        # Record target weights before training
        target_param_before = next(agent.target_net.parameters()).clone().detach()

        loss = agent.train_step()
        assert loss is not None
        assert loss >= 0.0

        # After soft update, target net parameters must have shifted towards policy net
        target_param_after = next(agent.target_net.parameters()).clone().detach()
        assert not torch.equal(target_param_before, target_param_after)

    def test_d3qn_save_load_weights(self, tmp_path: Path) -> None:
        """Test PyTorch state dict checkpointing."""
        agent1 = D3QNAgent(obs_dim=7, action_dim=4, device="cpu", seed=99)
        weight_file = tmp_path / "model.pt"
        agent1.save_weights(weight_file)

        agent2 = D3QNAgent(obs_dim=7, action_dim=4, device="cpu", seed=100)
        agent2.load_weights(weight_file)

        for p1, p2 in zip(agent1.policy_net.parameters(), agent2.policy_net.parameters()):
            torch.testing.assert_close(p1, p2)


class TestModelArtifactManager:
    """Test suite for Model Artifact Packaging & Contract #6 Compliance."""

    def test_export_and_validate_artifact(self, tmp_path: Path) -> None:
        """Export D3QN artifact and verify Technical Contract #6 conformance."""
        agent = D3QNAgent(obs_dim=7, action_dim=4, device="cpu", seed=42)
        artifact_dir = tmp_path / "models" / "d3qn_test_v1"

        meta_overrides = {
            "metrics": {
                "success_rate_pct": 98.5,
                "mean_reward": 88.2,
                "episodes_trained": 500,
            }
        }

        exported_path = ModelArtifactManager.export_artifact(
            target_dir=artifact_dir,
            agent=agent,
            metadata_overrides=meta_overrides,
        )

        assert exported_path.exists()
        assert (exported_path / "model.pt").exists()
        assert (exported_path / "metadata.json").exists()

        # Load and validate metadata schema
        with open(exported_path / "metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)

        is_valid, errors = ModelArtifactManager.validate_metadata(metadata)
        assert is_valid, f"Metadata validation failed: {errors}"
        assert metadata["metrics"]["success_rate_pct"] == 98.5

        # Test loading artifact back
        loaded_agent, loaded_meta = ModelArtifactManager.load_artifact(exported_path, device="cpu")
        assert loaded_meta["algorithm"] == "D3QN"

        # Compare outputs
        dummy_obs = np.random.randn(7).astype(np.float32)
        act1 = agent.select_action(dummy_obs, evaluate=True)
        act2 = loaded_agent.select_action(dummy_obs, evaluate=True)
        assert act1 == act2

    def test_metadata_validation_errors(self) -> None:
        """Test that invalid metadata dictionaries are rejected with descriptive errors."""
        # Missing required fields
        invalid_meta = {"algorithm": "D3QN"}
        is_valid, errors = ModelArtifactManager.validate_metadata(invalid_meta)
        assert not is_valid
        assert len(errors) > 0

        # Invalid observation dimension
        invalid_meta_dim = {
            "model_id": "test",
            "algorithm": "D3QN",
            "framework": "PyTorch",
            "version": "1.0.0",
            "environment": {"observation_dim": 10, "action_dim": 4},
            "architecture": {},
            "training_config": {},
            "metrics": {},
        }
        is_valid_dim, errors_dim = ModelArtifactManager.validate_metadata(invalid_meta_dim)
        assert not is_valid_dim
        assert any("observation_dim" in e for e in errors_dim)
