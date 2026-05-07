# SDD-Workflow 上下文遗忘风险报告

## 问题诊断

### 现状分析

**会遗忘上下文吗？答案：是的，在特定场景下会。**

---

## 风险场景

### HIGH RISK: Phase 3 大量编辑期间

**问题描述**：
- Phase 3 (Module Development) 是执行时间最长的阶段
- LLM 可能进行 50+ 次文件编辑操作
- Context window 有限（通常 ~200k tokens）
- 早期需求、设计决策、约束条件被挤出 context window

**现有保护**：
1. ✅ Phase 3 开始时强制刷新（`Phase3Orchestrator.execute()` line 51）
2. ✅ Step 完成后检查刷新（`_check_and_refresh_context`）
3. ❌ **Step 执行期间无保护**（大量编辑操作无监控）

**ContextMonitor 问题**：
- `Director.record_edit()` 存在但从未被调用
- LLM 调用 `write_file/edit_file` 时，Python 无法拦截
- ContextMonitor 是被动监控，无法主动触发

**后果**：
- LLM 开始偏离原始需求/设计
- 实现方向错误，但直到 Step 完成才发现
- Phase 3-5 期间可能已经严重偏离

---

### MEDIUM RISK: Session 恢复后注入内容有限

**问题描述**：
- `inject_memory_context()` 仅注入 Progressive Disclosure Layer 1
- Layer 1 是索引表（ID + Type + Title），无详细内容
- 早期详细讨论、设计理据、研究发现不可见

**现有保护**：
1. ✅ Layer 2/3 提供方法（`get_memory_timeline`, `get_memory_full_details`）
2. ❌ **LLM 不知道需要调用这些方法**

**后果**：
- LLM 仅看到索引，看不到详情
- 可能忽略早期关键决策的理据
- 重复讨论已解决的问题

---

### LOW RISK: Phase transitions 上下文丢失

**问题描述**：
- Phase 1 → Phase 2 → Phase 3 之间，context 可能被压缩
- Phase 边界摘要写入文件，但注入内容有限

**现有保护**：
1. ✅ `PhaseCompressionMiddleware` 检查摘要存在
2. ✅ 每个摘要包含 5 要素（完成、决策、问题、待解决、下一阶段）
3. ✅ Session 恢复时注入 task_plan.md, findings.md, progress.md

**后果**：
- Phase 边界保护较好，风险较低

---

## 根本原因

### ContextMonitor 被动监控

**设计缺陷**：
- `record_edit()` 需要外部调用
- LLM 工具调用不在 Python 控制流内
- 无法自动拦截 `write_file/edit_file` 调用

**代码验证**：
```python
# src/director.py:143
def record_edit(self, file_path: str):
    self._context_monitor.record_edit(file_path)
    should_refresh, reason = self._context_monitor.should_refresh()
    if should_refresh:
        # ... 刷新上下文
```

**问题**：这个方法从未被调用！

---

### Progressive Disclosure 依赖 LLM 主动行为

**设计缺陷**：
- Layer 1 自动注入，但 Layer 2/3 需要主动调用
- LLM 不知道可以调用 `get_memory_timeline()` 和 `get_memory_full_details()`
- 注入内容有限（仅索引表）

**代码验证**：
```python
# src/director.py:369
indices = disclosure.get_index(limit=15)  # 仅 Layer 1
index_table = disclosure.format_index_table(indices)
context.metadata["injected_context"] = index_table  # 仅注入索引
```

**问题**：LLM 看不到完整需求/设计详情！

---

## 唯一可靠保护

### Phase 6 AGENTS.md 全量快照

**保护机制**：
- Phase 6 生成完整的 `AGENTS.md`
- 包含全部需求、设计决策、实现文件、审查制品
- Session 恢复时注入 AGENTS.md 前 1000 字符

**问题**：
- Phase 6 是最后阶段，Phase 3-5 期间可能已偏离
- AGENTS.md 仅在特性完成后生成
- 无法保护 Phase 3-5 执行期间的上下文

---

## 解决方案

### 方案1: 强制 Phase 3 分段执行

**描述**：将 `StepImplementModules` 拆分为多个 sub-steps

**实现**：
```python
# 每 N 个文件编辑后，强制注入上下文摘要
for i, module in enumerate(modules):
    if i % 5 == 0:  # 每 5 个模块后刷新
        self._check_and_refresh_context(context, f"Progress: {i}/{len(modules)}")
    # 实现模块
```

**优点**：控制编辑次数，定期刷新
**缺点**：需要改变 Phase 3 执行模式

---

### 方案2: 提高 Progressive Disclosure 默认层级

**描述**：默认注入 Layer 2（时间线）而非 Layer 1

**实现**：
```python
# 当前：仅注入 Layer 1
indices = disclosure.get_index(limit=15)
index_table = disclosure.format_index_table(indices)

# 改进：注入 Layer 2
timelines = disclosure.get_timeline()
timeline_content = disclosure.format_timeline_context(timelines)
context.metadata["injected_context"] = timeline_content
```

**优点**：
- LLM 看到需求详情、设计理据、时间上下文
- 不依赖 LLM 主动调用

**缺点**：
- 消耗更多 tokens（~200-300 tokens/节点）

---

### 方案3: 工具调用后自动触发 record_edit

**描述**：OpenCode 平台提供工具调用钩子

**实现**：
```python
# 需要平台支持
@tool_call_hook("write_file", "edit_file")
def after_tool_call(tool_name, result, context):
    director = context.metadata.get("_director")
    if director:
        director.record_edit(result.file_path)
```

**优点**：真正的自动监控
**缺点**：依赖平台支持（需要 OpenCode 提供 hook）

---

### 方案4: 在注入 context 后添加提示

**描述**：明确告诉 LLM 可调用方法

**实现**：
```python
# 在 inject_memory_context 后添加提示
prompt = """
Context injected (Progressive Disclosure Layer 1).

To get more details, call these methods:
- get_memory_timeline(around_id="<node_id>")  # Get chronological context
- get_memory_full_details(ids=["<node_id1>", "<node_id2>"])  # Get full content

Current memory nodes:
{index_table}
"""
print(prompt)
```

**优点**：LLM 知道可以调用方法
**缺点**：LLM 可能不主动调用

---

## 推荐方案

### 组合方案：方案2 + 方案4

**立即实施**：
1. 提高 Progressive Disclosure 默认层级（Layer 2）
2. 在注入后明确提示 LLM 可调用方法

**代码改动**：
```python
# src/director.py: _inject_with_progressive_disclosure

# Layer 2: 获取时间线（包含详情）
timelines = disclosure.get_timeline()
timeline_content = disclosure.format_timeline_context(timelines)

# 注入到 context
context.metadata["injected_context"] = timeline_content

# 添加提示
prompt = f"""
Context injected (Progressive Disclosure Layer 2 - Timeline).

You can see requirement details, design rationale, and chronological context.

To get even more details for specific nodes:
- get_memory_full_details(ids=["node_id_1", "node_id_2"])

Current memory timeline:
{timeline_content}
"""
print(prompt)
```

**效果**：
- LLM 看到 Layer 2（需求详情 + 设计理据 + 时间上下文）
- LLM 知道可以调用 `get_memory_full_details` 获取完整内容
- 不依赖平台支持，立即可实施

---

## 总结

**回答用户问题**：是的，在特定场景下会遗忘上下文。

**风险等级**：
- HIGH: Phase 3 大量编辑期间（ContextMonitor 被动监控）
- MEDIUM: Session 恢复后注入内容有限（仅 Layer 1）
- LOW: Phase transitions（保护较好）

**推荐解决**：
- 提高 Progressive Disclosure 默认层级（Layer 2）
- 在注入后明确提示 LLM 可调用方法
- 或等待平台支持工具调用钩子（真正的自动监控）