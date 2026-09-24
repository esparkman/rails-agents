# Codex compatibility pilot

## Scope

Phase 1 contains exactly five files: this specification, a personal global
instructions template, and native definitions for `rails-architect`,
`rails-model-engineer`, and `dhh-code-reviewer`. This is a reviewable pilot,
not an installed full-team migration. Claude sources and installed personal
configuration remain untouched.

The fifth file is `codex/templates/global-AGENTS.md`. The existing `templates/`
ignore rule intentionally keeps personal workflow configuration out of this public
repository. Keep that file local and deliver/install it privately; do not force-add
it. Git should show four new public files and this one ignored private template.

The operator task is to load the three custom roles in Codex, delegate a model
change through architecture and implementation, and receive an independent review
with actual verification evidence. Parsing TOML alone does not prove that journey.

## Source of truth and conversion

The root Markdown agents remain the source of Rails guidance. Each TOML records
the source path and SHA-256. Its `developer_instructions` consists of a Codex runtime
contract, a role boundary/workflow, and the adapted source body. Preserve source
examples as reference material; the target project's pinned versions and current
engineering rules govern implementation.

The source-body transformations are limited to:

- `~/Documents/Obsidian Vault/Claude Code/guardrails/` becomes
  `~/Development/rails-agents/guardrails/`.
- `orchestrating Claude Code session` becomes `orchestrating Codex session`.
- The `.claude/agents/` role-directory reference becomes `.codex/agents/`.
- YAML frontmatter becomes TOML `name`, `description`, and `developer_instructions`.
  Claude `model` and `tools` fields are omitted. The runtime contract explains
  operation/tool mapping; an omitted allowlist is not an equivalent security boundary.

The global template starts from the existing `~/.codex/AGENTS.md`, source SHA-256
`06758e17c0e523a080f928f6488ef9796136366a723d41735aae7eb6ac615972`.
It preserves the rules, adds a native discovery/permissions contract, corrects
agent paths and file formats, points guardrails at the existing bundle, and adapts
question, background-task, resume/fork, and compaction instructions. Personal
communication-style and Obsidian paths are retained.

The user's standing-role requirement is explicit at the top of the global template:
the main assistant and delegated Rails specialists act as expert Ruby on Rails
engineers, regardless of the selected GPT model. Rails handoffs must carry that
role and the applicable engineering standards. This does not override stack
detection, specialist delegation, or independent review.

Pilot variants are maintained snapshots. A repeatable converter and drift check
are future work; do not edit a snapshot and claim the source was updated. Review
source changes and regenerate/reconcile variants before installation.

## Runtime decisions

| Concern | Pilot behavior |
| --- | --- |
| Discovery | Standalone TOML under project `.codex/agents/` or personal `~/.codex/agents/`; verify the callable roster in a fresh session. |
| Models | Omit model and reasoning settings; inherit the parent's resolved settings. |
| Permissions | Inherit the parent; no new MCP credentials, tool grants, or sandbox bypass. |
| Architecture | Analyze and propose; return implementation ownership to the parent. |
| Implementation | Own assigned model/data files and tests; capture a failing regression before implementation. |
| Review | Independent findings with file/line evidence; implementer applies fixes. |
| Missing roles | Report dependencies to the parent and stop dependent work; no silent impersonation or built-in fallback. |
| Rails MCP | Confirm the target app; disclose local inspection fallback when unavailable. |
| Guardrails | Resolve through the bundle; historical paths within playbooks map to that same directory. |
| Hooks | None installed by this pilot; prompt-level requirements do not establish automated enforcement. |

Architect/reviewer edit restrictions are instructions, not separate sandbox
boundaries. Whether stronger per-role restrictions fit the existing test and vault
workflow should be evaluated before full deployment.

## Installation prerequisites (next phase)

1. Review the variants and choose personal or project scope. Back up existing files
   and refuse collisions rather than silently overwriting definitions or templates.
2. Resolve the bundle location. Its guardrails and reference/tomes resources must be
   readable from the target session. Check the personal communication-style file and
   target project's vault paths without copying personal secrets into this repository.
3. Account for instruction size. The global template exceeds the documented default
   32 KiB budget. Set `project_doc_max_bytes = 65536`, or a larger value sufficient
   for all combined instructions, before installing. Inspect `AGENTS.override.md`
   and project instruction conflicts. Do not blindly append duplicate TOML keys.
4. Install the three role files into the selected agent directory, and merge the
   global template deliberately. This directory under `codex/` is not automatically
   discovered. New definitions may require a fresh Codex session.
5. Verify actual discovery and the model/change/review journey below. Do not treat
   source files on disk as proof of loaded roles or hook enforcement.

## Reproducible static validation

Run from the repository root using Python 3.11+ (`tomllib` is in its standard library).
On this machine use `/opt/homebrew/bin/python3`; the shell may select Apple's 3.9.

```sh
/opt/homebrew/bin/python3 - <<'PY'
from pathlib import Path
import hashlib
import tomllib

root = Path.cwd()
roles = ('rails-architect', 'rails-model-engineer', 'dhh-code-reviewer')
expected = {'COMPATIBILITY.md', 'templates/global-AGENTS.md'}
expected.update('agents/' + name + '.toml' for name in roles)
actual = {str(p.relative_to(root / 'codex'))
          for p in (root / 'codex').rglob('*') if p.is_file()}
assert actual == expected, (actual, expected)
for name in roles:
    source = (root / (name + '.md')).read_bytes()
    text = (root / 'codex/agents' / (name + '.toml')).read_text()
    data = tomllib.loads(text)
    assert set(data) == {'name', 'description', 'developer_instructions'}
    assert data['name'] == name and data['description'].strip()
    assert hashlib.sha256(source).hexdigest() in text.splitlines()[1]
    body = source.decode().split('---', 2)[2].lstrip('\n')
    body = body.replace('~/Documents/Obsidian Vault/Claude Code/guardrails/',
                        '~/Development/rails-agents/guardrails/')
    body = body.replace('orchestrating Claude Code session',
                        'orchestrating Codex session')
    body = body.replace('`.claude/agents/`', '`.codex/agents/`')
    instructions = data['developer_instructions']
    assert instructions.split('## Adapted source guidance\n\n', 1)[1] == body
    for field in ('FILES_TOUCHED:', 'TESTS:', 'GATE:', 'UNVERIFIED:'):
        assert field in instructions
template = (root / 'codex/templates/global-AGENTS.md').read_text()
for old in ('.Codex/agents/', 'AskUserQuestion', 'run_in_background',
            '--continue', '--fork-session', 'Obsidian Vault/Codex/guardrails/'):
    assert old not in template, old
assert 'list any `.toml` files found' in template
assert 'project_doc_max_bytes = 65536' in template
assert len(template.encode()) < 65536
for name in ('CODE', 'TRAPS', 'DEBUG', 'VERIFY', 'RUNTIME', 'MECHANISM'):
    assert (root / 'guardrails' / (name + '.md')).is_file()
print('PASS: five pilot files; three TOML roles; source fidelity; native references; guardrails')
PY
```

There is no configured full-suite test runner, compiler/type-checker, or linter
for this pilot. The repository's story-card linter serves a different artifact.
The checks above validate configuration structure and source preservation, not
Ruby snippets, agent reasoning, role loading, or a Rails application.

## Fresh-session acceptance (not yet executed)

- In a disposable Rails development checkout, start a fresh Codex session after
  installing the pilot. Verify all three role names are actually callable and ask
  each to report its role and boundary without changing files.
- Delegate a small, explicitly specified model change to the architect, then model
  engineer. Confirm the engineer records the failing regression, implementation,
  passing regression and required checks. Include the operator-visible outcome.
- Invoke the reviewer independently on those files. Route any fixes back through
  the implementer. Verify missing required evidence prevents a green gate.
- Request a controller task with no controller role installed; verify it reports
  the missing dependency instead of implementing through a built-in role.
- Verify the full global instruction chain loads, including the final hardening
  section. Test scope conflicts and moved/missing bundle resources explicitly.

## Deferred work and tradeoffs

The repository contains 23 agents; three have pilot variants and 20 remain.
The two personal agents in `~/.claude/agents/` are separate from that roster.
The remaining 20 root agents, command/skill content comparison, installer,
conversion tooling, and hook adaptation require later approved phases. The copied
branch hook reads `tool_input.file_path`; Codex patch hooks provide their payload
via `tool_input.command`. Adapt and exercise realistic hook inputs before claiming
branch protection. Speech hooks and plugins need individual compatibility checks.

The perfectionist concern is snapshot drift and untested runtime enforcement.
The pragmatic benefit is preserving the original domain guidance in a small,
reviewable pilot before automating distribution. This pilot makes those limits
explicit and leaves the installed setups intact.

## References

- [Codex custom agents and inheritance](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Instruction discovery and size budget](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex hooks and tool input](https://learn.chatgpt.com/docs/hooks)
- Local `codex --help` confirms `resume --last` and `fork --last` commands.
