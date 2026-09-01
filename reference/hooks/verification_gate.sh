#!/usr/bin/env bash
# Verification-gate Stop hook — WARN mode.
# Makes the maker's self-review steps visible/enforceable: when a turn ends with
# app code changed, it checks that (1) an operator-task system test accompanies
# UI/controller changes and (2) a code review was recorded for this tree.
#
# WARN mode: it surfaces gaps on stderr and exits 0 (does not block). To promote
# to BLOCK once proven, see the tail of this script and Runbooks/Verification Gate Hook.
#
# Verified against code.claude.com/docs/en/hooks (2026-08-30):
#   - Stop/SubagentStop pass JSON on stdin incl. stop_hook_active, transcript_path.
#   - Block by exit 2 (stderr → Claude) or {"decision":"block","reason":...}.
#   - Must short-circuit when stop_hook_active=true (8-block loop override).

set -euo pipefail
INPUT="$(cat)"

# Loop guard — never re-block once we've already asked for continuation.
if [ "$(printf '%s' "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null)" = "true" ]; then
  exit 0
fi

repo="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$repo" || exit 0

changed="$(git status --porcelain 2>/dev/null || true)"
# The in-flight code surface (uncommitted). Committed-and-clean tasks are checked at commit time, not here.
app_code="$(printf '%s\n' "$changed" | grep -E ' (app/(controllers|models|views|helpers|jobs|mailers)/|config/routes\.rb)' || true)"
[ -z "$app_code" ] && exit 0   # no code task in flight → nothing to gate

warn=()

# (1) Operator-task test discipline: a UI/controller change should ship with a system test.
ui_change="$(printf '%s\n' "$app_code" | grep -E 'app/(views|controllers)/' || true)"
sys_change="$(printf '%s\n' "$changed" | grep -E ' test/system/' || true)"
if [ -n "$ui_change" ] && [ -z "$sys_change" ]; then
  warn+=("Operator-task test: app/views or app/controllers changed, but no test/system/ change. Add a system test that walks the journey (visit -> act -> assert the observable outcome), not just a controller POST. And before 'done', run the FULL suite INCLUDING test/system/ (sandbox-off for Selenium) — 'bin/rails test' excludes system by default.")
fi

# (2) Code review gate: was @dhh-code-reviewer run and recorded for this tree state?
marker="$repo/.claude/.last-review"
head_sha="$(git rev-parse HEAD 2>/dev/null || echo none)"
if [ ! -f "$marker" ] || [ "$(cat "$marker" 2>/dev/null)" != "$head_sha" ]; then
  warn+=("Code review gate: no @dhh-code-reviewer run recorded for this state. Run the reviewer, then record it: echo \"\$(git rev-parse HEAD)\" > .claude/.last-review")
fi

if [ ${#warn[@]} -gt 0 ]; then
  {
    echo "VERIFICATION GATE (warn mode) — self-review steps not evidenced before stopping:"
    for w in "${warn[@]}"; do echo "  - $w"; done
    echo "(warn only; not blocking. See Runbooks/Verification Gate Hook to promote to block.)"
  } >&2
fi

# WARN mode always allows the stop.
exit 0

# --- To PROMOTE TO BLOCK (after the warn phase proves quiet on false positives) ---
# Replace the final `exit 0` above with, when warnings exist:
#   printf '%s\n' "${warn[@]}" >&2
#   exit 2
# (exit 2 feeds stderr back to Claude on Stop so it addresses the gap and continues,
#  unless the emitted JSON also sets {"impossible": true}.)
