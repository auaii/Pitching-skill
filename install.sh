#!/usr/bin/env bash
# Install the pitch-deck-builder skill for one or more AI apps on this computer.
#
# Usage: ./install.sh [kiro] [claude] [codex] [all]   (no argument: every app found here)
#   kiro    Kiro Crew                    -> ~/.kiro/crew/skills/pitch-deck-builder
#   claude  Claude Code                  -> ~/.claude/skills/pitch-deck-builder
#   codex   ChatGPT desktop / Codex CLI  -> ~/.agents/skills/pitch-deck-builder
# claude.ai and ChatGPT web install by upload instead: run tools/package.sh.
# Works with macOS's built-in bash 3.2.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
src="$here/skills/pitch-deck-builder"
[ -f "$src/SKILL.md" ] || { echo "error: $src/SKILL.md not found" >&2; exit 2; }

app_home() {
  case "$1" in
    kiro) echo "$HOME/.kiro/crew" ;;
    claude) echo "$HOME/.claude" ;;
    codex) echo "$HOME/.agents" ;;
    *) return 1 ;;
  esac
}

targets="$*"
if [ -z "$targets" ]; then
  for t in kiro claude codex; do [ -d "$(app_home $t)" ] && targets="$targets $t"; done
  [ -n "$targets" ] || { echo "no AI app folders found; name one: ./install.sh claude" >&2; exit 1; }
fi
[ "$targets" = "all" ] && targets="kiro claude codex"

for t in $targets; do
  base="$(app_home "$t")" || { echo "unknown target: $t (use kiro, claude, codex or all)" >&2; exit 2; }
  d="$base/skills/pitch-deck-builder"
  if [ -d "$d" ]; then
    # Back up OUTSIDE skills/, or the app would load the backup as a duplicate skill.
    mkdir -p "$base/skill-backups"
    backup="$base/skill-backups/pitch-deck-builder-$(date +%Y%m%d-%H%M%S)"
    mv "$d" "$backup"
    echo "backed up old copy -> $backup"
  fi
  mkdir -p "$base/skills"
  cp -R "$src" "$d"
  find "$d" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
  echo "installed for $t -> $d"
done
echo "Python tools (optional): pip install -r \"$src/requirements.txt\""
