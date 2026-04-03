#!/bin/bash
# Switchback Running — one-command installer
# Creates a private repo with the framework + space for your personal data.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/rlacombe/switchback-running/main/install.sh | bash

set -euo pipefail

UPSTREAM="rlacombe/switchback-running"
REPO_NAME="switchback-personal"
INSTALL_DIR="${SWITCHBACK_DIR:-$HOME/$REPO_NAME}"

info()  { echo "  → $*"; }
error() { echo "  ✗ $*" >&2; }
ok()    { echo "  ✓ $*"; }

echo ""
echo "Switchback Running — installer"
echo "==============================="
echo ""

# ---- Prerequisites ----

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

# ---- Already installed? ----

if [ -d "$INSTALL_DIR" ] && [ -f "$INSTALL_DIR/switchback.sh" ]; then
  info "Already installed at $INSTALL_DIR"
  info "Run: cd $INSTALL_DIR && ./switchback.sh"
  exit 0
fi

# ---- Download framework ----

echo ""
info "Downloading Switchback framework..."
mkdir -p "$INSTALL_DIR"
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
curl -sL "https://github.com/$UPSTREAM/tarball/main" | tar xz -C "$TMPDIR" --strip-components=1
cp -r "$TMPDIR"/. "$INSTALL_DIR"/
cd "$INSTALL_DIR"
ok "Framework downloaded"

# ---- Initialize git repo ----

git init -q
ok "Git repo initialized"

# ---- Configure for personal data ----

# Remove personal-data ignores so athlete/ and SOUL.md are tracked
sed -i.bak '/^SOUL\.md$/d' .gitignore 2>/dev/null || true
sed -i.bak '/^athlete\/\*$/d' .gitignore 2>/dev/null || true
sed -i.bak '/^!athlete\/\.gitignore$/d' .gitignore 2>/dev/null || true
sed -i.bak '/^!athlete\/profile\.example\.md$/d' .gitignore 2>/dev/null || true
rm -f .gitignore.bak
[ -f athlete/.gitignore ] && rm athlete/.gitignore

# Create personal data from templates
mkdir -p athlete
[ ! -f SOUL.md ] && cp SOUL.example.md SOUL.md
[ ! -f athlete/profile.md ] && cp athlete/profile.example.md athlete/profile.md
[ ! -f athlete/notes.md ] && touch athlete/notes.md

# Make scripts executable
chmod +x switchback.sh scripts/*.sh 2>/dev/null || true

# Initial commit
git add -A
git commit -q -m "Initial Switchback setup"
ok "Initial commit created"

# ---- Private remote (optional) ----

echo ""
if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
  GH_USER=$(gh api user -q .login 2>/dev/null || echo "")
  if [ -n "$GH_USER" ]; then
    read -rp "  → Create a private GitHub repo ($GH_USER/$REPO_NAME) to back up your data? [Y/n] " answer
    answer="${answer:-Y}"
    if [[ "$answer" =~ ^[Yy] ]]; then
      if gh repo view "$GH_USER/$REPO_NAME" &>/dev/null 2>&1; then
        info "Repo already exists: $GH_USER/$REPO_NAME"
        git remote add origin "https://github.com/$GH_USER/$REPO_NAME.git" 2>/dev/null || true
      else
        gh repo create "$REPO_NAME" --private --source=. --push
      fi

      # Verify it's private
      VISIBILITY=$(gh repo view "$GH_USER/$REPO_NAME" --json visibility -q .visibility 2>/dev/null || echo "UNKNOWN")
      if [ "$VISIBILITY" = "PUBLIC" ]; then
        error "Repo is public! Making it private..."
        gh repo edit "$GH_USER/$REPO_NAME" --visibility private
      fi
      ok "Private repo ready: https://github.com/$GH_USER/$REPO_NAME"
    fi
  fi
else
  info "GitHub CLI not found — skipping remote backup setup."
  info "Your data is local. You can add a remote later with:"
  echo "    gh repo create $REPO_NAME --private --source=. --push"
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

# ---- Done ----

echo ""
echo "==============================="
echo "  Installation complete!"
echo "  Installed to: $INSTALL_DIR"
echo ""
echo "  Framework updates happen automatically at each session start."
echo ""
echo "  Launching Switchback for first-time setup..."
echo "  (This will connect Intervals.icu and build your athlete profile)"
echo ""

exec "$INSTALL_DIR/switchback.sh"
