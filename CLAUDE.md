# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of specialized AI agent prompt files for Ruby on Rails development. These agents are designed to work together as a codebase-aware development team that can be dropped into any Rails project.

**Not a Rails application** - This repository contains only Markdown agent definition files, not executable Ruby code.

## Agent Architecture

Nineteen specialized agents form a complete Rails development team:

| Agent | Role | Model | Tools |
|-------|------|-------|-------|
| `rails-architect` | Technical lead, system design, architectural decisions | opus | Read, Glob, Grep, Bash |
| `rails-security-performance` | Security audits, performance optimization | opus | Read, Glob, Grep, Bash |
| `dhh-code-reviewer` | Post-write review against DHH's standards — **mandatory gate** after any Ruby/JS/Svelte change | opus | Read, Write, Edit, Glob, Grep, Bash |
| `rails-model-engineer` | Models, migrations, ActiveRecord, database | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-controller-engineer` | Controllers, routing, authentication, APIs | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-hotwire-engineer` | Views, Hotwire, Stimulus, frontend | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-viewcomponent-engineer` | ViewComponent design, slots, variants, component-driven UI | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-authentication` | Magic links, sessions, identity patterns, OAuth | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-background-jobs` | Background jobs, Solid Queue, recurring tasks, async processing | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-mailer` | Action Mailer, email templates, previews, delivery configuration | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-data-migration` | Data migrations, seeds, backfills, bulk data operations | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-domain-logic` | Service objects, form objects, query objects, POROs | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-api-serializer` | JSON API serialization, versioning, pagination | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-accessibility` | WCAG compliance, ARIA, keyboard navigation, screen readers | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-i18n` | Locale files, translations, date/time formatting | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-active-storage` | File uploads, image variants, direct uploads, cloud storage | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-testing-expert` | Tests, fixtures, coverage | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-deployment` | Kamal, Docker, production configuration, server operations | sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `rails-git-workflow` | Branching, commit hygiene, pull requests, merges, releases, tags | sonnet | Read, Grep, Glob, Bash, Edit |

## Agent File Format

Each agent file uses YAML frontmatter followed by Markdown:

```markdown
---
name: agent-name
description: Brief description of agent role
model: sonnet
tools: Read,Write,Edit,Glob,Grep,Bash
---

# Agent Name

[Agent instructions in Markdown]
```

## Workflow Pattern

Agents are designed to be invoked in sequence for feature development:
1. **Architecture** - `@rails-architect` designs approach
2. **Data Layer** - `@rails-model-engineer` implements models/migrations
3. **Data Migrations** - `@rails-data-migration` handles seeds and backfills
4. **Domain Logic** - `@rails-domain-logic` implements service/form/query objects
5. **API Layer** - `@rails-controller-engineer` builds controllers/routes
6. **API Serialization** - `@rails-api-serializer` shapes JSON responses
7. **Frontend** - `@rails-hotwire-engineer` creates views/JS
8. **Components** - `@rails-viewcomponent-engineer` builds ViewComponents
9. **Accessibility** - `@rails-accessibility` ensures WCAG compliance
10. **Internationalization** - `@rails-i18n` adds translations
11. **File Uploads** - `@rails-active-storage` handles attachments
12. **Email** - `@rails-mailer` implements mailers and templates
13. **Testing** - `@rails-testing-expert` writes tests
14. **Security/Performance Review** - `@rails-security-performance` audits
15. **DHH Code Review (mandatory gate)** - `@dhh-code-reviewer` reviews against Rails-core standards; task is not complete until this passes
16. **Git Workflow** - `@rails-git-workflow` branches, commits, opens the PR, merges, and tags the release
17. **Deployment** - `@rails-deployment` handles production deploy

> **Note:** Step 15 is a blocking gate enforced by the global CLAUDE.md ("MANDATORY: DHH Code Review Gate"). Any Ruby, JavaScript, Svelte, or ViewComponent change must pass through `@dhh-code-reviewer` before the task is marked done or a commit is proposed. The user can waive per-task with explicit opt-out language ("skip review", "no review", etc.).

## Pipeline discipline (from the 2026-08-31 harness retro)

**Size-aware tiers — match ceremony to blast radius.** The scoping step stamps one tier:
- **Trivial** (≤1 file, no schema/route/security change): testing-expert (red) → implementer → `@dhh-code-reviewer` → commit. **Skip the architect.**
- **Standard** (default): the full Workflow Pattern above.
- **Structural** (schema / security / multi-file): full pipeline **+ a mandatory footgun/transaction review** (loaded-association `dependent: :destroy` cascades, money, N+1, auth, multi-record transactions).

**Full suite INCLUDING system is a named pre-dhh step (owned by `@rails-testing-expert`).** `bin/rails test` excludes `test/system/` by default; run the full suite incl. system (sandbox-off for Selenium) and confirm green before the dhh gate. A step, not an orchestrator habit — a real bug (D2 system-destroy) slipped once because it was implicit.

**Fan-out is the default for disjoint-file work.** Launch independent files in parallel (≥2 independent files); serialize only true dependencies (migration before the controller that uses it).

**Every agent ends with a machine-checkable status block** the orchestrator verifies cheaply (files exist, tallies match a quick re-run) instead of parsing prose:
```
FILES_TOUCHED: <list>
TESTS: <cmd> -> <runs>/<assertions>/<failures>
GATE: red|green
UNVERIFIED: <anything not run this turn>
```

**Stories come from the Story Writer, gated.** Build from DoR-passing, source-cited cards (`@story-writer` + `dor_lint.rb`), not a re-derived reading — keeps iteration structure faithful and boundaries pinned. Intent precedence: **PRD/intent > human-in-chat > cited source (book) > existing app.**

**Verification lives in structure, not memory.** The `Stop` verification-gate hook (Runbooks/Verification Gate Hook) enforces operator-task test + review before "done"; safety properties belong in named steps and agent definitions, never in one actor's vigilance.

## Reference Tomes (all agents)

A curated shelf of Rails/Ruby/PostgreSQL books is available to **every** agent for
the **how/why** behind a pattern — idiom, OO design, testing strategy, PG behavior.
Catalog + usage: `reference/tomes/tomes.md`; reader: `reference/tomes/tome.sh`
(`list` / `find` / `toc` / `search` / `chapter`). The shelf resolves via `$TOMES_DIR`
plus standard fallbacks, so any agent with Bash can read it with no setup.

- Reach for a tome when a decision turns on **idiom or design judgment** (a Rails 8
  convention, an OO refactor, a Minitest approach, a PostgreSQL behavior) rather than
  on this app's facts. **Quote the source line you rely on** (verify-before-asserting).
- **`rails-mcp` remains the authority for THIS app's schema/routes/models** — tomes are
  never a source for what this codebase currently contains, only for how/why.

## Key Design Principles

- **Codebase Analysis First**: Each agent analyzes the target Rails project on first invocation to learn existing patterns
- **Pattern Matching**: Agents match the existing style of the codebase rather than imposing new patterns
- **Agent Collaboration**: Agents reference each other and delegate to specialists
- **Agent OS Integration**: Designed to work with Agent OS workflows and product specs in `.agent-os/` directories

## Modifying Agents

When updating agent files:

1. **Preserve the frontmatter format**:
   ```yaml
   ---
   name: agent-name
   description: Brief description
   model: sonnet
   tools: Read,Write,Edit,Glob,Grep,Bash
   ---
   ```

2. **Key sections to include**:
   - "Your First Task: Analyze the Codebase" - Critical for pattern learning
   - Code examples with both Minitest and RSpec variants
   - "Integration with Other Agents" cross-references
   - Best Practices (Do's and Don'ts)

3. **When adding patterns**:
   - Extract minimal, focused examples
   - Include context on when to use the pattern
   - Add under "Advanced Patterns" section if it exists

See `README.md` section "Updating & Customizing Agents" for detailed guidance.
