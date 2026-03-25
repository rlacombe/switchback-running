# Switchback Running

An AI-powered ultrarunning training companion. Switchback connects to your [Intervals.icu](https://intervals.icu) account — your training calendar, wellness data, and fitness trends — and uses [established exercise science](#recommended-reading) to help you train smarter and prepare for your next trail race. It works through natural conversation: reviewing workouts, adjusting plans, flagging risks, and answering questions about your training.

Switchback is agent-agnostic — it works with [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Gemini CLI](https://github.com/google-gemini/gemini-cli), and [Codex CLI](https://github.com/openai/codex). Use whichever you prefer.

## Why This Exists

Books like [Training for the Uphill Athlete](#recommended-reading), [Training Essentials for Ultrarunners](#recommended-reading), [Science of Running](#recommended-reading), and [The Happy Runner](#recommended-reading) have distilled decades of coaching wisdom into frameworks any runner can learn from. But most of us train without a coach — and even with one, the day-to-day decisions (what to do when your HRV is down, your schedule just changed, or you're not sure if that soreness is a warning sign) fall on you.

Switchback reads your training data, applies those frameworks, and helps you make better decisions day to day.

> [!IMPORTANT]
> **Switchback is not a replacement for a human coach.** If you can work with one, you should — see [Working with a Coach](#working-with-a-coach) below. For the many runners who train alone, it offers something better than a static plan: science-based guidance that adapts to how your training is actually going.

We encourage you to [buy the books](#recommended-reading). They're excellent, they'll make you a better and more self-aware athlete, and they support authors who've dedicated their careers to helping runners like us go after their dreams.

## Getting Started

### Prerequisites

- **[Intervals.icu](https://intervals.icu)** account connected to your sports watch (Garmin, Suunto, COROS, Apple Watch, etc.). Intervals.icu is free, syncs your training data automatically, and is built by a small team — please consider [becoming a Supporter](https://intervals.icu).
- **An AI coding agent** — Switchback works with any of these (install at least one):

| Agent | Install | Features |
|-------|---------|----------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | `npm install -g @anthropic-ai/claude-code` | Full experience — slash commands, session memory, MCP |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `npm install -g @anthropic-ai/gemini-cli` | Core companion + live data via MCP |
| [Codex CLI](https://github.com/openai/codex) | `npm install -g @openai/codex` | Core companion (no live data yet) |

The launcher auto-detects which agents you have installed. If you have multiple, it asks you to pick one and remembers your choice.

### Set up Switchback

```bash
git clone https://github.com/rlacombe/switchback-running.git
cd switchback-running
./switchback.sh
```

On first run, ask your companion to help you set up (or type `/setup` in Claude Code) — it will walk you through connecting your Intervals.icu account, building your athlete profile, and choosing a name and personality for your companion.

To make `switchback` available from anywhere, add an alias to your shell profile:

```bash
echo 'alias switchback="/path/to/switchback-running/switchback.sh"' >> ~/.zshrc
source ~/.zshrc
```

Then just run `switchback` from any directory.

### Updating

```bash
cd switchback-running
git pull
```

This updates the companion framework, knowledge base, and skills without touching your personal data in `athlete/`.

### How it works

Switchback is not a traditional app — there's no UI to install, no server to run. The repository contains a companion framework and knowledge base that your AI agent loads automatically. When you run `switchback`, it picks up where you left off — your companion greets you and delivers a morning briefing.

The companion framework lives in `COMPANION.md` and is generated into agent-specific instruction files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) that each agent discovers automatically.

Your personal data stays local and is never committed — this includes `athlete/` (your profile and coaching notes) and `SOUL.md` (your companion's name and personality). See `SOUL.example.md` for the default persona.

## What You Can Do

### Morning check-in

```
> What's on tap for today?

Today's workout: Easy run — 6 mi, Zone 2
Wellness: Sleep 7.2h, HRV 48 (below your 52 avg), resting HR 54
Form: TSB -4 (neutral) — CTL 42, ATL 46

You're slightly fatigued with below-average HRV. Good day for your easy run,
but keep it genuinely easy. If you feel flat in the first mile, no shame in
cutting to 5.
```

### Checking your progress

```
> /check

Looking at the last 14 days:
- Volume: 42 → 51 mi (+21%) — above the 10% ramp guideline
- Sleep: averaging 6.1h (down from 7.3h two weeks ago)
- HRV: 3-day trend declining, now 12% below your baseline
- TSB: -18 and falling

This is a yellow flag. The volume jump alone is manageable, but
combined with declining sleep and HRV, you're accumulating more
fatigue than you're absorbing. I'd recommend swapping tomorrow's
intervals for an easy run and prioritizing sleep this week. If HRV
doesn't recover by Friday, consider making this a recovery week.
```

### Race readiness

```
> Am I on track to run UTMB in 4 months?

Let me pull your data and check...

Based on 12 weeks of training history:
- Current fitness (CTL): 52 — you'll want 65-75 for UTMB
- Weekly volume: 45 mi avg — target is 55-65 mi with significant vert
- Vert: 4,200 ft/week — UTMB demands suggest building to 8,000-10,000
- Long run: longest is 3:45 — you'll need multiple 5-6h efforts

You have time, but it's tight. Here's what I'd prioritize over the
next 16 weeks...
```

### Just ask

You're not limited to slash commands. Ask anything:

- *"Should I run or cross-train tomorrow?"*
- *"What's my vert progression been like this month?"*
- *"Is my HRV trend concerning?"*
- *"What does Scott Johnston think about weighted hiking?"*
- *"Build me a 12-week plan for a mountain 50K"*

## Skills (Claude Code)

These slash commands are available in Claude Code. Other agents support the same capabilities through natural conversation — just ask.

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

## Training Philosophy

Three principles guide every recommendation:

1. **Health before performance.** Long-term health always comes first. Overtraining, under-recovery, and injury risk get flagged — even if it means recommending DNS.
2. **Push hard when ready.** Within the bounds of health, your companion is direct and demanding. Easy days easy, hard days hard.
3. **Evidence over tradition.** Recommendations cite physiology and established frameworks. When experts disagree, both approaches are presented with reasoning — you choose.

### Knowledge Base

The `knowledge/` directory contains 17 reference docs covering training science topics — from aerobic base and periodization to race execution and injury prevention. Each doc synthesizes positions from Johnston, Koop, Magness, and the Roches with specific protocols, quotes, and decision frameworks. Your companion reads these before making recommendations.

## Recommended Reading

The training framework draws from these books. We recommend them for any ultrarunner who wants to understand the science behind their training:

- **Training for the Uphill Athlete** by Scott Johnston, Steve House & Kilian Jornet — [Amazon](https://www.amazon.com/Training-Uphill-Athlete-Mountain-Mountaineers/dp/1938340841) | Coaching: [Evoke Endurance](https://evokeendurance.com) (Johnston) · [Uphill Athlete](https://uphillathlete.com)
- **Training Essentials for Ultrarunners** by Jason Koop — [Amazon](https://www.amazon.com/Training-Essentials-Ultrarunning-Compete-Ultramarathon/dp/1937715566) | Coaching: [Jason Koop](https://jasonkoop.com) · [CTS](https://trainright.com)
- **Science of Running** by Steve Magness — [Amazon](https://www.amazon.com/Science-Running-Efficiently-Ultramarathons-Sprints/dp/0615942946) | [stevemagness.com](https://stevemagness.com) · [scienceofrunning.com](https://scienceofrunning.com)
- **The Happy Runner** by Dr. Megan Roche & David Roche — [Amazon](https://www.amazon.com/Happy-Runner-Lasting-Running-Success/dp/1492567647) | [swaprunning.com](https://www.swaprunning.com) · [Some Work All Play Podcast](https://podcasts.apple.com/us/podcast/some-work-all-play/id1463503118)

This project is not affiliated with any of these authors or organizations. If you can work with them directly, you should — Switchback is not a substitute for a real coaching relationship.

## Working with a Coach

The best thing you can do for your running is work with a real coach. A good coach sees things data can't capture — your form, your confidence, the way you carry stress — and builds a relationship that adapts to who you are, not just what your numbers say.

Switchback is designed to complement that relationship, not replace it. Between coaching sessions, it can handle the daily details: adjusting a workout when your schedule changes, reviewing an activity, or explaining why a training block is structured the way it is. Some coaches may find it useful in their own practice.

**If you're a coach** and you're curious about how Switchback could support your athletes, please feel free to adopt it! [Let me know](https://github.com/rlacombe/switchback-running/issues) if you find it helpful.

**If you're looking for a coach**, the authors of the [recommended books](#recommended-reading) above all offer coaching services:
- [Evoke Endurance](https://evokeendurance.com) (Scott Johnston)
- [Jason Koop / CTS](https://jasonkoop.com)
- [Uphill Athlete](https://uphillathlete.com)
- [Steve Magness](https://stevemagness.com)
- [SWAP Running](https://www.swaprunning.com) (Dr. Megan Roche & David Roche)

## Disclaimer

> [!IMPORTANT]
> This project is for informational and educational purposes only. It is not medical advice. Use it at your own risk. The author, [Intervals.icu](https://intervals.icu), and the AI providers are not responsible for any injuries, health issues, or other consequences resulting from training decisions you make based on your companion's recommendations. Always consult a qualified healthcare professional before starting or modifying a training program.

Happy trails! Stay safe and have fun out there. 🤟⛰️🏃

## License

MIT
