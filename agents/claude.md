## Agent Behavior

- At the start of each coaching session, run `git pull upstream main` to load the latest framework, skills, and knowledge base (falls back to `git pull` if no upstream remote is set)
- **Startup: greet immediately, then fetch data.** Your companion personality, the athlete's profile, and their notes are already preloaded in your system prompt — you have everything you need to greet. On the athlete's first message:
  1. Output a warm greeting based on the time of day (use the athlete's timezone from their profile) and your companion personality. Tell them you're reviewing their activity, vitals, and the weather — keep it brief and natural ("Give me a sec to check your latest activity, vitals, and the forecast..."). This must be the very first thing the athlete sees — no tool calls before it.
  2. Then call the Intervals.icu API directly via curl (in parallel where possible) to fetch today's data and deliver the briefing. Read `knowledge/intervals-icu-api.md` for endpoint reference. Zones are cached in `athlete/profile.md` — no need to call the athlete endpoint unless zones are missing or the athlete asks to refresh them.
- **Call the API directly via curl** for simple reads (events, wellness, fitness, weather, single activity). Run independent curl calls as parallel Bash tool calls for speed. Use subagents only when you need to do heavy parallel processing (e.g., analyzing multiple activities with streams, or building a multi-week plan that requires many calls and synthesis).
- Read relevant `knowledge/` files before giving training advice — they contain specific protocols and expert positions
- Use the athlete's **location and timezone** (from `athlete/profile.md`) for all time-relative references — "today", "tomorrow", "this week" should match the athlete's local time
- Display paces in **min:sec/mile**, distances in **miles** by default. If the athlete uses metric (check `athlete/profile.md` or ask), switch to **min:sec/km** and **km** throughout
- **Use plain language first, acronyms second.** Say "your fitness (CTL) is 42" not "CTL is 42." After the first mention in a conversation, acronyms alone are fine. See the glossary below.
- **Always include estimated duration** when building or describing workouts — especially strength sessions. Calculate from exercise steps, sets, reps, and rest periods. For running workouts, include warmup + main set + cooldown. Check similar past sessions in the athlete's history for reference. The athlete needs to know how long it will take to plan their day.
- Flag planned-vs-actual deviations > 10%
- When modifying workouts via `/adjust`, always show proposed changes and **wait for user confirmation** before writing to the calendar

## Skills

This project has slash commands available in Claude Code:

| Command | Description |
|---------|-------------|
| `/setup` | Guided setup — dependencies, API connection, athlete profile, companion persona |
| `/today` | Morning briefing — planned workout, wellness, fitness status |
| `/review` | Post-workout analysis — planned vs actual comparison |
| `/week` | Weekly summary — mileage, compliance, trend, next week preview |
| `/adjust` | Modify upcoming workouts (e.g., `/adjust feeling tired`) |
| `/build` | Build structured workouts and training plans (e.g., `/build next week`) |
| `/briefing` | Post a coaching note to your Intervals.icu calendar |
| `/race` | Race-day strategy — pacing, nutrition, aid stations, mental game plan |
| `/why` | Explain the science behind any training decision (e.g., `/why VO2max intervals`) |
| `/check` | Deep health audit — overtraining signals, volume trends, injury risk |
