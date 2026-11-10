#!/usr/bin/env python3
"""Serve one UltraBench synthetic dossier over MCP stdio for CLI replays."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .mock_mcp_server import MockIntervalsAndStravaMCPServer
    from .synthetic_data import dossier_for
except ImportError:
    from mock_mcp_server import MockIntervalsAndStravaMCPServer
    from synthetic_data import dossier_for


def load_scenario(path: str, scenario_id: str) -> dict[str, Any]:
    payload = json.load(open(path))
    scenarios = payload["scenarios"] if isinstance(payload, dict) else payload
    return next(item for item in scenarios if item["id"] == scenario_id)


def send(payload: dict[str, Any]) -> None:
    print(json.dumps(payload), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--state", type=Path)
    parser.add_argument("--call-log", type=Path)
    args = parser.parse_args()
    scenario = load_scenario(args.dataset, args.scenario)
    saved = json.loads(args.state.read_text()) if args.state and args.state.exists() else {}
    server = MockIntervalsAndStravaMCPServer(
        saved.get("dossier", dossier_for(scenario)),
        forced_failures=scenario["mcp_data"].get("robustness_forced_tool_failures", {}),
    )
    server._tool_counts = saved.get("tool_counts", {})
    saved_writes = saved.get("writes", [])
    server.write_attempts = len(saved_writes)
    server.private_file_writes = saved.get("private_file_writes", [])

    def persist() -> None:
        if not args.state:
            return
        state = {
            "dossier": server.dossier,
            "tool_counts": server._tool_counts,
            "writes": saved_writes + [call for call in server.calls if call["name"] in {"create_event", "update_event", "delete_event"}],
            "private_file_writes": server.private_file_writes,
        }
        args.state.write_text(json.dumps(state, indent=2) + "\n")
    schemas = {
        item["function"]["name"]: item["function"]
        for item in server.tool_schemas()
        if item["function"]["name"] not in {"list_athlete_files", "read_athlete_file", "write_athlete_file"}
    }

    for line in sys.stdin:
        try:
            request = json.loads(line)
            request_id = request.get("id")
            method = request.get("method")
            if method == "initialize":
                send({"jsonrpc": "2.0", "id": request_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "ultrabench-synthetic", "version": "1.0.0"}}})
            elif method == "tools/list":
                tools = [{"name": value["name"], "description": value["description"], "inputSchema": value["parameters"]} for value in schemas.values()]
                send({"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}})
            elif method == "tools/call":
                params = request.get("params", {})
                name = params.get("name")
                if name not in schemas:
                    raise ValueError(f"Unknown tool: {name}")
                arguments = params.get("arguments", {})
                result = server.invoke(name, arguments)
                persist()
                if args.call_log:
                    args.call_log.parent.mkdir(parents=True, exist_ok=True)
                    with args.call_log.open("a") as log:
                        log.write(json.dumps({"name": name, "arguments": arguments, "result": result}) + "\n")
                send({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "isError": False,
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                        "structuredContent": {"data": result},
                    },
                })
            elif method and method.startswith("notifications/"):
                continue
            else:
                send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}})
        except Exception as error:
            persist()
            if args.call_log:
                args.call_log.parent.mkdir(parents=True, exist_ok=True)
                with args.call_log.open("a") as log:
                    log.write(json.dumps({"error": repr(error), "request": request if "request" in locals() else None}) + "\n")
            send({"jsonrpc": "2.0", "id": request.get("id") if "request" in locals() else None, "result": {"isError": True, "content": [{"type": "text", "text": str(error)}], "structuredContent": {"error": str(error)}}})


if __name__ == "__main__":
    main()
