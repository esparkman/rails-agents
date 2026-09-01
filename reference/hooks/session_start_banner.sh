#!/usr/bin/env bash
# SessionStart hook — deterministic harness-status banner.
#
# Produced by the environment, not the model: if this banner's facts appear at
# session start, the wiring is genuinely in place; if the agents line says
# "none" or a symlink is BROKEN, the harness is not fully wired in this repo.
# It reports verified state so the model's init block reflects reality instead
# of memory.
set -uo pipefail
shopt -s nullglob

repo="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo" 2>/dev/null || true

global="$HOME/.claude/CLAUDE.md"
if [ -f "$global" ]; then
  g="present ($(wc -l < "$global" | tr -d ' ') lines)"
else
  g="MISSING"
fi

if [ -d .claude/agents ]; then
  links=(.claude/agents/*.md)
  total=${#links[@]}
  broken=0
  for l in "${links[@]}"; do [ -e "$l" ] || broken=$((broken + 1)); done
  bundle="$(readlink .claude/agents/rails-architect.md 2>/dev/null)"; bundle="$(dirname "$bundle" 2>/dev/null)"
  a="$total agents"
  [ "$broken" -gt 0 ] && a="$a, $broken BROKEN"
  [ -n "$bundle" ] && [ "$bundle" != "." ] && a="$a -> $bundle"
  [ "$total" -eq 0 ] && a="none (delegation OFF)"
else
  a="none (delegation OFF)"
fi

if grep -q verification_gate .claude/settings.json 2>/dev/null; then
  h="armed"
else
  h="not installed"
fi

read -r -d '' banner <<EOF || true
HARNESS CHECK (SessionStart hook — environment-verified, not model memory):
  global CLAUDE.md : $g
  agents           : $a
  verification gate: $h
EOF

# Plain stdout (visible where the client surfaces hook output) AND
# additionalContext (guaranteed into the model's context) — belt and suspenders.
printf '%s\n' "$banner"
esc=$(printf '%s' "$banner" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null)
[ -n "$esc" ] && printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' "$esc"
