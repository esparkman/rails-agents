# Rails Development Team Agents

A complete team of specialized AI agents for Ruby on Rails development. Drop these agents into any Rails project and they'll analyze your codebase, learn your patterns, and help you build features following your established conventions.

## 🎯 Overview

These agents form a **codebase-aware Rails development team** that:
- ✅ **Analyzes your codebase** on first use to learn your patterns
- ✅ **Matches your style** (testing framework, authentication, frontend stack)
- ✅ **Works together** as a cohesive team
- ✅ **Integrates with Agent OS** workflows
- ✅ **Follows Rails best practices** while respecting your choices

## 👥 The Team

### 🏗️ @rails-architect
**Technical Lead & System Designer**

**Model**: Claude Sonnet 4.5
**Tools**: Read, Glob, Grep, Bash

**Responsibilities**:
- Architectural decisions and system design
- Where code should live and how to organize it
- Database schema design
- Feature planning and technical approach

**Use When**:
- Planning new features
- Making architectural decisions
- Designing database schemas
- Evaluating technical approaches

---

### 🗄️ @rails-model-engineer
**Data Layer Specialist**

**Model**: Claude Sonnet 4.5
**Tools**: Read, Write, Edit, Glob, Grep, Bash

**Responsibilities**:
- Models, migrations, and database design
- ActiveRecord associations and validations
- Concerns and query optimization
- Data layer implementation

**Use When**:
- Creating or modifying models
- Writing migrations
- Extracting concerns
- Optimizing database queries

---

### 🎛️ @rails-controller-engineer
**API & Request Handler**

**Model**: Claude Sonnet 4.5
**Tools**: Read, Write, Edit, Glob, Grep, Bash

**Responsibilities**:
- Controllers and routing
- Authentication and authorization
- Strong parameters
- API endpoint design

**Use When**:
- Creating controllers and routes
- Implementing authentication/authorization
- Building API endpoints
- Handling request/response logic

---

### 🎨 @rails-hotwire-engineer
**Frontend & Interaction Specialist**

**Model**: Claude Sonnet 4.5
**Tools**: Read, Write, Edit, Glob, Grep, Bash

**Responsibilities**:
- Views, partials, and layouts
- JavaScript interactions (Hotwire, React, Vue, etc.)
- Frontend components and UI
- Real-time features

**Use When**:
- Creating views and UI
- Adding JavaScript functionality
- Building frontend components
- Implementing real-time features

---

### 🧪 @rails-testing-expert
**Quality Assurance & Testing**

**Model**: Claude Sonnet 4.5
**Tools**: Read, Write, Edit, Glob, Grep, Bash

**Responsibilities**:
- Comprehensive test coverage
- Test fixtures/factories
- Integration and system tests
- Test quality and best practices

**Use When**:
- Writing any tests
- Improving test coverage
- Creating fixtures or factories
- Testing new features

---

### 🔒 @rails-security-performance
**Security & Performance Auditor**

**Model**: Claude Sonnet 4.5
**Tools**: Read, Glob, Grep, Bash

**Responsibilities**:
- Security audits and vulnerability reviews
- Authorization and authentication checks
- Performance optimization
- Query optimization and N+1 prevention

**Use When**:
- Security reviews
- Performance optimization
- Auditing code for vulnerabilities
- Production readiness checks

---

## 🚀 How to Use

### First Time Setup

1. **Drop the agents into your Rails project**:
   ```bash
   cp -r .claude/agents /path/to/your/rails/project/.claude/
   ```

2. **On first use, each agent will**:
   - Analyze your codebase patterns
   - Learn your conventions
   - Document what they observe
   - Match your existing style

### Basic Usage

```markdown
# Get architectural guidance
@rails-architect: How should I implement user notifications?

# Implement a model
@rails-model-engineer: Create a Notification model with polymorphic associations

# Build the API
@rails-controller-engineer: Add controller and routes for notifications

# Create the UI
@rails-hotwire-engineer: Build the notification UI with real-time updates

# Write tests
@rails-testing-expert: Write comprehensive tests for notifications

# Security review
@rails-security-performance: Audit the notification system for security issues
```

### Team Workflow

**For a new feature**, follow this workflow:

1. **Architecture** → @rails-architect designs the approach
2. **Data Layer** → @rails-model-engineer implements models
3. **API Layer** → @rails-controller-engineer builds controllers
4. **Frontend** → @rails-hotwire-engineer creates views
5. **Testing** → @rails-testing-expert writes tests
6. **Review** → @rails-security-performance audits

### Example: Adding a New Feature

```markdown
## Feature: User Notifications

### Step 1: Architecture
@rails-architect: Design a notification system with:
- Multiple notification types (mention, like, comment)
- Mark as read functionality
- Real-time delivery

### Step 2: Data Layer
@rails-model-engineer: Implement the Notification model based on the architecture

### Step 3: API
@rails-controller-engineer: Create NotificationsController with index, show, mark_read actions

### Step 4: UI
@rails-hotwire-engineer: Build notification dropdown with unread count

### Step 5: Testing
@rails-testing-expert: Write model, controller, and system tests

### Step 6: Review
@rails-security-performance: Audit for N+1 queries and authorization issues
```

## 🧠 How They Learn Your Codebase

On first invocation, each agent:

1. **Reads representative files** from your codebase
2. **Documents patterns** they observe
3. **Matches your style** in all implementations

### What They Learn

- **Rails version** and feature usage
- **Database choice** (PostgreSQL, MySQL, SQLite)
- **Testing framework** (RSpec vs Minitest)
- **Frontend stack** (Hotwire, React, Vue, traditional)
- **Authentication** (Devise, custom, etc.)
- **Authorization** (Pundit, CanCanCan, custom)
- **Background jobs** (Sidekiq, Resque, Solid Queue)
- **Code organization** (concerns, service objects, etc.)
- **Naming conventions** and code style

## 🤝 Agent Collaboration

Agents naturally work together:

```markdown
# Architect designs → Model implements → Controller exposes →
# Frontend visualizes → Testing validates → Security secures
```

They reference each other:
- "Based on @rails-architect's design..."
- "Following the pattern @rails-model-engineer established..."
- "Coordinating with @rails-controller-engineer on strong parameters..."

## 🔗 Integration with Agent OS

These agents enhance Agent OS workflows:

```markdown
# 1. Create product specs
@.agent-os/instructions/core/create-spec.md

# 2. Get architectural review
@rails-architect: Review the spec and provide technical design

# 3. Implement with the team
@.agent-os/instructions/core/implement-spec.md
(Agents automatically contribute during implementation)

# 4. Test thoroughly
@rails-testing-expert: Ensure comprehensive coverage

# 5. Security audit
@rails-security-performance: Final review before deployment
```

Agents reference:
- `.agent-os/product/overview.md` - Product vision
- `.agent-os/product/roadmap.md` - Feature priorities
- `.agent-os/product/tech-stack.md` - Technology decisions

## 📋 Best Practices

### 1. Ask the Right Agent

Match your question to the agent's expertise:
- Architecture questions → @rails-architect
- Data modeling → @rails-model-engineer
- API design → @rails-controller-engineer
- UI work → @rails-hotwire-engineer
- Testing → @rails-testing-expert
- Security/Performance → @rails-security-performance

### 2. Provide Context

```markdown
# ✅ Good
@rails-model-engineer: Add polymorphic Comments that work on Posts and Photos

# ❌ Vague
@rails-model-engineer: Add comments
```

### 3. Follow the Workflow

Start with architecture, implement layer by layer, test thoroughly, audit for security.

### 4. Trust the Analysis

On first use, agents analyze your codebase and match your patterns. Trust their recommendations—they're based on what you're already doing.

### 5. Iterate Together

```markdown
@rails-architect: Design user following system
# Review design, provide feedback
@rails-model-engineer: Implement the design from @rails-architect
# Iterate as needed
```

## 🎯 What Makes These Agents Special

### Codebase-Aware
They analyze and match YOUR patterns, not generic examples.

### Team Players
They work together as a cohesive development team.

### Consistent
They ensure new code matches existing conventions.

### Comprehensive
From architecture to testing to security—full coverage.

### Framework Agnostic
They adapt to your choices: RSpec or Minitest, Hotwire or React, Devise or custom auth.

## 📚 Agent Details

Each agent file contains:
- **Model specification** (Claude Sonnet 4.5)
- **Available tools** for their work
- **Analysis instructions** for learning your codebase
- **Best practices** for Rails development
- **Code examples** showing common patterns
- **Integration guidelines** with other agents
- **Anti-patterns** to avoid

## 🔄 Updating Agents

As your codebase evolves:
- Agents continue to learn from new code they read
- They maintain consistency with established patterns
- They can suggest improvements while respecting your conventions

## ❓ Questions & Troubleshooting

**Q: Do I need all agents?**
A: No! Use the ones you need. They work independently or together.

**Q: What if my project uses RSpec instead of Minitest?**
A: The testing agent analyzes your `spec/` directory and adapts automatically.

**Q: Can I customize the agents?**
A: Yes! Edit the agent files to add project-specific patterns or guidelines.

**Q: Do they work with Rails API-only apps?**
A: Yes! They adapt to your Rails configuration and won't suggest view code if you don't have views.

**Q: What about monolithic vs modular Rails apps?**
A: They analyze your structure and follow your organization patterns.

## 🤝 Contributing

Found a pattern these agents should handle better? Edit the agent files to add:
- New pattern examples
- Additional best practices
- Better analysis instructions
- More comprehensive examples

## 📄 License

These agents are designed to be dropped into any Rails project. Use them freely in your development workflow.

---

**Built for**: Any Ruby on Rails Application
**Version**: 1.0
**Model**: Claude Sonnet 4.5
**Integration**: Agent OS Compatible