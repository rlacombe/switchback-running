#!/bin/bash
# Switchback Running — one-command installer
# Forks the repo (private), clones it, installs deps, and launches setup.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/rlacombe/switchback-running/main/install.sh | bash

set -euo pipefail

UPSTREAM="rlacombe/switchback-running"
INSTALL_DIR="${SWITCHBACK_DIR:-$HOME/switchback-running}"

# ---- Helpers ----

info()  { echo "  → $*"; }
error() { echo "  ✗ $*" >&2; }
ok()    { echo "  ✓ $*"; }

# ---- Prerequisites ----

echo ""
echo "Switchback Running — installer"
echo "==============================="
echo ""

# GitHub CLI
if ! command -v gh &>/dev/null; then
  error "GitHub CLI (gh) is required for forking."
  echo "    Install: https://cli.github.com"
  exit 1
fi

# Check gh auth
if ! gh auth status &>/dev/null 2>&1; then
  error "GitHub CLI is not authenticated. Run: gh auth login"
  exit 1
fi
ok "GitHub CLI authenticated"

# At least one AI agent
HAS_AGENT=false
command -v claude &>/dev/null && HAS_AGENT=true
command -v codex  &>/dev/null && HAS_AGENT=true
command -v gemini &>/dev/null && HAS_AGENT=true

if [ "$HAS_AGENT" = false ]; then
  error "No AI agent found. Install at least one:"
  echo "    Claude Code:  npm install -g @anthropic-ai/claude-code"
  echo "    Gemini CLI:   npm install -g @google/gemini-cli"
  echo "    Codex CLI:    npm install -g @openai/codex"
  exit 1
fi
ok "AI agent detected"

# ---- Fork ----

echo ""
GH_USER=$(gh api user -q .login)

# Check if fork already exists
if gh repo view "$GH_USER/switchback-running" &>/dev/null 2>&1; then
  info "Fork already exists: $GH_USER/switchback-running"
else
  info "Forking $UPSTREAM → $GH_USER/switchback-running..."
  gh repo fork "$UPSTREAM" --default-branch-only --clone=false
  ok "Forked"
fi

# Make it private
VISIBILITY=$(gh repo view "$GH_USER/switchback-running" --json visibility -q .visibility)
if [ "$VISIBILITY" != "PRIVATE" ]; then
  info "Setting fork to private (your training data will live here)..."
  gh repo edit "$GH_USER/switchback-running" --visibility private
  ok "Fork is now private"
else
  ok "Fork is already private"
fi

# ---- Clone ----

echo ""
if [ -d "$INSTALL_DIR" ]; then
  info "Directory already exists: $INSTALL_DIR"
  cd "$INSTALL_DIR"

  # Verify it's the right repo
  ORIGIN=$(git remote get-url origin 2>/dev/null || echo "")
  if [[ "$ORIGIN" != *"$GH_USER/switchback-running"* ]]; then
    error "$INSTALL_DIR exists but points to a different repo: $ORIGIN"
    error "Remove it or set SWITCHBACK_DIR to a different location and re-run."
    exit 1
  fi
  ok "Using existing clone"
else
  info "Cloning to $INSTALL_DIR..."
  gh repo clone "$GH_USER/switchback-running" "$INSTALL_DIR"
  cd "$INSTALL_DIR"
  ok "Cloned"
fi

# ---- Upstream remote (pull-only) ----

if git remote get-url upstream &>/dev/null 2>&1; then
  ok "Upstream remote already set"
else
  info "Adding upstream remote (pull-only — push disabled)..."
  git remote add upstream "https://github.com/$UPSTREAM.git"
  git remote set-url --push upstream DISABLE
  ok "Upstream remote configured"
fi

# ---- Configure gitignore for personal data ----

if grep -q "^SOUL\.md$" .gitignore 2>/dev/null; then
  info "Configuring .gitignore for personal data..."

  # Remove lines that ignore personal data
  sed -i.bak '/^SOUL\.md$/d' .gitignore
  sed -i.bak '/^athlete\/\*$/d' .gitignore
  sed -i.bak '/^!athlete\/\.gitignore$/d' .gitignore
  sed -i.bak '/^!athlete\/profile\.example\.md$/d' .gitignore
  rm -f .gitignore.bak

  # Remove athlete/.gitignore if it exists
  [ -f athlete/.gitignore ] && rm athlete/.gitignore

  ok "Personal data will now be tracked in your private fork"
else
  ok "Gitignore already configured for personal data"
fi

# ---- Shell alias ----

echo ""
SHELL_NAME=$(basename "$SHELL")
case "$SHELL_NAME" in
  zsh)  RC_FILE="$HOME/.zshrc" ;;
  bash) RC_FILE="$HOME/.bashrc" ;;
  *)    RC_FILE="" ;;
esac

if [ -n "$RC_FILE" ]; then
  if grep -q "alias switchback=" "$RC_FILE" 2>/dev/null; then
    ok "Shell alias already set"
  else
    read -rp "  → Add 'switchback' alias to $RC_FILE? [Y/n] " answer
    answer="${answer:-Y}"
    if [[ "$answer" =~ ^[Yy] ]]; then
      echo "" >> "$RC_FILE"
      echo "# Switchback Running" >> "$RC_FILE"
      echo "alias switchback=\"$INSTALL_DIR/switchback.sh\"" >> "$RC_FILE"
      ok "Alias added — run 'source $RC_FILE' or open a new terminal"
    fi
  fi
fi

# ---- Launch ----

echo ""
echo "==============================="
echo "  Installation complete!"
echo ""
echo "  Your private fork: https://github.com/$GH_USER/switchback-running"
echo "  Installed to: $INSTALL_DIR"
echo ""
echo "  Launching Switchback for first-time setup..."
echo "  (This will connect Intervals.icu and build your athlete profile)"
echo ""

exec "$INSTALL_DIR/switchback.sh"
