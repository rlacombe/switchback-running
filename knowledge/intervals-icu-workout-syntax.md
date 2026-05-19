# Intervals.icu Workout Description Syntax

This file is the **source of truth** for writing the `description` field passed to `create_event` / `update_event`. Read it before building any workout. The Intervals.icu parser is strict, and a single malformed line will silently break Garmin export — the watch will then refuse to load the workout or skip steps.

The platform's own docs are scattered across forum threads; sources at the bottom of this file. The rules below are the consolidated, tested set.

---

## The five non-negotiable rules

1. **`m` means minutes. Never meters.** Use `mtr` for meters, `km` for kilometers, `mi` for miles. `400m` parses as "400 minutes." This single mistake is the most common cause of broken workouts.
2. **One intensity target per step.** HR and Pace **cannot** be combined on the same step — the parser drops one or fails. Pick whichever target matches the intent of that step. (Confirmed by Sam, the platform author, in the forum thread.)
3. **Every step must have a quantitative target.** Never write `- 5m easy`. "Easy" is not a target. Use `Z1 HR`, `Z1 Pace`, `60% Pace`, `65% HR`, etc. — always a zone, a percentage, or an absolute value.
4. **Every step starts with `- ` (dash + space).** Section headers (`Warmup`, `Main Set`, `Cooldown`) are the only lines without a leading dash.
5. **Every interval has a paired recovery.** Strides, reps, intervals — each fast step needs a recovery step inside the same repeat block. The Garmin watch needs both halves to lap correctly.

If any of these are violated, the workout will display in Intervals.icu's web view but break on the watch.

---

## Quick reference card

```
[Section Header] [Nx (optional)]
- [duration OR distance] [ONE target] [optional cadence] [optional cue]
```

| Element | Examples |
|---|---|
| Duration | `1h`, `45m`, `30s`, `1m30s`, `5'`, `30"` |
| Distance | `1km`, `5km`, `1mi`, `4.5mi`, `400mtr` |
| Pace zone | `Z1 Pace`, `Z2 Pace`, `Z3-Z4 Pace` |
| HR zone | `Z1 HR`, `Z2 HR`, `Z2-Z3 HR` |
| Pace % | `60% Pace`, `78-82% Pace`, `90% Pace` (of threshold pace) |
| HR % | `70% HR`, `75-80% HR` (of max HR) |
| LTHR % | `90-95% LTHR`, `95% LTHR` (of threshold HR) |
| Absolute pace | `5:00/km Pace`, `8:30/mi Pace` |
| Ramp | `10m ramp 60%-75% Pace`, `15m ramp Z1-Z2 HR` |
| Cadence | append `90rpm` after target |
| Repeat | `Strides 4x` (in header) or `4x` (own line) |
| Cue text | text before duration: `- Surge 30s 95% Pace` |

---

## Sections and structure

A workout is a sequence of **sections**, separated by blank lines. Sections contain **steps** (lines starting with `- `).

**Standard section names:** `Warmup`, `Main Set`, `Cooldown`. You can also use custom names like `Strides`, `Hill Reps`, `Build`, `Recovery`.

**Repeats:** put `Nx` either in the section header or on its own line before the steps to repeat:

```
Main Set 4x
- 5m Z3 Pace
- 2m Z1 HR
```

is equivalent to:

```
Main Set
4x
- 5m Z3 Pace
- 2m Z1 HR
```

**Blank lines are load-bearing.** Leave one empty line before and after every repeat block. Sections also need to be separated by blank lines.

**Nested repeats are not supported.** If you need nested structure (e.g., 3 sets of (4 × 30s/30s)), flatten it into a single repeat (`12x`) or split into multiple sections.

---

## Duration and distance

**Time units:** `h`, `m`, `s`. Combine freely: `1h2m30s`, `1m30s`, `2h`. Short forms: `5'` = 5 minutes, `30"` = 30 seconds, `1'30"` = 1m30s.

**Distance units:**

| Unit | Meaning |
|---|---|
| `mtr` | meters |
| `km` | kilometers |
| `mi` | miles |
| `m` | **MINUTES** — never meters |

`400mtr` = 400 meters. `400m` = 400 minutes (6h40m). The parser will happily build a 6-hour 40-minute step and the watch will struggle.

**Pick time or distance per step, not both.** `- 1km Z2 Pace` or `- 5m Z2 HR`, not both.

---

## Intensity targets for running

Every step needs **one** of these, chosen based on what the step is for.

### Pace targets

- **Pace zones:** `Z1 Pace`, `Z2 Pace`, `Z3 Pace`, `Z4 Pace`, `Z5 Pace`. Ranges allowed: `Z2-Z3 Pace`.
- **Pace as % of threshold pace:** `78-82% Pace`, `60% Pace`, `92% Pace`. The athlete's threshold pace is set in their Intervals.icu profile (cached in `athlete/profile.md`). 100% = threshold pace.
- **Absolute pace:** `5:00/km Pace`, `8:30/mi Pace`, `7:00-6:30/mi Pace`. Match the unit to the athlete's preferred system.

### Heart rate targets

- **HR zones:** `Z1 HR`, `Z2 HR`, `Z3 HR`, `Z4 HR`, `Z5 HR`. Ranges allowed: `Z2-Z3 HR`.
- **HR as % of max HR:** `70% HR`, `75-80% HR`. 100% = max HR.
- **HR as % of LTHR:** `90-95% LTHR`, `95% LTHR`. 100% = lactate threshold HR.

### Picking HR vs Pace per step

Since you can only have one target per step, pick the one that matches the intent:

| Step type | Anchor to | Why |
|---|---|---|
| Warmup, cooldown | **HR** (`Z1 HR` or `Z1-Z2 HR`) | Lets pace settle naturally; protects against cold-start. |
| Long run, easy run, recovery run | **HR** (`Z1 HR` or `Z2 HR`) | Prevents HR drift in heat/fatigue from corrupting aerobic intent. |
| Aerobic threshold / Z2 work | **HR** (`Z2 HR`) | Aerobic adaptation is HR-driven; pace will drift with conditions. |
| Tempo, steady state | **Pace** (`Z3 Pace` or `85-90% Pace`) | Pace is the training stimulus; HR lags by 60-90s and lies in heat. |
| Threshold intervals (CrisisIntervals, cruise) | **Pace** (`Z4 Pace` or `92-100% Pace`) | Anchor to exact intensity; HR is too laggy for 3-15 min reps. |
| VO2 max, hard intervals | **Pace** (`Z5 Pace` or `100-110% Pace`) | HR can't catch up; pace targets the energy system. |
| Strides, hill sprints | **Pace** (`92%+ Pace`) + cadence | Neuromuscular; HR is irrelevant on a 20s effort. |
| Recovery jog between intervals | **HR** (`Z1 HR` or under 70% HR) | The point is HR drop, not pace. |

**Why this works:** the athlete's pace zones and HR zones in Intervals.icu are calibrated to the same physiological intensities. A step prescribed at `Z3 Pace` will land roughly in `Z3 HR` anyway — you're just choosing which one the watch enforces as the alert.

### Garmin export and "every second accounted for"

Intervals.icu pushes workouts to Garmin Connect via the calendar sync. On Garmin watches, each step gets **one** target type (HR range, pace range, or open). The watch alerts when you fall outside the range.

This is exactly why one-target-per-step is the rule, not a guideline. If you write `- 30m Z1 HR Z1 Pace`, the parser drops one and Garmin gets whichever survives — unpredictable. Pick one.

To satisfy "every second accounted for with HR and pace":
- Every step gets one of HR or Pace as its primary, hard target (what the watch enforces).
- The other metric should naturally track because the zones are calibrated to the same intensity.
- Never use `easy`, `steady`, `moderate`, or other prose. Always a number or zone.

---

## Strides — the canonical pattern

Strides are short (15-30s) accelerations at near-max pace with full recovery between. They're a neuromuscular session, not a cardiovascular one.

**Wrong** (the user's broken example):
```
4x20s strides 92% (0w)
```
Problems: no recovery step, repeat syntax broken, `(0w)` is invalid for running (watts is cycling-only), no cadence cue.

**Right:**
```
Strides 4x
- 20s 95% Pace 95rpm
- 40s Z1 HR
```

- `Strides 4x` is the section header with the repeat count.
- The `20s` stride is anchored to **pace** (HR can't catch up in 20s).
- `95rpm` enforces fast turnover — the whole point of strides.
- The `40s Z1 HR` is the recovery jog, anchored to HR (let it drop).
- Recovery should be 2-3× the stride length for true neuromuscular work.

**Variation with explicit pace:**
```
Strides 6x
- 20s 4:30/mi Pace 95rpm
- 60s Z1 HR
```

**Hill sprints variation:**
```
Hill Sprints 6x
- Sprint uphill 15s Z5 Pace 90-95rpm
- Walk down 75s Z1 HR
```
Note the cue text "Sprint uphill" before the duration — it shows on the watch screen as a prompt.

---

## Ramps

Use `ramp` (case-insensitive) for gradual intensity changes. The watch will linearly interpolate the target across the step.

```
- 15m ramp 60%-75% Pace
- 10m ramp Z1-Z2 HR
- 5m ramp 50-90% Pace 90rpm
```

Useful for warmups, progressive long runs, and finishing surges.

---

## Cadence

Append `Nrpm` after the intensity target. Optional but recommended for:
- Strides and hill sprints (`90-95rpm` — enforce neuromuscular intent).
- Easy runs where the athlete is working on cadence cleanup (`88-92rpm`).
- Form drills.

Examples: `- 10m Z2 Pace 88rpm`, `- 20s 95% Pace 95rpm`, `- 5m Z3 Pace 86-90rpm`.

---

## Cue text (step prompts)

Text before the duration becomes the prompt that displays on the watch when the step starts.

```
- Easy aerobic 30m Z2 HR
- Surge to threshold 5m Z4 Pace
- Walk recovery 60s Z1 HR
```

For **timed prompts within a single step** (rare, but useful for long ramps):

```
- 10m ramp 50-90% Pace    30^Halfway through warmup    300^Last 5 minutes, building <!>
```

Format: `[time in seconds]^[prompt]` repeated as needed, ending with `<!>` before the step parameters. The `<!>` separator is required.

---

## Markdown for notes

Standard Markdown is ignored by the parser, so you can layer commentary without breaking the workout:

```
**Goal:** Aerobic base + neuromuscular wake-up.

Warmup
- 5m Z1 HR

Main Set
- 30m Z2 HR

Strides 4x
- 20s 95% Pace 95rpm
- 40s Z1 HR

Cooldown
- 5m Z1 HR

---

*Sunset 8:14pm — bring a headlamp if running late.*
```

Headers (`#`, `##`, `###`), bold, italic, links, and tables all work. Use this for the rationale block, safety reminders, and post-run notes — don't bury commentary inside step lines.

---

## Worked example: fixing a broken workout

Here is the broken workout the agent recently produced, and the corrected version, line by line. Use this as a regression test before writing any workout.

### Broken

```
Easy + neuromuscular wake-up.

Warmup

5m easy
Main Set

30m Z1 HR (108-135bpm) Z1 Pace (9:31-11:54 for 2.8mi)
4x20s strides 92% (0w)
Cooldown

5m easy
```

**Problems:**

1. `5m easy` — no leading dash; "easy" is not a valid target.
2. `30m Z1 HR (108-135bpm) Z1 Pace (9:31-11:54 for 2.8mi)` — combines HR and Pace on one step (parser drops one); parenthetical text `(108-135bpm)` and `(9:31-11:54 for 2.8mi)` is not parsed and clutters the watch display.
3. `4x20s strides 92% (0w)` — `4x` belongs on its own line as a section header or standalone repeat marker; `(0w)` is cycling-only (watts) and meaningless for running; no recovery step between strides; no cadence cue; "92%" alone is ambiguous (HR? Pace? LTHR?).
4. Blank lines between section header and first step break the section grouping.

### Corrected

```
**Goal:** Easy + neuromuscular wake-up.

Warmup
- 5m Z1 HR

Main Set
- 30m Z2 HR

Strides 4x
- 20s 95% Pace 95rpm
- 40s Z1 HR

Cooldown
- 5m Z1 HR
```

**Why each step is anchored where it is:**

- Warmup/cooldown → HR. Lets the body settle into and out of effort.
- Main set 30m → HR (Z2 for true aerobic). The original prescription was Z1, which is recovery — for an easy aerobic run the standard is Z2. Anchoring to HR means the pace will be whatever it needs to be for the athlete to stay aerobic (correct for an easy day, especially in heat).
- Strides 20s → Pace at 95% with 95rpm. Neuromuscular intent: enforce both speed and turnover. HR is irrelevant on a 20-second effort.
- Recovery between strides 40s → HR Z1. The goal of recovery is HR drop; let pace fall where it falls.

Total time: 5 + 30 + (4 × 1m) + 5 = **44 minutes**. Always state estimated duration when presenting the workout.

---

## Reference templates

Copy these as starting points. All have been validated against the parser rules.

### Easy aerobic run + strides

```
Warmup
- 5m Z1 HR

Main Set
- 40m Z2 HR

Strides 5x
- 20s 95% Pace 95rpm
- 40s Z1 HR

Cooldown
- 5m Z1 HR
```

### Tempo run

```
Warmup
- 15m ramp Z1-Z2 HR

Main Set
- 25m Z3 Pace

Cooldown
- 10m Z1 HR
```

### Threshold intervals (cruise)

```
Warmup
- 15m ramp 60-75% Pace

Main Set 4x
- 6m 95-100% Pace
- 2m Z1 HR

Cooldown
- 10m Z1 HR
```

### VO2 max

```
Warmup
- 15m ramp 60-75% Pace

Build
- 4x
- 30s 95% Pace 90rpm
- 30s Z1 HR

Main Set 5x
- 3m 105-110% Pace
- 2m Z1 HR

Cooldown
- 10m Z1 HR
```

### Long run with finish surge

```
Warmup
- 10m Z1 HR

Main Set
- 2h Z2 HR

Finish
- 10m ramp Z2-Z3 Pace

Cooldown
- 5m Z1 HR
```

### Hill repeats

```
Warmup
- 15m Z1-Z2 HR

Hill Reps 6x
- Climb hard 90s Z4 Pace
- Jog down 3m Z1 HR

Cooldown
- 10m Z1 HR
```

### Back-to-back long (Saturday of a B2B)

```
Warmup
- 10m Z1 HR

Main Set
- 2h30m Z2 HR

Cooldown
- 5m Z1 HR

---

**Notes:** Time-on-feet focus. Eat 60-80g carbs/hr. Carry electrolytes — temps forecast 75°F.
```

---

## Validation checklist

Before calling `create_event`, run the description through this checklist:

- [ ] Every step starts with `- `.
- [ ] No step combines HR and Pace targets.
- [ ] No step uses prose like "easy", "steady", "moderate" instead of a target.
- [ ] No bare `m` is being used for meters (use `mtr`, `km`, or `mi`).
- [ ] Every fast interval has a paired recovery step inside the same repeat block.
- [ ] Strides have a cadence cue (`90-95rpm`).
- [ ] No `(parenthetical)` clutter inside step lines.
- [ ] Repeats use `Nx` either as a section header suffix (`Main Set 4x`) or on their own line.
- [ ] Blank lines separate sections and repeat blocks.
- [ ] No nested repeats.
- [ ] No `(0w)`, `200w`, or other power targets on Run-type workouts (unless the athlete has a Stryd or equivalent run power meter — check profile first).
- [ ] Estimated duration matches sum of step durations.

When in doubt, dry-run the description against the **Worked example** above.

---

## Sources

- [Workout Builder Syntax Quick Guide — Intervals.icu Forum](https://forum.intervals.icu/t/workout-builder-syntax-quick-guide/123701)
- [Workout builder — Intervals.icu Forum (main thread)](https://forum.intervals.icu/t/workout-builder/1163)
- [Intervals.icu Workout Format — ZonePace](https://zonepace.cc/intervals-workout-format)
- [Intervals.icu workout markdown format rules — Forum](https://forum.intervals.icu/t/intervals-icu-workout-markdown-format-rules/115629)
- [Syntax of workout specification — Forum](https://forum.intervals.icu/t/syntax-of-workout-specification/109320)
- [Skill doc for creating workouts using intervals.icu plain text format (bsima)](https://gist.github.com/bsima/e02048ce45cecb603fceb90ef6e50f73)
- [Runna → Intervals.icu workout converter skill (gesteves)](https://gist.github.com/gesteves/a7b80222eb0bd7df1480e4fbb8be3741)
