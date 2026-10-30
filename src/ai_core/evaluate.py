"""RoboPilot Multi-Seed Evaluation & Scientific Benchmark Runner.

Strictly adheres to RoboPilot Constitution (ZERO TOLERANCE FOR FAKE DATA):
- Runs across 3-5 random seeds (Mean ± Std)
- Compares against theoretical A* ground truth
- Measures step latency, path suboptimality ratio, and collision rates.

Designed by Tab 2 (@tab_2) & Tab 7 (@tab_7).
Specification: docs/ALGORITHM_COMPARISON.md, docs/TEST_PLAN.md.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure repository root is on PYTHONPATH
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np

from src.ai_core.algorithms.artifact import ModelArtifactManager
from src.ai_core.algorithms.astar import AStarPlanner
from src.ai_core.algorithms.d3qn import D3QNAgent
from src.ai_core.algorithms.q_learning import QLearningAgent
from src.ai_core.env.warehouse_env import WarehouseGridEnv


def evaluate_astar(
    map_path: str | Path,
    num_runs: int = 10,
) -> Dict[str, Any]:
    """Evaluate A* deterministic ground truth baseline."""
    env = WarehouseGridEnv(map_file=map_path)
    planner = AStarPlanner(env.grid_map)

    latencies: List[float] = []
    plan = planner.plan(env.start_pos, env.goal_pos)

    for _ in range(num_runs):
        t0 = time.perf_counter()
        planner.plan(env.start_pos, env.goal_pos)
        latencies.append((time.perf_counter() - t0) * 1000.0)

    found = plan["found"]
    length = plan["length"] if found else 0

    return {
        "name": "A* Search",
        "success_rate_mean": 100.0 if found else 0.0,
        "success_rate_std": 0.0,
        "path_length_mean": float(length),
        "path_length_std": 0.0,
        "collision_rate_mean": 0.0,
        "collision_rate_std": 0.0,
        "latency_ms_mean": float(np.mean(latencies)),
        "latency_ms_std": float(np.std(latencies)),
    }


def evaluate_q_learning(
    map_path: str | Path,
    q_table_path: Optional[str | Path] = None,
    seeds: List[int] = [42, 123, 999],
    episodes_per_seed: int = 20,
) -> Dict[str, Any]:
    """Evaluate Tabular Q-Learning agent across multiple random seeds."""
    env = WarehouseGridEnv(map_file=map_path, observation_mode="coordinates")
    agent = QLearningAgent(grid_width=env.width, grid_height=env.height)

    if q_table_path and Path(q_table_path).exists():
        agent.load(q_table_path)
    else:
        # Train brief policy if no checkpoint exists
        for ep in range(150):
            env.reset(seed=ep)
            done = False
            truncated = False
            while not (done or truncated):
                pos = (env.robot_pos[0], env.robot_pos[1])
                act = agent.select_action(pos, evaluate=False)
                _, r, done, truncated, _ = env.step(act)
                npos = (env.robot_pos[0], env.robot_pos[1])
                agent.update(pos, act, r, npos, done)
            agent.decay_epsilon()

    seed_successes: List[float] = []
    seed_steps: List[float] = []
    seed_collisions: List[float] = []
    all_latencies: List[float] = []

    for seed in seeds:
        succ_list: List[bool] = []
        step_list: List[int] = []
        coll_list: List[bool] = []

        for ep in range(episodes_per_seed):
            env.reset(seed=seed * 1000 + ep)
            done = False
            truncated = False
            steps = 0
            had_collision = False

            while not (done or truncated):
                pos = (env.robot_pos[0], env.robot_pos[1])
                t0 = time.perf_counter()
                act = agent.select_action(pos, evaluate=True)
                all_latencies.append((time.perf_counter() - t0) * 1000.0)

                _, _, done, truncated, info = env.step(act)
                if info.get("collision", False):
                    had_collision = True
                steps += 1

            succ_list.append(bool(info.get("is_success", False)))
            step_list.append(steps)
            coll_list.append(had_collision)

        seed_successes.append(float(np.mean(succ_list) * 100.0))
        seed_steps.append(float(np.mean(step_list)))
        seed_collisions.append(float(np.mean(coll_list) * 100.0))

    return {
        "name": "Tabular Q-Learning",
        "success_rate_mean": float(np.mean(seed_successes)),
        "success_rate_std": float(np.std(seed_successes)),
        "path_length_mean": float(np.mean(seed_steps)),
        "path_length_std": float(np.std(seed_steps)),
        "collision_rate_mean": float(np.mean(seed_collisions)),
        "collision_rate_std": float(np.std(seed_collisions)),
        "latency_ms_mean": float(np.mean(all_latencies)) if all_latencies else 0.0,
        "latency_ms_std": float(np.std(all_latencies)) if all_latencies else 0.0,
    }


def evaluate_d3qn(
    map_path: str | Path,
    artifact_dir: Optional[str | Path] = None,
    seeds: List[int] = [42, 123, 999],
    episodes_per_seed: int = 20,
    device: str = "cpu",
) -> Dict[str, Any]:
    """Evaluate D3QN agent across multiple random seeds."""
    env = WarehouseGridEnv(map_file=map_path, observation_mode="proximity_raycast")

    if artifact_dir and Path(artifact_dir).exists():
        agent, _ = ModelArtifactManager.load_artifact(artifact_dir, device=device)
    else:
        agent = D3QNAgent(input_dim=7, action_dim=4, device=device)

    seed_successes: List[float] = []
    seed_steps: List[float] = []
    seed_collisions: List[float] = []
    all_latencies: List[float] = []

    for seed in seeds:
        succ_list: List[bool] = []
        step_list: List[int] = []
        coll_list: List[bool] = []

        for ep in range(episodes_per_seed):
            obs, _ = env.reset(seed=seed * 1000 + ep)
            done = False
            truncated = False
            steps = 0
            had_collision = False

            while not (done or truncated):
                t0 = time.perf_counter()
                act = agent.select_action(obs, evaluate=True)
                all_latencies.append((time.perf_counter() - t0) * 1000.0)

                next_obs, _, done, truncated, info = env.step(act)
                if info.get("collision", False):
                    had_collision = True
                obs = next_obs
                steps += 1

            succ_list.append(bool(info.get("is_success", False)))
            step_list.append(steps)
            coll_list.append(had_collision)

        seed_successes.append(float(np.mean(succ_list) * 100.0))
        seed_steps.append(float(np.mean(step_list)))
        seed_collisions.append(float(np.mean(coll_list) * 100.0))

    return {
        "name": "D3QN (PyTorch)",
        "success_rate_mean": float(np.mean(seed_successes)),
        "success_rate_std": float(np.std(seed_successes)),
        "path_length_mean": float(np.mean(seed_steps)),
        "path_length_std": float(np.std(seed_steps)),
        "collision_rate_mean": float(np.mean(seed_collisions)),
        "collision_rate_std": float(np.std(seed_collisions)),
        "latency_ms_mean": float(np.mean(all_latencies)) if all_latencies else 0.0,
        "latency_ms_std": float(np.std(all_latencies)) if all_latencies else 0.0,
    }


def print_comparison_table(results: List[Dict[str, Any]], astar_steps: float) -> None:
    """Render comparison table strictly conforming to Zero Fake Data Constitution."""
    header = (
        f"| {'Thuật toán (Algorithm)':<22} | "
        f"{'Tỷ lệ thành công (%)':<20} | "
        f"{'Độ dài bước (Mean ± Std)':<25} | "
        f"{'Tỷ số vs A*':<11} | "
        f"{'Tỷ lệ va chạm (%)':<18} | "
        f"{'Độ trễ (ms/bước)':<17} |"
    )
    separator = "|" + "-" * 24 + "|" + "-" * 22 + "|" + "-" * 27 + "|" + "-" * 13 + "|" + "-" * 20 + "|" + "-" * 19 + "|"

    print("\n" + "=" * 110)
    print("      ROBOPILOT BENCHMARK MULTI-SEED SCIENTIFIC EVALUATION REPORT")
    print("=" * 110)
    print(header)
    print(separator)

    for r in results:
        ratio_str = f"{r['path_length_mean'] / astar_steps:.2f}" if astar_steps > 0 else "N/A"
        succ_str = f"{r['success_rate_mean']:.1f} ± {r['success_rate_std']:.1f}%"
        step_str = f"{r['path_length_mean']:.1f} ± {r['path_length_std']:.1f}"
        coll_str = f"{r['collision_rate_mean']:.1f} ± {r['collision_rate_std']:.1f}%"
        lat_str = f"{r['latency_ms_mean']:.3f} ± {r['latency_ms_std']:.3f}"

        row = (
            f"| {r['name']:<22} | "
            f"{succ_str:<20} | "
            f"{step_str:<25} | "
            f"{ratio_str:<11} | "
            f"{coll_str:<18} | "
            f"{lat_str:<17} |"
        )
        print(row)
    print("=" * 110 + "\n")


def main() -> None:
    """CLI Entry point for benchmark evaluation."""
    parser = argparse.ArgumentParser(description="RoboPilot Multi-Seed Benchmark Evaluation")
    parser.add_argument("--map", type=str, default="maps/benchmark_easy_10x10.json")
    parser.add_argument("--artifact-dir", type=str, default=None, help="Path to Contract #6 model artifact bundle")
    parser.add_argument("--qtable-path", type=str, default=None, help="Path to Q-Learning pickle table")
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 999], help="Random seeds (min 3)")
    parser.add_argument("--episodes-per-seed", type=int, default=10, help="Episodes per random seed")
    parser.add_argument("--device", type=str, default="cpu")
    args = parser.parse_args()

    print(f"[Benchmark] Evaluating Map: {args.map}")
    print(f"[Benchmark] Seeds: {args.seeds} ({len(args.seeds)} seeds)")

    astar_res = evaluate_astar(args.map)
    astar_steps = astar_res["path_length_mean"]

    q_res = evaluate_q_learning(
        args.map,
        q_table_path=args.qtable_path,
        seeds=args.seeds,
        episodes_per_seed=args.episodes_per_seed,
    )

    d3qn_res = evaluate_d3qn(
        args.map,
        artifact_dir=args.artifact_dir,
        seeds=args.seeds,
        episodes_per_seed=args.episodes_per_seed,
        device=args.device,
    )

    print_comparison_table([astar_res, q_res, d3qn_res], astar_steps=astar_steps)


if __name__ == "__main__":
    main()
