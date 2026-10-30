"""RoboPilot Core Training CLI Script.

Supports:
- A* Search validation
- Tabular Q-Learning training & export
- Dueling Double DQN (D3QN) training & Contract #6 Model Artifact Packaging

Designed by Tab 4 (@tab_4) — ML/RL Engineer & Training Architect.
Specification: docs/TRAINING_PIPELINE.md, docs/MODEL_LIFECYCLE.md.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure repository root is on PYTHONPATH
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from typing import Any, Dict, List

import numpy as np
import torch

from src.ai_core.algorithms.artifact import ModelArtifactManager
from src.ai_core.algorithms.astar import AStarPlanner
from src.ai_core.algorithms.d3qn import D3QNAgent
from src.ai_core.algorithms.q_learning import QLearningAgent
from src.ai_core.env.warehouse_env import WarehouseGridEnv


def train_astar(map_path: str | Path, verbose: bool = True) -> Dict[str, Any]:
    """Execute A* baseline pathfinding on given map."""
    env = WarehouseGridEnv(map_file=map_path)
    planner = AStarPlanner(env.grid_map)
    res = planner.plan(env.start_pos, env.goal_pos)

    if verbose:
        print(f"\n[A* Baseline] Map: {map_path}")
        print(f"  Path Found: {res['found']}")
        print(f"  Optimal Steps: {res['length']}")
        print(f"  Nodes Expanded: {res['nodes_expanded']}")
        print(f"  Execution Time: {res['execution_time_ms']:.3f} ms")
        if res["found"]:
            print(f"  Waypoints: {res['path'][:5]} ... {res['path'][-2:]}")

    return res


def train_q_learning(
    map_path: str | Path,
    episodes: int = 500,
    seed: int = 42,
    export_dir: str | Path | None = None,
    log_interval: int = 50,
    verbose: bool = True,
) -> Dict[str, Any]:
    """Train Tabular Q-Learning baseline agent."""
    env = WarehouseGridEnv(map_file=map_path, observation_mode="coordinates")
    agent = QLearningAgent(
        grid_width=env.width,
        grid_height=env.height,
        seed=seed,
    )

    success_history: List[bool] = []
    reward_history: List[float] = []
    step_history: List[int] = []

    start_time = time.perf_counter()

    for ep in range(1, episodes + 1):
        obs, _ = env.reset(seed=seed + ep)
        done = False
        truncated = False
        ep_reward = 0.0
        steps = 0

        while not (done or truncated):
            pos = (env.robot_pos[0], env.robot_pos[1])
            action = agent.select_action(pos, evaluate=False)
            _, reward, done, truncated, info = env.step(action)
            next_pos = (env.robot_pos[0], env.robot_pos[1])

            agent.update(pos, action, reward, next_pos, done)
            ep_reward += reward
            steps += 1

        agent.decay_epsilon()
        success = bool(info.get("is_success", False))
        success_history.append(success)
        reward_history.append(ep_reward)
        step_history.append(steps)

        if verbose and (ep % log_interval == 0 or ep == episodes):
            recent_succ = np.mean(success_history[-log_interval:]) * 100.0
            recent_rew = np.mean(reward_history[-log_interval:])
            print(
                f"[QLearning] Ep {ep:4d}/{episodes} | "
                f"Success: {recent_succ:5.1f}% | "
                f"Mean Rew: {recent_rew:7.2f} | "
                f"Epsilon: {agent.epsilon:.3f}"
            )

    elapsed_s = time.perf_counter() - start_time
    final_success_rate = float(np.mean(success_history[-100:] if len(success_history) >= 100 else success_history) * 100.0)

    if export_dir:
        out_p = Path(export_dir)
        out_p.mkdir(parents=True, exist_ok=True)
        agent.save(out_p / "q_table.pkl")
        if verbose:
            print(f"[QLearning] Exported Q-table to {out_p / 'q_table.pkl'}")

    return {
        "episodes": episodes,
        "final_success_rate": final_success_rate,
        "elapsed_seconds": elapsed_s,
    }


def train_d3qn(
    map_path: str | Path,
    episodes: int = 500,
    seed: int = 42,
    batch_size: int = 64,
    lr: float = 0.0005,
    device: str | None = None,
    export_dir: str | Path | None = None,
    log_interval: int = 50,
    verbose: bool = True,
) -> Dict[str, Any]:
    """Train Dueling Double Deep Q-Network (D3QN) agent."""
    env = WarehouseGridEnv(map_file=map_path, observation_mode="proximity_raycast")

    agent = D3QNAgent(
        input_dim=7,
        action_dim=4,
        learning_rate=lr,
        batch_size=batch_size,
        buffer_capacity=50000,
        seed=seed,
        device=device,
    )

    success_history: List[bool] = []
    reward_history: List[float] = []
    step_history: List[int] = []
    loss_history: List[float] = []

    start_time = time.perf_counter()

    for ep in range(1, episodes + 1):
        obs, _ = env.reset(seed=seed + ep)
        done = False
        truncated = False
        ep_reward = 0.0
        steps = 0
        ep_losses: List[float] = []

        while not (done or truncated):
            action = agent.select_action(obs, evaluate=False)
            next_obs, reward, done, truncated, info = env.step(action)

            # Store transition: flag done only if true terminal (not time limit truncated)
            terminal = done and not truncated
            agent.store_transition(obs, action, reward, next_obs, terminal)

            # Gradient update step
            loss = agent.train_step()
            if loss is not None:
                ep_losses.append(loss)

            obs = next_obs
            ep_reward += reward
            steps += 1

        agent.decay_epsilon()
        success = bool(info.get("is_success", False))
        success_history.append(success)
        reward_history.append(ep_reward)
        step_history.append(steps)
        if ep_losses:
            loss_history.append(float(np.mean(ep_losses)))

        if verbose and (ep % log_interval == 0 or ep == episodes):
            recent_succ = np.mean(success_history[-log_interval:]) * 100.0
            recent_rew = np.mean(reward_history[-log_interval:])
            recent_loss = np.mean(loss_history[-log_interval:]) if loss_history else 0.0
            print(
                f"[D3QN] Ep {ep:4d}/{episodes} | "
                f"Success: {recent_succ:5.1f}% | "
                f"Mean Rew: {recent_rew:7.2f} | "
                f"Loss: {recent_loss:.4f} | "
                f"Epsilon: {agent.epsilon:.3f}"
            )

    elapsed_s = time.perf_counter() - start_time
    eval_window = 100 if len(success_history) >= 100 else len(success_history)
    final_success_rate = float(np.mean(success_history[-eval_window:]) * 100.0)
    final_mean_reward = float(np.mean(reward_history[-eval_window:]))
    final_avg_steps = float(np.mean(step_history[-eval_window:]))

    # Packaging Model Artifact conforming to Technical Contract #6
    if export_dir:
        meta_overrides = {
            "metrics": {
                "success_rate_pct": final_success_rate,
                "mean_reward": final_mean_reward,
                "avg_steps_to_goal": final_avg_steps,
                "episodes_trained": episodes,
                "training_duration_sec": elapsed_s,
            },
            "training_config": {
                "learning_rate": lr,
                "batch_size": batch_size,
                "seed": seed,
            },
        }
        artifact_path = ModelArtifactManager.export_artifact(
            target_dir=export_dir,
            agent=agent,
            metadata_overrides=meta_overrides,
        )
        if verbose:
            print(f"[D3QN] Contract #6 Artifact successfully exported to: {artifact_path}")

    return {
        "episodes": episodes,
        "final_success_rate": final_success_rate,
        "final_mean_reward": final_mean_reward,
        "final_avg_steps": final_avg_steps,
        "elapsed_seconds": elapsed_s,
    }


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="RoboPilot Model Training & Baseline Benchmarking CLI"
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default="D3QN",
        choices=["AStar", "astar", "QLearning", "qlearning", "D3QN", "d3qn"],
        help="Algorithm to run/train",
    )
    parser.add_argument(
        "--map",
        type=str,
        default="maps/benchmark_easy_10x10.json",
        help="Path to warehouse grid map JSON",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=300,
        help="Number of training episodes",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Batch size for D3QN buffer sampling",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=0.0005,
        help="Learning rate",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Hardware accelerator ('cpu' or 'cuda')",
    )
    parser.add_argument(
        "--export-dir",
        type=str,
        default="models/d3qn_warehouse_v1",
        help="Directory to package and export trained model artifact",
    )
    parser.add_argument(
        "--log-interval",
        type=int,
        default=50,
        help="Log progress every N episodes",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress training stdout logs",
    )
    return parser.parse_args()


def main() -> None:
    """Main CLI entry point."""
    args = parse_args()
    algo = args.algorithm.upper()
    verbose = not args.quiet

    if verbose:
        print("=" * 65)
        print("   ROBOPILOT RL TRAINING & BENCHMARK PIPELINE (PHASE 2)")
        print(f"   Algorithm: {algo} | Map: {args.map} | Seed: {args.seed}")
        print("=" * 65)

    if algo == "ASTAR":
        train_astar(args.map, verbose=verbose)
    elif algo in ("QLEARNING", "Q_LEARNING"):
        train_q_learning(
            map_path=args.map,
            episodes=args.episodes,
            seed=args.seed,
            export_dir=args.export_dir,
            log_interval=args.log_interval,
            verbose=verbose,
        )
    elif algo == "D3QN":
        train_d3qn(
            map_path=args.map,
            episodes=args.episodes,
            seed=args.seed,
            batch_size=args.batch_size,
            lr=args.lr,
            device=args.device,
            export_dir=args.export_dir,
            log_interval=args.log_interval,
            verbose=verbose,
        )
    else:
        print(f"Error: Unknown algorithm '{args.algorithm}'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
