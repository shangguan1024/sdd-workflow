---
name: sdd-workflow
description: "Use when developing a software feature, fixing a bug, or refactoring code that requires end-to-end development workflow with phase gates and design documentation."
version: "2.2"
author: "opencode team"
categories:
  - workflow
  - multi-agent
  - software-development
enforcement:
  phase_gate: true
dependencies:
  - brainstorming@^1.0.0
  - writing-plans@^1.0.0
  - subagent-driven-development@^1.0.0
  - verification-before-completion@^1.0.0
  - code-review-quality@^1.0.0
---

# SDD-Workflow v2.2

## Overview

Complete 7-phase workflow (Phase 0-6) for software development with mandatory phase gates and Total-Part design documentation.

## When to Use

- Software feature development (large or standard)
- Bug fixing
- Code refactoring
- Any task requiring systematic development process

## Phase Overview

| Phase | Name | Skill | Gate |
|-------|------|-------|------|
| 0 | Research & Understanding | understanding | Anti-Superficiality Check |
| 1 | Requirements & Design | brainstorming | Design Approved |
| 2 | Implementation Planning | writing-plans | Plan Approved |
| 3 | Module Development | subagent-driven-dev | Compile + Unit Tests |
| 4 | Integration & Testing | verification-before-* | Integration Tests Pass |
| 5 | Code Quality Review | code-review-quality | Review Artifacts Verified |
| 6 | Memory Persistence | auto-document | Documentation Complete |

**Large features: Phase 0-6** (Scene Analysis → Understanding → Design → Planning → Development → Testing → Review → Persistence)

**Standard features: Phase 0-6** (skip Scene Analysis in Phase 0)

**Phase Prerequisites:**
- Phase N requires Phase N-1 output (sequential execution)
- Phase 0 contains Research + Understanding (combined)
- Phase 1-6 mandatory for all features

## Key Principles

### Phase Gate System (Mandatory)

Every phase transition requires Developer Confirmation Gate:

```
1. Current phase output exists?
2. Next phase input requirements met?
3. Developer explicit confirmation received?
4. If ANY is NO → STOP
```

**No exceptions:**
- Not for "simple additions"
- Not for "urgent deadlines"
- User must explicitly approve each phase

### Total-Part Design Document Structure

```
Part 1: Overall Architecture (Overview, Requirements, Module List)
Part 2: Overall Data Flow (PlantUML Component + Sequence)
Part 3: Module Decomposition (Mermaid Flowchart + 8-dim Interfaces + 5-dim Dependencies)
Part 4: Integration & Verification
```

See: `design-doc-template.md` for complete structure

### Dual Visualization

| Layer | Tool | Use |
|-------|------|-----|
| Architecture | PlantUML | Module dependencies, interaction sequences |
| Module Internal | Mermaid | Function flow, call sequences, state transitions |

See: `visualization-guide.md` for examples

## Quick Reference

### Large Feature Trigger

Complexity >= HIGH when:
- Tasks > 5
- Modules > 3
- Cross-team collaboration
- Complex business scenarios

**Large features execute all phases (0 → 1 → 2 → 3 → 4 → 5 → 6)**

**Standard features skip Scene Analysis in Phase 0, execute (Phase 0 → 1 → 2 → 3 → 4 → 5 → 6)**

### Phase 0: Research & Understanding

```
✅ Codebase analysis: 5+ specific files
✅ Technical principles: 2+ external citations
✅ Constraints: 2+
✅ Alternatives: 2+ with 3+ pros/cons each
```

### Phase 1: Design Requirements

**For all features:**
- Design document with Total-Part structure

**For large features:**
- Public Interfaces: 8-dimension deep definition (see: `interface-example.md`)
- Peripheral Module Dependencies: 5-dimension deep analysis (see: `dependency-example.md`)

### Memory Artifacts (Phase 6)

```
docs/features/<feature>/findings.md
docs/features/<feature>/task_plan.md
docs/features/<feature>/design.md
PROJECT_STATE.md
AGENTS.md
```

## Commands

```bash
sdd init                  # Initialize project
sdd start <feature>       # Start feature development
sdd resume <feature>      # Resume incomplete feature
sdd status                # View project status
sdd complete              # Force complete workflow
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skip phase gate | Return to previous phase, get explicit approval |
| Shallow understanding | Read 5+ specific files, cite external sources |
| Missing dependencies analysis | Analyze 5 dimensions for each dependency module |
| Skip testing | Run unit tests before proceeding to Phase 4 |

## Red Flags - STOP

- Code before Understanding phase
- "I already manually tested it"
- "Phase gate is just ritual"
- "This is different because..."
- Missing peripheral module analysis

**All mean: Return to appropriate phase. Start over.**

## See Also

**Reference files in this skill directory:**

- `phases-reference.md` - Phase 0-6 detailed steps and gate requirements
- `design-doc-template.md` - Complete design document structure (Part 1-4)
- `interface-example.md` - Public Interfaces 8-dimension definition with template
- `dependency-example.md` - Peripheral Module Dependencies 5-dimension analysis
- `visualization-guide.md` - PlantUML/Mermaid minimal examples