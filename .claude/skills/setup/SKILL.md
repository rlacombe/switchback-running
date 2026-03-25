---
description: "Guided setup — installs dependencies, connects Intervals.icu, and builds your athlete profile"
user-invocable: true
---

# /setup — Guided Setup

Walk the user through setup step by step. Be friendly and patient — assume they are not technical. Confirm each step before moving to the next. Do not dump a wall of instructions; go one step at a time.

## Step 1: Install dependencies

Check if `node_modules` exists in the project directory. If not, run `npm install`. If Node.js is not installed, tell the user to install it from https://nodejs.org (LTS version) and come back.

Tell the user what you're doing and show the result.

## Step 2: Connect to Intervals.icu

Check if `INTERVALS_API_KEY` and `INTERVALS_ATHLETE_ID` are set in the environment.

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
5. Detect their shell (check `$SHELL` — likely `~/.zshrc` or `~/.bashrc`). Add the export lines to their shell profile:
   ```
   export INTERVALS_API_KEY="their_key"
   export INTERVALS_ATHLETE_ID="their_id"
   ```
6. Tell the user they need to **restart Claude Code** for the environment variables to take effect. The MCP server reads these on startup.
7. **Stop here.** Tell them to quit Claude Code, open a new terminal, start `claude` again in this directory, and run `/setup` again to continue. Do NOT proceed to Step 3.

## Step 3: Verify the connection

Make a test API call using `get_wellness` for today. If it succeeds, tell the user the connection is working. If it fails, help them debug (wrong key, wrong athlete ID, etc.).

## Step 4: Build the athlete profile

Tell the user you're going to ask a few questions to personalize the coaching. Ask them conversationally — one or two questions at a time, not a long form. Create the `athlete/` directory if it doesn't exist, then use their answers to fill in `athlete/profile.md` (copied from `ATHLETE.example.md` if it doesn't exist yet). Also create an empty `athlete/notes.md` for Virgil's persistent observations. This folder is gitignored — their personal data stays local and won't be overwritten by `git pull`.

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

After gathering answers, write their data to `athlete/profile.md` (filling in the template from `ATHLETE.example.md`). Show them what you wrote and ask if anything needs adjusting.

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

## Step 6: Done

Tell them they're all set — greet them by name using their new companion persona. Suggest they try `/today` to see their first morning briefing, or just start chatting.
