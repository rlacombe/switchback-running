# Virgil | Ultrarunning training companion

[Your companion](https://en.wikipedia.org/wiki/Virgil_(Dante)) through ultratrail hell and back! Virgil connects to your [Intervals.icu](https://intervals.icu) account — your training calendar, wellness data, and fitness trends — and uses [established exercise science](#recommended-reading) to help you make the most of your training and prepare for your next trail race. Built on [Claude Code](https://docs.anthropic.com/en/docs/claude-code), Virgil works through natural conversation: reviewing workouts, adjusting plans, flagging risks, and answering questions about your training.

## Why This Exists

Books like [Training for the Uphill Athlete](#recommended-reading), [Training Essentials for Ultrarunners](#recommended-reading), and [Science of Running](#recommended-reading) have distilled decades of coaching wisdom into frameworks any runner can learn from. But most of us train without a coach — and even with one, the day-to-day decisions (what to do when your HRV is down, your schedule just changed, or you're not sure if that soreness is a warning sign) fall on you.

Virgil reads your training data, applies those frameworks, and talks you through it.

> [!IMPORTANT]
> **Virgil is not a replacement for a human coach.** If you can work with one, you should — see [Working with a Coach](#working-with-a-coach) below. For the many runners who train alone, Virgil offers something better than a static plan: science-based guidance that adapts to how your training is actually going.

We encourage you to [buy the books](#recommended-reading). They're excellent, they'll make you a better and more self-aware athlete, and they support authors who've dedicated their careers to helping runners like us go after their dreams.

## Getting Started

### Prerequisites

- **[Intervals.icu](https://intervals.icu)** account connected to your sports watch (Garmin, Suunto, COROS, Apple Watch, etc.). Intervals.icu is free, syncs your training data automatically, and is built by a small team — please consider [supporting them](https://intervals.icu).
- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** — a command-line interface for Claude. You'll need an Anthropic account with a Claude Pro or Max subscription.

### Install Claude Code

If you don't have Claude Code yet:

```bash
npm install -g @anthropic-ai/claude-code
```

This gives you the `claude` command. On first run, it will walk you through signing in to your Anthropic account. See the [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code) for details.

### Set up Virgil

```bash
git clone https://github.com/rlacombe/virgil-running.git
cd virgil-running
claude
```

That's it — you're now talking to Virgil. Type `/setup` and it will walk you through connecting your Intervals.icu account and building your athlete profile.

### Updating

```bash
cd virgil-running
git pull
```

This updates the coaching framework, knowledge base, and skills without touching your personal data in `athlete/`.

### How it works

Virgil is not a traditional app — there's no UI to install, no server to run. The repository contains a coaching framework and knowledge base that Claude Code loads automatically. When you run `claude` inside this directory, it becomes Virgil.

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

### Just ask

You're not limited to slash commands. Ask anything:

- *"Am I ready for a 50K in October?"*
- *"Should I run or cross-train tomorrow?"*
- *"What's my vert progression been like this month?"*
- *"Is my HRV trend concerning?"*
- *"What does Scott Johnston think about weighted hiking?"*

## Skills

| Command | Description |
|---------|-------------|
| `/setup` | Guided setup — dependencies, API connection, athlete profile |
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
2. **Push hard when ready.** Within the bounds of health, Virgil is direct and demanding. Easy days easy, hard days hard.
3. **Evidence over tradition.** Recommendations cite physiology and established frameworks. When experts disagree, both approaches are presented with reasoning — you choose.

### Knowledge Base

The `knowledge/` directory contains 16 reference docs covering training science topics — from aerobic base and periodization to race execution and injury prevention. Each doc synthesizes positions from Johnston, Koop, and Magness with specific protocols, quotes, and decision frameworks. Virgil reads these before making recommendations.

## Recommended Reading

The training framework draws from these books. We recommend them for any ultrarunner who wants to understand the science behind their training:

- **Training for the Uphill Athlete** by Scott Johnston, Steve House & Kilian Jornet — [Amazon](https://www.amazon.com/Training-Uphill-Athlete-Mountain-Mountaineers/dp/1938340841) | Coaching: [Evoke Endurance](https://evokeendurance.com) (Johnston) · [Uphill Athlete](https://uphillathlete.com)
- **Training Essentials for Ultrarunners** by Jason Koop — [Amazon](https://www.amazon.com/Training-Essentials-Ultrarunning-Compete-Ultramarathon/dp/1937715566) | Coaching: [Jason Koop](https://jasonkoop.com) · [CTS](https://trainright.com)
- **Science of Running** by Steve Magness — [Amazon](https://www.amazon.com/Science-Running-Efficiently-Ultramarathons-Sprints/dp/0615942946) | [stevemagness.com](https://stevemagness.com) · [scienceofrunning.com](https://scienceofrunning.com)

This project is not affiliated with any of these authors or organizations. If you can work with them directly, you should — Virgil is not a substitute for a real coaching relationship.

## Working with a Coach

The best thing you can do for your running is work with a real coach. A good coach sees things data can't capture — your form, your confidence, the way you carry stress — and builds a relationship that adapts to who you are, not just what your numbers say.

Virgil is designed to complement that relationship, not replace it. Between coaching sessions, it can handle the daily details: adjusting a workout when your schedule changes, reviewing an activity, or explaining why a training block is structured the way it is. Some coaches may find it useful in their own practice.

**If you're a coach** and you're curious about how Virgil could support your athletes, please feel free to adapt it in your daily practice! [Reach out](https://github.com/rlacombe/virgil-running/issues), I'd love to help.

**If you're looking for a coach**, the authors of the [recommended books](#recommended-reading) above all offer coaching services:
- [Evoke Endurance](https://evokeendurance.com) (Scott Johnston)
- [Jason Koop / CTS](https://jasonkoop.com)
- [Uphill Athlete](https://uphillathlete.com)

## Disclaimer

> [!IMPORTANT]
> This project is for informational and educational purposes only. It is not medical advice. Use it at your own risk. The author, [Intervals.icu](https://intervals.icu), and [Anthropic](https://anthropic.com) are not responsible for any injuries, health issues, or other consequences resulting from training decisions you make based on Virgil's recommendations. Always consult a qualified healthcare professional before starting or modifying a training program.

Happy trails! Stay safe and have fun out there. 🤟⛰️🏃

## License

MIT
