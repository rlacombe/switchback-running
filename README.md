# Virgil | Ultrarunning training companion

[Your companion](https://en.wikipedia.org/wiki/Virgil_(Dante)) through ultratrail hell and back! Virgil connects to your [Intervals.icu](https://intervals.icu) account — your training calendar, wellness data, and fitness trends — and uses [established exercise science](#recommended-reading) to help you make the most of your training and prepare for your next trail race. Built on [Claude Code](https://docs.anthropic.com/en/docs/claude-code), Virgil works through natural conversation: reviewing workouts, adjusting plans, flagging risks, and answering questions about your training.

## Why This Exists

The best coaches and athletes in ultrarunning have spent lifetimes learning what works — on hundred-mile courses, at altitude, through seasons of trial and injury and quiet persistence. Books like [Training for the Uphill Athlete](#recommended-reading), [Training Essentials for Ultrarunners](#recommended-reading), and [Science of Running](#recommended-reading) have distilled that wisdom into frameworks any runner can learn from.

But most recreational athletes don't have access to a coach — or, if they do, their time is sparse and focused on high-level goals and critical advice, rather than the minutiae of a changing schedule.

Virgil aims to bridge that gap — it reads your training data, applies established coaching frameworks, and talks you through what to do on a Tuesday morning when your HRV is down and your schedule just changed.

> [!IMPORTANT]
> **Virgil is not a replacement for a human coach.** A good coach brings experience, intuition, and a relationship that no tool can replicate. If you can work with one, you should — see [Working with a Coach](#working-with-a-coach) below.

Virgil can complement that relationship by handling the day-to-day details between sessions. For the many runners who train alone, it offers something better than a static plan: science-based guidance that adapts to how your training is actually going.

We encourage you to [buy the books](#recommended-reading). They're excellent, they'll make you a better and more self-aware athlete, and they support the authors whose work makes this project possible.

## Getting Started

### Prerequisites

- **[Intervals.icu](https://intervals.icu)** account connected to your sports watch (Garmin, Suunto, COROS, Apple Watch, etc.). Intervals.icu is free and syncs your training data automatically.
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

### How it works

Virgil is not a traditional app — there's no UI to install, no server to run. The repository contains a coaching framework (`CLAUDE.md`), a knowledge base (`knowledge/`), and a set of skills (`.claude/skills/`) that turn Claude Code into a specialized training companion. When you run `claude` inside this directory, it loads the framework automatically and becomes Virgil.

Your personal data is stored in `ATHLETE.md` (gitignored) and stays local — it won't be shared or overwritten when you pull updates.

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

### After a workout

```
> How did my tempo go?

Planned: 8 mi with 3x10min at threshold
Actual: 8.3 mi, 1:05:12, avg HR 158

Your tempo intervals averaged 7:42/mi at 165 bpm — right in your threshold
zone. Solid execution. The 0.3 mi overshoot is fine. Recovery between
intervals was clean — HR dropped to 138 within 90 seconds each time.

One flag: your pace drifted from 7:35 to 7:52 across the three intervals.
That's normal fatigue, but watch for a pattern — if drift worsens next week,
we may need to shorten the intervals or add recovery.
```

### Weekly summary

```
> /week

This week: 38.2 mi / 3,400 ft vert (planned 40 mi)
Compliance: 95% — you skipped Thursday's strides, everything else on target
Fitness trend: CTL 42 → 43 (building), TSB recovering toward race week

Next week is your last big week before taper. Saturday's long run (18 mi,
4,200 ft) is the key session. Prioritize sleep and easy effort through
Wednesday to arrive fresh.
```

### Adjusting the plan

```
> I have a work trip Tuesday through Thursday — can't run those days.

Looking at your week. You have a tempo Tuesday, easy Wednesday, and
hill repeats Thursday. Here's what I'd do:

- Move the tempo to Monday (swap with your scheduled easy day)
- Tuesday–Thursday: rest. Travel fatigue is real, don't fight it.
- Keep Friday's easy run as a shakeout
- Saturday long run stays — you'll be fresh for it

Want me to update the calendar?
```

### Understanding your training

```
> /why am I doing VO2max intervals before building my base?

Two coaches approach this differently:

Scott Johnston says base first — build your aerobic engine for months
before adding intensity. His logic: "There is no shortcut to building
the aerobic base." Most amateurs have aerobic deficiency syndrome and
need Z2 volume before anything else.

Jason Koop says VO2max first — it's the least specific workout for
ultras, so it goes furthest from race day. His logic: raising the
ceiling lifts everything below it. "Targeting VO2max has a greater
lifting effect on lactate-threshold fitness than training at aerobic
intensities has on lifting VO2max."

Your AeT/AnT spread is 12% — that suggests your aerobic base could
use work. Johnston's approach may be the better fit right now. Once
that spread drops below 10%, intensity becomes more productive.
```

### Race-day planning

```
> /race

Race: Canyons 100K — April 26, 2025
Fitness: CTL 48, TSB trending to +6 by race day (fresh)

Pacing: 14:30-15:00 overall, 18:00/mi climbs, 10:30/mi descents
Nutrition: 260 cal/hr, 60g carbs/hr, 600mg sodium/L
Mental: Associate on climbs and technical. Dissociate on fire roads.
ADAPT framework if things go sideways.

[Full aid station table, gear plan, and cutoff analysis...]
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

We are not affiliated with any of these authors or organizations. If you can work with them directly, you should — Virgil is not a substitute for a real coaching relationship.

**[Intervals.icu](https://intervals.icu)** is the training platform that powers the data layer. It's free, but please consider supporting it — it's an incredible tool built by a small team.

## Working with a Coach

The best thing you can do for your running is work with a real coach. A good coach sees things data can't capture — your form, your confidence, the way you carry stress — and builds a relationship that adapts to who you are, not just what your numbers say.

Virgil is designed to complement that relationship, not replace it. Between coaching sessions, it can handle the daily details: adjusting a workout when your schedule changes, reviewing an activity, or explaining why a training block is structured the way it is. Some coaches may find it useful in their own practice.

**If you're a coach** and you're curious about how Virgil could support your athletes, please [reach out](https://github.com/rlacombe/virgil-running/issues) — we'd love to hear from you.

**If you're looking for a coach**, the authors whose work powers this project all offer coaching services:
- [Evoke Endurance](https://evokeendurance.com) (Scott Johnston)
- [Jason Koop / CTS](https://jasonkoop.com)
- [Uphill Athlete](https://uphillathlete.com)

## Disclaimer

> [!IMPORTANT]
> This project is for informational and educational purposes only. It is not medical advice. Use it at your own risk. The author, [Intervals.icu](https://intervals.icu), and [Anthropic](https://anthropic.com) are not responsible for any injuries, health issues, or other consequences resulting from training decisions you make based on Virgil's recommendations. Always consult a qualified healthcare professional before starting or modifying a training program.

Happy trails! Stay safe and have fun out there. 🤟⛰️🏃

## License

MIT
