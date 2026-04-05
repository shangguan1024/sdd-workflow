# SDD-Workflow Usage Guide

## Basic Commands

### Start SDD-Workflow
```bash
/opencode use using-superpowers
/opencode use sdd-workflow
```

### Check Current Status
```bash
/opencode status
```

### Switch Development Modes
```bash
/switch-to-multi    # Multi-agent parallel development
/switch-to-single   # Single-agent sequential development
```

### Control Subagents
```bash
/pause-agents      # Pause all subagents
/resume-agents     # Resume all subagents
/abort-agents      # Terminate all subagents
```

### Resume Previous Session
```bash
/opencode resume
```

## Required Dependencies

This skill requires the following dependencies to be installed:

- `nexus-mapper`: For architecture discovery and knowledge graph generation
- `nexus-query`: For precise code structure queries during development  
- `rust-best-practices`: For Rust-specific guidance and patterns
- `planning-with-files`: For file-based planning and progress tracking
- `multi-agent-orchestration`: For coordinating multiple subagents
- `subagent-driven-development`: For subagent execution and testing

## Automatic Features

### Language Detection
SDD-Workflow automatically detects project languages and recommends appropriate skills:
- **Rust**: rust-best-practices, build-rust
- **JavaScript/TypeScript**: react-best-practices, frontend-design  
- **Python**: python-best-practices, django-patterns
- **Go**: go-best-practices, goroutine-patterns

### Architecture Discovery
When starting on a new or existing project, SDD-Workflow will:
1. Check for existing `.nexus-map/` knowledge graph
2. If not found, automatically run `nexus-mapper` to generate architecture knowledge
3. Load architecture context for intelligent requirement analysis
4. Provide impact analysis for new feature requests

### Intelligent Mode Selection
Based on project complexity, SDD-Workflow recommends development modes:
- **Multi-agent mode**: For complex projects with multiple modules
- **Single-agent mode**: For simple projects or personal development

## Project Structure Generated

SDD-Workflow creates the following standard project structure:

```
project/
├── PROJECT_STATE.md          # Global project state
├── AGENTS.md                # AI persistence instructions  
├── task_plan.md             # Main progress tracking
├── findings.md              # Research discoveries
├── progress.md              # Session logging
├── .nexus-map/              # Generated knowledge graph
│   ├── INDEX.md
│   ├── arch/
│   ├── concepts/
│   └── raw/
└── docs/
    ├── specs/               # Requirement specifications
    ├── plans/               # Implementation plans
    ├── adr/                 # Architecture decision records
    ├── snapshots/           # State snapshots
    └── reviews/             # Code review reports
```