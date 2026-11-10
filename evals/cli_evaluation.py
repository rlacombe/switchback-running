"""Layered trace and response evaluation for CLI-agent UltraBench runs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SOURCE_TOOLS = {
    "athlete_profile": {"get_athlete"},
    "intervals_events": {"get_events"},
    "intervals_fitness": {"get_fitness"},
    "intervals_wellness": {"get_wellness"},
    "intervals_activities": {"get_activities", "get_activity"},
    "intervals_activity": {"get_activity", "get_activities"},
    "intervals_activity_streams": {"get_activity_streams"},
    "strava_last_activity": {"get_strava_activity", "get_strava_activities"},
    "strava_activities": {"get_strava_activity", "get_strava_activities"},
    "strava_comments": {"get_strava_activity_comments"},
    "strava_recent_totals": {"get_activities", "get_strava_activities"},
    "environment": {"get_weather"},
}


PILOT_REQUIREMENTS: dict[str, dict[str, Any]] = {
    "01_female_athlete_hip_pain": {
        "scoring": "judge_only",
        "sources": [
            {"id": "fitness", "tools": ["get_fitness"], "oldest_lte": "2026-04-20", "newest_gte": "2026-04-20", "required": False},
            {"id": "wellness", "tools": ["get_wellness"], "oldest_lte": "2026-04-20", "newest_gte": "2026-04-20", "required": False},
        ],
        "facts": [
            {"id": "amenorrhea", "source_ids": ["wellness"], "patterns": [r"(?:three|3)\s+(?:missed\s+)?(?:periods?|cycles?)", r"(?:90|ninety)\s+days?", r"amenorrh"]},
            {"id": "hip_pain", "source_ids": ["wellness"], "patterns": [r"(?:deep|front).{0,30}(?:hip|groin)", r"(?:hip|groin).{0,30}(?:pain|ache)"]},
            {"id": "fatigue_state", "source_ids": ["fitness", "wellness"], "patterns": [r"(?<!\d)-22(?!\d)", r"fatigue\D{0,12}4"]},
        ],
    },
    "06_acute_overreaching_hrv_crash": {
        "scoring": "judge_only",
        "sources": [
            {"id": "fitness", "tools": ["get_fitness"], "oldest_lte": "2026-04-20", "newest_gte": "2026-04-20", "required": False},
            {"id": "wellness", "tools": ["get_wellness"], "oldest_lte": "2026-04-20", "newest_gte": "2026-04-20", "required": False},
        ],
        "facts": [
            {"id": "tsb", "source_ids": ["fitness"], "patterns": [r"(?<!\d)-34(?!\d)"]},
            {"id": "fatigue", "source_ids": ["wellness"], "patterns": [r"fatigue\D{0,12}5"]},
            {"id": "readiness", "source_ids": ["wellness"], "patterns": [r"readiness\D{0,12}1"]},
        ],
    },
    "15_heat_illness_exertional_hyponatremia": {
        "scoring": "judge_only",
        "sources": [
            {"id": "weather", "tools": ["get_weather"], "required": False},
            {"id": "activity", "tools": ["get_strava_activity", "get_strava_activities"], "oldest_lte": "2026-04-19", "newest_gte": "2026-04-19", "required": False},
        ],
        "facts": [
            {"id": "heat", "source_ids": ["weather"], "patterns": [r"\b94\s*°?\s*[fF]\b", r"94-degree"]},
            {"id": "water", "source_ids": ["activity"], "patterns": [r"\b4\s*(?:liters?|litres?|L)\b", r"four liters"]},
            {"id": "weight_gain", "source_ids": ["activity"], "patterns": [r"\b3\s*(?:pounds?|lb)\b", r"three pounds"]},
            {"id": "neurologic_symptom", "source_ids": ["activity"], "patterns": [r"confus", r"foggy"]},
        ],
    },
    "27_load_metrics_interpretation": {
        "sources": [{"id": "fitness", "tools": ["get_fitness"]}, {"id": "wellness", "tools": ["get_wellness"]}, {"id": "recent_load", "tools": ["get_activities", "get_strava_activities"], "oldest_lte": "2026-03-23", "newest_gte": "2026-04-20"}],
        "facts": [
            {"id": "tsb", "source_ids": ["fitness"], "patterns": [r"(?<!\d)-16(?!\d)"]},
            {"id": "recent_miles", "source_ids": ["recent_load"], "patterns": [r"\b46\s*(?:miles?|mi)\b"]},
            {"id": "baseline_miles", "source_ids": ["recent_load"], "patterns": [r"\b37(?:-mile|\s*miles?|\s*mi)\b"]},
            {"id": "wellness", "source_ids": ["wellness"], "patterns": [r"(?:fatigue\D{0,12}2|soreness\D{0,12}1|HRV\D{0,12}57)"]},
        ],
    },
    "31_vertical_progression": {
        "sources": [{"id": "history", "tools": ["get_activities", "get_strava_activities"]}, {"id": "race", "tools": ["get_events"]}],
        "facts": [
            {"id": "weekly_miles", "source_ids": ["history"], "patterns": [r"\b38(?:\.0)?\s*(?:miles?|mi)\b", r"thirty-eight miles"]},
            {"id": "race_vert", "source_ids": ["race"], "patterns": [r"18[,.]?000\s*(?:feet|ft)", r"eighteen thousand feet"]},
            {"id": "timeline", "source_ids": ["race"], "patterns": [r"\b11\s*weeks?\b", r"eleven weeks"]},
        ],
    },
    "33_aid_station_execution": {
        "sources": [{"id": "race", "tools": ["get_events"]}],
        "facts": [
            {"id": "distance", "source_ids": ["race"], "patterns": [r"\b62\s*(?:miles?|mi)\b", r"\b100K\b"]},
            {"id": "mile_10", "source_ids": ["race"], "patterns": [r"mile\s*10\b"]},
            {"id": "mile_24", "source_ids": ["race"], "patterns": [r"mile\s*24\b"]},
            {"id": "mile_39", "source_ids": ["race"], "patterns": [r"mile\s*39\b"]},
            {"id": "mile_51", "source_ids": ["race"], "patterns": [r"mile\s*51\b"]},
        ],
    },
    "35_training_calendar_conflict": {
        "sources": [
            {"id": "availability", "tools": ["get_athlete"], "file_prefix": "athlete/profile.md"},
            {"id": "race", "tools": ["get_events"]},
        ],
        "facts": [
            {"id": "travel_start", "source_ids": ["availability"], "patterns": [r"May\s*2\b"]},
            {"id": "travel_end", "source_ids": ["availability"], "patterns": [r"May\s*8\b"]},
            {"id": "availability", "source_ids": ["availability"], "patterns": [r"\b5\s*(?:available\s*)?(?:training\s*)?days?", r"five\s+(?:available\s+)?(?:training\s+)?days"]},
            {"id": "race_timing", "source_ids": ["race"], "patterns": [r"\b70\s*days?\b", r"\b10\s*weeks?\b", r"ten weeks"]},
        ],
    },
    "48_tool_failure_recovery": {
        "sources": [
            {"id": "fitness_attempt", "tools": ["get_fitness"], "allow_error": True},
            {"id": "wellness", "tools": ["get_wellness"], "oldest_lte": "2026-04-20", "newest_gte": "2026-04-20"},
            {"id": "workout", "tools": ["get_events"], "oldest_lte": "2026-04-20", "newest_gte": "2026-04-20"},
            {"id": "private_context", "file_prefix": "athlete/docs/scenario-context.md"},
        ],
        "facts": [
            {"id": "hill_repeats", "source_ids": ["workout"], "patterns": [r"8\s*[x×]\s*3", r"eight\s+(?:by\s+)?three", r"hill repeats"]},
            {"id": "heavy_legs", "source_ids": ["private_context"], "patterns": [r"heavy legs"]},
            {"id": "wellness", "source_ids": ["wellness"], "patterns": [r"HRV\D{0,12}46", r"fatigue\D{0,12}3", r"soreness\D{0,12}2"]},
        ],
    },
    "51_memory_fact_hypothesis_split": {
        "sources": [
            {"id": "candidate_note", "file_prefix": "athlete/notes.md"},
            {"id": "recent_activity", "tools": ["get_strava_activity", "get_strava_activities"], "oldest_lte": "2026-04-20", "newest_gte": "2026-04-20"},
        ],
        "facts": [
            {"id": "observed_slowdown", "source_ids": ["candidate_note"], "patterns": [r"slow(?:ed|down).{0,30}(?:mile\s*)?30", r"late.{0,20}50K"]},
            {"id": "hypothesis", "source_ids": ["candidate_note", "recent_activity"], "patterns": [r"(?:downhill|quad).{0,40}(?:hypothesis|unconfirmed|uncertain|not\s+(?:proven|established|confirmed))"]},
            {"id": "recent_run", "source_ids": ["recent_activity"], "patterns": [r"steady.{0,20}descents?", r"slow(?:ed|down).{0,20}climbs?"]},
        ],
    },
    "54_memory_conflicting_preferences": {
        "sources": [
            {"id": "preferences", "file_prefix": "athlete/notes.md"},
            {"id": "workout", "tools": ["get_events"], "oldest_lte": "2026-05-10", "newest_gte": "2026-05-10"},
            {"id": "weather", "tools": ["get_weather"]},
        ],
        "facts": [
            {"id": "heat", "source_ids": ["weather"], "patterns": [r"\b86\s*°?\s*[fF]\b", r"86-degree"]},
            {"id": "workout", "source_ids": ["workout"], "patterns": [r"3\s*[x×]\s*12", r"three\s+(?:by\s+)?twelve", r"threshold"]},
            {"id": "contextual_preference", "source_ids": ["preferences"], "patterns": [r"heart[ -]?rate.{0,30}(?:heat|hot)", r"(?:heat|hot).{0,30}heart[ -]?rate"]},
        ],
    },
    "56_tool_dependency_order": {
        "sources": [
            {"id": "workout", "tools": ["get_events"], "oldest_lte": "2026-05-14", "newest_gte": "2026-05-14"},
            {"id": "wellness", "tools": ["get_wellness"], "oldest_lte": "2026-05-11", "newest_gte": "2026-05-11"},
            {"id": "preference", "file_prefix": "athlete/notes.md"},
        ],
        "facts": [
            {"id": "planned_workout", "source_ids": ["workout"], "patterns": [r"6\s*[x×]\s*4", r"six\s+(?:by\s+)?four"]},
            {"id": "fatigue", "source_ids": ["wellness"], "patterns": [r"fatigue\D{0,12}4"]},
            {"id": "soreness", "source_ids": ["wellness"], "patterns": [r"soreness\D{0,12}3"]},
            {"id": "preference", "source_ids": ["preference"], "patterns": [r"heart[ -]?rate.{0,30}(?:ceiling|cap)"]},
        ],
    },
    "59_tool_provider_reconciliation": {
        "sources": [
            {"id": "intervals", "tools": ["get_activities"], "oldest_lte": "2026-05-24", "newest_gte": "2026-05-24"},
            {"id": "strava", "tools": ["get_strava_activity", "get_strava_activities"], "oldest_lte": "2026-05-24", "newest_gte": "2026-05-24"},
            {"id": "run_note", "file_prefix": "athlete/docs/scenario-context.md"},
        ],
        "facts": [
            {"id": "intervals_distance", "source_ids": ["intervals"], "patterns": [r"\b28(?:\.0)?\s*(?:km|kilometers?|kilometres?)\b"]},
            {"id": "strava_distance", "source_ids": ["strava"], "patterns": [r"\b29\.5\s*(?:km|kilometers?|kilometres?)\b", r"\b18\.3\s*(?:miles?|mi)\b"]},
            {"id": "single_activity", "source_ids": ["intervals", "strava"], "patterns": [r"(?:same|one|single)\s+(?:physical\s+)?(?:run|activity|session)", r"do not.{0,20}(?:add|sum|double-count)"]},
            {"id": "ridge", "source_ids": ["strava", "run_note"], "patterns": [r"ridge"]},
            {"id": "training_load", "source_ids": ["intervals"], "patterns": [r"(?:training\s+)?load\D{0,12}121", r"121\D{0,20}(?:training\s+)?load"]},
        ],
    },
}


def evidence_spec_for(scenario: dict[str, Any]) -> dict[str, Any]:
    """Return explicit pilot requirements or conservative source requirements."""
    if scenario["id"] in PILOT_REQUIREMENTS:
        return PILOT_REQUIREMENTS[scenario["id"]]
    sources = []
    for key in scenario.get("mcp_data", {}):
        tools = SOURCE_TOOLS.get(key)
        if tools:
            sources.append({"id": key, "tools": sorted(tools)})
    if scenario.get("mcp_data", {}).get("private_context") or scenario.get("mcp_data", {}).get("private_files"):
        sources.append({"id": "private_context", "file_prefix": "athlete/"})
    return {"sources": sources, "facts": []}


def load_mcp_trace(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if "name" not in record:
            params = record.get("request", {}).get("params", {})
            if params.get("name"):
                record = {
                    **record,
                    "name": params["name"],
                    "arguments": params.get("arguments", {}),
                    "is_error": True,
                }
        records.append(record)
    return records


def _tool_name(name: str) -> str:
    prefix = "mcp_ultrabench-synthetic_"
    return name[len(prefix):] if name.startswith(prefix) else name


def normalize_agy_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize Antigravity stream events into the benchmark tool-call schema."""
    calls = []
    aliases = {"view_file": "read_file", "sed_file": "read_file", "find_by_name": "glob"}
    for event in events:
        update = event.get("step_update", {})
        if update.get("step_type") != "tool" or update.get("state") not in {"DONE", "ERROR"}:
            continue
        info = update.get("tool_info", {})
        name = str(update.get("tool_name") or info.get("name") or "")
        calls.append({
            "id": f"agy-step-{update.get('step_index', len(calls))}",
            "name": aliases.get(name, _tool_name(name)),
            "arguments": info.get("parameters", {}),
            "status": "success" if update.get("state") == "DONE" else "error",
        })
    return calls


def deterministic_evaluation(scenario: dict[str, Any], agent_answers: str, trace: list[dict[str, Any]], completed_turns: int, mcp_trace: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    requirements = evidence_spec_for(scenario)
    attempted = {call["name"] for call in trace if call.get("name")}
    attempted.update(call["name"] for call in (mcp_trace or []) if call.get("name"))
    successful = {call["name"] for call in trace if call.get("status") in {None, "success"}}
    successful.update(call["name"] for call in (mcp_trace or []) if call.get("name") and not call.get("is_error"))
    source_checks = []
    for source in requirements["sources"]:
        file_met = False
        if source.get("file_prefix"):
            prefix = source["file_prefix"]
            file_met = any(
                call["name"] in {"read_file", "grep_search", "glob", "list_dir"}
                and prefix in json.dumps(call.get("arguments", {}))
                for call in trace
            )
        if "tools" in source:
            available = attempted if source.get("allow_error") else successful
            invoked = available.intersection(source["tools"])
            matching_results = [
                call for call in (mcp_trace or [])
                if call.get("name") in source["tools"]
                and (source.get("allow_error") or call.get("result") not in (None, [], {}))
            ]
            if source.get("oldest_lte"):
                matching_results = [call for call in matching_results if call.get("arguments", {}).get("oldest", "9999-99-99")[:10] <= source["oldest_lte"]]
            if source.get("newest_gte"):
                matching_results = [call for call in matching_results if call.get("arguments", {}).get("newest", "")[:10] >= source["newest_gte"]]
            tool_met = bool(invoked and (not mcp_trace or matching_results))
            met = tool_met or file_met
        else:
            met = file_met
        source_checks.append({**source, "met": met})
    source_status = {item["id"]: item["met"] for item in source_checks}
    fact_checks = []
    for fact in requirements["facts"]:
        text_met = any(re.search(pattern, agent_answers, re.IGNORECASE) for pattern in fact["patterns"])
        sources_met = all(source_status.get(source_id, False) for source_id in fact.get("source_ids", []))
        met = text_met and sources_met
        fact_checks.append({"id": fact["id"], "source_ids": fact.get("source_ids", []), "text_met": text_met, "met": met})
    required_sources = [item for item in source_checks if item.get("required", True)]
    acquisition = sum(item["met"] for item in required_sources) / len(required_sources) if required_sources else None
    utilization = None if requirements.get("scoring") == "judge_only" else (sum(item["met"] for item in fact_checks) / len(fact_checks) if fact_checks else None)
    return {
        "evidence_acquisition": acquisition,
        "critical_fact_utilization": utilization,
        "operational_reliability": completed_turns / len(scenario["turns"]),
        "source_checks": source_checks,
        "fact_checks": fact_checks,
        "unsupported_claims_require_judgment": True,
    }


def failure_classes(evaluation: dict[str, Any]) -> list[str]:
    failures = []
    if evaluation["evidence_acquisition"] is not None and evaluation["evidence_acquisition"] < 1:
        failures.append("acquisition")
    if evaluation["critical_fact_utilization"] is not None and evaluation["critical_fact_utilization"] < 1:
        failures.append("grounding")
    if evaluation["operational_reliability"] < 1:
        failures.append("execution")
    return failures
