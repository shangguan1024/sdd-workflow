# SDD-Workflow v2.4

Software Development Director Workflow: a 7-phase skill designed to run with `E:/workspace/coding/tools/sdd-workflow-plugin`.

## Plugin Pairing

Configure opencode with both the plugin and this skill:

```json
{
  "plugin": [
    "E:/workspace/coding/tools/sdd-workflow-plugin/dist/index.js"
  ],
  "skills": {
    "paths": [
      "C:/Users/shangguanjingshi/.config/opencode/skills/sdd-workflow"
    ]
  }
}
```

Build the plugin if needed:

```bash
cd E:/workspace/coding/tools/sdd-workflow-plugin
npm install
npm run build
```

## Quick Start

```text
sdd_init template=standard
sdd_start feature=<feature>
sdd_gate phase=1 action=check
```

CLI fallback:

```bash
node E:/workspace/coding/tools/sdd-workflow-plugin/bin/sdd.js init
node E:/workspace/coding/tools/sdd-workflow-plugin/bin/sdd.js start <feature>
```

## Documentation

| File | Purpose |
|------|---------|
| `SKILL.md` | Source of truth for plugin coordination, tools, phases, gates, and artifacts |
| `USAGE.md` | Setup and operational commands |
| `phases-reference.md` | Detailed Phase 0-6 steps and gate checks |
| `design-doc-template.md` | Total-Part design document structure |
| `interface-example.md` | 8-dimension public interface definition |
| `dependency-example.md` | 5-dimension dependency analysis |
| `visualization-guide.md` | PlantUML and Mermaid rules |
| `templates/task_plan_template.md` | Task plan starter template |
| `templates/change_summary_template.md` | Optional final handoff summary template |

## 7-Phase Workflow

```text
Phase 0: Research & Understanding
Phase 1: Requirements & Design
Phase 2: Implementation Planning
Phase 3: Module Development
Phase 4: Integration & Testing
Phase 5: Code Quality Review
Phase 6: Memory Persistence
```

The plugin enforces gates and state. The skill explains how to satisfy them.
