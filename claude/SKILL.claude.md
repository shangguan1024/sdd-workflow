---
name: sdd-workflow
description: Use when developing a software feature, fixing a bug, or refactoring code that requires an end-to-end development workflow with phase gates, structured design/planning/verification/review documentation, and cross-phase memory handoff.
---

# SDD-Workflow v2.5（Claude Code 版）

规范化的软件研发工作流：7 个 Phase，每个 Phase 之间由 **Phase Gate** 强制门控——未完成当前 Phase 并得到用户确认，就无法进入下一 Phase。

## CLI 命令

本 skill 的状态机与工件产出由一个 CLI 引擎驱动。**命令前缀**（下文简写为 `sdd`）：

```
node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js"
```

例如 `sdd gate 1 check` 实际执行：

```bash
node "__SDD_CLAUDE_DIR__/engine/bin/sdd.js" gate 1 check
```

## 常用命令对照（opencode 工具 → Claude Code CLI）

| 操作 | opencode 工具 | Claude Code CLI |
|------|--------------|-----------------|
| 初始化项目 | `sdd_init` | `sdd init` |
| 开始功能（进入 Phase 0） | `sdd_start feature="X"` | `sdd start X` |
| 查看状态 | `sdd_status verbose=true` | `sdd status --verbose` |
| 恢复工作流 | `sdd_resume feature="X"` | `sdd resume X` |
| 完成工作流 | `sdd_complete feature="X"` | `sdd complete X` |
| 上下文刷新 | `sdd_refresh reason="..."` | `sdd refresh ...` |
| Gate 检查 | `sdd_gate phase=N action=check` | `sdd gate N check` |
| Gate 批准 | `sdd_gate phase=N action=approve confirmed=true` | `sdd gate N approve --confirmed true` |
| Gate 阻止 | `sdd_gate phase=N action=block` | `sdd gate N block` |
| 回滚 | `sdd_rollback target_phase=N code_scope="..." confirmed=true` | `sdd rollback --target_phase N --code_scope <scope> --confirmed true` |

> 子技能调用：opencode 的 `skill("name")` 在本环境中改为「使用 `name` 技能」。当前 Phase 的推荐技能会由 hook 自动注入（每次提交 prompt 时），无需手动 dispatch。

## 7 个 Phase 概览

| Phase | 名称 | 默认主技能 | 产出 | 进入下一 Phase 的 Gate |
|-------|------|-----------|------|----------------------|
| 0 | Research & Requirement Clarification | *(无，按文档内置步骤)* | `findings.md`（Phase 0 section） | `gate 1` |
| 1 | Requirements & Design | `brainstorming` | `design.md` | `gate 2` |
| 2 | Implementation Planning | `writing-plans` | `task_plan.md` | `gate 3` |
| 3 | Module Development | `subagent-driven-development` | 代码变更 | `gate 4` |
| 4 | Integration & Testing | `verification-before-completion` | 测试结果（含命令输出） | `gate 5` |
| 5 | Code Quality Review | `requesting-code-review` | `reviews/*.md` | `gate 6` |
| 6 | Memory Persistence | *(无，按文档内置步骤)* | `PROJECT_STATE.md` / `AGENTS.md` | `complete` |

> Phase 0 与 Phase 6 的默认主技能（`comprehensive-research-agent`、`memory-systems`）在 Claude Code 中未安装——按 `phases-reference.md` 的内置步骤执行即可，门控与工件产出不受影响。

## 快速开始

```bash
sdd init                 # 1. 初始化项目（生成 .sdd/、CONSTITUTION/、docs/）
sdd start user-auth      # 2. 开始功能，进入 Phase 0
sdd status --verbose     # 3. 查看当前 Phase / feature / 编辑计数
```

随后按 Phase 流程推进：

1. **读文档**：用 Read 工具读 `phases-reference.md` 中当前 Phase 的章节（任务 / Gate / 产出格式）。
2. **调子技能**（如可用）：使用 hook 注入的当前 Phase 主技能（如 `brainstorming`）。
3. **执行任务**：产出该 Phase 的工件（findings/design/task_plan 等）。
4. **Gate 检查**：`sdd gate N check`（N 为目标 Phase 编号，即当前 Phase + 1）。
5. **Gate 批准**：`sdd gate N approve` → 会提示需要人工确认 → 询问用户 → 用户同意后 `sdd gate N approve --confirmed true`。

## Phase Gate 协议（强制）

- 每个 Phase 必须先 `check` 通过，再 `approve`，且 `approve` **必须经用户确认**后加 `--confirmed true` 才真正过渡。
- hook 会强制执行工具限制：**Phase 0 禁止 `Bash`/`Edit`**（只允许 Read/Glob/Grep/Write，且 Write 仅限 `docs/features/<feature>/`）；**Phase 1 禁止 `Bash`**；Phase 2+ 放行全部工具。
- 单文件编辑 ≥ 15 次会被 hook 硬性阻止，≥ 5 次会收到方向提醒。
- 尝试跳过 gate 直接进入下一 Phase 会被 hook 拒绝。

## 回滚（rollback）

```bash
sdd rollback --target_phase 2 --code_scope related --confirmed true   # 回滚 SDD 状态+文档+关联代码（推荐）
sdd rollback --target_phase 2 --code_scope none --confirmed true      # 只回滚 SDD 状态+文档，不碰代码
sdd rollback --target_phase 2 --code_scope all --confirmed true       # 全量回滚一切
sdd rollback --target_phase 2 --code_scope related                    # 仅查看回滚计划（不执行）
```

`code_scope` 语义：`none` = 只回 SDD 状态+文档；`related` = 额外回 task_plan.md 中列出的代码；`all` = 回滚所有变更。回滚依赖每次 gate 批准时记录的 git SHA（`checkpoint.json`）。

## 技能分发（配置驱动）

每个 Phase 的主技能由 `.sdd/workflow_config.json` 配置驱动（不硬编码）：

- `skills` 字段非空 → **完全替换**该 Phase 的默认主技能
- `additional_skills` 字段 → 在主技能之后追加（始终追加）
- 例：`{ "phases": [{ "id": 1, "skills": ["brainstorming", "test-driven-development"], "additional_skills": ["code-review-quality"] }] }`

## 文档索引

| 文档 | 用途 | Phase |
|------|------|-------|
| `phases-reference.md` | Phase 0–6 详细步骤 + Gate 要求 | All |
| `design-doc-template.md` | 设计文档 Total-Part 模板 | 1 |
| `interface-example.md` | 8 维接口定义示例 | 1 |
| `dependency-example.md` | 5 维依赖分析示例 | 1 |
| `visualization-guide.md` | PlantUML/Mermaid 规范 | All |
| `USAGE.md` | 使用示例（含 opencode 版遗留安装说明） | Setup |

## Red Flags（禁止）

- ❌ 未读 `phases-reference.md` 就开始执行
- ❌ 未调用当前 Phase 的推荐子技能
- ❌ 跳过 `sdd gate N check` 直接 approve
- ❌ Gate 未通过就尝试下一 Phase
- ❌ Phase 1 设计阶段跳过知识库直接代码搜索（Knowledge Base First Principle）
