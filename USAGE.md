# SDD-Workflow 简化命令使用指南

## 安装命令

将 `sdd.cmd` 文件复制到您的项目目录或添加到系统 PATH：

```bash
# 方法1: 复制到当前项目目录
copy "<SKILL_DIR>\bin\sdd.cmd" .

# 方法2: 临时添加到 PATH（Windows PowerShell）
$env:PATH += ";<SKILL_DIR>\bin"

# 方法3: 永久添加到 PATH（需要管理员权限）
setx PATH "%PATH%;<SKILL_DIR>\bin"
```

## 简化命令列表

### `sdd start`
**功能**: 开始新的需求开发
- 加载必要的技能 (using-superpowers, sdd-workflow)
- 初始化项目状态检测
- 创建标准项目结构
- 启动完整的 SDD-Workflow 开发流程
- 自动创建 git worktree 用于隔离开发
- 应用测试驱动开发 (TDD) 方法论

**使用示例**:
```bash
sdd start
```

### `sdd resume`
**功能**: 继续之前的开发会话
- 检查现有的 task_plan.md 和 PROJECT_STATE.md
- 从最后一个检查点恢复开发上下文
- 继续执行未完成的任务

**使用示例**:
```bash
sdd resume
```

### `sdd status`
**功能**: 查看当前项目状态
- 显示 PROJECT_STATE.md 中的项目信息
- 检查 task_plan.md 的任务进度状态
- 报告知识图谱 (.nexus-map/) 的可用性

**使用示例**:
```bash
sdd status
```

### `sdd graph`
**功能**: 查看或生成知识图谱
- 如果存在 .nexus-map/ 目录，显示现有知识图谱结构
- 如果不存在，创建 .nexus-map/ 目录和基本结构
- 为架构发现和影响分析准备环境

**使用示例**:
```bash
sdd graph
```

### `sdd help`
**功能**: 显示帮助信息
- 列出所有可用的简化命令
- 提供每个命令的简要说明

**使用示例**:
```bash
sdd help
```

## 完整工作流示例

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

## 故障排除

### 命令未找到
如果收到 `'sdd' is not recognized as an internal or external command` 错误：
1. 确保 `sdd.cmd` 在当前目录或 PATH 中
2. 使用完整路径运行：`.\sdd.cmd start`
3. 或者使用 PowerShell：`& .\sdd.cmd start`

### 权限问题
在某些系统上可能需要以管理员身份运行来修改系统 PATH。

## 集成说明

这些简化命令封装了 SDD-Workflow 的核心功能，但实际的智能工作流执行仍然需要通过 opencode 的技能系统。命令主要提供便捷的入口点和状态管理功能。