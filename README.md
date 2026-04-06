# SDD-Workflow

Software Development Director Workflow - 智能软件开发生命周期管理技能

## 作用

SDD-Workflow 是一个面向 AI Agent 的软件开发生命周期管理系统，通过 6 个阶段（需求分析 → 架构设计 → 实现规划 → 模块开发 → 代码审查 → 记忆持久化）的结构化流程，引导 AI 完成软件开发任务。

### 核心功能

- **多 Agent 协作**: 支持子 Agent 驱动的并行开发模式
- **架构感知**: 与 nexus-mapper/nexus-query 集成，提供代码架构分析和影响分析
- **TDD 支持**: 内置测试驱动开发工作流
- **代码审查**: 结构化的代码审查流程和反馈机制
- **知识图谱**: 自动维护项目知识图谱，支持快速上下文恢复

## 安装

### 前提条件

- opencode v0.5.0+
- Python 3.10+

### 安装步骤

1. 克隆仓库：
```bash
git clone git@github.com:shangguan1024/sdd-workflow.git
```

2. 将 `bin/sdd` 目录添加到系统 PATH 或项目目录

3. 使用简化命令：
```bash
sdd start        # 开始新需求开发
sdd resume       # 继续之前的开发会话
sdd status       # 查看当前项目状态
sdd graph        # 生成/查看知识图谱
sdd help         # 显示帮助
```

## 使用说明

### 完整工作流

```bash
# 1. 开始新的功能开发
sdd start

# 2. 检查当前状态
sdd status

# 3. 生成知识图谱（如果需要）
sdd graph

# 4. 中断开发后继续
sdd resume

# 5. 查看帮助
sdd help
```

### 开发阶段

1. **需求分析**: 理解用户意图，收集需求
2. **架构设计**: 设计系统架构和模块划分
3. **实现规划**: 制定详细的实现计划
4. **模块开发**: 编写代码和测试
5. **代码审查**: 审查代码质量和可维护性
6. **记忆持久化**: 保存开发知识到知识图谱

## 项目结构

```
sdd-workflow/
├── SKILL.md          # 核心技能定义
├── SKILL.yaml        # 技能配置
├── USAGE.md          # 使用指南
├── INTEGRATION.md    # 集成说明
├── bin/              # 简化命令脚本
├── evals/            # 技能评估
├── references/       # 参考文档
└── templates/        # 模板文件
```

## 依赖技能

- nexus-mapper / nexus-query: 代码架构分析
- rust-best-practices: Rust 最佳实践
- planning-with-files: 文件规划
- multi-agent-orchestration: 多 Agent 协作
- brainstorming: 头脑风暴
- code-review-quality: 代码审查
- systematic-debugging: 系统调试
- test-driven-development: 测试驱动开发
- using-git-worktrees: Git worktree 支持
