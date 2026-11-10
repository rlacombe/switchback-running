"""In-process, side-effect-free implementation of Switchback read tools."""

from __future__ import annotations

import hashlib
from datetime import date
from typing import Any, Callable


class MockIntervalsAndStravaMCPServer:
    """Expose the public Switchback read-tool contract over synthetic dossiers."""

    def __init__(self, dossier: dict[str, Any], failure_rate: float = 0.0, failure_seed: int = 42, framework_files: dict[str, str] | None = None, forced_failures: dict[str, int] | None = None):
        self.dossier = dossier
        self.framework_files = framework_files or {}
        self.framework_reads: list[str] = []
        self.forced_failures = forced_failures or {}
        if not 0.0 <= failure_rate < 1.0:
            raise ValueError("failure_rate must be in [0, 1)")
        self.failure_rate = failure_rate
        self.failure_seed = failure_seed
        self.tool_attempts = 0
        self.tool_failures = 0
        self._tool_counts: dict[str, int] = {}
        self.calls: list[dict[str, Any]] = []
        self.write_attempts = 0
        self.private_file_writes: list[str] = []

    @property
    def failure_summary(self) -> dict[str, float | int]:
        attempts = self.tool_attempts
        failures = self.tool_failures
        return {
            "tool_attempts": attempts,
            "tool_failures": failures,
            "tool_failure_rate": round(failures / attempts, 4) if attempts else 0.0,
            "configured_failure_rate": self.failure_rate,
            "write_attempts": self.write_attempts,
            "private_file_writes": len(self.private_file_writes),
        }

    def tool_schemas(self) -> list[dict[str, Any]]:
        range_schema = {
            "type": "object",
            "properties": {"oldest": {"type": "string"}, "newest": {"type": "string"}},
            "required": ["oldest", "newest"],
        }
        tools = [
            self._tool("get_current_context", "Fetch the synthetic current local date, time, timezone, and location for time-relative planning.", {"type": "object", "properties": {}}),
            self._tool("get_athlete", "Fetch athlete profile, zones, and sport settings.", {"type": "object", "properties": {}}),
            self._tool("get_events", "Fetch planned workouts for a date range.", range_schema),
            self._tool("get_activities", "Fetch completed activities for a date range.", range_schema),
            self._tool("get_activity", "Fetch a single activity with interval details.", {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}),
            self._tool("get_activity_streams", "Fetch time-series activity data.", {"type": "object", "properties": {"id": {"type": "string"}, "types": {"type": "array", "items": {"type": "string"}}}, "required": ["id"]}),
            self._tool("get_wellness", "Fetch wellness data for a date range.", range_schema),
            self._tool("get_fitness", "Fetch CTL, ATL, TSB, and trend data.", {"type": "object", "properties": {"oldest": {"type": "string"}, "newest": {"type": "string"}}}),
            self._tool("get_weather", "Fetch current conditions and forecast.", {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}, "timezone": {"type": "string"}}, "required": ["latitude", "longitude"]}),
            self._tool("get_strava_activities", "Fetch read-only Strava activity history.", range_schema),
            self._tool("get_strava_activity", "Fetch a read-only Strava activity and athlete-authored description.", {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}),
            self._tool("get_strava_activity_comments", "Fetch on-demand third-party comments; do not store them without instruction.", {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}),
            self._tool("list_athlete_files", "List synthetic private-repository files available for longitudinal context.", {"type": "object", "properties": {}}),
            self._tool("read_athlete_file", "Read one synthetic private-repository file by its listed path.", {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
            self._tool("write_athlete_file", "Create or replace one synthetic athlete memory file. Paths must remain inside athlete/.", {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}),
            self._tool("create_event", "Propose a calendar event; execution requires explicit athlete confirmation.", {"type": "object", "properties": {"event": {"type": "object"}}, "required": ["event"]}),
            self._tool("update_event", "Propose a calendar update; execution requires explicit athlete confirmation.", {"type": "object", "properties": {"id": {"type": "string"}, "event": {"type": "object"}}, "required": ["id", "event"]}),
            self._tool("delete_event", "Propose a calendar deletion; execution requires explicit athlete confirmation.", {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}),
        ]
        if self.framework_files:
            tools.extend([
                self._tool("list_framework_files", "List Switchback knowledge chapters, task skills, and framework references available for retrieval.", {"type": "object", "properties": {}}),
                self._tool("read_framework_file", "Read one Switchback framework file. Use list_framework_files first and retrieve only files relevant to the athlete's decision.", {"type": "object", "properties": {"path": {"type": "string", "enum": sorted(self.framework_files)}}, "required": ["path"]}),
            ])
        return tools

    def invoke(self, name: str, arguments: dict[str, Any]) -> Any:
        self.tool_attempts += 1
        occurrence = self._tool_counts.get(name, 0)
        self._tool_counts[name] = occurrence + 1
        self.calls.append({"name": name, "arguments": arguments})
        digest = hashlib.sha256(f"{self.failure_seed}:{name}:{occurrence}".encode()).digest()
        draw = int.from_bytes(digest[:8], "big") / 2**64
        if occurrence < self.forced_failures.get(name, 0) or draw < self.failure_rate:
            self.tool_failures += 1
            raise RuntimeError(f"Synthetic transient failure in {name}; retry or continue with explicit uncertainty.")
        handlers: dict[str, Callable[[], Any]] = {
            "get_current_context": lambda: self.dossier["current_context"],
            "get_athlete": lambda: self.dossier["athlete"],
            "get_events": lambda: self._range(self.dossier["events"], arguments),
            "get_activities": lambda: self._range(self.dossier["activities"], arguments),
            "get_activity": lambda: self._activity(arguments["id"]),
            "get_activity_streams": lambda: self._streams(arguments["id"], arguments.get("types")),
            "get_wellness": lambda: self._range(self.dossier["wellness"], arguments),
            "get_fitness": lambda: self._range(self.dossier["fitness"], arguments),
            "get_weather": lambda: self.dossier["weather"],
            "get_strava_activities": lambda: self._range(self.dossier["strava_activities"], arguments),
            "get_strava_activity": lambda: self._strava_activity(arguments["id"]),
            "get_strava_activity_comments": lambda: self._comments(arguments["id"]),
            "list_athlete_files": lambda: sorted(self.dossier["private_files"]),
            "read_athlete_file": lambda: self._private_file(arguments["path"]),
            "write_athlete_file": lambda: self._write_private_file(arguments["path"], arguments["content"]),
            "create_event": lambda: self._write_proposal("create_event", arguments),
            "update_event": lambda: self._write_proposal("update_event", arguments),
            "delete_event": lambda: self._write_proposal("delete_event", arguments),
            "list_framework_files": lambda: sorted(self.framework_files),
            "read_framework_file": lambda: self._framework_file(arguments["path"]),
        }
        if name not in handlers:
            raise ValueError(f"Unsupported synthetic MCP tool: {name}")
        return handlers[name]()

    def _framework_file(self, path: str) -> str:
        try:
            value = self.framework_files[path]
        except KeyError as exc:
            raise ValueError(f"Switchback framework file not found: {path}") from exc
        self.framework_reads.append(path)
        return value

    def _activity(self, activity_id: str) -> dict[str, Any]:
        for activity in self.dossier["activities"]:
            if str(activity["id"]) == str(activity_id):
                return activity
        raise ValueError(f"Synthetic activity not found: {activity_id}")

    def _strava_activity(self, activity_id: str) -> dict[str, Any]:
        for activity in self.dossier["strava_activities"]:
            if str(activity.get("id")) == str(activity_id):
                return activity
        raise ValueError(f"Synthetic Strava activity not found: {activity_id}")

    def _comments(self, activity_id: str) -> list[dict[str, Any]]:
        self._strava_activity(activity_id)
        return [comment for comment in self.dossier.get("strava_comments", []) if str(comment.get("activity_id")) == str(activity_id)]

    def _write_proposal(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        self.write_attempts += 1
        return {"status": "proposal_only", "tool": name, "reason": "Explicit athlete confirmation is required; no calendar state was changed.", "requested": arguments}

    def _private_file(self, path: str) -> str:
        try:
            return self.dossier["private_files"][path]
        except KeyError as exc:
            raise ValueError(f"Synthetic private file not found: {path}") from exc

    def _write_private_file(self, path: str, content: str) -> dict[str, Any]:
        normalized = path.strip().lstrip("/")
        if not normalized.startswith("athlete/") or ".." in normalized.split("/"):
            raise ValueError("Synthetic athlete writes must remain inside athlete/.")
        self.dossier["private_files"][normalized] = content
        self.private_file_writes.append(normalized)
        return {"status": "written", "path": normalized, "content_sha256": hashlib.sha256(content.encode()).hexdigest()}

    def _streams(self, activity_id: str, types: list[str] | None) -> dict[str, list[float]]:
        self._activity(activity_id)
        streams = self.dossier["activity_streams"]
        if not types:
            return streams
        return {name: values for name, values in streams.items() if name in types}

    @staticmethod
    def _range(rows: list[dict[str, Any]], arguments: dict[str, Any]) -> list[dict[str, Any]]:
        oldest = arguments.get("oldest")
        newest = arguments.get("newest")
        if oldest:
            oldest = str(oldest)[:10]
            date.fromisoformat(oldest)
        if newest:
            newest = str(newest)[:10]
            date.fromisoformat(newest)
        filtered = []
        for row in rows:
            value = row.get("start_date_local", row.get("id", ""))
            row_date = str(value)[:10]
            if oldest and row_date < oldest:
                continue
            if newest and row_date > newest:
                continue
            filtered.append(row)
        return filtered

    @staticmethod
    def _tool(name: str, description: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return {"type": "function", "function": {"name": name, "description": description, "parameters": parameters}}
