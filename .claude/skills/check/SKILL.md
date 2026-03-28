---
description: "Deep health and readiness audit — overtraining signals, volume trends, injury risk"
user-invocable: true
---

# /check — Health & Readiness Audit

Goes deeper than `/today`'s daily snapshot. Analyzes multi-week trends to flag overtraining risk, volume ramp issues, recovery adequacy, and injury warning signs.

## Step 1: Read knowledge base

Read these coaching files for detection criteria and thresholds:
- `knowledge/recovery-overtraining.md` — FOR/NFOR/OTS stages, detection methods, warning signs
- `knowledge/injury-prevention.md` — red flags, volume ramp limits, return protocols
- `knowledge/volume-progression.md` — 10% rule, build:recovery ratios, CTL ramp rates
- `knowledge/age-gender.md` — age/gender-specific recovery considerations

## Step 2: Gather data

Call the Intervals.icu API via curl (see `knowledge/intervals-icu-api.md`). Run independent calls as parallel Bash tool calls:
- Wellness endpoint for the last 30 days — sleep, HRV, resting HR, fatigue, mood trends
- Fitness endpoint for the last 30 days — CTL/ATL/TSB progression
- Activities endpoint for the last 30 days — actual volume, frequency, intensity
- Events endpoint for the last 30 days — planned vs completed (compliance)
Read `athlete/profile.md` for injury history, age, known weaknesses, and cached zones.

## Step 3: Analyze

### Volume Trends
- Weekly mileage progression over 4 weeks — flag increases >10%/week
- CTL ramp rate — flag if >5 points/week sustained
- Are recovery weeks happening? Check for step-back every 3-4 weeks
- Build:recovery ratio — is it 3:1 or 2:1? Should it be?

### Wellness Trends
- HRV trend: declining over 7+ days = concern
- Resting HR trend: rising over 7+ days = concern
- Sleep: average over 30 days, trend direction, any sustained <7h periods
- Fatigue/mood: worsening trend over 7+ days

### Overtraining Risk Assessment
Using the FOR → NFOR → OTS framework from `knowledge/recovery-overtraining.md`:
- Steve House's 3 warning signs: slow warmup, poor sleep, suspected injury (2+ = immediate rest)
- Performance decline: are recent workouts showing pace/HR regression?
- Compliance: missed workouts may indicate fatigue-driven avoidance

### Injury Risk
- Volume spike detection (acute:chronic ratio)
- Any reported soreness or pain patterns
- Shoe mileage if tracked

## Step 4: Display

Present findings as a health report card:

**Overall Status:** Green / Yellow / Red

**Volume & Load**
- Weekly progression (table: last 4 weeks)
- CTL trend and ramp rate
- Recovery week compliance

**Wellness Trends**
- HRV: current vs 30-day average, trend direction
- Resting HR: current vs 30-day average, trend direction
- Sleep: average, trend, any flags
- Fatigue/mood: trend

**Risk Flags**
- List any specific concerns with severity (watch / caution / stop)
- For each flag, cite the reasoning from the knowledge base

**Recommendations**
- Specific actions based on findings (e.g., "Take a recovery week", "Reduce volume by 20% this week", "Monitor HRV for 3 more days before deciding")
- If red flags: recommend consulting a medical professional for any pain or injury concerns
- Reference the relevant expert guidance
