#!/bin/bash
# Switchback Running — installer

UPSTREAM="rlacombe/switchback-running"
DIR="${SWITCHBACK_DIR:-$HOME/switchback-personal}"

info() { echo "  → $*"; }
error() { echo "  ✗ $*" >&2; }
ok() { echo "  ✓ $*"; }

echo ""
echo "  Switchback Running — installer"
echo ""

# ---- Already installed? ----

if [ -d "$DIR" ] && [ -f "$DIR/switchback.sh" ]; then
  info "Already installed at $DIR"
  echo ""
  echo "  To launch:  $DIR/switchback.sh"
  echo "  To update:  $DIR/switchback.sh update"
  exit 0
fi

# ---- Agent ----

if command -v claude &>/dev/null || command -v gemini &>/dev/null || command -v codex &>/dev/null; then
  ok "AI agent found"
else
  info "No AI agent found. Installing Gemini CLI (free)..."
  if command -v brew &>/dev/null; then
    brew install gemini-cli || { error "Install failed. Try: brew install gemini-cli"; exit 1; }
  elif command -v npm &>/dev/null; then
    npm install -g @google/gemini-cli || { error "Install failed. Try: npm install -g @google/gemini-cli"; exit 1; }
  else
    error "Can't install Gemini CLI — need Homebrew or npm."
    echo "    Mac:     /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "    Or:      https://nodejs.org"
    exit 1
  fi
  ok "Gemini CLI installed"
fi

# ---- Download ----

info "Downloading Switchback..."
TMP=$(mktemp -d)
curl -fsSL "https://github.com/$UPSTREAM/tarball/main" | tar xz -C "$TMP" --strip-components=1
if [ ! -f "$TMP/switchback.sh" ]; then
  error "Download failed. Check your internet connection."
  rm -rf "$TMP"
  exit 1
fi
mv "$TMP" "$DIR"
chmod +x "$DIR/switchback.sh" "$DIR/scripts/"*.sh 2>/dev/null
ok "Installed to $DIR"

# ---- Create personal files from templates ----

cd "$DIR"
[ ! -f SOUL.md ] && [ -f SOUL.example.md ] && cp SOUL.example.md SOUL.md
[ ! -f athlete/profile.md ] && [ -f athlete/profile.example.md ] && cp athlete/profile.example.md athlete/profile.md
[ ! -f athlete/notes.md ] && mkdir -p athlete && touch athlete/notes.md

# ---- Shell alias ----

RC_FILE=""
case "$(basename "$SHELL" 2>/dev/null)" in
  zsh)  RC_FILE="$HOME/.zshrc" ;;
  bash) RC_FILE="$HOME/.bashrc" ;;
esac

if [ -n "$RC_FILE" ] && ! grep -q "alias switchback=" "$RC_FILE" 2>/dev/null; then
  echo "" >> "$RC_FILE"
  echo "# Switchback Running" >> "$RC_FILE"
  echo "alias switchback=\"$DIR/switchback.sh\"" >> "$RC_FILE"
  ok "Added 'switchback' command — open a new terminal to use it"
fi

# ---- Launch ----

echo ""
echo "  To launch Switchback: switchback"
echo "  (or: $DIR/switchback.sh)"
echo ""

exec "$DIR/switchback.sh"
