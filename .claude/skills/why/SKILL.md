---
description: "Explain the science behind a training decision — what the experts say and why"
user-invocable: true
---

# /why — Training Science Explained

The athlete asks about any training concept, workout choice, or decision. Read the relevant knowledge base files, present expert positions, and connect the science to the athlete's situation.

Examples:
- `/why VO2max intervals`
- `/why am I running so slow on easy days`
- `/why weighted hiking for muscular endurance`
- `/why reverse periodization`
- `/why should I taper two weeks out`

## Step 1: Identify the topic

Map the athlete's question to the relevant knowledge base file(s) in `knowledge/`:
- aerobic-base.md, volume-progression.md, workout-types.md, muscular-endurance.md
- strength-training.md, periodization.md, long-runs.md, taper.md
- race-execution.md, recovery-overtraining.md, heat-altitude.md, mental-performance.md
- nutrition.md, downhill-training.md, injury-prevention.md, age-gender.md

Read the relevant file(s). If the question spans multiple topics, read all of them.

## Step 2: Gather athlete context (if relevant)

If the question relates to the athlete's current training, call the Intervals.icu API via curl (see `knowledge/intervals-icu-api.md`) to personalize the explanation:
- Zones are cached in `athlete/profile.md` — use those to reference actual numbers
- Fitness endpoint — their current CTL/ATL/TSB
- Activities or events endpoint — recent training context

Skip this step if the question is purely conceptual (e.g., "what is ADS?").

## Step 3: Explain

Structure the response as:

1. **The concept** — What it is and why it matters, in plain language
2. **What the experts say** — Present each expert's position with their reasoning:
   - Scott Johnston's view and logic
   - Jason Koop's view and logic
   - Steve Magness's view and logic
3. **Where they agree** — Common ground
4. **Where they disagree** — The tension, presented fairly with both sides
5. **What this means for you** — Connect to the athlete's actual data, goals, and current training phase. If approaches conflict, explain which might fit their situation and why — then let them choose.

## Guidelines

- Lead with the science, not opinions
- Use the athlete's actual zones and data when available — "your AeT is at 145bpm" is better than "your aerobic threshold"
- When experts disagree, present both sides honestly. Don't pick a winner unless the athlete's data clearly favors one approach
- Keep it conversational, not like a textbook
- Include key quotes from the experts — they carry weight
- If the athlete's question reveals a misconception, address it directly but respectfully
