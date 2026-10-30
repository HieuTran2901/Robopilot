"""Tabular Q-Learning Agent: Classical Reinforcement Learning Baseline.

Designed by Tab 2 (@tab_2) — Robotics & RL Research Specialist.
Specification: docs/RL_RESEARCH.md, docs/ALGORITHM_COMPARISON.md.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np


class QLearningAgent:
    """Tabular Q-Learning with Epsilon-Greedy Exploration Schedule."""

    def __init__(
        self,
        grid_width: int,
        grid_height: int,
        action_dim: int = 4,
        learning_rate: float = 0.1,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
        seed: Optional[int] = None,
    ) -> None:
        """Initialize Q-Learning agent."""
        self.width = grid_width
        self.height = grid_height
        self.num_states = self.width * self.height
        self.action_dim = action_dim

        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        self.rng = np.random.default_rng(seed)

        # Initialize Q-table: zeros of shape (num_states, action_dim)
        self.q_table = np.zeros((self.num_states, self.action_dim), dtype=np.float64)

    def encode_state(self, pos: Tuple[int, int]) -> int:
        """Map 2D coordinates (x, y) to 1D discrete index."""
        x, y = pos
        return int(y * self.width + x)

    def select_action(self, pos: Tuple[int, int], evaluate: bool = False) -> int:
        """Select action using epsilon-greedy policy.

        Args:
            pos: (x, y) robot position.
            evaluate: If True, select greedily without exploration (epsilon=0).
        """
        state_idx = self.encode_state(pos)
        if not evaluate and self.rng.random() < self.epsilon:
            return int(self.rng.integers(0, self.action_dim))

        # Break ties randomly
        q_vals = self.q_table[state_idx]
        max_val = np.max(q_vals)
        best_actions = np.flatnonzero(q_vals == max_val)
        return int(self.rng.choice(best_actions))

    def update(
        self,
        pos: Tuple[int, int],
        action: int,
        reward: float,
        next_pos: Tuple[int, int],
        done: bool,
    ) -> float:
        """Perform Bellman TD(0) update.

        Returns:
            TD error delta.
        """
        s = self.encode_state(pos)
        s_next = self.encode_state(next_pos)

        target = reward
        if not done:
            target += self.gamma * np.max(self.q_table[s_next])

        td_error = target - self.q_table[s, action]
        self.q_table[s, action] += self.lr * td_error
        return float(td_error)

    def decay_epsilon(self) -> None:
        """Decay exploration rate."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, filepath: str | Path) -> None:
        """Serialize Q-table to pickle."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "q_table": self.q_table,
            "width": self.width,
            "height": self.height,
            "epsilon": self.epsilon,
            "lr": self.lr,
            "gamma": self.gamma,
        }
        with open(filepath, "wb") as f:
            pickle.dump(payload, f)

    def load(self, filepath: str | Path) -> None:
        """Load Q-table from pickle."""
        with open(filepath, "rb") as f:
            payload = pickle.load(f)
        self.q_table = payload["q_table"]
        self.width = payload["width"]
        self.height = payload["height"]
        self.epsilon = payload["epsilon"]
        self.lr = payload["lr"]
        self.gamma = payload["gamma"]
