#!/usr/bin/env python3
"""Run paired UltraBench trajectories through Antigravity CLI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .cli_evaluation import deterministic_evaluation, failure_classes, load_mcp_trace, normalize_agy_events
    from .cli_protocol import CONDITIONS, REPO_ROOT, SWITCHBACK_ROOT, file_hashes, manifest_parity_report, prepare_workspace, runtime_context, scenario_by_id
except ImportError:
    from cli_evaluation import deterministic_evaluation, failure_classes, load_mcp_trace, normalize_agy_events
    from cli_protocol import CONDITIONS, REPO_ROOT, SWITCHBACK_ROOT, file_hashes, manifest_parity_report, prepare_workspace, runtime_context, scenario_by_id

DEFAULT_SCENARIOS = ("27_load_metrics_interpretation", "31_vertical_progression", "33_aid_station_execution", "35_training_calendar_conflict")
DEFAULT_MODEL = "gemini-3.8-flash-medium"
USAGE_KEYS = ("input_tokens", "output_tokens", "thinking_tokens", "cache_read_tokens", "total_tokens")
CLI_ENV_ALLOWLIST = {
    "HOME", "PATH", "SHELL", "TMPDIR", "TMP", "TEMP", "USER", "LOGNAME",
    "LANG", "LC_ALL", "LC_CTYPE", "TERM", "COLORTERM", "NO_COLOR",
    "CODEX_HOME", "CLAUDE_CONFIG_DIR", "XDG_CONFIG_HOME", "XDG_CACHE_HOME",
}
FORBIDDEN_AGENT_COMMAND_MARKERS = (
    "curl ", "wget ", "http://", "https://", "intervals.icu", "strava.com",
    "intervals_api_key", "strava_client_secret", "strava_refresh_token",
)


def load_env(path: Path) -> dict[str, str]:
    env = os.environ.copy()
    if path.exists():
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                env.setdefault(name.removeprefix("export ").strip(), value.strip().strip('"').strip("'"))
    return env


def cli_env(source: dict[str, str] | None = None) -> dict[str, str]:
    """Return the complete environment exposed to target CLI agents."""
    source = os.environ if source is None else source
    return {name: value for name, value in source.items() if name in CLI_ENV_ALLOWLIST}


def forbidden_agent_commands(trace: list[dict[str, Any]]) -> list[str]:
    """Find attempts to bypass benchmark tools through shell or direct network access."""
    violations = []
    for item in trace:
        if item.get("name") != "run_command":
            continue
        command = str(item.get("arguments", {}).get("command", ""))
        lowered = command.lower()
        if any(marker in lowered for marker in FORBIDDEN_AGENT_COMMAND_MARKERS):
            violations.append(command)
    return violations


def parse_stream_output(stdout: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    events = [json.loads(raw) for raw in stdout.splitlines() if raw.strip()]
    result = next((event["result"] for event in reversed(events) if event.get("event") == "result"), None)
    if result is None:
        raise ValueError("Antigravity CLI returned no result event")
    return events, result


def observed_models(events: list[dict[str, Any]]) -> set[str]:
    return {str(event["init"]["model"]) for event in events if event.get("event") == "init" and event.get("init", {}).get("model")}


def cli_result_error(payload: dict[str, Any]) -> str | None:
    if payload.get("status") != "SUCCESS":
        return str(payload.get("status") or "CLI_ERROR")
    return None if str(payload.get("response", "")).strip() else "EMPTY_RESPONSE"


def add_usage(*items: dict[str, int]) -> dict[str, int]:
    return {key: sum(int(item.get(key, 0)) for item in items) for key in USAGE_KEYS}


def usage_delta(current: dict[str, Any], previous: dict[str, int]) -> dict[str, int]:
    return {key: max(0, int(current.get(key, 0)) - int(previous.get(key, 0))) for key in USAGE_KEYS}


def usage_accounting(usage: dict[str, int]) -> dict[str, int | float]:
    uncached, cached = usage.get("input_tokens", 0), usage.get("cache_read_tokens", 0)
    prompt = uncached + cached
    return {
        "prompt_tokens": prompt, "cached_prompt_tokens": cached, "uncached_prompt_tokens": uncached,
        "output_tokens": usage.get("output_tokens", 0), "thinking_tokens": usage.get("thinking_tokens", 0),
        "cache_rate": round(cached / prompt, 4) if prompt else 0.0,
    }


def protocol_hash() -> str:
    benchmark_paths = [
        REPO_ROOT / "evals/scenarios_dev.json", REPO_ROOT / "evals/synthetic_data.py",
        REPO_ROOT / "evals/cli_protocol.py", REPO_ROOT / "evals/cli_evaluation.py",
        REPO_ROOT / "evals/cli_replay_mcp.py", REPO_ROOT / "evals/run_cli_replays.py",
        REPO_ROOT / "evals/validation_set.json",
    ]
    framework_paths = [
        SWITCHBACK_ROOT / "AGENTS.md", SWITCHBACK_ROOT / "CLAUDE.md",
        SWITCHBACK_ROOT / "agents/core.md",
        *sorted((SWITCHBACK_ROOT / "knowledge").glob("*.md")),
        *sorted((SWITCHBACK_ROOT / ".claude/skills").glob("*/SKILL.md")),
    ]
    digest = hashlib.sha256()
    for namespace, root, paths in (
        ("benchmark", REPO_ROOT, benchmark_paths),
        ("framework", SWITCHBACK_ROOT, framework_paths),
    ):
        for path in paths:
            digest.update(f"{namespace}/{path.relative_to(root)}".encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def validate_output_root(output: Path) -> Path:
    resolved = output.resolve()
    forbidden = (REPO_ROOT, SWITCHBACK_ROOT)
    if any(resolved == root or root in resolved.parents for root in forbidden):
        raise RuntimeError("CLI workspaces must be outside the benchmark and Switchback repositories to prevent parent-instruction leakage")
    return resolved


def condition_order(scenario_id: str, replicate: int) -> tuple[str, ...]:
    return CONDITIONS if (int(scenario_id.split("_", 1)[0]) + replicate) % 2 else tuple(reversed(CONDITIONS))


def run_turn(command: list[str], workspace: Path, env: dict[str, str], timeout: int) -> tuple[subprocess.CompletedProcess[str], int]:
    retries = 0
    while True:
        try:
            completed = subprocess.run(command, cwd=workspace, env=env, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            return subprocess.CompletedProcess(command, 124, error.stdout or "", error.stderr or "CLI turn timed out"), retries
        # AGY sometimes writes provider errors only to --log-file and exits with
        # empty stderr. Retry silent nonzero exits; failed retries remain visible.
        transient = completed.returncode != 0 and (
            not completed.stderr.strip()
            or any(marker in completed.stderr.lower() for marker in ("rate limit", "temporarily unavailable", "connection reset", "timeout", "unavailable"))
        )
        if not transient or retries >= 2:
            return completed, retries
        retries += 1
        time.sleep(2**retries)


def quota_error(text: str) -> bool:
    return any(marker in text.lower() for marker in ("credits are depleted", "insufficient quota", "resource_exhausted", "quota exceeded"))


def cli_preflight(model: str, env: dict[str, str], timeout: int) -> dict[str, Any]:
    completed = subprocess.run(["agy", "models"], env=env, capture_output=True, text=True, timeout=timeout)
    if completed.returncode != 0:
        raise RuntimeError(f"Antigravity model preflight failed: {completed.stderr[:500]}")
    available = {line.split("\t", 1)[0].strip() for line in completed.stdout.splitlines() if line.strip() and not line.startswith("Fetching")}
    if model not in available:
        raise RuntimeError(f"Antigravity model {model} is unavailable; available models: {sorted(available)}")
    return {"requested_model": model, "available": True}


def run_trajectory(scenario: dict[str, Any], condition: str, replicate: int, model: str, run_root: Path, env: dict[str, str], timeout: int, attempt: int = 1) -> dict[str, Any]:
    workspace = run_root / "workspaces" / scenario["id"] / f"replicate-{replicate}" / condition
    artifacts = run_root / "artifacts" / scenario["id"] / f"replicate-{replicate}" / condition / f"attempt-{attempt}"
    dataset = REPO_ROOT / "evals/scenarios_dev.json"
    workspace_manifest = prepare_workspace(scenario, condition, workspace, artifacts, Path(sys.executable), dataset)
    dossier = json.loads((artifacts / "mcp-state.json").read_text())["dossier"]
    conversation_id = None
    previous_usage = {key: 0 for key in USAGE_KEYS}
    total_usage = {key: 0 for key in USAGE_KEYS}
    turns, responses, all_events = [], [], []
    verified_models: set[str] = set()
    infrastructure_error = retryable_failure = None
    total_retries = 0

    for index, turn in enumerate(scenario["turns"]):
        command = ["agy", "--model", model, "--output-format", "stream-json", "--sandbox", "--dangerously-skip-permissions", "--disable-slash-commands", "--log-file", str(artifacts / f"turn-{index + 1}.log")]
        if conversation_id is None:
            command.append("--new-project")
            prompt = f"{runtime_context(scenario, dossier)}\n\n{turn['user_prompt']}"
        else:
            command.extend(["--conversation", conversation_id])
            prompt = turn["user_prompt"]
        command.extend(["--print", prompt])
        started = time.monotonic()
        completed, retries = run_turn(command, workspace, env, timeout)
        total_retries += retries
        record: dict[str, Any] = {"turn": turn["turn"], "user_prompt": turn["user_prompt"], "exit_code": completed.returncode, "duration_seconds": round(time.monotonic() - started, 3), "infrastructure_retries": retries, "stderr": completed.stderr, "stdout": completed.stdout}
        response = ""
        if completed.returncode == 0:
            try:
                events, payload = parse_stream_output(completed.stdout)
                record["result"], record["events"] = payload, events
                all_events.extend(events)
                verified_models.update(observed_models(events))
                response = str(payload.get("response", ""))
                conversation_id = str(payload.get("conversation_id") or conversation_id or "") or None
                cumulative = {key: int(payload.get("usage", {}).get(key, 0)) for key in USAGE_KEYS}
                turn_usage = usage_delta(cumulative, previous_usage)
                if any(cumulative[key] < previous_usage[key] for key in USAGE_KEYS):
                    turn_usage = cumulative
                previous_usage = cumulative
                record["usage"] = turn_usage
                total_usage = add_usage(total_usage, turn_usage)
                retryable_failure = cli_result_error(payload)
            except (ValueError, json.JSONDecodeError) as error:
                record["parse_error"], retryable_failure = str(error), "INVALID_STREAM"
        record["completed"] = completed.returncode == 0 and bool(response.strip())
        responses.append(response)
        turns.append(record)
        (artifacts / "trajectory.json").write_text(json.dumps({"conversation_id": conversation_id, "turns": turns}, indent=2) + "\n")
        combined_error = completed.stderr + completed.stdout
        if quota_error(combined_error):
            infrastructure_error = "quota_depleted"
            break
        if completed.returncode != 0:
            infrastructure_error = f"cli_exit_{completed.returncode}"
            break
        if retryable_failure:
            break

    native_trace = normalize_agy_events(all_events)
    command_violations = forbidden_agent_commands(native_trace)
    mcp_trace = load_mcp_trace(artifacts / "mcp-calls.jsonl")
    transcript = "\n\n".join(f"Athlete: {turn['user_prompt']}\nAgent: {response}" for turn, response in zip(scenario["turns"], responses))
    evaluation = deterministic_evaluation(scenario, "\n\n".join(responses), native_trace, sum(item["completed"] for item in turns), mcp_trace)
    final_hashes, initial_hashes = file_hashes(workspace), workspace_manifest["workspace_hashes"]
    mutations = {"added": sorted(set(final_hashes) - set(initial_hashes)), "deleted": sorted(set(initial_hashes) - set(final_hashes)), "changed": sorted(path for path in set(initial_hashes) & set(final_hashes) if initial_hashes[path] != final_hashes[path])}
    model_verified = verified_models == {model}
    failures = failure_classes(evaluation)
    if command_violations and "external_access_attempt" not in failures:
        failures.append("external_access_attempt")
    if not model_verified and "execution" not in failures:
        failures.append("execution")
    result = {
        "scenario_id": scenario["id"], "condition": condition, "replicate": replicate, "attempt": attempt,
        "conversation_id": conversation_id, "requested_model": model, "observed_models": sorted(verified_models), "model_verified": model_verified,
        "workspace_manifest": workspace_manifest, "workspace_mutations": mutations, "turns": turns, "transcript": transcript,
        "native_trace": native_trace, "mcp_trace": mcp_trace, "evaluation": evaluation, "failure_classes": failures,
        "forbidden_agent_commands": command_violations,
        "infrastructure_retries": total_retries, "infrastructure_valid": infrastructure_error is None, "infrastructure_error": infrastructure_error,
        "retryable_failure": retryable_failure, "usage": total_usage, "usage_accounting": usage_accounting(total_usage),
        "duration_seconds": round(sum(turn["duration_seconds"] for turn in turns), 3),
    }
    (artifacts / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def run_trajectory_with_restart(scenario: dict[str, Any], condition: str, replicate: int, model: str, run_root: Path, env: dict[str, str], timeout: int) -> dict[str, Any]:
    failed_attempts = []
    for attempt in (1, 2):
        result = run_trajectory(scenario, condition, replicate, model, run_root, env, timeout, attempt)
        if not result.get("retryable_failure"):
            result["failed_attempts"] = failed_attempts
            return result
        failed_attempts.append({"attempt": attempt, "reason": result["retryable_failure"], "usage": result["usage"], "duration_seconds": result["duration_seconds"]})
    result["failed_attempts"] = failed_attempts
    result["usage"] = add_usage(*(item["usage"] for item in failed_attempts))
    result["usage_accounting"] = usage_accounting(result["usage"])
    result["infrastructure_valid"], result["infrastructure_error"] = False, "agent_response_failure_exhausted"
    return result


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {}
    for condition in CONDITIONS:
        all_rows = [row for row in results if row["condition"] == condition]
        rows = [row for row in all_rows if row.get("infrastructure_valid", True)]
        def mean(key: str) -> float | None:
            values = [row["evaluation"][key] for row in rows if row["evaluation"][key] is not None]
            return round(sum(values) / len(values), 4) if values else None
        tokens = add_usage(*(row.get("usage", {}) for row in rows)) if rows else {key: 0 for key in USAGE_KEYS}
        summary[condition] = {
            "trajectories": len(rows), "invalid_trajectories": len(all_rows) - len(rows), "evidence_acquisition": mean("evidence_acquisition"),
            "critical_fact_utilization": mean("critical_fact_utilization"), "operational_reliability": mean("operational_reliability"),
            "strict_deterministic_successes": sum(not row["failure_classes"] for row in rows), "model_verified": bool(rows) and all(row["model_verified"] for row in rows),
            "duration_seconds": round(sum(row.get("duration_seconds", 0) for row in rows), 3), "tokens": tokens, "usage_accounting": usage_accounting(tokens),
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output", type=Path, default=Path("/tmp/ultrabench-agy-pilot"))
    parser.add_argument("--scenarios", default=",".join(DEFAULT_SCENARIOS))
    parser.add_argument("--replicates", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--conditions", default=",".join(CONDITIONS), help="Comma-separated conditions to run")
    args = parser.parse_args()
    dataset = REPO_ROOT / "evals/scenarios_dev.json"
    scenarios = [scenario_by_id(dataset, item.strip()) for item in args.scenarios.split(",") if item.strip()]
    conditions = tuple(item.strip() for item in args.conditions.split(",") if item.strip())
    unknown = set(conditions) - set(CONDITIONS)
    if unknown:
        raise ValueError(f"Unknown conditions: {sorted(unknown)}")
    output = validate_output_root(args.output)
    output.mkdir(parents=True, exist_ok=True)
    env = cli_env()
    cli_version = subprocess.run(["agy", "--version"], capture_output=True, text=True, env=env).stdout.strip()
    preflight = cli_preflight(args.model, env, args.timeout)
    results_path = output / "results.json"
    if args.resume and results_path.exists():
        run = json.loads(results_path.read_text())
        if run.get("requested_model") != args.model or run.get("protocol") != "antigravity-agent-v1" or run.get("protocol_hash") != protocol_hash():
            raise RuntimeError("Cannot resume a run with a different protocol or model")
        results = run["results"]
    else:
        results = []
        run = {"protocol": "antigravity-agent-v1", "protocol_hash": protocol_hash(), "created_at_utc": datetime.now(timezone.utc).isoformat(), "cli": "agy", "cli_version": cli_version, "requested_model": args.model, "preflight": preflight, "replicates": args.replicates, "results": results}
    completed = {(row["scenario_id"], row["replicate"], row["condition"]): row for row in results if row.get("infrastructure_valid", True)}
    results[:] = [row for row in results if row.get("infrastructure_valid", True)]
    for replicate in range(1, args.replicates + 1):
        for scenario in scenarios:
            pair: dict[str, dict[str, Any]] = {}
            for condition in (item for item in condition_order(scenario["id"], replicate) if item in conditions):
                key = (scenario["id"], replicate, condition)
                if key in completed:
                    print(f"{scenario['id']} / replicate {replicate} / {condition} (checkpoint)", flush=True)
                    pair[condition] = completed[key]
                    continue
                print(f"{scenario['id']} / replicate {replicate} / {condition}", flush=True)
                result = run_trajectory_with_restart(scenario, condition, replicate, args.model, output, env, args.timeout)
                results.append(result)
                pair[condition] = result
                run["summary"] = summarize(results)
                results_path.write_text(json.dumps(run, indent=2) + "\n")
                if not result["infrastructure_valid"]:
                    raise RuntimeError(f"Infrastructure blocked {scenario['id']} / {condition}: {result['infrastructure_error']}")
                if not result["model_verified"]:
                    raise RuntimeError(f"Model mismatch for {scenario['id']} / {condition}: {result['observed_models']}")
            if "cli_agent" in pair:
                parity = {
                    condition: manifest_parity_report(pair["cli_agent"]["workspace_manifest"], pair[condition]["workspace_manifest"])
                    for condition in ("switchback", "switchback_core") if condition in pair
                }
                parity_path = output / "artifacts" / scenario["id"] / f"replicate-{replicate}" / "parity.json"
                parity_path.parent.mkdir(parents=True, exist_ok=True)
                parity_path.write_text(json.dumps(parity, indent=2) + "\n")
                failures = {condition: report["mismatches"] for condition, report in parity.items() if not report["passed"]}
                if failures:
                    raise RuntimeError(f"Shared workspace parity failed for {scenario['id']}: {failures}")
    run["summary"] = summarize(results)
    results_path.write_text(json.dumps(run, indent=2) + "\n")
    print(results_path)


if __name__ == "__main__":
    main()
