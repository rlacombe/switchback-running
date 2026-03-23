---
description: "Weekly summary — mileage, compliance, fitness trend, and next week preview"
user-invocable: true
---

# /week — Weekly Summary

1. Determine the current week (Monday–Sunday)
2. Fetch in parallel:
   - `get_activities` for this week
   - `get_events` for this week (planned)
   - `get_activities` for last week (for comparison)
   - `get_events` for next week (preview)
   - `get_fitness` for the last 14 days (trend)
3. Display:
   - **This Week:**
     - Total miles, duration, elevation gain
     - Number of runs completed vs planned
     - Compliance rate (% of planned workouts completed)
   - **vs Last Week:**
     - Miles change (absolute and %)
     - Flag if > 10% increase
   - **Fitness Trend (14-day):**
     - CTL, ATL, TSB current values and direction
   - **Next Week Preview:**
     - List upcoming planned workouts (name, type, distance/duration)
     - Total planned miles
4. End with a brief coaching note on the week and any adjustments to consider
