#!/usr/bin/env python3
"""Regenerate native Codex agents from the repository's flat frontmatter Markdown.

Requires Python 3.11+. --check is read-only. Source Markdown is never modified.
Generated files carry source and output hashes; local edits are never overwritten.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parent.parent
EXTRA_ROLES = ("dhh-code-reviewer", "product-manager", "story-writer")
PILOT_HASHES = {
    "dhh-code-reviewer": "7e4c140e660646fdf378b2c97d806090273e028e3ac09256fba2acdaa565ca33",
    "rails-architect": "6968990f6d43c8f475521097c6af9029765b91754e61c9b4a088758f46291aa8",
    "rails-model-engineer": "4d015ec51d2d4662128e19dd0fc7ffdc0106d085a583806e4c0dae2f01565b15",
}
CONTRACT = """## Codex runtime contract

Always act as an expert Ruby on Rails engineer and technical collaborator within
your assigned specialty. This posture applies regardless of the selected GPT model.
Use idiomatic Ruby, Rails conventions, operator-task TDD, evidence-based debugging,
and independent review. Read the target AGENTS.md and pinned versions first; source
examples illustrate patterns, not executable or version-independent prescriptions.
Target rules govern normalization, model ordering, authorization and minimal comments.

Use only tools exposed by the current Codex session. Read/Grep/Glob/Bash/Edit/Write
below describe operations, not callable tool names or allowlists: use shell reads,
rg/rg --files, and available patch tools. Model and reasoning effort inherit from
the parent. Permissions, available tools and MCP connections come from the actual
session; this instruction file grants none and cannot enforce a tool sandbox.
Never bypass permissions or assume a path is writable or denied from source examples.
Ask the parent to handle vault writes that require additional permission.

Discover actual Rails/Fizzy MCP operations and verify the connected repository and
environment before use. If unavailable, read complete relevant local schema/routes/
files and disclose the fallback. Source tool names are capability examples, not a
promise that those tools exist. Configuration or code does not prove production use;
runtime claims require current logs, job runs, traffic or equivalent observations.

Resolve bundle resources using the parent-provided checkout location, defaulting to
~/Development/rails-agents. Guardrail references inside bundled playbooks resolve
to this bundle's guardrails directory. External book and vault paths remain external;
report a missing resource instead of claiming to have read it.

Use available Codex collaboration tools with a callable custom role. @name is a role
reference, not a tool call. The full bundle roster is listed below. File presence is
not proof a role is callable: return missing dependencies to the parent, never
impersonate absent roles or silently substitute built-ins. Respect assigned ownership
and preserve other agents' edits. Route human questions through the parent when a
supported question tool is unavailable; unanswered questions are not approval.

Writing .codex/.current-story records the active DoR-passing story; it does not grant
permission, prove a hook is installed, or replace review. Verify the installed hook
and its actual contract before claiming mechanical enforcement. Only record a story
that passed the deterministic lint. Create its parent directory if authorized and
needed. Never reuse a stale story marker for unrelated work. No source board role
authorizes sending comments/messages without the user's explicit authorization.

This runtime contract and role boundary govern the adapted guidance below.
End with FILES_TOUCHED, TESTS (commands and observed results), GATE (red/green/not
applicable), and UNVERIFIED. Green requires all applicable checks and independent
review. Include RCA findings and out-of-scope evidence for the parent to persist.
"""
ENGINEER = """Own only assigned domain files and tests. Before application changes, name the
operator task and observable outcome, write a failing test, and capture the failure.
Implement the change, rerun that regression and all configured required checks.
Test sad paths, authorization and persisted effects as applicable. Each feature needs
an actual operator journey; internal-state assertions alone do not prove usability.
Tests are part of implementation, never a future handoff. Ask the parent for missing
specialists. Return exact changed files and fresh verification for independent
dhh-code-reviewer review. Do not self-approve or claim completion before that gate.
"""
BOUNDARIES = {
    "rails-architect": """Analyze, validate approaches and plan; do not edit application code or tests.
Return ownership, acceptance criteria, tradeoffs and implementation dependencies.
Code examples are proposals for the implementing specialist. Request review through
the parent after implementation; architecture approval is not final code review.
""",
    "dhh-code-reviewer": """Review the parent's exact changed files and current diff, including untracked files.
Never apply your own suggestions or edit application files. Code suggestions are
review feedback for the original implementer. Check operator outcomes, sad paths,
authorization, database constraints and fresh verification alongside idiomatic style.
Separate critical findings from optional improvements and cite file and line. State
explicitly when no critical issues were found. Missing verification keeps GATE red.
Request fixes via the parent and independently review them again when critical issues
were found. A HEAD-only marker cannot prove review of uncommitted content.
""",
    "rails-qa": """Exercise the running dev/staging app as an operator; never mutate production data.
Do not modify application code, tests or config and do not fix your own findings.
Write only QA artifacts or scratch evidence. Report each journey with screenshots,
reproduction steps, severity and uncovered areas. Produce dated Markdown and
self-contained HTML reports in the project's vault QA/ directory; request the parent
to persist/open them when permissions or browser control are unavailable.
""",
    "rails-git-workflow": """Own Git operations only; do not write application code. Preserve unrelated changes,
require verification and independent review before commits, and push only when the
user authorized it. Inspect the actual shell and permissions instead of assuming the
historical harness restrictions below. Do not delete data/schema to repair a migration;
route that decision to the migration specialist with explicit data-loss authorization.
""",
    "product-manager": """Coordinate priorities and gates; do not implement application code.
Do not delete Fizzy boards, cards, or columns through any tool or API. These are behavioral limits,
not native TOML tool-deny enforcement. Restrict board actions to the authorized task.
DoR evidence and an active marker do not replace independent review or user consent.
""",
    "story-writer": """Author source-grounded story artifacts only; do not edit application code, tests,
migrations or boards. Never invent product boundaries. Escalate unresolved questions
through the parent and keep the story NOT-READY until its deterministic lint passes.
""",
}
REPLACEMENTS = (
    ("guardrail-path", "~/Documents/Obsidian Vault/Claude Code/guardrails/", "~/Development/rails-agents/guardrails/"),
    ("orchestrator", "orchestrating Claude Code session", "orchestrating Codex session"),
    ("agent-directory", ".claude/agents/", ".codex/agents/"),
    ("story-marker", ".claude/.current-story", ".codex/.current-story"),
    ("project-instructions", "`CLAUDE.md`", "`AGENTS.md`"),
    ("questions", "`AskUserQuestion`", "the available Codex question tool (or the parent orchestrator)"),
    ("delegation", "via the Agent tool", "via available Codex collaboration tools with the story-writer custom role"),
)


def digest(content):
    return hashlib.sha256(content).hexdigest()


def parse_source(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing flat frontmatter")
    front, separator, body = text[4:].partition("\n---\n")
    if separator == "" or body.strip() == "":
        raise ValueError(f"{path}: missing frontmatter terminator or guidance")
    metadata = {}
    for line in front.splitlines():
        key, colon, value = line.partition(":")
        if colon == "" or key in metadata:
            raise ValueError(f"{path}: malformed or duplicate frontmatter key")
        if key not in {"name", "description", "model", "tools", "disallowedTools"}:
            raise ValueError(f"{path}: unsupported metadata {key!r}; adapt explicitly")
        if value.strip() == "" or value.strip() in {"|", ">"}:
            raise ValueError(f"{path}: only nonempty single-line metadata is supported")
        metadata[key] = value.strip()
    name = metadata.get("name", "")
    if re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", name) is None or name != path.stem:
        raise ValueError(f"{path}: invalid name or filename/name collision")
    if metadata.get("description", "") == "":
        raise ValueError(f"{path}: missing description")
    denied = metadata.get("disallowedTools")
    if denied is not None and (name != "product-manager" or denied !=
            "mcp__fizzy__fizzy_delete_board, mcp__fizzy__fizzy_delete_card, mcp__fizzy__fizzy_delete_column"):
        raise ValueError(f"{path}: unsupported tool denylist; adapt explicitly")
    return metadata, body, digest(raw)


def adapt(body, name):
    audit = []
    for label, before, after in REPLACEMENTS:
        count = body.count(before)
        if count:
            body = body.replace(before, after)
            audit.append(f"{label}:{count}")
    if name == "rails-qa":
        start = body.index("- **Prefer the real UI.**")
        end = body.index("- **Fall back to HTTP", start)
        body = body[:start] + """- **Prefer the real UI.** Discover an available Codex browser integration and read
  its skill before using it. Use its actual exposed schema, never invented tool names.
  Inspect browser context first, create your own tab, drive click/type/navigation
  flows, and screenshot every notable PASS and FAIL. Save evidence under `/tmp`.
  If no browser integration is callable, report the limitation and use HTTP only
  for outcomes it can prove; browser-only behavior remains unverified.
""" + body[end:]
        audit.append("browser-capabilities:1")
    if name == "rails-git-workflow":
        start = body.index("- **Sandbox ↔ git contract")
        end = body.index("\n## Output", start)
        body = body[:start] + """- **Sandbox and Git.** Read the current Codex permissions before operations that
  rewrite the working tree. If denied, use the supported approval mechanism; do not
  assume config/ is denied or disable the sandbox from a historical recipe. Inspect
  repository state after interrupted operations and preserve the user's changes.
- **Never `git stash -u`, never `git clean`, never sweep agent directories.** Preserve
  both `.claude/` and `.codex/` configurations and symlinks. Stage explicit pathspecs;
  never blanket-stash or clean untracked agent definitions.
""" + body[end:]
        audit.append("sandbox-git:1")
    return body, audit


def render(path, metadata, body, source_hash, roster):
    body, audit = adapt(body, metadata["name"])
    instructions = CONTRACT + "\n## Full bundle roster\n\n" + ", ".join(roster)
    instructions += "\n\n## Role boundary\n\n" + BOUNDARIES.get(metadata["name"], ENGINEER)
    instructions += "\n## Adapted source guidance\n" + body
    encoded = "\n".join(json.dumps(line, ensure_ascii=False)[1:-1] for line in instructions.split("\n"))
    payload = f"# Source: {path.name}\n# Source SHA-256: {source_hash}\n"
    payload += "# Adaptations: " + ", ".join(audit or ["runtime-contract-only"]) + "\n"
    payload += f"name = {json.dumps(metadata['name'])}\n"
    payload += f"description = {json.dumps(metadata['description'], ensure_ascii=False)}\n"
    payload += 'developer_instructions = """\n' + encoded + '"""\n'
    if tomllib.loads(payload)["developer_instructions"] != instructions:
        raise ValueError(f"{path}: TOML serialization changed guidance")
    return f"# Generated SHA-256: {digest(payload.encode())}\n" + payload


def sync(source, output, check=False):
    if output.is_symlink():
        raise ValueError(f"{output}: symlink output directory refused")
    paths = sorted([*source.glob("rails-*.md"), *(source / f"{name}.md" for name in EXTRA_ROLES
                                                 if (source / f"{name}.md").exists())])
    if paths == []:
        raise ValueError(f"{source}: no agent definitions found")
    parsed = [(path, *parse_source(path)) for path in paths]
    roster = [metadata["name"] for _, metadata, _, _ in parsed]
    if len(set(roster)) != len(roster):
        raise ValueError("duplicate agent names")
    expected = {f"{name}.toml" for name in roster}
    unexpected = sorted(p.name for p in output.glob("*.toml") if p.name not in expected)
    if unexpected:
        raise ValueError(f"unexpected output files (not deleted): {', '.join(unexpected)}")
    changes = []
    for path, metadata, body, source_hash in parsed:
        target = output / f"{metadata['name']}.toml"
        if target.is_symlink():
            raise ValueError(f"{target}: symlink destination refused")
        generated = render(path, metadata, body, source_hash, roster)
        current = target.read_bytes() if target.exists() else None
        if current is not None and current != generated.encode():
            header, _, payload = current.partition(b"\n")
            valid = header == f"# Generated SHA-256: {digest(payload)}".encode()
            known_pilot = digest(current) == PILOT_HASHES.get(metadata["name"])
            if not valid and not known_pilot:
                raise ValueError(f"{target}: locally modified or unmanaged output; preserve and reconcile manually")
        if current != generated.encode():
            changes.append((target, generated))
    if check and changes:
        raise ValueError("stale/missing generated agents: " + ", ".join(p.name for p, _ in changes))
    if not check:
        output.mkdir(parents=True, exist_ok=True)
        for target, generated in changes:
            target.write_text(generated, encoding="utf-8")
    return len(roster), len(changes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "codex" / "agents")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        count, changed = sync(args.source, args.output, args.check)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"{count} agents validated; {changed} files {'stale' if args.check else 'updated'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
