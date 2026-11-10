"""Shared protocol primitives for the CLI-agent UltraBench."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

try:
    from .synthetic_data import dossier_for
except ImportError:
    from synthetic_data import dossier_for


BENCHMARK_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BENCHMARK_ROOT
SWITCHBACK_ROOT = Path(
    os.environ.get(
        "SWITCHBACK_ROOT",
        BENCHMARK_ROOT.parents[1] / "Agents" / "switchback-running",
    )
).expanduser().resolve()
BASELINE_PROMPT = "Help this athlete make well-grounded endurance-training decisions. Use available files and tools when relevant."
CONDITIONS = ("cli_agent", "switchback", "switchback_core")
DIAGNOSTIC_CONDITIONS = ("switchback_router",)

EVIDENCE_ROUTER = """
## Evidence Routing

Gather athlete-specific evidence before giving relevant advice. Use live MCP tools
for current fitness, wellness, activities, weather, events, and calendar state;
use athlete files for durable history and preferences. In particular:

- upcoming races, aid stations, or scheduled workouts: call `get_events`;
- current load or readiness: call `get_fitness` and `get_wellness`;
- recent volume or completed training: call `get_activities`;
- scheduling conflicts: inspect both athlete availability and `get_events`.

Do not substitute general knowledge for available athlete-specific evidence. State
plainly when required evidence cannot be retrieved.
""".strip()

def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): sha256_bytes(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git" not in path.parts and path.name != "mcp-calls.jsonl"
    }


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    return payload["scenarios"] if isinstance(payload, dict) else payload


def scenario_by_id(path: Path, scenario_id: str) -> dict[str, Any]:
    return next(item for item in load_scenarios(path) if item["id"] == scenario_id)


def runtime_context(scenario: dict[str, Any], dossier: dict[str, Any]) -> str:
    current = dossier["current_context"]
    return (
        "UltraBench uses a fictional athlete and synthetic data. "
        f"The simulated local date is {current['local_date']}; timezone: {current['timezone']}."
    )


def _copy_private_files(dossier: dict[str, Any], output: Path) -> None:
    for relative, content in dossier["private_files"].items():
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)


def prepare_workspace(
    scenario: dict[str, Any],
    condition: str,
    output: Path,
    artifacts: Path,
    python: Path,
    dataset: Path,
    harness: str = "agy",
) -> dict[str, Any]:
    """Materialize one isolated condition workspace."""
    if condition not in CONDITIONS + DIAGNOSTIC_CONDITIONS:
        raise ValueError(f"Unknown CLI condition: {condition}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    required_framework_files = (
        SWITCHBACK_ROOT / "SOUL.example.md",
        SWITCHBACK_ROOT / "AGENTS.md",
        SWITCHBACK_ROOT / "CLAUDE.md",
        SWITCHBACK_ROOT / "agents" / "core.md",
    )
    missing = [str(path) for path in required_framework_files if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Switchback framework checkout is incomplete. Set SWITCHBACK_ROOT. "
            f"Missing: {', '.join(missing)}"
        )
    dossier = dossier_for(scenario)
    _copy_private_files(dossier, output)
    shutil.copy2(SWITCHBACK_ROOT / "SOUL.example.md", output / "SOUL.example.md")

    if harness not in {"agy", "claude", "codex"}:
        raise ValueError(f"Unknown CLI harness: {harness}")
    instruction_name = "CLAUDE.md" if harness == "claude" else "AGENTS.md"

    if condition in {"switchback", "switchback_router"}:
        instruction_source = SWITCHBACK_ROOT / ("CLAUDE.md" if harness == "claude" else "AGENTS.md")
        shutil.copy2(instruction_source, output / instruction_name)
        if condition == "switchback_router":
            with (output / instruction_name).open("a") as instructions:
                instructions.write("\n\n" + EVIDENCE_ROUTER + "\n")
        for directory in ("knowledge", "agents"):
            shutil.copytree(SWITCHBACK_ROOT / directory, output / directory)
        shutil.copytree(SWITCHBACK_ROOT / ".claude" / "skills", output / ".claude" / "skills")
    elif condition == "switchback_core":
        shutil.copy2(SWITCHBACK_ROOT / "agents" / "core.md", output / instruction_name)
        shutil.copytree(SWITCHBACK_ROOT / "knowledge", output / "knowledge")
        shutil.copytree(SWITCHBACK_ROOT / "agents", output / "agents")
        shutil.copytree(SWITCHBACK_ROOT / ".claude" / "skills", output / ".claude" / "skills")
    else:
        (output / instruction_name).write_text(BASELINE_PROMPT + "\n")

    artifacts.mkdir(parents=True, exist_ok=True)
    state_path = artifacts / "mcp-state.json"
    call_log = artifacts / "mcp-calls.jsonl"
    state_path.write_text(json.dumps({"dossier": dossier, "tool_counts": {}, "writes": []}, indent=2) + "\n")
    settings = {
        "mcpServers": {
            "ultrabench-synthetic": {
                "command": str(python),
                "args": [
                    str(REPO_ROOT / "evals" / "cli_replay_mcp.py"),
                    "--dataset", str(dataset),
                    "--scenario", scenario["id"],
                    "--state", str(state_path),
                    "--call-log", str(call_log),
                ],
            }
        },
    }
    if harness == "agy":
        (output / ".agents").mkdir()
        (output / ".agents" / "mcp_config.json").write_text(json.dumps(settings, indent=2) + "\n")
    (artifacts / "mcp-config.json").write_text(json.dumps(settings, indent=2) + "\n")
    manifest = {
        "scenario_id": scenario["id"],
        "condition": condition,
        "harness": harness,
        "runtime_context": runtime_context(scenario, dossier),
        "shared_private_files": sorted(dossier["private_files"]),
        "workspace_hashes": file_hashes(output),
    }
    (artifacts / "workspace-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def parity_report(baseline: Path, switchback: Path) -> dict[str, Any]:
    """Verify shared athlete artifacts are identical and enumerate treatment files."""
    left = file_hashes(baseline)
    right = file_hashes(switchback)
    shared_prefixes = ("athlete/", "SOUL.md", "SOUL.example.md")
    shared_paths = sorted(path for path in set(left) | set(right) if path.startswith(shared_prefixes))
    mismatches = [path for path in shared_paths if left.get(path) != right.get(path)]
    return {
        "passed": not mismatches,
        "shared_paths": shared_paths,
        "mismatches": mismatches,
        "baseline_only": sorted(set(left) - set(right)),
        "switchback_only": sorted(set(right) - set(left)),
        "different_common_files": sorted(path for path in set(left) & set(right) if left[path] != right[path]),
    }


def manifest_parity_report(baseline: dict[str, Any], switchback: dict[str, Any]) -> dict[str, Any]:
    """Compare immutable starting manifests rather than post-agent workspaces."""
    left = baseline["workspace_hashes"]
    right = switchback["workspace_hashes"]
    shared_prefixes = ("athlete/", "SOUL.md", "SOUL.example.md")
    shared_paths = sorted(path for path in set(left) | set(right) if path.startswith(shared_prefixes))
    mismatches = [path for path in shared_paths if left.get(path) != right.get(path)]
    return {
        "passed": not mismatches,
        "shared_paths": shared_paths,
        "mismatches": mismatches,
        "treatment_files": sorted(path for path in set(right) - set(left) if not path.startswith(".agents/")),
    }
