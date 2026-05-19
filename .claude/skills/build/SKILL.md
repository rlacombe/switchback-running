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

Fetch data using MCP tools (call them directly, in parallel where possible):
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

Build each workout's `description` field using the Intervals.icu workout text format. The API parses this to generate structured workout steps that sync to Garmin.

**Read `knowledge/intervals-icu-workout-syntax.md` before writing any workout.** It is the source of truth for the parser rules, with worked examples and a validation checklist. The short version:

- Every step starts with `- ` (dash + space).
- Every step has exactly **one** quantitative target: `Z2 HR`, `Z3 Pace`, `90-95% LTHR`, `78-82% Pace`, etc. Never `easy`, never both HR + Pace.
- `m` means minutes. Use `mtr` for meters, `km`, or `mi`.
- Every fast interval has a paired recovery step inside the same repeat block.
- Repeats use `Nx` (e.g. `Strides 4x` as a section header).

**Canonical example:**
```
Warmup
- 5m Z1 HR

Main Set
- 30m Z2 HR

Strides 4x
- 20s 95% Pace 95rpm
- 40s Z1 HR

Cooldown
- 5m Z1 HR
```

Run every workout through the validation checklist in `knowledge/intervals-icu-workout-syntax.md` before calling `create_event`.

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
