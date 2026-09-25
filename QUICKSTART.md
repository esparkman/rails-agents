# rails-agents — quickstart (agent bundle for the harness)

These are Rails specialist agents. They're **Bring-Your-Own agents** for
[the harness](https://github.com/octanelabsdev/harness) — the harness supplies the mechanism
(hooks, guardrails, PM pipeline), you supply the agents. You can also use these agents
standalone (without the harness).

## 1. Get the harness (the mechanism)
```sh
git clone https://github.com/octanelabsdev/harness ~/harness
~/harness/install.sh /path/to/your-rails-app     # interactive: choose the "rails" stack
```
This wires the harness plugin + your `.claude/harness.json` (stack profile + gates). It ships
**no agents** — that's this repo's job.

## 2. Drop these agents into your project
Clone this repo, then link (or copy) the agent files into your project's `.claude/agents/`:
```sh
git clone https://github.com/octanelabsdev/rails-agents ~/rails-agents
cd /path/to/your-rails-app
mkdir -p .claude/agents
for f in ~/rails-agents/rails-*.md ~/rails-agents/dhh-code-reviewer.md; do
  ln -sfn "$f" ".claude/agents/$(basename "$f")"
done
# gitignore the machine-local symlinks so a personal path never gets committed:
printf '%s\n' '.claude/agents/rails-*.md' '.claude/agents/dhh-code-reviewer.md' >> .claude/agents/.gitignore
```
(Copy instead of symlink if you'd rather vendor them into the repo.)

## 3. (Optional) the reference bookshelf
Some agents consult a local reference shelf for idiom/design judgment. The reader lives in the
harness — its **`bookshelf` skill** reads **your own** EPUBs from `$TOMES_DIR` (nothing is shipped).

## What's here
- `rails-*.md`, `dhh-code-reviewer.md` — the specialist agents (architecture, models, controllers,
  Hotwire, ViewComponents, testing, security/performance, deployment, and more).
- `reference/lessons.md` — accumulated review lessons the agents apply.

The harness's guardrails, verification/pipeline gates, session banner, and story-writer /
product-manager pipeline are **not** here anymore — they live in
[octanelabsdev/harness](https://github.com/octanelabsdev/harness).
