# SDD-Workflow v2.3

**Software Development Director Workflow** - 7-phase workflow with mandatory gates.

## Installation

```json
{
  "plugin": ["opencode-sdd-workflow"],
  "skills": {
    "paths": ["~/.config/opencode/skills/sdd-workflow"]
  }
}
```

## Quick Start

```bash
sdd init                    # Initialize project
sdd start <feature>         # Start feature (Phase 0)
sdd status                  # Check current phase
sdd gate <phase> approve    # Transition phase (requires confirmation)
sdd resume <feature>        # Resume interrupted workflow
```

## Documentation

| File | Purpose |
|------|---------|
| `SKILL.md` | Phase overview, key principles |
| `phases-reference.md` | Phase 0-6 detailed steps |
| `design-doc-template.md` | Total-Part design structure |
| `interface-example.md` | 8-dimension interface definition |
| `dependency-example.md` | 5-dimension dependency analysis |
| `visualization-guide.md` | PlantUML/Mermaid usage |
| `usage.md` | CLI commands and workflow examples |

## 7-Phase Workflow

```
Phase 0: Research & Understanding
Phase 1: Requirements & Design
Phase 2: Implementation Planning
Phase 3: Module Development
Phase 4: Integration & Testing
Phase 5: Code Quality Review
Phase 6: Memory Persistence
```

Each phase requires explicit human approval before transition.

## Support

- Issues: https://github.com/anomalyco/opencode/issues