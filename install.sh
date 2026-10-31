#!/usr/bin/env bash
# Install this library's skills and agents into ~/.claude (and optionally ~/.agents for Codex).
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE=link; CODEX=0
for arg in "$@"; do
  case "$arg" in
    --copy) MODE=copy ;;
    --codex) CODEX=1 ;;
    -h|--help) echo "usage: ./install.sh [--copy] [--codex]"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 1 ;;
  esac
done

place() {  # place <source> <dest>
  local src="$1" dest="$2"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ -L "$dest" ]; then rm "$dest"
    else mv "$dest" "$dest.bak.$(date +%Y%m%d%H%M%S)"; echo "  backed up existing $(basename "$dest")"; fi
  fi
  if [ "$MODE" = copy ]; then cp -R "$src" "$dest"; else ln -s "$src" "$dest"; fi
}

install_skills() {  # install_skills <dir>
  mkdir -p "$1"
  for s in "$REPO"/skills/*/; do
    s="${s%/}"; place "$s" "$1/$(basename "$s")"
  done
  echo "skills -> $1 ($MODE)"
}

install_skills "$HOME/.claude/skills"

mkdir -p "$HOME/.claude/agents"
for a in "$REPO"/.claude/agents/*.md; do place "$a" "$HOME/.claude/agents/$(basename "$a")"; done
echo "agents -> $HOME/.claude/agents ($MODE)"

[ "$CODEX" = 1 ] && install_skills "$HOME/.agents/skills"

echo "Done. Open 'claude' and ask: what skills do you have?"
