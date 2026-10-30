"""WarehouseGridEnv: Gymnasium-compliant 2D Warehouse Simulation Environment.

Designed by Tab 3 (@tab_3) — Simulation & Environment Designer.
Specifications: docs/ENVIRONMENT_SPEC.md, docs/STATE_ACTION_SPEC.md, docs/REWARD_DESIGN.md.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import gymnasium as gym
from gymnasium import spaces
import numpy as np


class WarehouseGridEnv(gym.Env):
    """Gymnasium 2D Warehouse Navigation Environment with PBRS and obstacle dynamics."""

    metadata = {
        "render_modes": ["ansi", "rgb_array"],
        "render_fps": 30,
    }

    # Tile identifiers
    TILE_EMPTY = 0
    TILE_OBSTACLE = 1
    TILE_START = 2
    TILE_GOAL = 3
    TILE_CHARGER = 4

    # Actions: 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
    ACTION_UP = 0
    ACTION_DOWN = 1
    ACTION_LEFT = 2
    ACTION_RIGHT = 3

    ACTION_DELTAS: Dict[int, Tuple[int, int]] = {
        ACTION_UP: (0, -1),
        ACTION_DOWN: (0, 1),
        ACTION_LEFT: (-1, 0),
        ACTION_RIGHT: (1, 0),
    }

    ACTION_HEADINGS: Dict[int, str] = {
        ACTION_UP: "UP",
        ACTION_DOWN: "DOWN",
        ACTION_LEFT: "LEFT",
        ACTION_RIGHT: "RIGHT",
    }

    def __init__(
        self,
        map_path_or_config: Optional[str | Path | Dict[str, Any]] = None,
        observation_mode: str = "proximity_raycast",
        render_mode: Optional[str] = None,
        max_sensor_range: int = 5,
        enable_battery: bool = True,
        gamma: float = 0.99,
        map_file: Optional[str | Path] = None,
    ) -> None:
        """Initialize WarehouseGridEnv.

        Args:
            map_path_or_config: File path to map JSON or dict containing grid config.
            observation_mode: "proximity_raycast" (7-dim float) or "coordinates" (4-dim int).
            render_mode: "ansi" or "rgb_array".
            max_sensor_range: Raycast distance horizon (cells).
            enable_battery: Whether battery constraint is enabled.
            gamma: Discount factor for Potential-based Reward Shaping (PBRS).
            map_file: Optional alias for map_path_or_config.
        """
        super().__init__()

        self.observation_mode = observation_mode
        self.render_mode = render_mode
        self.max_sensor_range = max_sensor_range
        self.enable_battery = enable_battery
        self.gamma = gamma

        # Allow map_file as alias
        map_source = map_file if map_file is not None else map_path_or_config
        # Load or generate map layout
        self._load_map_config(map_source)

        # Action space: 4 discrete directions
        self.action_space = spaces.Discrete(4)

        # Observation space
        if self.observation_mode == "coordinates":
            self.observation_space = spaces.Box(
                low=np.array([0, 0, 0, 0], dtype=np.int32),
                high=np.array(
                    [self.width - 1, self.height - 1, self.width - 1, self.height - 1],
                    dtype=np.int32,
                ),
                dtype=np.int32,
            )
        elif self.observation_mode == "proximity_raycast":
            # [ray_up, ray_down, ray_left, ray_right, delta_x, delta_y, dist_norm]
            self.observation_space = spaces.Box(
                low=-1.0,
                high=1.0,
                shape=(7,),
                dtype=np.float32,
            )
        else:
            raise ValueError(f"Unsupported observation_mode: {self.observation_mode}")

        # Maximum steps per episode
        self.max_steps = int(round(2.5 * (self.width + self.height)))

        # State attributes
        self.robot_pos: Tuple[int, int] = self.start_pos
        self.goal_pos: Tuple[int, int] = self.default_goal_pos
        self.charging_dock: Optional[Tuple[int, int]] = self.default_charging_dock
        self.heading: str = "UP"
        self.step_count: int = 0
        self.battery_level: float = 100.0
        self.is_collision: bool = False

    @property
    def grid_map(self) -> np.ndarray:
        """Alias for 2D obstacle grid array (0=free, 1=obstacle)."""
        return self.grid

    def _load_map_config(
        self, map_config: Optional[str | Path | Dict[str, Any]]
    ) -> None:
        """Parse map JSON or dictionary."""
        if map_config is None:
            # Default fallback 10x10 map
            self.width = 10
            self.height = 10
            self.start_pos = (1, 1)
            self.default_goal_pos = (8, 8)
            self.default_charging_dock = (1, 8)
            self.grid = np.zeros((self.height, self.width), dtype=np.int32)
            # Add simple shelf obstacles
            for y in range(1, 5):
                self.grid[y, 3] = self.TILE_OBSTACLE
            for y in range(5, 9):
                self.grid[y, 6] = self.TILE_OBSTACLE
            return

        if isinstance(map_config, (str, Path)):
            with open(map_config, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = map_config

        self.width = int(data["grid_size"]["width"])
        self.height = int(data["grid_size"]["height"])
        self.start_pos = (int(data["start_pos"][0]), int(data["start_pos"][1]))
        self.default_goal_pos = (int(data["goal_pos"][0]), int(data["goal_pos"][1]))

        dock = data.get("charging_dock")
        self.default_charging_dock = (int(dock[0]), int(dock[1])) if dock else None

        self.grid = np.zeros((self.height, self.width), dtype=np.int32)
        for obs in data.get("obstacles", []):
            ox, oy = int(obs[0]), int(obs[1])
            if 0 <= ox < self.width and 0 <= oy < self.height:
                self.grid[oy, ox] = self.TILE_OBSTACLE

    def _compute_potential(self, pos: Tuple[int, int]) -> float:
        """Compute Potential function Phi(s) = - Manhattan(pos, goal) / norm_factor."""
        norm_factor = float(self.width + self.height - 2)
        if norm_factor <= 0:
            return 0.0
        manhattan_dist = abs(pos[0] - self.goal_pos[0]) + abs(pos[1] - self.goal_pos[1])
        return -float(manhattan_dist) / norm_factor

    def _cast_ray(self, origin: Tuple[int, int], delta: Tuple[int, int]) -> int:
        """Measure distance in cells along delta until an obstacle or boundary is reached."""
        x, y = origin
        dx, dy = delta
        distance = 0
        while distance < self.max_sensor_range:
            nx = x + dx * (distance + 1)
            ny = y + dy * (distance + 1)
            if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                break
            if self.grid[ny, nx] == self.TILE_OBSTACLE:
                break
            distance += 1
        return distance

    def _get_observation(self) -> np.ndarray:
        """Build observation according to configured mode."""
        if self.observation_mode == "coordinates":
            return np.array(
                [self.robot_pos[0], self.robot_pos[1], self.goal_pos[0], self.goal_pos[1]],
                dtype=np.int32,
            )

        # Egocentric sensor mode (7-dimensional float32 vector)
        ray_up = self._cast_ray(self.robot_pos, (0, -1))
        ray_down = self._cast_ray(self.robot_pos, (0, 1))
        ray_left = self._cast_ray(self.robot_pos, (-1, 0))
        ray_right = self._cast_ray(self.robot_pos, (1, 0))

        norm_ray_up = float(ray_up) / float(self.max_sensor_range)
        norm_ray_down = float(ray_down) / float(self.max_sensor_range)
        norm_ray_left = float(ray_left) / float(self.max_sensor_range)
        norm_ray_right = float(ray_right) / float(self.max_sensor_range)

        # Relative goal vector
        delta_x = (
            float(self.goal_pos[0] - self.robot_pos[0]) / float(self.width - 1)
            if self.width > 1
            else 0.0
        )
        delta_y = (
            float(self.goal_pos[1] - self.robot_pos[1]) / float(self.height - 1)
            if self.height > 1
            else 0.0
        )

        norm_factor = float(self.width + self.height - 2)
        manhattan_dist = abs(self.robot_pos[0] - self.goal_pos[0]) + abs(
            self.robot_pos[1] - self.goal_pos[1]
        )
        dist_norm = float(manhattan_dist) / norm_factor if norm_factor > 0 else 0.0

        obs = np.array(
            [
                norm_ray_up,
                norm_ray_down,
                norm_ray_left,
                norm_ray_right,
                delta_x,
                delta_y,
                dist_norm,
            ],
            dtype=np.float32,
        )
        return np.clip(obs, -1.0, 1.0)

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset environment to initial state."""
        super().reset(seed=seed)

        self.robot_pos = self.start_pos
        self.goal_pos = self.default_goal_pos
        self.charging_dock = self.default_charging_dock
        self.heading = "UP"
        self.step_count = 0
        self.battery_level = 100.0
        self.is_collision = False

        if options and "goal_pos" in options:
            self.goal_pos = tuple(options["goal_pos"])  # type: ignore

        obs = self._get_observation()
        info = {
            "step_count": 0,
            "robot_pos": list(self.robot_pos),
            "goal_pos": list(self.goal_pos),
            "battery_level": self.battery_level,
            "is_collision": False,
            "is_goal": False,
        }
        return obs, info

    def step(
        self, action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Execute one navigation step."""
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action {action} for {self.action_space}")

        self.step_count += 1
        prev_pos = self.robot_pos
        phi_prev = self._compute_potential(prev_pos)

        # Update heading
        self.heading = self.ACTION_HEADINGS[action]

        # Calculate candidate position
        dx, dy = self.ACTION_DELTAS[action]
        candidate_x = prev_pos[0] + dx
        candidate_y = prev_pos[1] + dy

        # Collision check O(1)
        collision = False
        if (
            candidate_x < 0
            or candidate_x >= self.width
            or candidate_y < 0
            or candidate_y >= self.height
        ):
            collision = True
        elif self.grid[candidate_y, candidate_x] == self.TILE_OBSTACLE:
            collision = True

        self.is_collision = collision
        if collision:
            next_pos = prev_pos
        else:
            next_pos = (candidate_x, candidate_y)

        self.robot_pos = next_pos
        phi_next = self._compute_potential(next_pos)

        # Battery update
        if self.enable_battery:
            battery_loss = 0.5 + (1.0 if collision else 0.0)
            self.battery_level = max(0.0, self.battery_level - battery_loss)

            # Check charging dock
            if self.charging_dock and next_pos == self.charging_dock:
                self.battery_level = 100.0

        # Termination & Truncation checks
        is_goal = next_pos == self.goal_pos
        terminated = is_goal or (self.enable_battery and self.battery_level <= 0.0)
        truncated = (not terminated) and (self.step_count >= self.max_steps)

        # Reward Calculation: Base Reward + PBRS Shaping
        base_reward = -0.5  # Step penalty
        if is_goal:
            base_reward += 100.0
        elif collision:
            base_reward += -10.0

        if self.enable_battery and self.battery_level <= 0.0 and not is_goal:
            base_reward += -50.0

        if truncated:
            base_reward += -20.0

        # PBRS Shaping: F(s, s') = gamma * Phi(s') - Phi(s)
        shaping_reward = self.gamma * phi_next - phi_prev
        total_reward = float(base_reward + shaping_reward)

        obs = self._get_observation()
        info = {
            "step_count": self.step_count,
            "robot_pos": list(self.robot_pos),
            "goal_pos": list(self.goal_pos),
            "heading": self.heading,
            "battery_level": self.battery_level,
            "is_collision": collision,
            "is_goal": is_goal,
            "base_reward": base_reward,
            "shaping_reward": shaping_reward,
            "total_reward": total_reward,
        }

        return obs, total_reward, terminated, truncated, info

    def render(self) -> Optional[np.ndarray | str]:
        """Render the warehouse grid."""
        if self.render_mode == "ansi":
            lines: List[str] = []
            for y in range(self.height):
                row_str: List[str] = []
                for x in range(self.width):
                    pos = (x, y)
                    if pos == self.robot_pos:
                        row_str.append("R")
                    elif pos == self.goal_pos:
                        row_str.append("G")
                    elif self.charging_dock and pos == self.charging_dock:
                        row_str.append("B")
                    elif self.grid[y, x] == self.TILE_OBSTACLE:
                        row_str.append("#")
                    else:
                        row_str.append(".")
                lines.append(" ".join(row_str))
            return "\n".join(lines)
        elif self.render_mode == "rgb_array":
            # 3-channel RGB image (30x30 pixels per grid cell)
            cell_size = 30
            img = np.zeros(
                (self.height * cell_size, self.width * cell_size, 3), dtype=np.uint8
            )
            # Background
            img[:] = [240, 240, 240]

            for y in range(self.height):
                for x in range(self.width):
                    y0, y1 = y * cell_size, (y + 1) * cell_size
                    x0, x1 = x * cell_size, (x + 1) * cell_size
                    if self.grid[y, x] == self.TILE_OBSTACLE:
                        img[y0:y1, x0:x1] = [50, 50, 50]  # Dark gray obstacle
                    elif (x, y) == self.goal_pos:
                        img[y0:y1, x0:x1] = [34, 197, 94]  # Green goal
                    elif self.charging_dock and (x, y) == self.charging_dock:
                        img[y0:y1, x0:x1] = [245, 158, 11]  # Orange charger

            # Draw robot
            rx, ry = self.robot_pos
            ry0, ry1 = ry * cell_size + 4, (ry + 1) * cell_size - 4
            rx0, rx1 = rx * cell_size + 4, (rx + 1) * cell_size - 4
            img[ry0:ry1, rx0:rx1] = [59, 130, 246]  # Blue robot

            return img
        return None

    def close(self) -> None:
        """Clean up environment resources."""
        pass
