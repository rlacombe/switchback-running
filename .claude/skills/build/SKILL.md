---
description: "Build structured workouts and training plans, then add them to your Intervals.icu calendar"
user-invocable: true
---

# /build — Build & Schedule Workouts

The user will describe what they need (e.g., "plan next week", "build a 4-week block", "create a long run for Saturday", "I need a tempo workout tomorrow").

## Step 1: Read knowledge base

Read these coaching files to inform workout design:
- `knowledge/periodization.md` — phase structure, block design, intensity ordering
- `knowledge/workout-types.md` — workout definitions, RPE targets, work:rest ratios
- `knowledge/volume-progression.md` — safe ramp rates, recovery week placement
- `knowledge/long-runs.md` — if building long runs or multi-day plans
- `knowledge/muscular-endurance.md` — if building ME sessions
- `knowledge/strength-training.md` — if scheduling strength work alongside running

## Step 2: Gather context

Call the Intervals.icu API via curl (see `knowledge/intervals-icu-api.md`). Run independent calls as parallel Bash tool calls:
- Fitness endpoint for the last 14 days — current CTL/ATL/TSB trend
- Activities endpoint for the last 14 days — recent training load and volume
- Events endpoint for the date range the user is asking about — existing planned workouts
- Wellness endpoint for the last 7 days — sleep, HRV, fatigue trends

## Step 3: Design the plan

Based on the user's request and the data:
- Respect current fitness level and volume progression (no >10% weekly increase)
- Follow periodization principles (easy/hard alternation, step-back weeks every 3–4 weeks)
- Use the athlete's actual zones from `athlete/profile.md` for intensity prescription
- If planning multiple weeks, include a step-back week at ~70% volume every 3–4 weeks
- Consider the race date if one is set — work backward from taper
- Check for existing events in the date range and work around them (or note conflicts)

## Step 4: Write workouts using description syntax

Build each workout's `description` field using the Intervals.icu workout text format. The API parses this to generate structured workout steps.

### Syntax reference

**Sections:**
- `Warmup` / `Cooldown` — special section names
- `Main Set 3x` — repeating section (number before `x`)
- `3x` on its own line before steps also works

**Duration/distance:**
- Time: `1h`, `10m`, `30s`, `1m30`, `5'`, `30"`
- Distance: `2km`, `1mi`, `400m`

**Intensity (running):**
- Pace percentage: `78-82%`, `90%`
- LTHR percentage: `95% LTHR`
- Zones: `Z2`, `Z4` (pace zones), `Z2 HR`, `Z4 HR` (HR zones)
- Ramps: `10m ramp 50%-75%`
- Cadence target: `10m 75% 90rpm`

**Example workout:**
```
Warmup
- 15m ramp 60-75%

Main Set 3x
- 8m 88-92%
- 3m 60%

Cooldown
- 10m easy
```

## Step 5: Present the plan

Display each day's workout clearly:
- **Date** — Workout name
  - Type (Run, Ride, etc.), planned duration, planned distance
  - Workout description (the structured text)
  - Brief coaching rationale for the session

If planning multiple weeks, show a week-by-week summary table first, then the daily detail.

## Step 6: Wait for confirmation

Explicitly ask: **"Should I add these workouts to your calendar?"**

Do NOT call the create event endpoint until the user confirms. If they want changes, revise and show again.

## Step 7: Create events

After confirmation, for each workout call the create event endpoint with:
- `category`: `"WORKOUT"`
- `start_date_local`: the date in `YYYY-MM-DD` format
- `name`: workout name
- `description`: the structured workout text from Step 3
- `type`: sport type (e.g., `"Run"`, `"Ride"`)
- `moving_time`: planned duration in seconds (if specified)
- `distance`: planned distance in meters (if specified)

Show confirmation of all created events with their IDs.
