---
description: "Weekly summary — mileage, compliance, fitness trend, and next week preview"
user-invocable: true
---

# /week — Weekly Summary

1. Determine the current week (Monday–Sunday). Read `knowledge/volume-progression.md` for safe ramp rates and recovery week guidelines, and `knowledge/periodization.md` for training phase context.
2. Call the Intervals.icu API via curl (see `knowledge/intervals-icu-api.md`). Run independent calls as parallel Bash tool calls:
   - Activities endpoint for this week
   - Events endpoint for this week (planned)
   - Activities endpoint for last week (for comparison)
   - Events endpoint for next week (preview)
   - Fitness endpoint for the last 14 days (trend)
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
4. End with a brief coaching note on the week, grounded in training science:
   - If volume increased >10%: flag per `knowledge/volume-progression.md`
   - If compliance is low: consider if it signals fatigue per `knowledge/recovery-overtraining.md`
   - Preview next week in context of periodization principles from `knowledge/periodization.md`
