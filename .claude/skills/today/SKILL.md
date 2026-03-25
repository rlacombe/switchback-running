---
description: "Morning briefing — today's planned workout, wellness, and fitness status"
user-invocable: true
---

# /today — Morning Briefing

1. Get today's date. Read `knowledge/recovery-overtraining.md` for overtraining warning signs and `knowledge/workout-types.md` for workout execution guidance.
2. Fetch in parallel:
   - `get_events` for the next 14 days (oldest=today, newest=today+13) — today's workout plus the full training block ahead for context
   - `get_wellness` for the last 3 days (oldest=today-2, newest=today) — trend context, not just a snapshot
   - `get_fitness` for the last 7 days to show trend
   - `get_athlete` for zone context (HR, pace, power zones)
   - `get_weather` using the athlete's lat/lon from their profile — current conditions and forecast
3. Display:
   - **Today's Workout:** Name, type, planned distance/duration. If the workout has structured steps, show target zones/paces using the athlete's actual zone values. If rest day, say so.
   - **This Week / Next Week:** Brief overview of the 2-week plan ahead — session names, days, types. Highlight the training block context (build week? recovery week? race week?) so today's workout makes sense in the bigger picture.
   - **Wellness:** Sleep, HRV, resting HR, fatigue, mood (whatever is available)
   - **Form Status:** Current TSB with label (fresh/neutral/tired/fatigued)
   - **CTL/ATL:** Current values and 7-day trend direction
   - **Weather:** Current conditions and today's forecast (temp, feels-like, wind, precipitation, UV). Flag heat/cold/rain concerns that affect the workout — suggest timing adjustments, hydration, or gear.
4. End with a one-line recommendation grounded in the knowledge base (e.g., reference workout purpose from `knowledge/workout-types.md`, or flag recovery concerns per `knowledge/recovery-overtraining.md`)
5. Flag any injury risk signals (volume spike, sustained negative TSB, poor sleep) using criteria from `knowledge/injury-prevention.md`
