"""A* Search Algorithm: Theoretical Optimal Ground Truth Baseline.

Designed by Tab 2 (@tab_2) — Robotics & RL Research Specialist.
Specification: docs/ALGORITHM_COMPARISON.md.
"""

from __future__ import annotations

import heapq
import time
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np


class AStarPlanner:
    """A* Pathfinding on 2D Grid with Manhattan Distance Heuristic."""

    # 4 Cardinal directions: (dx, dy, action_code)
    DIRECTIONS: List[Tuple[int, int, int]] = [
        (0, -1, 0),  # UP
        (0, 1, 1),   # DOWN
        (-1, 0, 2),  # LEFT
        (1, 0, 3),   # RIGHT
    ]

    def __init__(self, grid: np.ndarray) -> None:
        """Initialize planner with binary obstacle grid (0=empty, 1=obstacle)."""
        self.grid = grid
        self.height, self.width = grid.shape

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Admissible and consistent Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def plan(
        self, start: Tuple[int, int], goal: Tuple[int, int]
    ) -> Dict[str, Any]:
        """Compute shortest path from start to goal.

        Args:
            start: (x, y) start coordinates.
            goal: (x, y) goal coordinates.

        Returns:
            Dict containing:
                "found": bool
                "path": List of (x, y) tuples from start to goal
                "actions": List of action integers to traverse path
                "length": Number of steps in path
                "nodes_expanded": Total nodes evaluated
                "execution_time_ms": Time taken in milliseconds
        """
        start_time = time.perf_counter()

        if (
            start[0] < 0
            or start[0] >= self.width
            or start[1] < 0
            or start[1] >= self.height
            or goal[0] < 0
            or goal[0] >= self.width
            or goal[1] < 0
            or goal[1] >= self.height
        ):
            return {
                "found": False,
                "path": [],
                "actions": [],
                "length": 0,
                "nodes_expanded": 0,
                "execution_time_ms": (time.perf_counter() - start_time) * 1000.0,
            }

        if self.grid[start[1], start[0]] == 1 or self.grid[goal[1], goal[0]] == 1:
            return {
                "found": False,
                "path": [],
                "actions": [],
                "length": 0,
                "nodes_expanded": 0,
                "execution_time_ms": (time.perf_counter() - start_time) * 1000.0,
            }

        # Priority Queue: (f_score, counter, current_node)
        counter = 0
        open_set: List[Tuple[int, int, Tuple[int, int]]] = []
        heapq.heappush(open_set, (self._heuristic(start, goal), counter, start))

        came_from: Dict[Tuple[int, int], Tuple[Tuple[int, int], int]] = {}
        g_score: Dict[Tuple[int, int], int] = {start: 0}
        closed_set: Set[Tuple[int, int]] = set()

        nodes_expanded = 0

        while open_set:
            _, _, current = heapq.heappop(open_set)
            nodes_expanded += 1

            if current == goal:
                # Reconstruct path and action sequence
                path: List[Tuple[int, int]] = [current]
                actions: List[int] = []

                curr = current
                while curr in came_from:
                    parent, action = came_from[curr]
                    actions.append(action)
                    path.append(parent)
                    curr = parent

                path.reverse()
                actions.reverse()
                exec_time = (time.perf_counter() - start_time) * 1000.0

                return {
                    "found": True,
                    "path": path,
                    "actions": actions,
                    "length": len(actions),
                    "nodes_expanded": nodes_expanded,
                    "execution_time_ms": exec_time,
                }

            if current in closed_set:
                continue
            closed_set.add(current)

            for dx, dy, action in self.DIRECTIONS:
                neighbor = (current[0] + dx, current[1] + dy)

                # Boundary check
                if (
                    neighbor[0] < 0
                    or neighbor[0] >= self.width
                    or neighbor[1] < 0
                    or neighbor[1] >= self.height
                ):
                    continue

                # Obstacle check
                if self.grid[neighbor[1], neighbor[0]] == 1:
                    continue

                tentative_g = g_score[current] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = (current, action)
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self._heuristic(neighbor, goal)
                    counter += 1
                    heapq.heappush(open_set, (f_score, counter, neighbor))

        exec_time = (time.perf_counter() - start_time) * 1000.0
        return {
            "found": False,
            "path": [],
            "actions": [],
            "length": 0,
            "nodes_expanded": nodes_expanded,
            "execution_time_ms": exec_time,
        }
