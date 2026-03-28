---
description: "Post a coaching note to your Intervals.icu calendar with today's briefing"
user-invocable: true
---

# /briefing — Post Coaching Note to Calendar

Creates a NOTE event on the Intervals.icu calendar with a coaching summary for today. The note appears alongside your planned workout — visible in Intervals.icu and any synced calendar (Google, Apple, Outlook).

## Step 1: Read knowledge base

Read `knowledge/recovery-overtraining.md` and `knowledge/workout-types.md` to inform the coaching note with relevant training science.

## Step 2: Gather data

Call the Intervals.icu API via curl (see `knowledge/intervals-icu-api.md`). Run independent calls as parallel Bash tool calls:
- Events endpoint for today (oldest=today, newest=today) — planned workouts
- Wellness endpoint for today (oldest=today, newest=today) — sleep, HRV, RHR, fatigue, mood
- Fitness endpoint for the last 7 days — CTL/ATL/TSB trend
- Zones are cached in `athlete/profile.md` — skip the athlete endpoint unless zones are missing

## Step 3: Write the coaching note

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

## Step 4: Post to calendar

Call the create event endpoint with:
- `category`: `"NOTE"`
- `start_date_local`: today's date in `YYYY-MM-DD` format
- `name`: `"Coach's Notes"`
- `description`: the coaching note from Step 2

## Step 5: Confirm

Tell the user the note has been posted. Mention that it will show up in Intervals.icu and any synced calendars.
