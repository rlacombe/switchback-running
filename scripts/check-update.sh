#!/bin/bash
# Switchback — check for framework updates (used as a SessionStart hook)
# Compares local framework version against the latest on GitHub.
# Only downloads if there's a new version.

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1

UPSTREAM="rlacombe/switchback-running"
VERSION_FILE=".switchback-version"

# Get latest commit SHA from GitHub
LATEST=$(curl -sf "https://api.github.com/repos/$UPSTREAM/commits/main" | grep '"sha"' | head -1 | cut -d'"' -f4)

if [ -z "$LATEST" ]; then
  # Can't reach GitHub — skip silently
  exit 0
fi

# Compare with stored version
if [ -f "$VERSION_FILE" ] && [ "$(cat "$VERSION_FILE")" = "$LATEST" ]; then
  # Already up to date
  exit 0
fi

# New version available — run update
./switchback.sh update

# Store the version
echo "$LATEST" > "$VERSION_FILE"
