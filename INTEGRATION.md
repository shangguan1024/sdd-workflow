# SDD-Workflow 简化命令集成指南

## 如何在 opencode 中使用简化命令

### 步骤 1: 加载 SDD-Workflow 技能

首先，您需要加载 SDD-Workflow 技能：

```
/opencode use using-superpowers
/opencode use sdd-workflow
```

### 步骤 2: 使用简化命令

一旦技能加载成功，您就可以直接使用以下简化命令：

#### `sdd start`
开始新的需求开发会话
- 自动检测项目状态
- 创建标准项目结构  
- 启动交互式需求收集流程

#### `sdd resume`
继续之前的开发会话
- 检查现有的内存工件
- 从最后一个检查点恢复上下文
- 继续执行未完成的任务

#### `sdd status`  
查看当前项目状态
- 显示 PROJECT_STATE.md 中的项目信息
- 报告 task_plan.md 的进度状态
- 显示知识图谱的可用性

#### `sdd graph`
管理知识图谱
- 查看现有的 .nexus-map/ 目录
- 如果不存在则生成新的知识图谱
- 提供架构影响分析

### 命令处理机制

当您在 opencode 中输入这些简化命令时，SDD-Workflow 技能会：

1. **识别命令模式** - 检测以 `sdd ` 开头的输入
2. **解析命令参数** - 提取具体的子命令（start, resume, status, graph）
3. **执行相应操作** - 调用内部命令处理器执行完整的工作流
4. **提供实时反馈** - 显示当前状态和下一步操作

### 集成优势

- **简化用户体验** - 无需记住复杂的技能加载命令
- **保持功能完整性** - 所有 SDD-Workflow 功能仍然可用
- **无缝集成** - 命令直接在 opencode 环境中执行
- **向后兼容** - 仍然支持传统的 `/opencode use` 命令

### 故障排除

如果简化命令不工作，请确保：

1. **技能已正确加载** - 运行 `/opencode use sdd-workflow` 
2. **在正确的上下文中** - 确保在项目目录中执行命令
3. **文件权限正常** - 确保可以读写 PROJECT_STATE.md 和相关文件

### 示例工作流

```bash
# 加载技能
/opencode use using-superpowers
/opencode use sdd-workflow

# 开始新功能开发
sdd start

# 检查状态
sdd status

# 生成知识图谱
sdd graph

# 中断后继续
sdd resume
```

这个集成确保您可以在 opencode 环境中直接使用简化的 `sdd` 命令，而不需要额外的批处理文件或系统 PATH 修改。