#!/usr/bin/env python3
"""Run UltraBench through native Claude Code or Codex CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .cli_evaluation import deterministic_evaluation, failure_classes, load_mcp_trace
    from .cli_protocol import CONDITIONS, REPO_ROOT, file_hashes, manifest_parity_report, prepare_workspace, runtime_context, scenario_by_id
    from .run_cli_replays import add_usage, cli_env, condition_order, forbidden_agent_commands, protocol_hash, quota_error, usage_accounting, validate_output_root
except ImportError:
    from cli_evaluation import deterministic_evaluation, failure_classes, load_mcp_trace
    from cli_protocol import CONDITIONS, REPO_ROOT, file_hashes, manifest_parity_report, prepare_workspace, runtime_context, scenario_by_id
    from run_cli_replays import add_usage, cli_env, condition_order, forbidden_agent_commands, protocol_hash, quota_error, usage_accounting, validate_output_root


def parse_json_lines(stdout: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in stdout.splitlines() if line.strip().startswith("{")]


def claude_result(events: list[dict[str, Any]]) -> dict[str, Any]:
    result = next((event for event in reversed(events) if event.get("type") == "result"), None)
    if not result:
        raise ValueError("Claude Code returned no result event")
    return result


def codex_result(events: list[dict[str, Any]]) -> dict[str, Any]:
    completed = next((event for event in reversed(events) if event.get("type") == "turn.completed"), None)
    failed = next((event for event in reversed(events) if event.get("type") == "turn.failed"), None)
    response = next((event.get("item", {}).get("text", "") for event in reversed(events) if event.get("item", {}).get("type") == "agent_message"), "")
    if failed:
        return {"status": "ERROR", "response": response, "error": failed.get("error")}
    if not completed:
        raise ValueError("Codex returned no completed turn")
    return {"status": "SUCCESS", "response": response, "usage": completed.get("usage", {})}


def normalize_native_events(harness: str, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    calls = []
    if harness == "claude":
        for event in events:
            message = event.get("message", {})
            for content in message.get("content", []) if isinstance(message, dict) else []:
                if content.get("type") != "tool_use":
                    continue
                name = str(content.get("name", ""))
                aliases = {"Read": "read_file", "Glob": "glob", "Grep": "grep_search"}
                calls.append({"id": content.get("id"), "name": aliases.get(name, name), "arguments": content.get("input", {}), "status": "success"})
    else:
        for event in events:
            if event.get("type") != "item.completed":
                continue
            item = event.get("item", {})
            item_type = item.get("type")
            if item_type == "mcp_tool_call":
                calls.append({"id": item.get("id"), "name": item.get("tool") or item.get("name"), "arguments": item.get("arguments", {}), "status": "error" if item.get("error") else "success"})
            elif item_type == "command_execution":
                command = str(item.get("command", ""))
                name = "read_file" if any(token in command for token in ("cat ", "sed ", "head ", "tail ")) else "run_command"
                calls.append({"id": item.get("id"), "name": name, "arguments": {"command": command}, "status": "success" if item.get("exit_code", 0) == 0 else "error"})
    return calls


def native_usage(harness: str, payload: dict[str, Any]) -> dict[str, int]:
    usage = payload.get("usage", {})
    if harness == "claude":
        output_details = usage.get("output_tokens_details", {})
        uncached = int(usage.get("input_tokens", 0)) + int(usage.get("cache_creation_input_tokens", 0))
        cached = int(usage.get("cache_read_input_tokens", 0))
        output = int(usage.get("output_tokens", 0))
        thinking = int(output_details.get("thinking_tokens", 0))
    else:
        cached = int(usage.get("cached_input_tokens", 0))
        uncached = max(0, int(usage.get("input_tokens", 0)) - cached)
        output = int(usage.get("output_tokens", 0))
        thinking = int(usage.get("reasoning_output_tokens", 0))
    return {"input_tokens": uncached, "output_tokens": output, "thinking_tokens": thinking, "cache_read_tokens": cached, "total_tokens": uncached + output}


def mcp_overrides(config_path: Path) -> list[str]:
    server = json.loads(config_path.read_text())["mcpServers"]["ultrabench-synthetic"]
    return [
        "-c", f'mcp_servers.ultrabench-synthetic.command={json.dumps(server["command"])}',
        "-c", f'mcp_servers.ultrabench-synthetic.args={json.dumps(server["args"])}',
    ]


CLAUDE_MCP_TOOLS = (
    "create_event",
    "delete_event",
    "get_activities",
    "get_activity",
    "get_activity_streams",
    "get_athlete",
    "get_current_context",
    "get_events",
    "get_fitness",
    "get_strava_activities",
    "get_strava_activity",
    "get_strava_activity_comments",
    "get_weather",
    "get_wellness",
    "update_event",
)


def claude_permission_denials(turns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        denial
        for turn in turns
        for denial in turn.get("result", {}).get("permission_denials", [])
        if str(denial.get("tool_name", "")).startswith("mcp__ultrabench-synthetic__")
    ]


def native_cli_env(env: dict[str, str], harness: str, artifacts: Path) -> dict[str, str]:
    """Isolate target shell startup while preserving native CLI authentication."""
    isolated = dict(env)
    if harness == "codex":
        home = artifacts / "home"
        home.mkdir(parents=True, exist_ok=True)
        isolated["HOME"] = str(home)
        isolated["CODEX_HOME"] = env.get("CODEX_HOME", str(Path.home() / ".codex"))
    return isolated


def command_for(harness: str, model: str, effort: str, prompt: str, workspace: Path, artifacts: Path, session_id: str | None) -> list[str]:
    if harness == "claude":
        command = [
            "claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
            "--model", model, "--effort", effort, "--permission-mode", "acceptEdits",
            "--allowedTools", ",".join(f"mcp__ultrabench-synthetic__{name}" for name in CLAUDE_MCP_TOOLS),
            "--disallowedTools", "Bash,WebFetch,WebSearch",
            "--setting-sources", "project", "--strict-mcp-config", "--mcp-config", str(artifacts / "mcp-config.json"),
        ]
        command.extend(["--resume", session_id] if session_id else ["--session-id", str(uuid.uuid4())])
        return command
    base = [
        "codex", "exec", "--json", "--model", model,
        "-c", f'model_reasoning_effort={json.dumps(effort)}',
        "-c", 'shell_environment_policy.inherit="none"',
        "--skip-git-repo-check", "--ignore-user-config", "--ignore-rules", "--approve-for-me",
        *mcp_overrides(artifacts / "mcp-config.json"),
    ]
    if session_id:
        return [*base, "resume", session_id, prompt]
    return [*base, "--cd", str(workspace), prompt]


def run_turn(command: list[str], workspace: Path, env: dict[str, str], timeout: int) -> tuple[subprocess.CompletedProcess[str], int]:
    for attempt in range(3):
        try:
            completed = subprocess.run(command, cwd=workspace, env=env, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            completed = subprocess.CompletedProcess(command, 124, error.stdout or "", error.stderr or "timeout")
        if completed.returncode == 0 or attempt == 2:
            return completed, attempt
        time.sleep(2 ** (attempt + 1))
    raise AssertionError("unreachable")


def run_trajectory(scenario: dict[str, Any], condition: str, harness: str, model: str, effort: str, root: Path, env: dict[str, str], timeout: int) -> dict[str, Any]:
    workspace = root / "workspaces" / scenario["id"] / condition
    artifacts = root / "artifacts" / scenario["id"] / condition
    manifest = prepare_workspace(scenario, condition, workspace, artifacts, Path(sys.executable), REPO_ROOT / "evals/scenarios_dev.json", harness=harness)
    target_env = native_cli_env(env, harness, artifacts)
    dossier = json.loads((artifacts / "mcp-state.json").read_text())["dossier"]
    session_id = None
    turns, responses, all_events = [], [], []
    total_usage = {key: 0 for key in ("input_tokens", "output_tokens", "thinking_tokens", "cache_read_tokens", "total_tokens")}
    total_cost = 0.0
    infrastructure_error = None
    for index, turn in enumerate(scenario["turns"]):
        prompt = f"{runtime_context(scenario, dossier)}\n\n{turn['user_prompt']}" if index == 0 else turn["user_prompt"]
        command = command_for(harness, model, effort, prompt, workspace, artifacts, session_id)
        started = time.monotonic()
        completed, retries = run_turn(command, workspace, target_env, timeout)
        record: dict[str, Any] = {"turn": turn["turn"], "user_prompt": turn["user_prompt"], "exit_code": completed.returncode, "stderr": completed.stderr, "stdout": completed.stdout, "duration_seconds": round(time.monotonic() - started, 3), "infrastructure_retries": retries}
        response = ""
        if completed.returncode == 0:
            try:
                events = parse_json_lines(completed.stdout)
                payload = claude_result(events) if harness == "claude" else codex_result(events)
                response = str(payload.get("result", "") if harness == "claude" else payload.get("response", ""))
                if harness == "claude":
                    session_id = str(payload.get("session_id") or session_id)
                    total_cost += float(payload.get("total_cost_usd", 0))
                else:
                    session_id = session_id or next((event.get("thread_id") for event in events if event.get("type") == "thread.started"), None)
                usage = native_usage(harness, payload)
                total_usage = add_usage(total_usage, usage)
                record.update({"events": events, "result": payload, "usage": usage})
            except (ValueError, json.JSONDecodeError) as error:
                record["parse_error"] = str(error)
        record["completed"] = completed.returncode == 0 and bool(response.strip())
        turns.append(record)
        responses.append(response)
        all_events.extend(record.get("events", []))
        if quota_error(completed.stderr + completed.stdout):
            infrastructure_error = "quota_depleted"
            break
        if not record["completed"]:
            infrastructure_error = f"{harness}_turn_failure"
            break
    native_trace = normalize_native_events(harness, all_events)
    permission_denials = claude_permission_denials(turns) if harness == "claude" else []
    if permission_denials:
        infrastructure_error = "benchmark_tool_permission_denied"
    command_violations = forbidden_agent_commands(native_trace)
    mcp_trace = load_mcp_trace(artifacts / "mcp-calls.jsonl")
    evaluation = deterministic_evaluation(scenario, "\n\n".join(responses), native_trace, sum(turn["completed"] for turn in turns), mcp_trace)
    initial, final = manifest["workspace_hashes"], file_hashes(workspace)
    mutations = {"added": sorted(set(final) - set(initial)), "deleted": sorted(set(initial) - set(final)), "changed": sorted(path for path in set(initial) & set(final) if initial[path] != final[path])}
    if harness == "claude":
        observed_models = {
            details.get("canonicalModel")
            for turn in turns
            for details in turn.get("result", {}).get("modelUsage", {}).values()
            if details.get("canonicalModel") and not details.get("canonicalModel", "").startswith("claude-haiku")
        }
        model_verified = all(turn["completed"] for turn in turns) and observed_models == {model}
    else:
        observed_models = {model} if all(turn["completed"] for turn in turns) else set()
        model_verified = observed_models == {model}
    failures = failure_classes(evaluation)
    if command_violations and "external_access_attempt" not in failures:
        failures.append("external_access_attempt")
    if not model_verified and "execution" not in failures:
        failures.append("execution")
    return {
        "scenario_id": scenario["id"], "condition": condition, "replicate": 1, "harness": harness, "requested_model": model,
        "effort": effort, "session_id": session_id, "observed_models": sorted(observed_models), "model_verified": model_verified,
        "model_verification_method": "canonical_model_usage" if harness == "claude" else "accepted_explicit_model_request",
        "workspace_manifest": manifest, "workspace_mutations": mutations, "turns": turns,
        "transcript": "\n\n".join(f"Athlete: {turn['user_prompt']}\nAgent: {response}" for turn, response in zip(scenario["turns"], responses)),
        "native_trace": native_trace, "mcp_trace": mcp_trace, "evaluation": evaluation, "failure_classes": failures,
        "forbidden_agent_commands": command_violations,
        "benchmark_tool_permission_denials": permission_denials,
        "infrastructure_valid": infrastructure_error is None, "infrastructure_error": infrastructure_error,
        "usage": total_usage, "usage_accounting": usage_accounting(total_usage), "total_cost_usd": round(total_cost, 6),
        "duration_seconds": round(sum(turn["duration_seconds"] for turn in turns), 3),
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {}
    for condition in CONDITIONS:
        rows = [row for row in results if row["condition"] == condition and row["infrastructure_valid"]]
        tokens = add_usage(*(row["usage"] for row in rows)) if rows else {}
        def mean(key: str) -> float | None:
            values = [row["evaluation"][key] for row in rows if row["evaluation"][key] is not None]
            return round(sum(values) / len(values), 4) if values else None
        summary[condition] = {
            "trajectories": len(rows),
            "evidence_acquisition": mean("evidence_acquisition"),
            "critical_fact_utilization": mean("critical_fact_utilization"),
            "operational_reliability": round(sum(row["evaluation"]["operational_reliability"] for row in rows) / len(rows), 4) if rows else None,
            "strict_deterministic_successes": sum(not row["failure_classes"] for row in rows),
            "usage": usage_accounting(tokens), "total_cost_usd": round(sum(row["total_cost_usd"] for row in rows), 4),
        }
    return summary


def build_preflight_report(payload: dict[str, Any], scenario_ids: list[str], conditions: tuple[str, ...]) -> dict[str, Any]:
    results = payload["results"]
    expected = {(scenario_id, condition) for scenario_id in scenario_ids for condition in conditions}
    actual = {(row["scenario_id"], row["condition"]) for row in results}
    checks = {
        "all_cells_present": actual == expected,
        "all_infrastructure_valid": all(row.get("infrastructure_valid") for row in results),
        "all_models_verified": all(row.get("model_verified") for row in results),
        "no_benchmark_tool_permission_denials": all(not row.get("benchmark_tool_permission_denials") for row in results),
        "all_turns_complete": all(len(row.get("turns", [])) == 3 and all(turn.get("completed") for turn in row["turns"]) for row in results),
        "mcp_reached_in_every_condition": all(row.get("mcp_trace") for row in results),
    }
    return {
        "passed": all(checks.values()),
        "protocol_hash": payload["protocol_hash"],
        "harness": payload["harness"],
        "requested_model": payload["requested_model"],
        "effort": payload["effort"],
        "scenario_ids": scenario_ids,
        "conditions": list(conditions),
        "checks": checks,
        "measured_cost_usd": round(sum(row.get("total_cost_usd", 0) for row in results), 6),
        "summary": summarize(results),
    }


def validate_preflight_report(path: Path, harness: str, model: str, effort: str, conditions: tuple[str, ...]) -> dict[str, Any]:
    report = json.loads(path.read_text())
    expected = {
        "passed": True,
        "protocol_hash": protocol_hash(),
        "harness": harness,
        "requested_model": model,
        "effort": effort,
        "conditions": list(conditions),
    }
    mismatches = {key: (report.get(key), value) for key, value in expected.items() if report.get(key) != value}
    if mismatches:
        raise ValueError(f"Preflight report does not authorize this run: {mismatches}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness", choices=("claude", "codex"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scenarios", required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--conditions", default=",".join(CONDITIONS), help="Comma-separated conditions to run")
    parser.add_argument("--preflight", action="store_true", help="Run one scenario and write a protocol-bound preflight report")
    parser.add_argument("--preflight-report", type=Path, help="Passing report required for a paid multi-scenario run")
    parser.add_argument("--confirm-paid-run", action="store_true")
    parser.add_argument("--max-trajectories", type=int)
    parser.add_argument("--max-budget-usd", type=float)
    args = parser.parse_args()
    output = validate_output_root(args.output)
    output.mkdir(parents=True, exist_ok=True)
    destination = output / "results.json"
    env = cli_env()
    conditions = tuple(item.strip() for item in args.conditions.split(",") if item.strip())
    unknown = set(conditions) - set(CONDITIONS)
    if unknown:
        raise ValueError(f"Unknown conditions: {sorted(unknown)}")
    scenario_ids = [item.strip() for item in args.scenarios.split(",") if item.strip()]
    expected_trajectories = len(scenario_ids) * len(conditions)
    if args.preflight:
        if len(scenario_ids) != 1:
            raise ValueError("Preflight requires exactly one scenario")
    else:
        if not args.confirm_paid_run:
            raise ValueError("Paid run requires --confirm-paid-run")
        if args.preflight_report is None:
            raise ValueError("Paid run requires --preflight-report")
        validate_preflight_report(args.preflight_report, args.harness, args.model, args.effort, conditions)
    if args.max_trajectories is None or expected_trajectories > args.max_trajectories:
        raise ValueError(f"Run requires --max-trajectories >= {expected_trajectories}")
    if args.max_budget_usd is None or args.max_budget_usd <= 0:
        raise ValueError("Run requires a positive --max-budget-usd")
    if args.resume and destination.exists():
        payload = json.loads(destination.read_text())
        results = [row for row in payload["results"] if row["infrastructure_valid"]]
        payload["results"] = results
    else:
        results = []
        payload = {"protocol": f"{args.harness}-native-v1", "protocol_hash": protocol_hash(), "created_at_utc": datetime.now(timezone.utc).isoformat(), "harness": args.harness, "requested_model": args.model, "effort": args.effort, "results": results}
    completed = {(row["scenario_id"], row["condition"]) for row in results}
    for scenario_id in scenario_ids:
        scenario = scenario_by_id(REPO_ROOT / "evals/scenarios_dev.json", scenario_id)
        pair = {}
        for condition in (item for item in condition_order(scenario_id, 1) if item in conditions):
            key = (scenario_id, condition)
            if key in completed:
                print(f"{scenario_id} / {condition} (checkpoint)", flush=True)
                pair[condition] = next(row for row in results if (row["scenario_id"], row["condition"]) == key)
                continue
            spent = sum(row.get("total_cost_usd", 0) for row in results)
            if spent >= args.max_budget_usd:
                raise RuntimeError(f"Budget cap reached before {scenario_id} / {condition}: ${spent:.4f} >= ${args.max_budget_usd:.4f}")
            print(f"{scenario_id} / {condition}", flush=True)
            result = run_trajectory(scenario, condition, args.harness, args.model, args.effort, output, env, args.timeout)
            results.append(result)
            pair[condition] = result
            payload["summary"] = summarize(results)
            destination.write_text(json.dumps(payload, indent=2) + "\n")
            if not result["infrastructure_valid"]:
                raise RuntimeError(f"Infrastructure blocked {scenario_id} / {condition}: {result['infrastructure_error']}")
        if "cli_agent" in pair:
            parity = {
                condition: manifest_parity_report(pair["cli_agent"]["workspace_manifest"], pair[condition]["workspace_manifest"])
                for condition in ("switchback", "switchback_core") if condition in pair
            }
            if not all(report["passed"] for report in parity.values()):
                raise RuntimeError(f"Workspace parity failed for {scenario_id}")
    payload["summary"] = summarize(results)
    destination.write_text(json.dumps(payload, indent=2) + "\n")
    if args.preflight:
        report = build_preflight_report(payload, scenario_ids, conditions)
        report_path = output / "preflight_report.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n")
        if not report["passed"]:
            raise RuntimeError(f"Preflight failed: {report['checks']}")
        print(report_path)
    print(destination)


if __name__ == "__main__":
    main()
