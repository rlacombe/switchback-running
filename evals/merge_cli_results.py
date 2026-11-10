#!/usr/bin/env python3
"""Merge disjoint UltraBench trajectory shards and verify cell completeness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .run_cli_replays import summarize as summarize_antigravity
    from .run_native_replays import summarize as summarize_native
except ImportError:
    from run_cli_replays import summarize as summarize_antigravity
    from run_native_replays import summarize as summarize_native


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-scenarios", type=int, required=True)
    parser.add_argument("--expected-conditions", type=int, default=2)
    parser.add_argument("inputs", type=Path, nargs="+")
    args = parser.parse_args()

    payloads = [json.loads(path.read_text()) for path in args.inputs]
    protocol = payloads[0]["protocol"]
    protocol_hash = payloads[0]["protocol_hash"]
    requested_model = payloads[0]["requested_model"]
    for payload in payloads[1:]:
        if (payload["protocol"], payload["protocol_hash"], payload["requested_model"]) != (
            protocol,
            protocol_hash,
            requested_model,
        ):
            raise ValueError("Shard protocol or model mismatch")

    valid = [row for payload in payloads for row in payload["results"] if row["infrastructure_valid"]]
    cells = [(row["scenario_id"], row["condition"]) for row in valid]
    if len(cells) != len(set(cells)):
        raise ValueError("Duplicate valid cells across shards")
    expected = args.expected_scenarios * args.expected_conditions
    if len(cells) != expected:
        raise ValueError(f"Expected {expected} valid cells, found {len(cells)}")

    valid.sort(key=lambda row: (int(row["scenario_id"].split("_", 1)[0]), row["condition"]))
    merged = {key: value for key, value in payloads[0].items() if key not in {"results", "summary"}}
    merged["results"] = valid
    summarize = summarize_antigravity if protocol == "antigravity-agent-v1" else summarize_native
    merged["summary"] = summarize(valid)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(merged, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
