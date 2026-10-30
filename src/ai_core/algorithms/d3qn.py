"""Dueling Double Deep Q-Network (D3QN) with Polyak Soft Updates and Replay Buffer.

Designed by Tab 4 (@tab_4) — ML/RL Engineer & Training Architect.
Specifications: docs/TRAINING_PIPELINE.md, docs/MODEL_LIFECYCLE.md.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


class DuelingQNetwork(nn.Module):
    """Dueling Neural Network Architecture for Q-value estimation.

    Separates state value V(s) and action advantage A(s, a) streams.
    Input: R^7 vector (4 proximity rays + delta_x + delta_y + dist_norm).
    Output: R^4 Q-values for 4 discrete actions.
    """

    def __init__(self, input_dim: int = 7, action_dim: int = 4) -> None:
        super().__init__()
        self.input_dim = input_dim
        self.action_dim = action_dim

        # Shared Feature Extractor
        self.feature_backbone = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
        )

        # Value Stream V(s) -> Scalar
        self.value_stream = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

        # Advantage Stream A(s, a) -> Vector of length action_dim
        self.advantage_stream = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass computing Q(s, a) via Dueling Aggregation."""
        features = self.feature_backbone(x)
        val = self.value_stream(features)  # (Batch, 1)
        adv = self.advantage_stream(features)  # (Batch, action_dim)

        # Identifiability aggregation: Q(s, a) = V(s) + (A(s, a) - mean(A))
        q_vals = val + (adv - adv.mean(dim=-1, keepdim=True))
        return q_vals


class ReplayBuffer:
    """Circular Experience Replay Buffer for storing and sampling transitions."""

    def __init__(self, capacity: int = 50000, obs_dim: int = 7) -> None:
        self.capacity = capacity
        self.obs_dim = obs_dim
        self.ptr = 0
        self.size = 0

        self.observations = np.zeros((capacity, obs_dim), dtype=np.float32)
        self.actions = np.zeros(capacity, dtype=np.int64)
        self.rewards = np.zeros(capacity, dtype=np.float32)
        self.next_observations = np.zeros((capacity, obs_dim), dtype=np.float32)
        self.dones = np.zeros(capacity, dtype=np.float32)

    def add(
        self,
        obs: np.ndarray,
        action: int,
        reward: float,
        next_obs: np.ndarray,
        done: bool,
    ) -> None:
        """Store a transition."""
        self.observations[self.ptr] = obs
        self.actions[self.ptr] = action
        self.rewards[self.ptr] = reward
        self.next_observations[self.ptr] = next_obs
        self.dones[self.ptr] = 1.0 if done else 0.0

        self.ptr = (self.ptr + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(
        self, batch_size: int, device: torch.device
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Sample a batch of transitions uniformly at random."""
        indices = np.random.randint(0, self.size, size=batch_size)

        b_obs = torch.as_tensor(self.observations[indices], device=device)
        b_actions = torch.as_tensor(self.actions[indices], device=device).unsqueeze(1)
        b_rewards = torch.as_tensor(self.rewards[indices], device=device).unsqueeze(1)
        b_next_obs = torch.as_tensor(self.next_observations[indices], device=device)
        b_dones = torch.as_tensor(self.dones[indices], device=device).unsqueeze(1)

        return b_obs, b_actions, b_rewards, b_next_obs, b_dones

    def __len__(self) -> int:
        return self.size


class D3QNAgent:
    """Dueling Double Deep Q-Network Agent."""

    def __init__(
        self,
        input_dim: int = 7,
        action_dim: int = 4,
        learning_rate: float = 0.0005,
        gamma: float = 0.99,
        tau: float = 0.005,
        buffer_capacity: int = 50000,
        batch_size: int = 64,
        epsilon_start: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
        seed: Optional[int] = None,
        device: Optional[str] = None,
        obs_dim: Optional[int] = None,
    ) -> None:
        """Initialize D3QN Agent."""
        if obs_dim is not None:
            input_dim = obs_dim

        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)
            random.seed(seed)

        self.input_dim = input_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.tau = tau
        self.batch_size = batch_size

        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        # Networks
        self.online_net = DuelingQNetwork(input_dim, action_dim).to(self.device)
        self.target_net = DuelingQNetwork(input_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.online_net.state_dict())
        self.target_net.eval()

        # Optimizer and Huber loss
        self.optimizer = optim.Adam(self.online_net.parameters(), lr=learning_rate)
        self.loss_fn = nn.SmoothL1Loss()

        # Memory buffer
        self.replay_buffer = ReplayBuffer(capacity=buffer_capacity, obs_dim=input_dim)

    @property
    def policy_net(self) -> DuelingQNetwork:
        """Alias for online network."""
        return self.online_net

    def store_transition(
        self,
        obs: np.ndarray,
        action: int,
        reward: float,
        next_obs: np.ndarray,
        done: bool,
    ) -> None:
        """Convenience method to store transition in replay buffer."""
        self.replay_buffer.add(obs, action, reward, next_obs, done)

    def train_step(self) -> Optional[float]:
        """Alias for step_learning."""
        return self.step_learning()

    def select_action(self, obs: np.ndarray, evaluate: bool = False) -> int:
        """Select action using epsilon-greedy policy."""
        if not evaluate and random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)

        with torch.no_grad():
            obs_tensor = torch.as_tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
            q_values = self.online_net(obs_tensor)
            best_action = q_values.argmax(dim=-1).item()
            return int(best_action)

    def get_q_values(self, obs: np.ndarray) -> List[float]:
        """Compute Q-values for all actions for telemetry and visualization."""
        with torch.no_grad():
            obs_tensor = torch.as_tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
            q_values = self.online_net(obs_tensor).squeeze(0)
            return [float(v) for v in q_values.cpu().numpy()]

    def step_learning(self) -> Optional[float]:
        """Sample batch, compute Double DQN loss, update online net and soft-update target."""
        if len(self.replay_buffer) < self.batch_size:
            return None

        b_obs, b_actions, b_rewards, b_next_obs, b_dones = self.replay_buffer.sample(
            self.batch_size, self.device
        )

        # Current Q-values
        current_q = self.online_net(b_obs).gather(1, b_actions)

        # Double DQN target computation:
        # a* = argmax_a Q_online(s', a)
        # y = r + gamma * (1 - done) * Q_target(s', a*)
        with torch.no_grad():
            next_online_q = self.online_net(b_next_obs)
            best_next_actions = next_online_q.argmax(dim=1, keepdim=True)
            next_target_q = self.target_net(b_next_obs).gather(1, best_next_actions)
            expected_q = b_rewards + (self.gamma * (1.0 - b_dones) * next_target_q)

        loss = self.loss_fn(current_q, expected_q)

        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.online_net.parameters(), max_norm=10.0)
        self.optimizer.step()

        # Polyak soft update of target network: theta_target = tau * theta_online + (1 - tau) * theta_target
        with torch.no_grad():
            for target_param, online_param in zip(
                self.target_net.parameters(), self.online_net.parameters()
            ):
                target_param.data.copy_(
                    self.tau * online_param.data + (1.0 - self.tau) * target_param.data
                )

        return float(loss.item())

    def decay_epsilon(self) -> None:
        """Decay exploration rate."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_weights(self, filepath: str | Path) -> None:
        """Save PyTorch online network state dict."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.online_net.state_dict(), filepath)

    def load_weights(self, filepath: str | Path) -> None:
        """Load PyTorch state dict into both online and target networks."""
        state_dict = torch.load(filepath, map_location=self.device)
        self.online_net.load_state_dict(state_dict)
        self.target_net.load_state_dict(state_dict)
        self.online_net.eval()
        self.target_net.eval()
