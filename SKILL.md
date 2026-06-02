---
name: sdd-workflow
description: "Use when developing a software feature, fixing a bug, or refactoring code that requires end-to-end development workflow with phase gates and design documentation."
version: "2.5"
author: "opencode team"
categories:
  - workflow
  - multi-agent
  - software-development
enforcement:
  phase_gate: true
  requires_plugin: "sdd-workflow-plugin"
dependencies:
  - brainstorming@^1.0.0
  - writing-plans@^1.0.0
  - subagent-driven-development@^1.0.0
  - verification-before-completion@^1.0.0
  - code-review-quality@^1.0.0
---

# SDD-Workflow v2.5

## Plugin + Skill 配合使用（必需）

**必须同时安装 Plugin 和 Skill 才能完整工作**：

| 组件 | 角色 | 功能 |
|------|------|------|
| **Plugin** | "Must do" | 强制约束、Phase Gate、工具命令 |
| **Skill** | "How to do" | 详细指导、设计模板、示例文档 |

**安装指南**: 见 `usage.md`

## Overview

Complete 7-phase workflow (Phase 0-6) for software development with mandatory phase gates and Total-Part design documentation.

## Phase Overview

| Phase | Name | Skill | Gate |
|-------|------|-------|------|
| 0 | Research & Understanding | **comprehensive-research-agent** (MUST call at start) | Anti-Superficiality Check |
| 1 | Requirements & Design | **brainstorming** (MUST use before design) | Design + Decomposition Approved |
| 2 | Implementation Planning | **writing-plans** | Plan Approved |
| 3 | Module Development | **subagent-driven-development** | Compile + Unit Tests |
| 4 | Integration & Testing | **verification-before-completion** (MUST run before claiming done) | Integration Tests Pass |
| 5 | Code Quality Review | **requesting-code-review** (MUST use before merge) | All 4 Artifacts Verified |
| 6 | Memory Persistence | **memory-systems** | Documentation Complete |

## Tool Commands (Plugin Provided)

| Tool | Description |
|------|-------------|
| `sdd_init` | Initialize project structure |
| `sdd_start` | Start feature (Phase 0) |
| `sdd_resume` | Resume workflow from checkpoint |
| `sdd_status` | Show current phase, feature, edit counts |
| `sdd_complete` | Complete workflow (Phase 6) |
| `sdd_gate` | Phase gate operations (check/approve/block) |
| `sdd_refresh` | Force context refresh |
| `sdd_memory_timeline` | Memory timeline (Layer 2) |
| `sdd_memory_details` | Memory details (Layer 3) |

## Key Principles

### Phase Gate System (Mandatory - Enforced by Plugin)

Every phase transition is enforced by the Plugin. You CANNOT skip phase gates.

```
1. Current phase output exists?
2. Next phase input requirements met?
3. Developer explicit confirmation received?
4. If ANY is NO → STOP (Plugin blocks tools)
```

**No exceptions:**
- Not for "simple additions"
- Not for "urgent deadlines"
- User must explicitly approve each phase via `sdd_gate approve`

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
| Module Internal (Interaction) | PlantUML | Module interaction sequences |
| Module Internal (Non-interaction) | Mermaid | Function flow, state transitions |

See: `visualization-guide.md` for examples

## Phase Execution Guide

### Phase 0: Research & Understanding

**Plugin Behavior:**
- ✅ Creates `docs/features/<feature>/findings.md`
- ✅ Blocks edit/write/bash tools
- ✅ Injects Phase 0 Prompt

**AI Tasks:**
1. Read `phases-reference.md` (Phase 0 detailed steps)
2. Analyze 5+ specific files
3. Cite 2+ external sources
4. Document 2+ constraints
5. Compare 2+ alternatives (3+ pros/cons each)
6. Write to findings.md Phase 0 section

**Gate Approval:**
```
sdd_gate phase=1 action=check   # Check requirements
sdd_gate phase=1 action=approve # Request human confirmation
```

### Phase 1: Requirements & Design

**Plugin Behavior:**
- ✅ Blocks bash tool (allows edit/write)
- ✅ Injects Phase 1 Prompt

**AI Tasks:**
1. Read `design-doc-template.md`
2. Read `interface-example.md` (8-dimension)
3. Read `dependency-example.md` (5-dimension)
4. Generate design document (Total-Part structure)
5. Constitution compliance check

**Gate Approval:**
```
sdd_gate phase=2 action=approve
```

### Phase 2-6

See `phases-reference.md` for detailed execution steps.

## Red Flags - STOP

- Code before Understanding phase (Plugin will block edit/write/bash)
- "I already manually tested it"
- "Phase gate is just ritual"
- Missing peripheral module analysis

**All mean: Return to appropriate phase. Start over.**

## See Also

**Reference files in this skill directory:**

- `usage.md` - **Plugin + Skill installation and usage guide**
- `phases-reference.md` - Phase 0-6 detailed steps and gate requirements
- `design-doc-template.md` - Complete design document structure (Part 1.x-4.x)
- `interface-example.md` - Public Interfaces 8-dimension definition with template
- `dependency-example.md` - Peripheral Module Dependencies 5-dimension analysis
- `visualization-guide.md` - PlantUML/Mermaid minimal examples