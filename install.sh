#!/bin/bash
# Switchback Running — one-command installer
# Creates a private repo, populates it with the framework, and launches setup.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/rlacombe/switchback-running/main/install.sh | bash

set -euo pipefail

UPSTREAM="rlacombe/switchback-running"
REPO_NAME="switchback-personal"
INSTALL_DIR="${SWITCHBACK_DIR:-$HOME/$REPO_NAME}"

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
  error "GitHub CLI (gh) is required."
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

# ---- Create private repo ----

echo ""
GH_USER=$(gh api user -q .login)

if [ -d "$INSTALL_DIR" ] && git -C "$INSTALL_DIR" remote get-url origin &>/dev/null 2>&1; then
  info "Already installed at $INSTALL_DIR"
  cd "$INSTALL_DIR"
  ok "Using existing installation"
else
  # Create the private repo on GitHub if it doesn't exist
  if gh repo view "$GH_USER/$REPO_NAME" &>/dev/null 2>&1; then
    info "Repo already exists: $GH_USER/$REPO_NAME"
  else
    info "Creating private repo: $GH_USER/$REPO_NAME..."
    gh repo create "$GH_USER/$REPO_NAME" --private --description "My Switchback Running companion"
    ok "Created"
  fi

  # Clone it
  info "Cloning to $INSTALL_DIR..."
  gh repo clone "$GH_USER/$REPO_NAME" "$INSTALL_DIR" 2>/dev/null || git clone "https://github.com/$GH_USER/$REPO_NAME.git" "$INSTALL_DIR"
  cd "$INSTALL_DIR"

  # Populate from the framework tarball
  info "Downloading Switchback framework..."
  TMPDIR=$(mktemp -d)
  trap "rm -rf $TMPDIR" EXIT
  curl -sL "https://github.com/$UPSTREAM/tarball/main" | tar xz -C "$TMPDIR" --strip-components=1
  cp -r "$TMPDIR"/. .

  # Configure gitignore for personal data
  sed -i.bak '/^SOUL\.md$/d' .gitignore
  sed -i.bak '/^athlete\/\*$/d' .gitignore
  sed -i.bak '/^!athlete\/\.gitignore$/d' .gitignore
  sed -i.bak '/^!athlete\/profile\.example\.md$/d' .gitignore
  rm -f .gitignore.bak
  [ -f athlete/.gitignore ] && rm athlete/.gitignore

  # Make scripts executable
  chmod +x switchback.sh install.sh scripts/*.sh 2>/dev/null || true

  # Initial commit
  git add -A
  git commit -m "Initial Switchback setup"
  git push -u origin main 2>/dev/null || git push -u origin HEAD:main
  ok "Framework installed"
fi

# ---- Verify repo is private ----

VISIBILITY=$(gh repo view "$GH_USER/$REPO_NAME" --json visibility -q .visibility 2>/dev/null || echo "UNKNOWN")
if [ "$VISIBILITY" = "PUBLIC" ]; then
  error "Your repo is public! Making it private..."
  gh repo edit "$GH_USER/$REPO_NAME" --visibility private
  ok "Repo is now private"
elif [ "$VISIBILITY" = "PRIVATE" ]; then
  ok "Repo is private"
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
echo "  Your private repo: https://github.com/$GH_USER/$REPO_NAME"
echo "  Installed to: $INSTALL_DIR"
echo ""
echo "  Launching Switchback for first-time setup..."
echo "  (This will connect Intervals.icu and build your athlete profile)"
echo ""

exec "$INSTALL_DIR/switchback.sh"
