# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of specialized AI agent prompt files for Ruby on Rails development. These agents are designed to work together as a codebase-aware development team that can be dropped into any Rails project.

**Not a Rails application** - This repository contains only Markdown agent definition files, not executable Ruby code.

## Agent Architecture

Eight specialized agents form a complete Rails development team:

| Agent | Role | Tools |
|-------|------|-------|
| `rails-architect` | Technical lead, system design, architectural decisions | Read, Glob, Grep, Bash |
| `rails-model-engineer` | Models, migrations, ActiveRecord, database | Read, Write, Edit, Glob, Grep, Bash |
| `rails-controller-engineer` | Controllers, routing, authentication, APIs | Read, Write, Edit, Glob, Grep, Bash |
| `rails-hotwire-engineer` | Views, Hotwire, Stimulus, frontend | Read, Write, Edit, Glob, Grep, Bash |
| `rails-testing-expert` | Tests, fixtures, coverage | Read, Write, Edit, Glob, Grep, Bash |
| `rails-security-performance` | Security audits, performance optimization | Read, Glob, Grep, Bash |
| `rails-background-jobs` | Background jobs, Solid Queue, recurring tasks, async processing | Read, Write, Edit, Glob, Grep, Bash |
| `rails-authentication` | Magic links, sessions, identity patterns, OAuth | Read, Write, Edit, Glob, Grep, Bash |

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
3. **API Layer** - `@rails-controller-engineer` builds controllers/routes
4. **Frontend** - `@rails-hotwire-engineer` creates views/JS
5. **Testing** - `@rails-testing-expert` writes tests
6. **Review** - `@rails-security-performance` audits

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
