---
description: "Post-workout analysis — compare planned vs actual for most recent activity"
user-invocable: true
---

# /review — Post-Workout Analysis

1. Get today's date. Read `knowledge/workout-types.md` to understand the purpose and targets of the workout type being reviewed. For long runs, also read `knowledge/long-runs.md`. For intervals, also read `knowledge/aerobic-base.md`.
2. Call the Intervals.icu API via curl (see `knowledge/intervals-icu-api.md`). Run independent calls as parallel Bash tool calls:
   - Activities endpoint for the last 3 days (to find the most recent)
   - Events endpoint for the last 3 days (to find matching planned workout)
3. Identify the most recent activity and fetch its details from the activity endpoint (with intervals)
4. Display:
   - **Workout Summary:** Name, type, date
   - **Planned vs Actual table:**
     | Metric | Planned | Actual | Diff |
     |--------|---------|--------|------|
     | Distance (mi) | | | |
     | Duration | | | |
     | Avg Pace (min/mi) | | | |
     | Elevation (ft) | | | |
   - **Heart Rate:** Avg, max, time in zones (if available)
   - **Cadence:** Avg (if available)
   - **Intervals/Laps:** Key splits if interval data exists
   - **Training Load:** load/TSS from the activity
5. If the activity warrants deeper analysis (tempo runs, intervals, long runs over 2 hours), use the activity streams endpoint to examine:
   - **Pace drift:** Compare first-half vs second-half average pace from `velocity_smooth`
   - **HR decoupling:** Compare pace:HR ratio in first half vs second half (decoupling > 5% suggests aerobic ceiling was reached)
   - **Elevation profile:** Correlate altitude changes with pace/HR to assess climbing efficiency
   Only fetch streams when the analysis would add value — not for every easy run.
6. Flag any planned-vs-actual deviations > 10%
7. One-line coaching note on the workout execution, grounded in the training science from the knowledge base (e.g., reference HR decoupling thresholds from `knowledge/aerobic-base.md`, or pacing principles from `knowledge/long-runs.md`)
