#!/bin/bash
# Switchback Running — launcher script
# Starts Claude Code with companion persona preloaded and greets the athlete

cd "$(dirname "$0")" || exit 1

# Preload SOUL.md as additional system context so the companion
# has its personality from the very first message
SOUL_FLAG=""
if [ -f SOUL.md ]; then
  SOUL_FLAG="--append-system-prompt-file SOUL.md"
fi

# Resume last session if available (preserves context), or start fresh
# The positional prompt becomes the first user message, triggering the greeting
exec claude $SOUL_FLAG --continue "Hey coach!"
