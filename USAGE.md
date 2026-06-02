# SDD-Workflow Usage Guide

## Quick Start

### 1. Load Skill
```
/opencode use using-superpowers
/opencode use sdd-workflow
```

### 2. CLI Commands (Plugin)
```bash
sdd init              # Initialize project
sdd start <feature>   # Start feature (Phase 0)
sdd resume <feature>  # Resume workflow
sdd status            # Show status
sdd complete          # Complete workflow
sdd gate <phase> <action>  # Gate operations
```

### 3. Tool Commands (Plugin in opencode dialog)
- `sdd_init`: Initialize project
- `sdd_start`: Start feature (Phase 0)
- `sdd_gate`: Phase gate check/approve
- `sdd_refresh`: Context refresh
- `sdd_memory_timeline`: Memory timeline (Layer 2)
- `sdd_memory_details`: Memory details (Layer 3)

## CLI Command Details

| Command | Description |
|---------|-------------|
| `sdd init` | Initialize project structure (.sdd/, CONSTITUTION/, docs/) |
| `sdd start <feature>` | Start feature development (Phase 0: Research) |
| `sdd resume <feature>` | Resume interrupted workflow from checkpoint |
| `sdd status` | Show current phase, feature, edit counts |
| `sdd complete` | Force complete workflow (Phase 6) |
| `sdd gate <phase> check` | Show phase gate requirements |
| `sdd gate <phase> approve` | Request human confirmation, transition phase |

## Workflow Example

```bash
# 1. Initialize project
sdd init

# 2. Start feature (Phase 0: Research)
sdd start user-auth

# Plugin blocks edit/write/bash
# AI reads Phase 0 guidance from Skill
# AI uses read/glob/grep for research

# 3. Gate check Phase 1
sdd gate 1 check

# Plugin shows requirements:
# - findings.md has Phase 0 section
# - 5+ files analyzed
# - 2+ citations

# 4. Approve Phase 1 gate
sdd gate 1 approve

# Plugin transitions to Phase 1
# AI reads Phase 1 guidance from Skill

# 5. Continue Phase 2-6...
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `'sdd' not recognized` | Add to PATH: `$env:PATH += ";<SKILL_DIR>\bin"` |
| Skill not loaded | Run: `/opencode use sdd-workflow` |
| Permission denied | Check PROJECT_STATE.md read/write permissions |

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