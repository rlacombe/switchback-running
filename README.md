# Intervals | Ultratrail Coaching Agent

An AI ultrarunning coach that lives in your terminal. It connects to your [Intervals.icu](https://intervals.icu) account — your training calendar, wellness data, and fitness trends — and uses [established exercise science](#recommended-reading) to help you make the most of your training and prepare for your next trail race. Built on [Claude Code](https://docs.anthropic.com/en/docs/claude-code), it coaches you through natural conversation: reviewing workouts, adjusting plans, flagging risks, and answering questions about your training.

## Why This Exists

The best coaches and athletes in ultrarunning have spent lifetimes learning what works — on hundred-mile courses, at altitude, through seasons of trial and injury and quiet persistence. Books like [Training for the Uphill Athlete](#recommended-reading), [Training Essentials for Ultrarunners](#recommended-reading), and [Science of Running](#recommended-reading) have distilled that wisdom into frameworks any runner can learn from.

But most recreational athletes don't have access to a coach — or, if they do, their time is sparse and focused on high-level goals and critical advice, rather than the minutiae of a changing schedule.

This project aims to bridge that gap: a tool that reads your training data, applies established coaching frameworks, and talks you through what to do on a Tuesday morning when your HRV is down and your schedule just changed.

> [!IMPORTANT]
> **This is not a replacement for a human coach.** A good coach brings experience, intuition, and a relationship that no AI can replicate. If you can work with one, you should.

This tool can complement that relationship by handling the day-to-day details between sessions. For the many runners who train alone, it offers something better than a static plan: science-based guidance that adapts to how your training is actually going.

We encourage you to [buy the books](#recommended-reading). They're excellent, they'll make you a better and more self-aware athlete, and they support the authors whose work makes this project possible.

## Getting Started

You need a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) account and an [Intervals.icu](https://intervals.icu) account connected to your sports watch or training device (e.g. Garmin, Suunto, COROS, Apple Watch). Then:

```bash
git clone https://github.com/rlacombe/intervals-coaching-agent.git
cd intervals-coaching-agent
claude
```

Type `/setup` and the coach will walk you through everything — connecting your Intervals.icu account and building your athlete profile.

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

### Just talking to your coach

You're not limited to slash commands. Ask anything:

- *"Am I ready for a 50K in October?"*
- *"Break down my race day nutrition plan"*
- *"Should I run or cross-train tomorrow?"*
- *"What's my vert progression been like this month?"*
- *"I have a work trip next week — adjust my schedule"*

## Skills

| Command | Description |
|---------|-------------|
| `/setup` | Guided setup — dependencies, API connection, athlete profile |
| `/today` | Morning briefing — planned workout, wellness, fitness status |
| `/review` | Post-workout analysis — planned vs actual comparison |
| `/week` | Weekly summary — mileage, compliance, trend, next week preview |
| `/adjust` | Modify upcoming workouts (e.g., `/adjust feeling tired`) |

## Coaching Philosophy

The coach follows three principles:

1. **Health before performance.** Long-term health always comes first. The coach will flag overtraining, under-recovery, and injury risk — even if it means recommending DNS.
2. **Push hard when ready.** Within the bounds of health, the coach is direct and demanding. Easy days easy, hard days hard.
3. **Evidence over tradition.** Recommendations cite physiology and established frameworks.

## Recommended Reading

The coaching framework draws from these books. We recommend them for any ultrarunner who wants to understand the science behind their training:

- **Training for the Uphill Athlete** by Scott Johnston, Steve House & Kilian Jornet — [Amazon](https://www.amazon.com/Training-Uphill-Athlete-Mountain-Mountaineers/dp/1938340841) | [uphillathlete.com](https://uphillathlete.com)
- **Training Essentials for Ultrarunners** by Jason Koop — [Amazon](https://www.amazon.com/Training-Essentials-Ultrarunning-Compete-Ultramarathon/dp/1937715566) | [trainright.com](https://trainright.com)
- **Science of Running** by Steve Magness — [Amazon](https://www.amazon.com/Science-Running-Efficiently-Ultramarathons-Sprints/dp/0615942946) | [scienceofrunning.com](https://scienceofrunning.com)

We are not affiliated with any of these authors or organizations.

**[Intervals.icu](https://intervals.icu)** is the training platform that powers the data layer. It's free, but please consider supporting it — it's an incredible tool built by a small team.

## Disclaimer

> [!IMPORTANT]
> This project is for informational and educational purposes only. It is not medical advice. Use it at your own risk. The author, [Intervals.icu](https://intervals.icu), and [Anthropic](https://anthropic.com) are not responsible for any injuries, health issues, or other consequences resulting from training decisions you make based on this tool. Always consult a qualified healthcare professional before starting or modifying a training program.

Happy trails! Stay safe and have fun out there. 🤟⛰️🏃

## License

MIT
