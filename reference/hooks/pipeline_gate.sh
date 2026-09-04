#!/usr/bin/env bash
# PreToolUse gate: no feature build without a prioritized, DoR-passing story.
#
# Blocks Edit/Write to the implementation surface (app/, lib/, db/migrate/) unless
# either (a) a `.claude/.current-story` marker stamped `DoR: PASSED` exists — written
# by the pipeline (story-writer authors the card, product-manager prioritizes it and
# writes the marker) — or (b) an explicit `.claude/.small-fix` bypass is declared for
# genuinely-independent small work. Tests, config, docs, and .claude/ are NOT gated.
#
# Enforces faithful-execution (features flow PRD -> DoR story -> PM -> engineer) in the
# environment. Per-repo mode: WARN by default (allow + announce, non-disruptive); promote
# to BLOCK by `touch .claude/.pipeline-block` so architect-straight-to-build becomes
# impossible rather than merely flagged. Same warn->block discipline as the verification gate.
set -uo pipefail

input=$(cat)
file_path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$file_path" ] && exit 0

dir=$(dirname "$file_path"); [ -d "$dir" ] || dir="$PWD"
repo=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || exit 0   # non-repo path -> allow

# Only gate the implementation surface. Everything else passes untouched.
case "$file_path" in
  */app/* | */lib/* | */db/migrate/*) : ;;
  *) exit 0 ;;
esac

cdir="$repo/.claude"

emit() { jq -n --arg d "$1" --arg r "$2" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:$d,permissionDecisionReason:$r}}'; }

# (a) explicit small-fix escape hatch — allowed, but surfaced every time so it can't hide
if [ -f "$cdir/.small-fix" ]; then
  what=$(head -1 "$cdir/.small-fix" 2>/dev/null)
  emit allow "SMALL-FIX BYPASS active${what:+ — $what}. Pipeline gate skipped for this edit; remove .claude/.small-fix when the fix is done."
  exit 0
fi

# (b) a prioritized, DoR-passing story is present
if [ -f "$cdir/.current-story" ] && grep -qiE "DoR:[[:space:]]*PASSED" "$cdir/.current-story" 2>/dev/null; then
  exit 0
fi

# otherwise: no card backs this feature edit.
# Per-repo mode: BLOCK if `.claude/.pipeline-block` exists (promoted), else WARN (default,
# non-disruptive) — mirrors the verification gate's warn->block discipline so a repo with
# work in flight isn't frozen the instant the gate is wired.
msg="Pipeline gate: no DoR-passing, PM-prioritized story backs this feature edit ($file_path). Route it — story-writer authors a DoR card, then product-manager prioritizes it and writes .claude/.current-story stamped 'DoR: PASSED'. If this is genuinely independent small work, declare it: printf '%s\\n' '<what + why>' > .claude/.small-fix"
if [ -f "$cdir/.pipeline-block" ]; then
  emit deny "$msg"
else
  emit allow "PIPELINE GATE (warn) — $msg  [warn only; touch .claude/.pipeline-block to enforce]"
fi
exit 0
