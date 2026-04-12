---
description: "Guided setup — connects Intervals.icu and builds your athlete profile"
user-invocable: true
---

# /setup — Guided Setup

Walk the user through setup step by step. Be friendly and patient — assume they are not technical. Confirm each step before moving to the next. Do not dump a wall of instructions; go one step at a time.

## Step 1: Connect to Intervals.icu

Check if `INTERVALS_API_KEY` and `INTERVALS_ATHLETE_ID` are set in the environment (either from a `.env` file or shell env).

**If both are set:** Tell the user they're already configured and skip to Step 3.

**If either is missing:** Walk them through it:

1. Ask if they have an Intervals.icu account. If not, tell them to create one at https://intervals.icu (it's free) and connect their watch/device, then come back.
2. Guide them to create an API key:
   - Go to https://intervals.icu/settings
   - Scroll to the **Developer** section
   - Click **Create API Key**
   - Copy the key
3. Guide them to find their Athlete ID:
   - It's in their Intervals.icu profile URL — looks like `i123456`
   - Or visible on the Settings page
4. Ask the user to paste their API key and Athlete ID.
5. Write a `.env` file in the project root:
   ```
   INTERVALS_API_KEY=their_key
   INTERVALS_ATHLETE_ID=their_id
   ```
   This file is already gitignored — their credentials stay local.
6. Tell the user to **restart Claude Code** (or open a new terminal) for the environment variables to take effect.

## Step 2: Verify the connection

Make a test call using the `get_wellness` MCP tool for today. If it succeeds, tell the user the connection is working. If it fails, help them debug (wrong key, wrong athlete ID, etc.).

## Step 3: Build the athlete profile

Tell the user you're going to ask a few questions to personalize the coaching. Ask them conversationally — one or two questions at a time, not a long form. Create the `athlete/` directory if it doesn't exist, then use their answers to fill in `athlete/profile.md` (copied from `athlete/profile.example.md` if it doesn't exist yet). Also create an empty `athlete/notes.md` for the companion's persistent observations.

Questions to cover (adapt based on what they've already answered):
- What's your name?
- How old are you?
- Height, weight, body type?
- How many miles per week are you currently running?
- What's your running experience? (years, races, distances)
- Any injuries or weaknesses to watch for?
- What does your typical training week look like? (days available, trail access, cross-training)
- What race are you training for? (name, date, distance, elevation, cutoffs)
- Why do you run? What motivates you?
- Any long-term goals beyond this race?

After gathering answers, write their data to `athlete/profile.md` (filling in the template from `athlete/profile.example.md`). Show them what you wrote and ask if anything needs adjusting.

Then fetch zones from Intervals.icu using the athlete endpoint and populate the **Zones** section of `athlete/profile.md` with the athlete's actual HR zones, pace zones, LTHR, FTP, and max HR. This caches the zones locally so daily briefings and workout skills don't need to call the athlete endpoint every time. Tell the athlete they can ask you to refresh zones anytime if they update them in Intervals.icu.

## Step 4: Verify repo setup

Check that the athlete's personal data is being tracked (not gitignored). If `SOUL.md` or `athlete/profile.md` show up in `git status` as untracked, they need to be committed. If the `.gitignore` still ignores `athlete/*` or `SOUL.md`, remove those lines.

If the repo has a remote, check visibility with `gh repo view --json visibility`. If public, warn the athlete and help them make it private.

Framework updates happen automatically via the SessionStart hook — no manual steps needed.

## Step 5: Personalize your companion

Tell the athlete they can customize who their companion is. Copy `SOUL.example.md` to `SOUL.md` as a starting point, then ask:

1. **Name**: "What would you like to call your companion? The default is Virgil, but you can pick any name — some runners name it after someone who inspires them."
2. **Inspiration**: "Is there a runner, coach, or person you admire? This helps shape the companion's personality." (e.g., Kilian Jornet, Courtney Dauwalter, their first coach, a training partner)
3. **Personality dimensions** — ask one at a time, offering two ends of a spectrum:
   - **Tone**: "Do you want your companion to feel more like a casual training buddy, or a professional coach?"
   - **Intensity**: "When your body is ready for hard work, do you want gentle encouragement, or someone who'll tell you straight: 'you've got more in you'?"
   - **Detail**: "Do you prefer brief, just-the-essentials advice, or deep explanations with the science behind it?"
   - **Humor**: "Should your companion keep things light, or stay serious?"
   - **Celebration**: "After a great session, do you want to be hyped up, or just get the analysis and move on?"

Write their answers to `SOUL.md`. If they want to skip this step, keep the defaults from `SOUL.example.md`.

Tell the athlete: "You can always change your companion's personality later by editing `SOUL.md` — it's a plain text file in your project folder. Change the name, tone, humor, or anything else. The companion reads it fresh at the start of every session."

## Step 6: Set up the `switchback` command

Ask the user: "Would you like to be able to launch Switchback from anywhere by just typing `switchback`?"

If yes:

1. Detect their shell from `$SHELL` (zsh → `~/.zshrc`, bash → `~/.bashrc`).
2. Get the absolute path to `switchback.sh` in this project directory (use `$PWD/switchback.sh`).
3. Check if an alias or function named `switchback` already exists in their shell profile. If so, tell them it's already set up.
4. If not, add the alias to their shell profile:
   ```
   alias switchback="/absolute/path/to/switchback-running/switchback.sh"
   ```
5. Run `source` on the profile file so it takes effect immediately.
6. Tell them they can now type `switchback` from any directory to start a session.

If they decline, tell them they can always run `./switchback.sh` from the project directory.

## Step 7: Done

Tell them they're all set — greet them by name using their new companion persona. Suggest they try `switchback` (or `/today`) to see their first morning briefing, or just start chatting.
