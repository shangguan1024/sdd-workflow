# SDD-Workflow 上下文管理改进报告

## 改进完成（2026-05-07）

### 已实施的改进

#### ✅ Progressive Disclosure 默认层级提升

**改进内容**：
- **从 Layer 1（索引）改为 Layer 2（时间线 + 详情）**
- LLM 现在可以看到：
  - 需求完整内容（而非仅标题）
  - 设计决策理据（rationale）
  - 时间上下文（chronological order）

**代码改动**：
```python
# 之前：仅注入 Layer 1
indices = disclosure.get_index(limit=15)
index_table = disclosure.format_index_table(indices)

# 改进：注入 Layer 2
timelines = disclosure.get_timeline(before=5, after=5)
timeline_content = disclosure.format_timeline_context(timelines)
```

**效果**：
- LLM 看到 ~200-300 tokens/节点（vs ~50-100 tokens/节点）
- 包含内容摘要（前 200 字符）
- 包含理据和备选方案

---

#### ✅ 明确提示信息告知 LLM 可调用方法

**改进内容**：
- 在注入后打印提示信息到 stdout
- 明确告知 LLM 如何获取更多详情

**提示内容**：
```
Context Injected: Progressive Disclosure Layer 2

You now have access to:
  - Requirement details
  - Design decision rationale
  - Chronological context

To get even more details for specific nodes:
  - Call get_memory_full_details(ids=['node_id_1', 'node_id_2'])
  - This will show complete content + alternatives + rationale
```

**效果**：
- LLM 知道可以调用 `get_memory_full_details()`
- 不依赖 LLM 主动发现方法

---

#### ✅ 增加注入内容长度

**改进内容**：
- AGENTS.md 注入长度：1000 chars -> 2000 chars
- 时间线范围：before=5, after=5（共最多 10 个节点）

**效果**：
- 更多上下文内容注入
- 减少遗忘风险

---

### 风险缓解效果

**之前的风险**：
- Phase 3 大量编辑期间：HIGH RISK
- Session 恢复后注入内容有限：MEDIUM RISK

**改进后**：
- Session 恢复后注入 Layer 2：**MEDIUM -> LOW**
- LLM 看到需求详情和设计理据：**大幅降低遗忘风险**

**剩余风险**：
- Phase 3 大量编辑期间仍无自动刷新（需要平台支持工具调用钩子）
- 但注入内容更丰富，降低了偏离概率

---

### Token 成本对比

| 层级 | Token 成本 | 内容 | 适用场景 |
|------|-----------|------|---------|
| Layer 1（索引） | ~50-100 tokens/节点 | ID + Type + Title | 快速浏览，查找特定节点 |
| Layer 2（时间线） | ~200-300 tokens/节点 | 内容摘要 + 理据 | **默认注入** |
| Layer 3（完整详情） | ~500-1000 tokens/节点 | 完整内容 + 备选方案 | 深入分析特定节点 |

**决策**：
- 默认注入 Layer 2（平衡 token 成本和上下文完整性）
- Layer 3 仅在 LLM 主动调用时使用

---

### 测试验证

**测试文件**：`tests/test_layer2_improvement.py`

**测试内容**：
- ✅ Layer 2 注入包含详情
- ✅ Director 注入 Layer 2
- ✅ 提示信息明确
- ✅ Token 成本对比

**测试结果**：全部通过

---

### 待实施改进

#### Phase 3 定期上下文注入机制

**问题**：
- Phase 3 大量编辑期间无自动刷新
- ContextMonitor 被动监控，无法拦截 LLM 工具调用

**解决方案**：
- **方案A**：等待平台支持工具调用钩子（最优）
- **方案B**：Phase 3 分段执行，每 N 个模块后强制注入（需要修改执行流程）

**当前状态**：待定（依赖平台支持或用户需求）

---

### 使用建议

**对用户的建议**：
1. **信任 Progressive Disclosure**：现在默认注入 Layer 2，包含详情
2. **LLM 会知道调用方法**：提示信息会告知 LLM 如何获取完整详情
3. **Phase 3 注意**：如果长时间编辑，建议手动运行 `sdd resume` 刷新上下文
4. **Phase 6 是可靠保护**：AGENTS.md 全量快照确保最终完整性

**对开发者的建议**：
1. 如果遇到 LLM 偏离需求，立即运行 `sdd resume`
2. 查看 `.sdd/current_context.md` 了解注入内容
3. 使用 `get_memory_full_details(ids=['xxx'])` 获取完整详情

---

### 总结

**改进状态**：✅ 主要改进已实施
- Progressive Disclosure 默认 Layer 2
- 明确提示信息
- 增加注入长度

**效果**：大幅降低上下文遗忘风险
- Session 恢复：MEDIUM -> LOW
- LLM 看到需求和设计详情

**剩余风险**：Phase 3 自动刷新（待平台支持）

**生产就绪**：改进后的 SDD-Workflow 更可靠