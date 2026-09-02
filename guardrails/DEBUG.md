<!-- guardrails v1 | adapted from github.com/TheColliny/FableClaudeMDForOpus (DEBUG.md). macOS/zsh + Rails/Laravel. -->
You are here because a test you expected to pass failed, a build/test/run command exited non-zero, a traceback appeared, run output contradicted your prediction, or the user reported a bug you have not reproduced this session.

Cite IDs as you go; the ESCALATION LADDER below is mandatory, not optional.

- D1. Reproduce FIRST: write down and run the exact reproduction command; paste its failing output and quote the line that shows the REPORTED symptom (a command failing for an unrelated reason is not a reproduction). The bug is fixed ONLY when that same command, unmodified, re-runs and passes — paste that too. Cannot reproduce? -> run the user's steps plus the D2 environment checks, write `CANNOT-REPRODUCE: <commands tried -> outputs>`, and ask for exact steps — never fix blind. (This is your global "Work From Raw Data" directive.)
- D2. "It worked before / stopped working": step 1 is environment re-verification, before touching code — server actually up (`lsof -ti :PORT`), right branch (`git branch --show-current`), gem/package installed (`bundle show <X>` / `composer show <X>` / `npm ls <X>`), env var set, migrations run (`bin/rails db:migrate:status | grep down`), assets/artifact rebuilt after the edit. Any environment belief last verified >15 messages ago or before a compaction is stale — re-verify with one command.
- D3. CAUSE line before any fix: `CAUSE: <file:line where the bad state originates> -> <propagation path> -> SYMPTOM: <file:line where it surfaces>`. Your edit targets the CAUSE end. Patching the symptom (nil check, rescue, default) instead? Label it `WORKAROUND: <why root cause is out of reach>`, then Grep the originating symbol repo-wide and paste every other place the same bad state flows.
- D4. Iterate on the NARROWEST failing test only (exact `-n` name / `--filter` / single file). Full suite only at two points per fix cycle: the baseline and the D8 confirmation — never inside the fix loop.
- D5. Never re-run a failing command unchanged. Before any re-run, state one line: the hypothesis and what changed since the last run. Suspected flake? Run the test 3x in isolation, paste all 3 outcomes; 3/3 pass -> log `FLAKE: 3/3 pass isolated`; any failure -> the bug is real.
- D6. Failed-attempts ledger: after EVERY failed fix, BEFORE trying again, record `ATTEMPT n [L<level>]: <what changed> -> <exact observed failure>`. A next attempt differing from a logged one only in surface details is FORBIDDEN -> move up the ESCALATION LADDER.
- D7. Same tool call failed twice with the same error? A third unchanged (or cosmetically varied) attempt is forbidden -> quote the error verbatim, state in one sentence what it implies, then change something structural: different tool, different path, read the config, or ask.
- D8. Fix landed? Two runs, both pasted: (1) the D1 re-run — original command, unmodified — passing; (2) the nearest enclosing suite green (summary line). Then run the fix-shaped-to-test check (`~/Documents/Obsidian Vault/Claude Code/guardrails/VERIFY.md`, "A test you just made pass shares literals with your fix").
- D9. Result contradicts your prediction — either direction? Do not rationalize it. Prove the executed code is the edited code (temporary marker log line, or printed file path + mtime) and re-run with caches cleared (`bin/rails tmp:clear`, `jest --no-cache`, clean build). Only then interpret.
- D10. About to weaken a failing check to get green? That is your global Code Review Gate / Hard-stop territory: quote the failure, propose the change, wait for approval. No skips, deleted tests, loosened asserts, raised tolerances, widened `rescue`, `# rubocop:disable` without justification.

## ESCALATION LADDER (invoked by D6)
The ATTEMPT count sets a floor that never moves down for the same bug.
- ATTEMPT 1-2: L1 — a different fix under the same hypothesis.
- ATTEMPT 3: L2 required — a NEW hypothesis, formed by re-reading the FULL error output verbatim and the failing code; quote the error line that drives it.
- ATTEMPT 4: L3 required — a pasted minimal reproduction or instrumentation output.
- ATTEMPT 5: L4 required — revert to last-known-good (name the commit/stash) and re-approach.
- ATTEMPT 6 does not exist: L5 — present the full ledger to the user and stop. (This is your global "Failure Recovery" directive.)

--- reference ---

## Red flags — your own words are the tripwire. If your reply contains the left column, do the right column.
| You are writing/thinking | Do this instead |
|---|---|
| "probably unrelated" | Treat as related: stash your change, rerun, paste the result |
| "pre-existing / not caused by my change" | Prove it: `git stash`, run on the clean tree, paste both results |
| "test is probably flaky" | Run the D5 flake procedure (3x isolated, paste all 3) |
| "should work now" | You have not run it. Run it; write `Verified: <command> -> <result line>` |
| "quick fix for now" | Stop. Write the CAUSE line (D3) first |
| "let me take a different approach" | Write the `ATTEMPT n [L<level>]` ledger line (D6) first and name the ladder level |
| "add a sleep / increase the timeout" | Detector-silencing (D10): find the race or slow path first |
| "must be a caching issue" | Run D9 now (code-identity proof + cache-clear) and paste it before claiming |
| "easiest to just rewrite this file" | Never rewrite to escape a bug you don't understand; state root cause first |
| "the linter/type error is noise" | Paste the exact message; explain it in one line or fix it |

## Same error, byte-identical, after your fix
Your code is not running. Verify you edited the file the process actually loads: restart the server/watcher/Spring (`bin/spring stop`), rebuild assets, check for a twin file (`~/Documents/Obsidian Vault/Claude Code/guardrails/CODE.md` C3), confirm the edit landed (`git diff -- <file>`).

## A previously-passing test fails after your edit
BEFORE touching the test, state in one line whether the behavior change is intended by the task. Only if intended: edit the expectation, quote old-expected vs new-expected with justification. Never run snapshot-update as a first response — it converts a caught regression into a certified one.

## The failure only happens in CI
Diff the environments before diffing the code: Ruby/PHP/Node version, env vars, DB state, `RAILS_ENV`/`APP_ENV`, cache. Grep `.github/workflows/*.yml` for the exact command CI runs — it is often not the command you ran locally.
