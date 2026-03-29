#!/bin/bash
# Switchback Running — multi-agent launcher
# Detects installed AI agents, remembers your preference, and launches
# with agent-appropriate configuration.

set -euo pipefail
cd "$(dirname "$0")" || exit 1

UPSTREAM="rlacombe/switchback-running"
PREF_FILE=".switchback-agent"

# ---- Update command ----

if [ "${1:-}" = "update" ]; then
  echo ""
  echo "Switchback — updating framework"
  echo "================================"
  echo ""

  # Download latest tarball from GitHub
  TMPDIR=$(mktemp -d)
  trap "rm -rf $TMPDIR" EXIT

  echo "  → Downloading latest version..."
  curl -sL "https://github.com/$UPSTREAM/tarball/main" | tar xz -C "$TMPDIR" --strip-components=1

  # Framework files to overwrite (everything except personal data)
  echo "  → Updating framework files..."

  # Directories — sync entirely
  for dir in knowledge agents scripts .claude/skills .gemini; do
    if [ -d "$TMPDIR/$dir" ]; then
      rm -rf "$dir"
      cp -r "$TMPDIR/$dir" "$dir"
    fi
  done

  # Root files — overwrite framework, skip personal
  for file in COMPANION.md CLAUDE.md AGENTS.md GEMINI.md README.md LICENSE \
              switchback.sh install.sh SOUL.example.md athlete/profile.example.md \
              scripts/generate-agent-docs.sh; do
    if [ -f "$TMPDIR/$file" ]; then
      mkdir -p "$(dirname "$file")"
      cp "$TMPDIR/$file" "$file"
    fi
  done

  # Make scripts executable
  chmod +x switchback.sh install.sh scripts/*.sh 2>/dev/null || true

  # Commit if there are changes
  if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
    git add -A
    git commit -m "Update Switchback framework to latest"
    echo "  ✓ Framework updated and committed"

    # Push if we have a remote
    if git remote get-url origin &>/dev/null 2>&1; then
      git push 2>/dev/null && echo "  ✓ Pushed to your repo" || echo "  → Push skipped (no remote or auth issue)"
    fi
  else
    echo "  ✓ Already up to date"
  fi

  echo ""
  exit 0
fi

# ---- Agent detection ----

declare -a AVAILABLE=()
command -v claude &>/dev/null && AVAILABLE+=("claude")
command -v codex  &>/dev/null && AVAILABLE+=("codex")
command -v gemini &>/dev/null && AVAILABLE+=("gemini")

if [ ${#AVAILABLE[@]} -eq 0 ]; then
  echo "No supported agent found. Install one of:"
  echo "  Claude Code:  npm install -g @anthropic-ai/claude-code"
  echo "  Codex CLI:    npm install -g @openai/codex"
  echo "  Gemini CLI:   npm install -g @anthropic-ai/gemini-cli"
  exit 1
fi

# ---- Agent selection ----

AGENT=""

# 1. --agent flag takes priority
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)  AGENT="$2"; shift 2 ;;
    --agent=*) AGENT="${1#*=}"; shift ;;
    *) ARGS+=("$1"); shift ;;
  esac
done

# 2. Saved preference (verify still installed)
if [ -z "$AGENT" ] && [ -f "$PREF_FILE" ]; then
  SAVED=$(tr -d '[:space:]' < "$PREF_FILE")
  if printf '%s\n' "${AVAILABLE[@]}" | grep -qx "$SAVED"; then
    AGENT="$SAVED"
  fi
fi

# 3. Only one agent available — use it
if [ -z "$AGENT" ] && [ ${#AVAILABLE[@]} -eq 1 ]; then
  AGENT="${AVAILABLE[0]}"
fi

# 4. Ask the user
if [ -z "$AGENT" ]; then
  echo "Multiple agents detected. Which would you like to use?"
  echo ""
  for i in "${!AVAILABLE[@]}"; do
    echo "  $((i+1))) ${AVAILABLE[$i]}"
  done
  echo ""
  read -rp "Pick a number (saved for next time): " choice
  idx=$((choice - 1))
  if [ "$idx" -ge 0 ] && [ "$idx" -lt ${#AVAILABLE[@]} ]; then
    AGENT="${AVAILABLE[$idx]}"
    echo "$AGENT" > "$PREF_FILE"
    echo "Saved: $AGENT"
  else
    echo "Invalid choice." >&2
    exit 1
  fi
fi

# Validate
if ! printf '%s\n' "${AVAILABLE[@]}" | grep -qx "$AGENT"; then
  echo "Agent '$AGENT' is not installed." >&2
  exit 1
fi

# ---- Build context ----
# Preload SOUL + athlete profile + notes into system prompt so the
# companion has personality, timezone, and athlete context from the
# very first token — no file reads needed at startup.

CONTEXT=$(mktemp)
trap "rm -f $CONTEXT" EXIT

# Inject current local date and time so the companion knows the time of day
echo "# Current Date and Time" >> "$CONTEXT"
echo "Right now it is $(date '+%A, %B %-d, %Y at %-I:%M %p %Z')." >> "$CONTEXT"
echo "" >> "$CONTEXT"

[ -f SOUL.md ] && cat SOUL.md >> "$CONTEXT"
[ -f athlete/profile.md ] && { echo ""; echo "# Athlete Profile"; cat athlete/profile.md; } >> "$CONTEXT"
[ -f athlete/notes.md ] && { echo ""; echo "# Companion Notes"; cat athlete/notes.md; } >> "$CONTEXT"

# ---- Launch ----

case "$AGENT" in
  claude)
    exec claude --append-system-prompt-file "$CONTEXT" "Hey!"
    ;;

  codex)
    exec codex "Hey!"
    ;;

  gemini)
    exec gemini "Hey!"
    ;;
esac
