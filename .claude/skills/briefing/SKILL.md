---
description: "Post a coaching note to your Intervals.icu calendar with today's briefing"
user-invocable: true
---

# /briefing — Post Coaching Note to Calendar

Creates a NOTE event on the Intervals.icu calendar with a coaching summary for today. The note appears alongside your planned workout — visible in Intervals.icu and any synced calendar (Google, Apple, Outlook).

## Step 1: Gather data

Fetch in parallel:
- `get_events` for today (oldest=today, newest=today) — planned workouts
- `get_wellness` for today (oldest=today, newest=today) — sleep, HRV, RHR, fatigue, mood
- `get_fitness` for the last 7 days — CTL/ATL/TSB trend
- `get_athlete` — zones for context

## Step 2: Write the coaching note

Compose a concise, actionable coaching note. Keep it short — this will be read on a calendar card, not a terminal. Structure:

```
[Wellness] Sleep Xh | HRV XX (vs avg XX) | RHR XX
[Form] TSB X (fresh/neutral/tired/fatigued) — CTL XX, ATL XX
[Today] {workout name}: {brief coaching cue for execution}
{one-line recommendation or flag if anything needs attention}
```

Guidelines:
- If wellness data suggests caution (poor sleep, low HRV, high fatigue), say so directly
- If the workout has structured intervals, include the key intensity targets using the athlete's actual zones
- If it's a rest day, note it and mention what's coming next
- Keep the entire note under ~150 words — it needs to fit a calendar card
- No greetings, no sign-offs — just the coaching content

## Step 3: Post to calendar

Call `create_event` with:
- `category`: `"NOTE"`
- `start_date_local`: today's date in `YYYY-MM-DD` format
- `name`: `"Coach's Notes"`
- `description`: the coaching note from Step 2

## Step 4: Confirm

Tell the user the note has been posted. Mention that it will show up in Intervals.icu and any synced calendars.
