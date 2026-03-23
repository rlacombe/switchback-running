---
description: "Morning briefing — today's planned workout, wellness, and fitness status"
user-invocable: true
---

# /today — Morning Briefing

1. Get today's date
2. Fetch in parallel:
   - `get_events` for today (oldest=today, newest=today)
   - `get_wellness` for today (oldest=today, newest=today)
   - `get_fitness` for the last 7 days to show trend
3. Display:
   - **Today's Workout:** Name, type, planned distance/duration. If rest day, say so.
   - **Wellness:** Sleep, HRV, resting HR, fatigue, mood (whatever is available)
   - **Form Status:** Current TSB with label (fresh/neutral/tired/fatigued)
   - **CTL/ATL:** Current values and 7-day trend direction
4. End with a one-line recommendation (e.g., "Good day for your long run" or "Consider cutting intensity — TSB is low and sleep was poor")
5. Flag any injury risk signals (volume spike, sustained negative TSB, poor sleep)
