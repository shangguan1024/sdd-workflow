# SDD-Workflow Usage Guide

## Quick Start

### 1. Load Skill
```
/opencode use using-superpowers
/opencode use sdd-workflow
```

### 2. Initialize Project (Optional)
Use `sdd_init` tool to initialize project structure:
- `.sdd/state.json` - Workflow state
- `CONSTITUTION/core.md` - Core principles
- `docs/features/` - Feature documentation directory

### 3. Start Feature (Phase 0)
Use `sdd_start` tool with feature name to begin Phase 0.

## Tool Commands

| Tool | Description |
|------|-------------|
| `sdd_init` | Initialize project structure |
| `sdd_start` | Start feature (Phase 0: Research) |
| `sdd_resume` | Resume interrupted workflow from checkpoint |
| `sdd_status` | Show current phase, feature, edit counts |
| `sdd_complete` | Force complete workflow (Phase 6) |
| `sdd_gate` | Phase gate check/approve/block operations |
| `sdd_refresh` | Force context refresh |
| `sdd_memory_timeline` | Memory timeline (Layer 2: Progressive Disclosure) |
| `sdd_memory_details` | Memory details (Layer 3: Full Disclosure) |

## Workflow Example

```
# 1. Initialize project (optional)
sdd_init

# 2. Start feature (Phase 0: Research)
sdd_start feature="user-auth"

# Phase 0 Guidance:
# - Read 5+ specific files
# - Cite 2+ external sources
# - Document constraints and alternatives
# - Use comprehensive-research-agent skill

# 3. Gate check Phase 1
sdd_gate phase=1 action=check

# Shows requirements:
# - findings.md has Phase 0 section
# - 5+ files analyzed
# - 2+ citations
# - Constraints documented

# 4. Approve Phase 1 gate (requires human confirmation)
sdd_gate phase=1 action=approve

# Transitions to Phase 1
# Use brainstorming skill before design

# 5. Continue Phase 2-6...
# Each phase requires explicit approval
```

## Phase Gate Operations

| Action | Description |
|--------|-------------|
| `check` | Show phase gate requirements (no transition) |
| `approve` | Request human confirmation, then transition |
| `block` | Force stay in current phase |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Skill not loaded | Run: `/opencode use sdd-workflow` |
| Phase gate blocking | Complete current phase requirements first |
| Context drift | Run: `sdd_refresh` to reload key requirements |

## Dependencies

SDD-Workflow integrates with:
- `brainstorming` - Phase 1 design exploration
- `writing-plans` - Phase 2 implementation planning
- `subagent-driven-development` - Phase 3 parallel execution
- `verification-before-completion` - Phase 4 testing verification
- `requesting-code-review` - Phase 5 quality review
- `memory-systems` - Phase 6 persistence architecture

## Project Structure

```
project/
├── .sdd/
│   └── state.json           # Workflow state
│   └── project.json         # Project config
├── CONSTITUTION/
│   └── core.md              # Core principles
├── PROJECT_STATE.md         # Global project state
├── AGENTS.md                # AI persistence instructions
└── docs/
    └── features/
        └── <feature>/
            ├── findings.md     # Research findings
            ├── design.md       # Design document
            ├── task_plan.md    # Implementation plan
            └── reviews/        # Code reviews
```