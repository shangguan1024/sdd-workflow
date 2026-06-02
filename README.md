# SDD-Workflow v2.3 - Fusion Architecture

**Software Development Director Workflow** - Fusion of Skill (Python) + Plugin (TypeScript) for complete development lifecycle.

## 🚀 Fusion Architecture

```
┌──────────────────────────────────────────────┐
│  Plugin (opencode-sdd-workflow TypeScript)   │
│  ├── Phase Gate Middleware (强制约束)        │
│  ├── Loop Detection Middleware               │
│  ├── Artifact Check Middleware               │
│  ├── Context Monitor                         │
│  ├── State Management (.sdd/state.json)     │
│  ├── CLI Tool (bin/sdd.js)                   │
│  └── Tool Commands (sdd_init, sdd_start...)  │
└──────────────────────────────────────────────┘
                    ↓ 注入上下文
┌──────────────────────────────────────────────┐
│  Skill (sdd-workflow Python)                 │
│  ├── Phase Prompts (Phase 0-6 指导)          │
│  ├── Detailed Documentation                  │
│  ├── Design Templates (Markdown)             │
│  ├── Interface Examples (8-dimension)        │
│  └── Dependency Examples (5-dimension)       │
└──────────────────────────────────────────────┘
```

**Role Division:**
- **Plugin = "Must do" (强制约束，阻止跳过阶段)**
- **Skill = "How to do" (引导模板，详细步骤说明)**

## 📦 Installation

### Install Plugin (TypeScript)

```bash
npm install opencode-sdd-workflow

# Or in opencode.json:
{
  "plugin": ["opencode-sdd-workflow"]
}
```

### Install Skill (Python)

```json
{
  "skills": {
    "paths": ["~/.config/opencode/skills/sdd-workflow"]
  }
}
```

### Recommended: Install Both

```json
{
  "plugin": ["opencode-sdd-workflow"],
  "skills": {
    "paths": ["~/.config/opencode/skills/sdd-workflow"]
  }
}
```

## 🎯 Quick Start

### 1. Using CLI (Plugin)

```bash
# Install globally
npm install -g opencode-sdd-workflow

# Initialize project
sdd init

# Start feature development
sdd start user-auth

# Check status
sdd status

# Resume interrupted workflow
sdd resume user-auth
```

### 2. Using Tool Commands (Plugin in opencode dialog)

```
"调用 sdd_init 工具初始化项目"
"调用 sdd_start 工具，参数 feature=user-auth"
"调用 sdd_gate 工具，参数 phase=1 action=check"
```

### 3. Using Skill Documentation

AI automatically reads:
- `SKILL.md` - Phase overview
- `phases-reference.md` - Detailed steps
- `design-doc-template.md` - Design template
- `interface-example.md` - 8-dimension interface
- `dependency-example.md` - 5-dimension dependency

## 🏗️ 7-Phase Workflow

| Phase | Name | Plugin Gate | Skill Guidance |
|-------|------|-------------|----------------|
| 0 | Research & Understanding | Blocks edit/write/bash | phases-reference.md Phase 0 |
| 1 | Requirements & Design | Blocks bash | design-doc-template.md |
| 2 | Implementation Planning | Open | task_plan_template.md |
| 3 | Module Development | Open | Phase 3 detailed steps |
| 4 | Integration & Testing | Open | Phase 4 detailed steps |
| 5 | Code Quality Review | Open | Phase 5 detailed steps |
| 6 | Memory Persistence | Open | Phase 6 detailed steps |

## 📄 Document Structure

### Plugin Generated (Auto)
- `.sdd/state.json` - State persistence
- `.sdd/project.json` - Project config
- `CONSTITUTION/core.md` - Core principles
- `docs/features/<feature>/findings.md` - Basic template
- `docs/features/<feature>/task_plan.md` - Basic template

### Skill Templates (AI Reads)
- `phases-reference.md` - 251 lines detailed steps
- `design-doc-template.md` - Complete design template
- `interface-example.md` - 8-dimension interface example
- `dependency-example.md` - 5-dimension dependency example
- `visualization-guide.md` - PlantUML/Mermaid examples

## 🔧 Plugin Tools

- `sdd_init`: Initialize project
- `sdd_start`: Start feature (Phase 0)
- `sdd_resume`: Resume workflow
- `sdd_status`: Show status
- `sdd_complete`: Complete workflow (Phase 6)
- `sdd_gate`: Phase gate operations (check/approve/block)
- `sdd_refresh`: Force context refresh
- `sdd_memory_timeline`: Memory timeline (Layer 2)
- `sdd_memory_details`: Memory details (Layer 3)

## 📊 Deleted Redundant Code

**Plugin replaced these Skill modules:**
- ✅ `middleware/` (entire directory)
- ✅ `scripts/` (entire directory)
- ✅ `src/cli.py`
- ✅ `src/memory_manager.py`
- ✅ `src/config_manager.py`
- ✅ `src/project_initializer.py`
- ✅ `src/phases/` (entire directory)

**Skill preserved:**
- ✅ All documentation files (*.md)
- ✅ All templates (Markdown format)
- ✅ All examples (interface, dependency, visualization)
- ✅ All tests (for validation)

## 📝 Example Workflow

```bash
# 1. Initialize project
sdd init

# 2. Start feature (Phase 0: Research)
sdd start user-auth

# Plugin automatically blocks edit/write/bash
# AI reads Skill Phase 0 guidance
# AI uses read/glob/grep for research

# 3. Gate check Phase 1
sdd gate 1 check

# Plugin shows requirements:
# - findings.md has Phase 0 section
# - 5+ files analyzed
# - 2+ citations
# - 2+ constraints

# 4. Approve Phase 1 gate
sdd gate 1 approve

# Plugin transitions to Phase 1
# Plugin injects Phase 1 prompt
# AI reads Skill Phase 1 guidance

# 5. Design document generated
# AI reads design-doc-template.md

# 6. Continue Phase 2-6...
```

## 🆕 Version History

- **v2.3**: Fusion architecture (Plugin + Skill)
- **v2.2**: Python-only implementation
- **v2.1**: Document optimization

See [CHANGELOG.md](CHANGELOG.md) for details.

## 💬 Support

- **Plugin Issues**: https://github.com/anomalyco/opencode/issues
- **Skill Issues**: https://github.com/anomalyco/opencode/issues

---

**Built with ❤️ by opencode team**