## Agent Behavior

- At the start of each coaching session, run `git pull` to load the latest framework, skills, and knowledge base
- **Startup sequence — greet while loading data in the background:**
  1. Read `athlete/profile.md` and `athlete/notes.md` (SOUL.md is already preloaded via system prompt)
  2. In the same response: output a brief, warm greeting based on the time of day (good morning / afternoon / evening) using your companion personality, AND launch a **background** subagent (`run_in_background: true`) to fetch today's briefing data (events for the next 14 days, wellness for 3 days, fitness for 7 days, athlete zones). If they haven't run `/setup` yet, greet them and suggest it instead.
  3. When the background agent completes and you're notified, deliver the `/today` briefing with the returned data.
- Always fetch live data via MCP tools — never guess or assume training data
- **Delegate all MCP calls to a subagent.** Always use a subagent via the Agent tool for MCP operations — both reads and writes. This keeps raw API output out of the main conversation. The subagent inherits MCP access automatically. Tell it exactly what data you need (or what to create/update/delete), and have it return a concise summary. For write operations, confirm the result to the athlete yourself in the main conversation based on what the subagent returns.
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
