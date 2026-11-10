#!/usr/bin/env python3
"""Summarize paired CLI-agent judgments on the paper's 0--100 scale."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path


def trajectory_score(row: dict) -> float:
    values = [float(value) for value in row["dimensions"].values() if value is not None]
    return (statistics.mean(values) - 1.0) * 25.0


def bootstrap_ci(values: list[float], samples: int = 5000, seed: int = 42) -> list[float]:
    generator = random.Random(seed)
    means = sorted(statistics.mean(generator.choice(values) for _ in values) for _ in range(samples))
    return [round(means[int(0.025 * (samples - 1))], 2), round(means[int(0.975 * (samples - 1))], 2)]


def summarize(path: Path) -> dict:
    payload = json.loads(path.read_text())
    valid = [row for row in payload["results"] if row.get("infrastructure_valid")]
    by_condition: dict[str, dict[str, float]] = {}
    for row in valid:
        by_condition.setdefault(row["condition"], {})[row["scenario_id"]] = trajectory_score(row)

    conditions = {
        condition: {
            "n": len(scores),
            "mean_score": round(statistics.mean(scores.values()), 2),
            "scenario_bootstrap_95pct_ci": bootstrap_ci(list(scores.values())),
        }
        for condition, scores in sorted(by_condition.items())
    }
    shared = sorted(set.intersection(*(set(scores) for scores in by_condition.values())))
    paired = {}
    if "cli_agent" in by_condition:
        baseline = by_condition["cli_agent"]
        for condition, scores in by_condition.items():
            if condition == "cli_agent":
                continue
            deltas = [scores[scenario] - baseline[scenario] for scenario in shared]
            paired[condition] = {
                "n": len(deltas),
                "mean_delta_vs_cli_agent": round(statistics.mean(deltas), 2),
                "paired_scenario_bootstrap_95pct_ci": bootstrap_ci(deltas),
            }
    return {"source": str(path), "conditions": conditions, "paired": paired}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path, nargs="+")
    args = parser.parse_args()
    print(json.dumps([summarize(path) for path in args.results], indent=2))


if __name__ == "__main__":
    main()
