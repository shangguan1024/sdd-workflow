# SDD-Workflow v2.1

**Software Development Director Workflow** - Complete end-to-end development workflow with 7-phase execution (Phase 0-6).

## 🚀 Features

### 7-Phase Workflow

- **Phase 0**: Research & Understanding
- **Phase 1**: Requirements Analysis & Design
- **Phase 2**: Implementation Planning
- **Phase 3**: Module Development
- **Phase 4**: Integration & Testing
- **Phase 5**: Code Quality Review
- **Phase 6**: Memory Persistence

### Key Capabilities

✅ **Phase Gate System** -强制执行每个Phase之间的转换检查  
✅ **Checkpoint Mechanism** -多层持久化，支持崩溃恢复  
✅ **Conversation Memory** -跨会话决策记忆持久化  
✅ **Quality Harness** -自动化质量评估和Gate引擎  
✅ **Error Recovery** -增强的错误恢复和重试机制  
✅ **Nexus Map Integration** -代码库架构自动分析  
✅ **Progressive Disclosure** -上下文渐进式加载  
✅ **Privacy Filter** -敏感数据自动过滤  
✅ **Middleware Hooks** -Loop检测、Artifact检查、Phase压缩

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/shangguan1024/sdd-workflow.git
cd sdd-workflow

# Install dependencies
pip install pyyaml toml

# Optional: Install development tools
pip install pytest pytest-cov ruff mypy pre-commit
```

## 🎯 Quick Start

### 1. Initialize Project

```bash
python src/cli.py init
```

Creates:
- `CONSTITUTION/` -项目宪法（设计原则、实现规范）
- `.nexus-map/` -代码库架构分析
- `docs/` -文档目录结构
- `PROJECT_STATE.md` -项目状态聚合
- `AGENTS.md` -跨会话恢复上下文

### 2. Start Feature Development

```bash
python src/cli.py start feature-name
```

Generates optimized document structure (7 required documents):
- `docs/features/<feature>/findings.md` -统一决策记录（Phase 0-5）
- `docs/features/<feature>/design-doc.md` -详细设计
- `docs/features/<feature>/task_plan.md` -任务进度（Phase 1-6）
- `docs/features/<feature>/.sdd/conversation_memory.json` -决策记忆

### 3. Resume Feature

```bash
python src/cli.py resume feature-name
```

Loads checkpoint and conversation memory for context recovery.

### 4. Check Status

```bash
python src/cli.py status feature-name --verbose
```

Shows:
- Current phase/step
- Last checkpoint timestamp
- Memory nodes count
- Required artifacts status

### 5. Complete Feature

```bash
python src/cli.py complete
```

Generates final artifacts and marks feature as completed.

## 📄 Document Structure (Optimized v2.1)

### Required Documents (7)

| Document | Purpose | When Generated |
|----------|---------|---------------|
| **AGENTS.md** | 跨会话恢复上下文 | Phase 6 |
| **findings.md** | 统一决策记录（Phase 0-5） | Phase 0 (init) + Phase 1-5 (append) |
| **design-doc.md** | 详细设计（接口定义） | Phase 1 |
| **task_plan.md** | 任务进度（Phase 1-6） | Phase 1 (init) + Phase 2-6 (append) |
| **architecture_review.md** | 架构审查 + 需求验证（合并） | Phase 5 |
| **code_quality_review.md** | 质量审查 + 测试覆盖（合并） | Phase 5 |
| **conversation_memory.json** | 决策记忆（跨会话） | Phase 6 |

### Optimization Results

- **Document Reduction**: 17 → 7 (59% reduction)
- **Review Artifacts**: 4 → 2 (50% reduction)
- **Phase 0 Outputs**: 2 → 1 (merged into findings.md)
- **Phase 6 Outputs**: 5 → 2 (merged into AGENTS + memory)

### Document Flow

```
Phase 0 → findings.md (init with Phase 0 section)
Phase 1 → findings.md (append Phase 1) + design-doc.md + task_plan.md (init)
Phase 2 → findings.md (append Phase 2) + task_plan.md (append)
Phase 3 → findings.md (append Phase 3) + task_plan.md (append)
Phase 4 → findings.md (append Phase 4) + task_plan.md (append)
Phase 5 → findings.md (append Phase 5) + 2 review documents (merged)
Phase 6 → AGENTS.md + conversation_memory.json + finalize all
```

## 🏗️ Architecture

### Layered Modular Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 0: CLI                            │
│              (命令行解析、用户交互)                          │
├─────────────────────────────────────────────────────────────┤
│                    Layer 1: Director                        │
│         (主状态机、Gate 控制、流程编排)                       │
├─────────────────────────────────────────────────────────────┤
│               Layer 2: Phase Orchestrators                 │
│    (Phase 1-6 各阶段流程定义、Step 管理)                     │
├─────────────────────────────────────────────────────────────┤
│                    Layer 3: Capabilities                   │
│              (具体能力接口：brainstorming 等)                │
└─────────────────────────────────────────────────────────────┘

支持模块:
├── checkpoint/     多层 Checkpoint 持久化机制
├── quality/        Quality Harness Pipeline
├── memory/         Conversation Memory + Progressive Disclosure
├── nexus_map/      Nexus Map Integration
├── error_recovery/ Error Recovery Manager
├── middleware/     Middleware Hooks (Gate, Loop, Artifact, Compression)
└── rules/          MD/YAML 多格式规则支持
```

### Module Responsibilities

| 模块 | 职责 |
|------|------|
| `src/cli.py` | Layer 0: 命令行解析、用户交互 |
| `src/director.py` | Layer 1: 主状态机、Gate 控制（1655行） |
| `src/phases/` | Layer 2: Phase 1-6 流程定义 |
| `src/capabilities/` | Layer 3: 能力接口（brainstorming, writing-plans等） |
| `src/checkpoint/` | Checkpoint 管理、持久化、恢复（5个模块） |
| `src/memory/` | Conversation Memory + Progressive Disclosure（5个模块） |
| `src/quality/` | 质量评估、Gate 引擎、报告（5个模块） |
| `src/error_recovery.py` | 错误恢复、重试机制（556行） |
| `middleware/` | Middleware Hooks（4个中间件） |

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov=middleware --cov-report=html

# Run specific test
python -m pytest tests/test_director.py -v

# Run workflow test
python scripts/test_workflow.py --mock
```

## 📊 Code Quality

```bash
# Lint with Ruff
ruff check src/ middleware/ scripts/

# Format with Ruff
ruff format src/ middleware/ scripts/

# Type check with MyPy
mypy src/ middleware/

# Run all checks
pre-commit run --all-files
```

## 🔧 Configuration

Configuration files are in `config/`:

- `constitution_enforcer.yaml` - Constitution 合规检查配置
- `artifact_checker.yaml` - 制品完整性检查配置
- `loop_detection.yaml` - Doom Loop 检测配置
- `error_recovery.yaml` - 错误恢复策略配置
- `privacy_filter.yaml` - 隐私过滤规则配置
- `understanding.yaml` - Research 能力配置

## 📝 Example Workflow

### Example: Implement a new feature

```bash
# 1. Initialize project (if not done)
python src/cli.py init

# 2. Start feature development
python src/cli.py start user-authentication

# 3. Phase 0: Research (automatic)
# - Generates findings.md with Phase 0 section
# - Analyzes codebase architecture via Nexus Map
# - Anti-Superficiality validation

# 4. Phase 1: Requirements & Design (automatic)
# - Brainstorming capability generates design
# - Constitution Enforcer validates design
# - Developer confirms design

# 5. Phase 2: Implementation Planning (automatic)
# - Writing-plans capability generates plan
# - Task breakdown and priority assignment
# - Developer confirms plan

# 6. Phase 3: Module Development (automatic)
# - Subagent-driven-development executes tasks
# - Context Monitor injects context every 50 edits
# - Loop Detection prevents doom loops

# 7. Phase 4: Integration & Testing (automatic)
# - Integration tests run
# - Issues fixed automatically

# 8. Phase 5: Code Quality Review (automatic)
# - Generates 2 merged review documents:
#   - architecture_review.md (includes requirements verification)
#   - code_quality_review.md (includes test coverage)
# - Constitution Enforcer validates implementation

# 9. Phase 6: Memory Persistence (automatic)
# - Generates AGENTS.md with context recovery
# - Saves conversation_memory.json
# - Updates PROJECT_STATE.md

# 10. Mark feature as completed
python src/cli.py complete
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m pytest tests/ -v`)
5. Run quality checks (`pre-commit run --all-files`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📜 License

MIT License - see LICENSE file for details.

## 📚 Documentation

- **Engineering Analysis Report**: `docs/engineering_analysis_report.md`
- **P0 Fix Summary**: `docs/p0_fix_summary.md`
- **Document Merge Plan**: `docs/document_merge_plan_complete.md`
- **Context Loss Risk**: `docs/context_loss_risk.md`
- **Missing Features Analysis**: `docs/missing_features_analysis.md`

## 🆕 Version History

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 💬 Support

- **Issues**: https://github.com/shangguan1024/sdd-workflow/issues
- **Email**: opencode@example.com

---

**Built with ❤️ by opencode team**