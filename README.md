# ⛰️ Switchback Running

**Training science companion for ultra trail.** Free and open-source.

```
⌚ Your Watch  →  📊 Intervals.icu  →  🤖 AI Agent  →  ⛰️ Switchback
  (Garmin,          (free, syncs        (the brain,       (your training
   Suunto, …)        your data)          free w/ Gemini)    companion)
```

## Quickstart

```bash
curl -fsSL switchback.run/install.sh -o /tmp/sb.sh && bash /tmp/sb.sh
```

The installer walks you through everything: installing an AI agent (free with [Gemini CLI](https://github.com/google-gemini/gemini-cli)), connecting [Intervals.icu](https://intervals.icu), and setting up your profile. Then type **`switchback`** to start.

Also works with [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Codex CLI](https://github.com/openai/codex), or [OpenClaw](https://github.com/openclaw/openclaw). More at **[switchback.run](https://switchback.run)**.

## Why This Exists

Books like [Training for the Uphill Athlete](#recommended-reading), [Training Essentials for Ultrarunners](#recommended-reading), [Science of Running](#recommended-reading), and [The Happy Runner](#recommended-reading) have distilled decades of coaching wisdom into frameworks any runner can learn from. But most of us train without a coach — and even with one, the day-to-day decisions (what to do when your HRV is down, your schedule just changed, or you're not sure if that soreness is a warning sign) fall on you.

Switchback reads your training data, applies those frameworks, and helps you make better decisions day to day.

> [!IMPORTANT]
> **Switchback is not a replacement for a human coach.** If you can work with one, you should — see [Working with a Coach](#working-with-a-coach) below. For the many runners who train alone, it offers something better than a static plan: science-based guidance that adapts to how your training is actually going.

We encourage you to [buy the books](#recommended-reading). They're excellent, they'll make you a better and more self-aware athlete, and they support authors who've dedicated their careers to helping runners like us go after their dreams.

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
> How's my training been going?

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

You can ask your companion anything about your training:

- *"Should I run or cross-train tomorrow?"*
- *"What's my vert progression been like this month?"*
- *"Is my HRV trend concerning?"*
- *"How should I fuel for a 50K?"*
- *"Build me a 12-week plan for a mountain 50K"*

### Make it yours

During setup, you choose a name and personality for your companion. By default your companion is called Virgil, inspired by Dante's faithful companion on his journey to hell and back. You can rename it after anyone who motivates you — a training partner, a runner you admire, that aid station volunteer who saved your race at mile 40. You also choose the tone, humor, and coaching style that work best for you.

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
| `/nutrition` | Post-run nutrition analysis — water, carbs, sodium, caffeine intake |
| `/why` | Explain the science behind any training decision (e.g., `/why VO2max intervals`) |
| `/check` | Deep health audit — overtraining signals, volume trends, injury risk |

## Getting Started

### What you'll need

1. **[Intervals.icu](https://intervals.icu)** — a free platform that syncs with your sports watch (Garmin, Suunto, COROS, Apple Watch, etc.). If you don't have an account yet, [create one](https://intervals.icu) and connect your watch — it takes a couple of minutes.

2. **An AI agent** — install at least one of these:

| Agent | Install command | Notes |
|-------|---------|----------|
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `npm install -g @google/gemini-cli` | **Free tier** — 1,000 requests/day, no credit card, just a Google account |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | `npm install -g @anthropic-ai/claude-code` | Recommended — full experience with slash commands |
| [Codex CLI](https://github.com/openai/codex) | `npm install -g @openai/codex` | Full experience with MCP support |

### Install

Open a terminal and run:

```bash
curl -fsSL switchback.run/install.sh -o /tmp/sb.sh && bash /tmp/sb.sh
```

That's it. The installer will:
- Download the Switchback framework and create a local repo
- Optionally create a **private GitHub repo** to back up your data (works with Claude Code Cloud too)
- Install everything and set up the `switchback` command
- Launch your companion for first-time setup — connecting Intervals.icu, building your athlete profile, and choosing a companion personality

**After that, just type `switchback` from anywhere to start a session.**

You can also open your private repo in [Claude Code Desktop](https://claude.ai/code) or [Claude Code Cloud](https://claude.ai/code) — it works everywhere.

### Updating

**Updates happen automatically.** At the start of each session, Switchback checks for new versions and updates the framework in the background. Your personal data (athlete profile, companion notes, race plans) is never touched.

### How it works

Switchback is not a traditional app — there's no UI, no server to run. The repository is a knowledge base and companion framework that your AI agent reads automatically. When you start a session, your companion greets you, pulls your latest training data from Intervals.icu, and picks up where you left off.

Your personal data (athlete profile, training zones, coaching notes, companion persona) lives in your private repo and is never shared publicly. You can launch Switchback from any machine — your data travels with you.

## Training Philosophy

Three principles guide every recommendation:

1. **Health before performance.** Long-term health always comes first. Overtraining, under-recovery, and injury risk get flagged — even if it means recommending DNS.
2. **Push hard when ready.** Within the bounds of health, your companion is direct and demanding. Easy days easy, hard days hard.
3. **Evidence over tradition.** Recommendations cite physiology and established frameworks. When experts disagree, both approaches are presented with reasoning — you choose.

### Knowledge Base

The `knowledge/` directory contains 18 reference docs covering training science topics — from aerobic base and periodization to race execution and injury prevention. Each doc synthesizes positions from Johnston, Koop, Magness, and the Roches with specific protocols, quotes, and decision frameworks. Your companion reads these before making recommendations.

## Recommended Reading

The training framework draws from these books. We recommend them for any ultrarunner who wants to understand the science behind their training:

- **Training for the Uphill Athlete** by Scott Johnston, Steve House & Kilian Jornet — [Amazon](https://www.amazon.com/Training-Uphill-Athlete-Mountain-Mountaineers/dp/1938340841) | [Evoke Endurance](https://evokeendurance.com) · [Uphill Athlete](https://uphillathlete.com)
- **Training Essentials for Ultrarunners** by Jason Koop — [Amazon](https://www.amazon.com/Training-Essentials-Ultrarunning-Compete-Ultramarathon/dp/1937715566) | [jasonkoop.com](https://jasonkoop.com) · [CTS](https://trainright.com)
- **Science of Running** by Steve Magness — [Amazon](https://www.amazon.com/Science-Running-Efficiently-Ultramarathons-Sprints/dp/0615942946) | [stevemagness.com](https://stevemagness.com)
- **The Happy Runner** by Dr. Megan Roche & David Roche — [Amazon](https://www.amazon.com/Happy-Runner-Lasting-Running-Success/dp/1492567647) | [SWAP Running](https://www.swaprunning.com)

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
