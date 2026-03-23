---
description: "Post-workout analysis — compare planned vs actual for most recent activity"
user-invocable: true
---

# /review — Post-Workout Analysis

1. Get today's date
2. Fetch in parallel:
   - `get_activities` for the last 3 days (to find the most recent)
   - `get_events` for the last 3 days (to find matching planned workout)
3. Identify the most recent activity and fetch its details with `get_activity` (with intervals)
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
5. Flag any planned-vs-actual deviations > 10%
6. One-line coaching note on the workout execution
