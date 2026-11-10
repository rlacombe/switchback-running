#!/usr/bin/env python3
"""Summarize frozen UltraBench CLI trajectories and panel judgments."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path


def score(dimensions: dict[str, float | None]) -> float:
    values = [float(value) for value in dimensions.values() if value is not None]
    return (statistics.mean(values) - 1.0) * 25.0


def bootstrap(values: list[float], samples: int = 5000, seed: int = 42) -> list[float]:
    rng = random.Random(seed)
    means = sorted(statistics.mean(rng.choice(values) for _ in values) for _ in range(samples))
    return [round(means[int(0.025 * (samples - 1))], 2), round(means[int(0.975 * (samples - 1))], 2)]


def quartiles(values: list[float]) -> list[float]:
    cuts = statistics.quantiles(values, n=4, method="inclusive")
    return [round(cuts[0], 2), round(statistics.median(values), 2), round(cuts[2], 2)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("evals/evaluation_manifest.json"))
    parser.add_argument("--run", action="append", required=True, metavar="MODEL=TRAJECTORIES,JUDGMENTS")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    strata = {item["scenario_id"]: item["primary_stratum"] for item in manifest["reserved_evaluation"]}
    records = []
    judge_records = []
    for spec in args.run:
        model, paths = spec.split("=", 1)
        trajectory_path, judgment_path = map(Path, paths.split(",", 1))
        trajectories = json.loads(trajectory_path.read_text())
        judgments = json.loads(judgment_path.read_text())
        source = {(row["scenario_id"], row["condition"]): row for row in trajectories["results"]}
        for row in judgments["results"]:
            if not row.get("infrastructure_valid"):
                continue
            key = (row["scenario_id"], row["condition"])
            trajectory = source[key]
            records.append({
                "model": model,
                "scenario": row["scenario_id"],
                "stratum": strata[row["scenario_id"]],
                "condition": row["condition"],
                "score": score(row["dimensions"]),
                "dimensions": row["dimensions"],
                "duration": float(trajectory["duration_seconds"]),
                "usage": trajectory.get("usage_accounting", {}),
                "cost": float(trajectory.get("total_cost_usd") or 0),
            })
            for panel in row["panel"]:
                judge_records.append({
                    "model": model,
                    "scenario": row["scenario_id"],
                    "condition": row["condition"],
                    "judge": panel["judge"],
                    "score": score(panel["judgment"]["dimensions"]),
                    "usage": panel.get("usage", {}),
                })

    report: dict = {"models": {}, "overall": {}, "judges": {}}
    for model in sorted({row["model"] for row in records}):
        subset = [row for row in records if row["model"] == model]
        model_report = {"conditions": {}, "paired": {}, "strata": {}, "dimensions": {}}
        for condition in ("cli_agent", "switchback"):
            cells = [row for row in subset if row["condition"] == condition]
            values = [row["score"] for row in cells]
            durations = [row["duration"] for row in cells]
            model_report["conditions"][condition] = {
                "n": len(cells),
                "mean": round(statistics.mean(values), 2),
                "ci": bootstrap(values),
                "latency_q1_median_q3_seconds": quartiles(durations),
                "total_duration_seconds": round(sum(durations), 2),
                "total_cost_usd": round(sum(row["cost"] for row in cells), 4),
                "usage": {
                    key: int(sum(row["usage"].get(key, 0) or 0 for row in cells))
                    for key in ("prompt_tokens", "cached_prompt_tokens", "uncached_prompt_tokens", "output_tokens", "thinking_tokens")
                },
            }
        by_key = {(row["scenario"], row["condition"]): row for row in subset}
        deltas = [by_key[(scenario, "switchback")]["score"] - by_key[(scenario, "cli_agent")]["score"] for scenario in strata]
        model_report["paired"] = {"mean_delta": round(statistics.mean(deltas), 2), "ci": bootstrap(deltas)}
        for stratum in sorted(set(strata.values())):
            ids = [scenario for scenario, name in strata.items() if name == stratum]
            stratum_deltas = [by_key[(sid, "switchback")]["score"] - by_key[(sid, "cli_agent")]["score"] for sid in ids]
            model_report["strata"][stratum] = {
                "n": len(ids),
                "raw": round(statistics.mean(by_key[(sid, "cli_agent")]["score"] for sid in ids), 2),
                "switchback": round(statistics.mean(by_key[(sid, "switchback")]["score"] for sid in ids), 2),
                "delta": round(statistics.mean(stratum_deltas), 2),
                "delta_ci": bootstrap(stratum_deltas),
            }
        for dimension in ("evidence_use", "domain_reasoning", "health_goal_alignment", "interaction", "memory_stewardship"):
            applicable = [row for row in subset if row["dimensions"].get(dimension) is not None]
            if not applicable:
                continue
            raw = [row["dimensions"][dimension] for row in applicable if row["condition"] == "cli_agent"]
            switchback = [row["dimensions"][dimension] for row in applicable if row["condition"] == "switchback"]
            model_report["dimensions"][dimension] = {
                "raw": round((statistics.mean(raw) - 1) * 25, 2),
                "switchback": round((statistics.mean(switchback) - 1) * 25, 2),
                "delta": round((statistics.mean(switchback) - statistics.mean(raw)) * 25, 2),
            }
        report["models"][model] = model_report

    all_by_key = defaultdict(list)
    for row in records:
        all_by_key[(row["scenario"], row["condition"])].append(row["score"])
    raw = [statistics.mean(all_by_key[(scenario, "cli_agent")]) for scenario in strata]
    switchback = [statistics.mean(all_by_key[(scenario, "switchback")]) for scenario in strata]
    deltas = [b - a for a, b in zip(raw, switchback)]
    report["overall"] = {
        "n_scenarios": len(strata),
        "n_trajectories": len(records),
        "raw": round(statistics.mean(raw), 2),
        "switchback": round(statistics.mean(switchback), 2),
        "mean_delta": round(statistics.mean(deltas), 2),
        "paired_ci": bootstrap(deltas),
    }
    for judge in sorted({row["judge"] for row in judge_records}):
        cells = [row for row in judge_records if row["judge"] == judge]
        by_condition = {condition: [row["score"] for row in cells if row["condition"] == condition] for condition in ("cli_agent", "switchback")}
        report["judges"][judge] = {
            condition: round(statistics.mean(values), 2) for condition, values in by_condition.items()
        } | {"delta": round(statistics.mean(by_condition["switchback"]) - statistics.mean(by_condition["cli_agent"]), 2)}

    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
