#!/bin/bash
# Switchback auto-update — called by SessionStart hook via curl
# Downloads latest framework from GitHub, overwrites framework files only.
# NEVER touches athlete/ or SOUL.md — personal data is sacred.

set -euo pipefail

UPSTREAM="rlacombe/switchback-running"
VERSION_FILE=".switchback-version"

# Check latest commit SHA (one fast API call)
LATEST=$(curl -sf "https://api.github.com/repos/$UPSTREAM/commits/main" \
  | grep '"sha"' | head -1 | cut -d'"' -f4)
[ -z "$LATEST" ] && exit 0

# Already up to date?
[ -f "$VERSION_FILE" ] && [ "$(cat "$VERSION_FILE")" = "$LATEST" ] && exit 0

# Download tarball
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
curl -sL "https://github.com/$UPSTREAM/tarball/main" \
  | tar xz -C "$TMPDIR" --strip-components=1

# Overwrite framework directories
for dir in knowledge agents scripts src .claude/skills .gemini; do
  if [ -d "$TMPDIR/$dir" ]; then
    rm -rf "$dir"
    cp -r "$TMPDIR/$dir" "$dir"
  fi
done

# Overwrite framework root files (never personal data)
for file in COMPANION.md CLAUDE.md AGENTS.md GEMINI.md README.md LICENSE \
            switchback.sh install.sh SOUL.example.md athlete/profile.example.md \
            .claude/settings.json .mcp.json; do
  if [ -f "$TMPDIR/$file" ]; then
    mkdir -p "$(dirname "$file")"
    cp "$TMPDIR/$file" "$file"
  fi
done

# Make scripts executable
chmod +x switchback.sh scripts/*.sh 2>/dev/null || true
[ -f install.sh ] && chmod +x install.sh

# Record version
echo "$LATEST" > "$VERSION_FILE"

# Commit framework update if there are changes (never stage athlete/)
if ! git diff --quiet 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard -- ':!athlete/' ':!SOUL.md' 2>/dev/null)" ]; then
  git add -A -- ':!athlete/' ':!SOUL.md'
  git commit -m "Auto-update Switchback framework" 2>/dev/null || true
  git push 2>/dev/null || true
fi
