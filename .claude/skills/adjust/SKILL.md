---
description: "Modify upcoming workouts based on how you're feeling or schedule changes"
user-invocable: true
---

# /adjust — Modify Upcoming Workouts

The user will provide a reason (e.g., "feeling tired", "knee is sore", "need to swap Thursday and Friday").

0. Read relevant knowledge base files based on the reason:
   - Fatigue/soreness: `knowledge/recovery-overtraining.md`, `knowledge/injury-prevention.md`
   - Schedule change: `knowledge/periodization.md` (preserve weekly structure principles)
   - Feeling great: `knowledge/volume-progression.md` (safe ramp limits)
   - Pain/injury concern: `knowledge/injury-prevention.md` (always recommend medical consultation first)
1. Call the Intervals.icu API via curl (see `knowledge/intervals-icu-api.md`). Run independent calls as parallel Bash tool calls:
   - Wellness endpoint for the last 3 days
   - Fitness endpoint for the last 7 days
   - Events endpoint for the next 7 days
2. Analyze the user's reason against the data:
   - If fatigue/soreness: consider reducing volume/intensity, adding rest
   - If schedule change: swap or move workouts while preserving weekly structure
   - If feeling great: consider modest additions (never reckless increases)
3. Display:
   - **Current Status:** Wellness + form summary
   - **Proposed Changes:** Table showing each affected day with before → after
   - Clear explanation of why each change is being made, citing training science from the knowledge base
4. **WAIT FOR USER CONFIRMATION** — explicitly ask "Should I apply these changes?" before calling the update event, create event, or delete event endpoints
5. Only after user confirms, apply the changes and show confirmation of what was updated
