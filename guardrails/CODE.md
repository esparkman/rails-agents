<!-- guardrails v1 | adapted from github.com/TheColliny/FableClaudeMDForOpus (CODE.md). macOS/zsh + Rails/Laravel. -->
You are here because you are about to create or modify a repo file — by Edit, Write, or a file-writing shell command — for the first time this session or since the last compaction.

Cite the ID with one line of evidence when an item fires; skipping a fired item is a violation.

Before the FIRST edit of each file:
- C1. Read the enclosing function/class plus the import/`require`/`use` block; file under 250 lines -> Read all of it. A Grep snippet is not a Read. Mandatory even for "obvious one-liners". (This is the compressed Hardening Layer iron rule 1 and your global "Edit Integrity" directive.)
- C2. Generated/vendored check: path contains `dist/`, `build/`, `out/`, `public/build/`, `public/packs/`, `node_modules/`, `vendor/`, `tmp/`, `coverage/`, `*.min.*`, or is a lockfile (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Gemfile.lock`, `composer.lock`), or `db/schema.rb`/`db/structure.sql` — or the first 10 lines say "DO NOT EDIT"/"@generated"? Do not edit -> change the source or generator (migration for schema.rb, the config for a lockfile), re-run it, and name the generator command.
- C3. Twin check: Grep the target file/symbol name repo-wide before the first edit. More than one definition? List all candidates and paste the evidence for the live one (the import/require line or stack frame pointing at it). Common Rails/Laravel names (`create`, `update`, `show`, `handle`, `call`) match many — this fires often.
- C4. Constraint check: print `CONSTRAINT CHECK: <path> — none apply` or `CONSTRAINT CHECK: <path> — matches '<constraint>', skipping/asking`, against any "don't/only/keep/stop" the user stated this session.

While editing:
- C5. Unfamiliar or third-party API with 2+ arguments: paste its real signature (from installed sources/type stubs, `ruby -e "require 'X'; puts M.method(:fn).parameters.inspect"`, `php -r`, `node_modules/**/*.d.ts`, or official docs) before writing the call. Cannot produce it? -> write `SIGNATURE UNVERIFIED: <fn>` and either pick an API whose signature you can paste, or stop and ask for the docs. (Compressed as Hardening Layer iron rule 2's cousin.)
- C6. First use of each third-party library this session: read its pinned version from the manifest/lockfile (`Gemfile.lock`, `composer.lock`, `package-lock.json`) and state `Using <lib> v<N> — writing v<N> idioms.`
- C7. Touching any category in `~/Documents/Obsidian Vault/Claude Code/guardrails/TRAPS.md` — dates/times, epochs/units, mutation-vs-copy, async, floats/money, sort, division/modulo, regex, familiar-API traps, closures, boolean logic? Read TRAPS.md and follow your rows — never guess load-bearing behavior.
- C8. Duplicated-then-adapted block: list every token that had to change; Grep the file with `-n` for each OLD token; confirm in one line per token that every hit's line number lies OUTSIDE the new block's range. Same term appears 3+ times per line? Extract a helper/partial/concern instead of pasting.
- C9. Edit with `replace_all=true`: first Grep the old_string in that file and paste every occurrence; confirm each should change. Never `replace_all` a string that is not a complete identifier or can occur inside another word -> one Edit per occurrence with unique surrounding context.
- C10. New project-local import (relative path, repo package, `require_relative`, autoloaded constant): confirm the target exists — Glob the module path or Grep the definition (`def <sym>|class <sym>|module <sym>|export .*<sym>|function <sym>`) — and paste the hit.

After each edit:
- C11. Run `git diff -- <file>` — any change on a line you did not intend to touch is corruption: revert and redo the Edit with more surrounding context in old_string. Ruby: also `ruby -c <file>`. JS/.mjs: `node --check <file>`. PHP: `php -l <file>`. No per-file syntax gate (.ts, .erb) -> rely on the project build/lint at VERIFY and say so.
- C12. Changed a signature, symbol name, return shape, config key, route, CLI flag, env var, enum member, DB column, or I18n key? Run REFERENCE SWEEP (below) now — before the next task step. (Compressed as Hardening Layer iron rule 2 and your "No Semantic Search" directive.)
- C13. New code doing I/O, network, parsing external input, or multi-step mutation: implement the failure path explicitly, then report `HANDLED FAILURES: <list>` and `NOT HANDLED (by choice): <list + reason>`. An empty failure list on I/O code is a defect.
- C14. Before any Edit that deletes "dead" code: paste all three greps first — (1) bare name repo-wide including non-code files (views, YAML, routes), (2) the name inside quotes (`'x'` and `"x"`) for dynamic dispatch/`send`/reflection, (3) barrel/`__all__`/route/registration/DI entries. Any ambiguous hit -> deprecate instead of delete.
- C15. Replacing more than half of a function or file? Follow "You are rewriting instead of editing" below the divider first.

## REFERENCE SWEEP (named procedure — invoked by C12 and Hardening Layer iron rule 2)
- RS1. Grep the affected symbol's name repo-wide with NO file-type filter (code, configs, YAML, ERB/Blade templates, routes, docs, fixtures, factories) — the OLD name if renamed, otherwise the unchanged name of the thing whose contract changed.
- RS2. Paste the hit list as `file:line`. A zero-hit result is pasted, never asserted.
- RS3. More than 50 hits? Re-run with a word-boundary pattern (`\b<name>\b`) excluding vendored paths (`node_modules/`, `dist/`, `vendor/`, `tmp/`); still >50 -> delegate the sweep to a subagent and disposition the returned list yourself.
- RS4. Disposition every hit in one line each: `updated` or `unaffected — <reason>`. Renames: additionally Grep the name as a string literal (logs, `send`/`public_send`, `params[:x]`, reflection, dynamic dispatch).
- RS5. Enum/union/state-machine changes: additionally Grep `case`/`when`/`switch`/`if`-chains over that type; update every branch set. Do not proceed to the next task step until every hit is dispositioned.

--- reference ---

## You are rewriting instead of editing
Rewriting a whole function/file is allowed only if the user asked, or more than half its lines change — the sole exception to "Edit, never Write", and it still requires a full Read of the current version this session first. Before the rewrite: list the current version's observable behaviors — every branch, default, side effect, handled error, callback/validation — and state where each survives in the new version. Any behavior not on the list is one you are deleting unknowingly. Before any Write over an existing file, run `git diff -- <file>` and confirm no uncommitted changes would be destroyed.

## Your Edit failed with "string not found"
The only permitted next action on that file is a Read of the target region — never a guessed retry, never a whole-file Write. Your memory of the file is provably wrong; it may have been changed by your own earlier edits, a formatter (rubocop/prettier/pint), or the user.

## Delegation note (your global directive interaction)
When your global CLAUDE.md routes this edit to a `@rails-*` / Laravel sub-agent, the sub-agent does not automatically read this file. Either perform the C1/C12 gates yourself before delegating, or include "read ~/Documents/Obsidian Vault/Claude Code/guardrails/CODE.md and follow C1, C12/REFERENCE SWEEP" in the sub-agent's prompt.
