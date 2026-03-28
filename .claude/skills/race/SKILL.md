---
description: "Race-day preparation — pacing, nutrition, aid stations, mental game plan, and taper check"
user-invocable: true
---

# /race — Race-Day Strategy

Builds a comprehensive race-day plan for the athlete's target race. The user may specify a race or default to the one in their athlete profile.

## Step 1: Read knowledge base

Read these coaching files for expert protocols:
- `knowledge/race-execution.md` — pacing, ADAPT framework, aid stations
- `knowledge/taper.md` — taper check, sharpening
- `knowledge/nutrition.md` — cal/hr, carb/hr, fluid targets, Bullseye plan
- `knowledge/heat-altitude.md` — environmental preparation
- `knowledge/mental-performance.md` — associative/dissociative strategies, crisis protocols

## Step 2: Gather data

Call the Intervals.icu API via curl (see `knowledge/intervals-icu-api.md`). Run independent calls as parallel Bash tool calls:
- Fitness endpoint for the last 21 days — CTL/ATL/TSB trend into race day
- Events endpoint for the next 14 days — remaining workouts and taper check
- Activities endpoint for the last 30 days — recent training volume and long runs
- Wellness endpoint for the last 7 days — sleep, HRV, fatigue trends

Read `athlete/profile.md` for race details (distance, elevation, cutoffs, key cutoffs) and cached zones.

## Step 3: Build the race plan

### Pacing Strategy
- Estimate finish time range based on current CTL, recent long run performances, and race profile
- Break the race into segments (e.g., by aid station) with target pace ranges
- Flag any tight cutoffs given projected pace
- Account for elevation — slower on climbs, faster on descents, with specific pace adjustments
- Reference Koop's "stay in the moment" pacing — focus on current segment, not the whole race

### Nutrition Plan
- Set cal/hr and carb/hr targets based on athlete weight and expected intensity (use `knowledge/nutrition.md`)
- Plan what to carry vs pick up at aid stations
- Fluid and sodium targets (600-800mg sodium/L)
- Gut training check — has the athlete practiced this plan in training?
- Warn about under-fueling (most ultrarunners consume 80-120 cal/hr vs 240-260 recommended)

### Aid Station Plan
- Time estimate for each aid station based on pacing
- What to do at each stop: refill, eat, gear change, crew access
- Keep it efficient — get in, get out (Koop)
- Mark crew-accessible stations and drop bag locations

### Mental Game Plan
- When to associate (climbs, technical terrain, aid stations, first 20%)
- When to dissociate (flat sections, middle stages, grinding terrain)
- ADAPT framework reminder for when things go wrong
- Personal mantras or reframing strategies from the athlete's "Why You Run"

### Taper Check
- Is TSB trending toward fresh (>0) by race day?
- Are the remaining planned workouts appropriate for taper?
- Flag if volume is still too high or if intensity should be adjusted
- Reference taper protocols from `knowledge/taper.md`

### Environmental Prep
- If race is at altitude or in heat, reference `knowledge/heat-altitude.md`
- Check if acclimatization protocols have been followed
- Flag any last-minute environmental concerns

## Step 4: Present the plan

Display as a structured race-day document:
1. **Race Overview** — name, date, distance, elevation, cutoff
2. **Fitness Status** — CTL, ATL, TSB, taper assessment
3. **Pacing Table** — segments with target pace, cumulative time, cutoff margin
4. **Nutrition Plan** — hourly targets, what to carry, what to get at aid stations
5. **Aid Station Plan** — table with station name, mile, estimated arrival, action items
6. **Mental Plan** — strategy by race phase
7. **Gear Notes** — any race-specific considerations

## Step 5: Offer to save

Ask if the athlete wants this posted as a NOTE on their race-day calendar via the create event endpoint.
