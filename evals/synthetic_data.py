"""Deterministic synthetic athlete dossiers for UltraBench.

No data in this module is derived from a real athlete, wearable export, or
private Switchback repository. Each scenario receives a coherent, synthetic
longitudinal record so target agents must retrieve and interpret tool results.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any


REFERENCE_DATE = date(2026, 4, 20)
MILES_TO_METERS = 1609.344


def dossier_for(scenario: dict[str, Any]) -> dict[str, Any]:
    """Build one deterministic synthetic dossier from a public scenario seed."""
    match = re.search(r"\d+", scenario["id"])
    number = int(match.group()) if match else 1
    mcp = scenario["mcp_data"]
    reference_date = date.fromisoformat(mcp.get("reference_date", REFERENCE_DATE.isoformat()))
    athlete_profile = mcp.get("athlete_profile", {})
    profile = {
        "id": f"synthetic-{number:02d}",
        "name": f"Synthetic Athlete {number:02d}",
        "sex": athlete_profile.get("gender", "X"),
        "birthday": f"{2026 - athlete_profile.get('age', 38)}-06-15",
        "city": "Summit Valley",
        "country": "US",
        "timezone": "America/Los_Angeles",
        "latitude": 37.4419,
        "longitude": -122.1430,
        "max_hr": 184,
        "resting_hr": 52,
        "lthr": 164,
        "threshold_pace": 285,
        "sportSettings": [{"type": "Run", "run_ftp": 285}],
        "hr_zones": [120, 138, 151, 164, 176],
        "pace_zones": [390, 350, 320, 290, 260],
    } | athlete_profile

    fitness_now = {"ctl": 64, "atl": 68, "rampRate": 1.5} | mcp.get("intervals_fitness", {})
    if fitness_now.get("ctl") is None:
        fitness_now["ctl"] = None
    if fitness_now.get("atl") is None:
        fitness_now["atl"] = None
    if "ramp_rate" in fitness_now and "rampRate" not in mcp.get("intervals_fitness", {}):
        fitness_now["rampRate"] = fitness_now["ramp_rate"]
    if fitness_now.get("tsb") is None and fitness_now.get("ctl") is not None and fitness_now.get("atl") is not None:
        fitness_now["tsb"] = fitness_now["ctl"] - fitness_now["atl"]

    wellness_now = {
        "id": reference_date.isoformat(),
        "hrv": 55,
        "restingHR": 52,
        "sleepSecs": 27000,
        "fatigue": 2,
        "soreness": 1,
        "mood": 3,
    } | mcp.get("intervals_wellness", {})
    recent_miles = mcp.get("strava_recent_totals", {}).get("past_7_days_miles")
    four_week_average_miles = mcp.get("strava_recent_totals", {}).get("4_week_avg_miles")
    recent_elevation_ft = mcp.get("strava_recent_totals", {}).get("past_7_days_elevation_gain_ft")
    activity = _current_activity(number, mcp, recent_miles, reference_date)
    activities = _merge_activities(
        _activities(number, fitness_now["ctl"], activity, recent_miles, four_week_average_miles, reference_date),
        mcp.get("intervals_activities", []),
    )
    if recent_elevation_ft and not mcp.get("intervals_activities"):
        total_elevation_m = recent_elevation_ft * 0.3048
        activities[-3]["total_elevation_gain"] = round(total_elevation_m * 0.20)
        activities[-2]["total_elevation_gain"] = round(total_elevation_m * 0.30)
        activities[-1]["total_elevation_gain"] = round(total_elevation_m * 0.50)
    activity = activities[-1]
    weather = _weather(mcp.get("environment", {}))
    events = _events(number, mcp.get("intervals_events", []), reference_date)
    notes = mcp.get("intervals_wellness", {}).get("notes", "")
    activity_memory = _activity_memory(activities, profile["timezone"], reference_date)
    private_context = mcp.get("private_context")
    profile_details = "".join(
        f"- {key.replace('_', ' ').capitalize()}: "
        f"{', '.join(value) if isinstance(value, list) else value}\n"
        for key, value in athlete_profile.items()
        if key != "gender"
    )
    profile_markdown = (
        f"# Synthetic Athlete {number:02d}\n\n"
        "- Goal: complete a mountainous ultratrail event safely\n"
        f"- Timezone: {profile['timezone']}\n"
        f"- Location: {profile['latitude']}, {profile['longitude']}\n"
        f"- LTHR: {profile['lthr']} bpm\n"
        f"- Current fitness: CTL {fitness_now['ctl']}, ATL {fitness_now['atl']}, TSB {fitness_now['tsb']}\n"
        f"- Training phase: {mcp.get('training_phase', 'Not specified')}\n"
        f"{profile_details}"
    )
    persistent_memory = (
        "# Persistent notes\n\n"
        f"- Synthetic athlete dossier {number:02d}; no real athlete data.\n"
        "- Season goal: complete a mountainous ultratrail event safely.\n"
        f"- Current reported context: {notes or 'No unusual symptoms recorded.'}\n"
    )

    return {
        "provenance": "synthetic",
        "reference_date": reference_date.isoformat(),
        "current_context": {
            "local_datetime": f"{reference_date.isoformat()}T07:00:00-07:00",
            "local_date": reference_date.isoformat(),
            "timezone": profile["timezone"],
            "latitude": profile["latitude"],
            "longitude": profile["longitude"],
        },
        "athlete": profile,
        "fitness": mcp.get("fitness_history") or _fitness_history(fitness_now, reference_date),
        "wellness": mcp.get("wellness_history") or _wellness_history(wellness_now, scenario["category"], reference_date),
        "activities": activities,
        "activity": activity,
        "activity_streams": mcp.get("intervals_activity_streams") or _streams(activity),
        "events": events,
        "weather": weather,
        "gear": mcp.get("strava_gear", {"id": f"synthetic-shoe-{number}", "name": "Synthetic Trail Shoe", "distance_metres": 310000}),
        "strava_activities": _strava_activities(number, mcp, activity, reference_date),
        "strava_comments": mcp.get("strava_comments", []),
        "activity_memory": activity_memory,
        "memory": persistent_memory,
        "profile_markdown": profile_markdown,
        "activity_memory_index": "\n".join(
            f"- {path}: {note.splitlines()[11] if len(note.splitlines()) > 11 else 'Synthetic activity note'}"
            for path, note in activity_memory.items()
        ),
        "private_files": {
            "athlete/profile.md": profile_markdown,
            "athlete/notes.md": persistent_memory,
            "SOUL.md": "# Sol\n\nA concise, data-first endurance companion.\n",
            **activity_memory,
            **({"athlete/docs/scenario-context.md": private_context} if private_context else {}),
            **mcp.get("private_files", {}),
        },
    }


def _current_activity(number: int, mcp: dict[str, Any], recent_miles: float | None, reference_date: date) -> dict[str, Any]:
    distance = round((recent_miles * 0.5 if recent_miles else 16.5) * MILES_TO_METERS)
    defaults = {
        "id": f"synthetic-activity-{number}",
        "name": "Synthetic Trail Long Run",
        "type": "Run",
        "sport_type": "TrailRun",
        "start_date_local": (reference_date - timedelta(days=1)).isoformat(),
        "distance": distance,
        "moving_time": 10200,
        "avg_hr": 146,
        "total_elevation_gain": 920,
        "icu_training_load": 148,
        "description": "Synthetic activity fixture.",
        "source": "synthetic",
    }
    return defaults | mcp.get("intervals_activity", {})


def _activities(seed: int, ctl: float, current: dict[str, Any], recent_miles: float | None, four_week_average_miles: float | None, reference_date: date) -> list[dict[str, Any]]:
    """Return 15 activities, including a coherent last-seven-day history."""
    stress_ctl = ctl if ctl is not None else 64
    offsets = [56, 52, 48, 44, 40, 36, 32, 28, 24, 20, 16, 12, 6, 3, 1]
    rows: list[dict[str, Any]] = []
    for index, offset in enumerate(offsets):
        stress = round(max(35, stress_ctl * 0.95 + ((seed + offset) % 9) - 4), 1)
        activity_type = "Ride" if index == 7 and seed % 4 == 0 else "Run"
        rows.append({
            "id": f"synthetic-activity-{seed}-{offset}",
            "name": "Synthetic aerobic session",
            "type": activity_type,
            "start_date_local": (reference_date - timedelta(days=offset)).isoformat(),
            "distance": 22000 + (seed % 5) * 1800,
            "moving_time": 7200 if activity_type == "Ride" else 9000,
            "avg_hr": 139 + seed % 6,
            "total_elevation_gain": 180 if activity_type == "Ride" else 850 + (seed % 4) * 120,
            "icu_training_load": stress,
            "source": "synthetic",
        })

    if recent_miles:
        total_meters = recent_miles * MILES_TO_METERS
        rows[-3]["distance"] = round(total_meters * 0.20)
        rows[-2]["distance"] = round(total_meters * 0.30)
        if "distance" not in current or current["distance"] is None:
            current["distance"] = round(total_meters * 0.50)
    if recent_miles is not None and four_week_average_miles is not None:
        prior_rows = [row for row, offset in zip(rows, offsets) if 7 < offset <= 28]
        prior_target = max(0.0, four_week_average_miles * 4 - recent_miles) * MILES_TO_METERS
        for row in prior_rows:
            row["distance"] = round(prior_target / len(prior_rows))
    rows[-1] = current
    return rows


def _merge_activities(generated: list[dict[str, Any]], supplied: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Overlay scenario-specific Intervals records while retaining 15-row history."""
    if not supplied:
        return generated
    supplied_ids = {str(row["id"]) for row in supplied}
    supplied_dates = {str(row.get("start_date_local", ""))[:10] for row in supplied if row.get("start_date_local")}
    merged = [
        row for row in generated
        if str(row["id"]) not in supplied_ids
        and str(row.get("start_date_local", ""))[:10] not in supplied_dates
    ]
    merged.extend(dict(row) for row in supplied)
    merged.sort(key=lambda row: str(row.get("start_date_local", "")))
    return merged[-15:]


def _strava_activities(number: int, mcp: dict[str, Any], current: dict[str, Any], reference_date: date) -> list[dict[str, Any]]:
    """Normalize scenario Strava records into callable synthetic activities."""
    supplied = mcp.get("strava_activities")
    if supplied is None:
        supplied = [mcp.get("strava_last_activity", current)]
    rows = []
    for index, row in enumerate(supplied):
        normalized = {
            "id": f"synthetic-strava-{number}-{index}",
            "start_date_local": (reference_date - timedelta(days=1)).isoformat(),
            "name": "Synthetic Strava Activity",
        } | dict(row)
        normalized["gear"] = mcp.get("strava_gear", {}).copy()
        rows.append(normalized)
    return rows


def _fitness_history(current: dict[str, Any], reference_date: date) -> list[dict[str, Any]]:
    if current.get("ctl") is None or current.get("atl") is None:
        return [{"id": reference_date.isoformat(), "ctl": None, "atl": None, "tsb": None, "rampRate": None}]
    rows = []
    for offset in range(14, -1, -1):
        ctl = round(current["ctl"] - offset * 0.18, 1)
        atl = round(current["atl"] - offset * 0.12, 1)
        rows.append({
            "id": (reference_date - timedelta(days=offset)).isoformat(),
            "ctl": ctl,
            "atl": atl,
            "tsb": round(ctl - atl, 1),
            "rampRate": current.get("rampRate", current.get("ramp_rate", 1.5)),
        })
    return rows


def _wellness_history(current: dict[str, Any], category: str, reference_date: date) -> list[dict[str, Any]]:
    rows = []
    worsening = category in {"female_athlete_health", "acute_strain_injury", "safety_guardrails", "clinical_medical_safety", "pharmacological_metabolic", "environmental_physiology"}
    noise = [0, 1, -1, 0, 2, -1, 1, 0, -2, 1, 0, -1, 1, 0, 0]
    for offset in range(14, -1, -1):
        days_from_start = 14 - offset
        hrv = current.get("hrv")
        resting_hr = current.get("restingHR")
        fatigue = current.get("fatigue", 2)
        soreness = current.get("soreness", 1)
        if worsening and hrv is not None:
            hrv = round(hrv + min(10, offset * 0.7) + noise[days_from_start] * 0.3, 1)
            resting_hr = round(resting_hr - min(5, offset * 0.35) - noise[days_from_start] * 0.2, 1)
            fatigue = max(1, fatigue - (offset // 5))
            soreness = max(1, soreness - (offset // 6))
        else:
            hrv = None if hrv is None else round(hrv + noise[days_from_start] * 0.5, 1)
            resting_hr = None if resting_hr is None else round(resting_hr - noise[days_from_start] * 0.15, 1)
        row = {
            "id": (reference_date - timedelta(days=offset)).isoformat(),
            "hrv": hrv,
            "restingHR": resting_hr,
            "sleepSecs": current.get("sleepSecs", 27000) + (days_from_start % 4 - 1) * 900,
            "fatigue": fatigue,
            "soreness": soreness,
            "mood": current.get("mood", 3),
        }
        if offset == 0:
            row.update(current)
        rows.append(row)
    return rows


def _events(number: int, events: list[dict[str, Any]], reference_date: date) -> list[dict[str, Any]]:
    if events:
        normalized = []
        for index, event in enumerate(events):
            value = dict(event)
            if "start_date_local" not in value:
                days = int(value.pop("days_to_event", 42))
                value["start_date_local"] = (reference_date + timedelta(days=days)).isoformat()
            value.setdefault("id", f"synthetic-event-{number}-{index}")
            normalized.append(value)
        return normalized
    return [{
        "id": f"synthetic-event-{number}",
        "name": "Synthetic Mountain Ultra",
        "category": "RACE",
        "start_date_local": (reference_date + timedelta(days=42)).isoformat(),
    }]


def _streams(activity: dict[str, Any]) -> dict[str, list[float]]:
    return {
        "heartrate": [132, 138, activity.get("avg_hr", 145), 149],
        "altitude": [350, 475, 620, 710],
        "velocity_smooth": [2.7, 2.6, 2.4, 2.2],
    }


def _activity_memory(activities: list[dict[str, Any]], timezone: str, reference_date: date) -> dict[str, str]:
    """Render the same compact, source-linked Markdown shape used by Switchback.

    These fixtures intentionally exclude routes and raw streams; those remain
    available only through the synthetic provider tool, matching the production
    activity-memory retention policy.
    """
    memories = {}
    for activity in activities:
        local_date = str(activity["start_date_local"])[:10]
        source_id = str(activity["id"])
        path = f"athlete/activities/{local_date[:4]}/{local_date[5:7]}/{local_date}--synthetic--{source_id}.md"
        distance_miles = activity.get("distance", 0) / MILES_TO_METERS
        duration = int(activity.get("moving_time", 0))
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        pace_seconds = duration / max(distance_miles, 0.1)
        pace_minutes, pace_remainder = divmod(round(pace_seconds), 60)
        elevation_feet = activity.get("total_elevation_gain", 0) * 3.28084
        tags = "[trail, aerobic]" if activity.get("type") == "Run" else "[cross-training, aerobic]"
        assessment = "Completed aerobic work; retain only as a synthetic historical reference."
        if activity.get("description"):
            description = activity["description"]
        else:
            description = "Synthetic fixture; no athlete-authored narrative."
        memories[path] = f'''---
id: "synthetic:{source_id}"
provider: synthetic
source_activity_id: "{source_id}"
start_date_local: "{activity['start_date_local']}"
timezone: {timezone}
activity_type: {activity.get('sport_type', activity.get('type', 'Run'))}
tags: {tags}
retrieved_at: "{reference_date.isoformat()}T12:00:00-07:00"
streams_available: true
route_retained: false
---

# {activity.get('name', 'Synthetic activity')}

## Snapshot

| Metric | Value |
|---|---|
| Distance | {distance_miles:.1f} mi |
| Moving time | {hours}:{minutes:02d}:{seconds:02d} |
| Elevation gain | {elevation_feet:,.0f} ft |
| Average pace | {pace_minutes}:{pace_remainder:02d} /mi |
| Average heart rate | {activity.get('avg_hr', 'Unavailable')} bpm |
| Training load | {activity.get('icu_training_load', 'Unavailable')} TSS |

## Athlete-reported note

{description}

## Plan and execution

Synthetic historical activity retained for longitudinal context; no claimed plan or deviation is fabricated.

## Companion assessment

{assessment}

## Data retention

This note retains a compact synthetic summary and source identifier. It intentionally excludes GPX, GPS coordinates, and raw second-by-second streams; retrieve those transiently through the synthetic provider tool only when a specific analysis requires them.
'''
    return memories


def _weather(environment: dict[str, Any]) -> dict[str, Any]:
    temperature = environment.get("temp_f", 58)
    return {
        "current": {
            "temperature_2m": temperature,
            "apparent_temperature": temperature,
            "wind_speed_10m": environment.get("wind_mph", 8),
            "weather_code": environment.get("weather_code", 1),
            "relative_humidity_2m": environment.get("humidity_percent"),
            "conditions": environment.get("conditions"),
            "elevation_ft": environment.get("elevation_ft"),
        },
        "daily": {
            "temperature_2m_max": [temperature],
            "temperature_2m_min": [temperature - 15],
            "precipitation_probability_max": [environment.get("precipitation_probability", 5)],
        },
    }
