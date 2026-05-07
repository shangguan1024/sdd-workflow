# SDD-Workflow Defects Report (After Deep Analysis)

## 日期：2026-05-07

## 发现的真实缺陷

### DEFECT-001 [HIGH] ErrorRecoveryManager 未集成

**位置**: src/director.py (lines 219, 316, 747, 827, 875)

**描述**: ErrorRecoveryManager 模块已创建但 Director 从未使用。所有 try-except 块仍使用普通的 Exception 处理，无错误分类或恢复尝试。

**影响**: 
- 错误被静默捕获，无分类记录
- 无自动恢复尝试
- 无错误日志持久化
- 用户无法获取错误诊断报告

**解决方案**:
```python
# 1. Director.__init__ 中添加
from .error_recovery import ErrorRecoveryManager
self._error_recovery_manager = ErrorRecoveryManager(project_root)

# 2. 替换所有 try-except 块
try:
    # operation
except Exception as e:
    error_record = self._error_recovery_manager.capture_error(
        exception=e,
        operation="start_feature",
        severity=ErrorSeverity.ERROR,
    )
    
    if self._error_recovery_manager.attempt_recovery(error_record):
        # retry operation
        return self.start_feature(command)
    
    # Generate error report
    error_report = self._error_recovery_manager.generate_error_report()
    return Result(success=False, message=error_report)
```

---

### DEFECT-002 [MEDIUM] CheckpointManager 缺少测试

**位置**: src/checkpoint/manager.py

**描述**: CheckpointManager 是会话恢复的核心模块，但没有专门的测试文件。持久化和恢复逻辑未经验证。

**影响**:
- Checkpoint bugs 可能导致会话丢失
- 无法恢复特性开发进度
- realtime_sync bugs 可能未被发现

**解决方案**:
```python
# 创建 tests/test_checkpoint_manager.py
# 测试内容:
# - save_checkpoint: 验证 JSON 写入
# - load_checkpoint: 验证恢复
# - enable_realtime_sync: 验证 30s interval
# - recovery after interruption
```

---

### DEFECT-003 [MEDIUM] start_feature phase transitions 可能缺少 middleware 检查

**位置**: src/director.py: start_feature

**描述**: run_middleware_before 在 resume_feature (line 720) 的 phase transitions 中被调用，但在 start_feature 中仅在 Phase 1 entry 时调用了一次 (line 305)。后续 phase transitions 可能缺少 Constitution 检查。

**影响**:
- Constitution violations 在新特性 workflow 中可能被忽略
- PhaseGateMiddleware 可能仅检查 Phase 1，不检查后续 phases

**解决方案**:
```python
# 在 start_feature 的 phase execution loop 中添加 middleware 检查
# 类似 resume_feature 的实现 (line 720-729)

for phase_num in range(1, 7):
    orchestrator = self.phase_orchestrators.get(Phase(phase_num))
    
    # 添加 middleware 检查
    gate_result = self.run_middleware_before(phase_num, {
        "feature_name": feature_name,
        "session_id": self._session_id,
    })
    if not gate_result.allowed:
        print(f"Phase Gate blocked: {gate_result.message}")
        return Result(success=False, message=gate_result.message)
    
    orchestrator.execute(context)
```

---

### DEFECT-004 [LOW] Privacy Filter 性能未验证

**位置**: src/memory/privacy_filter.py: _filter_text regex loops

**描述**: Privacy Filter 对每个节点执行多次 regex 匹配。对于大型 context (AGENTS.md + ConversationMemory，可能 >10k chars)，性能未知。

**影响**:
- Context injection 可能变慢
- Regex 循环可能消耗 CPU 时间

**解决方案**:
```python
# 1. Benchmark 测试
test_context_size = 10000  # chars
start_time = time.time()
filtered = privacy_filter.filter_context_summary(large_context)
elapsed = time.time() - start_time
print(f"Privacy Filter: {elapsed}s for {test_context_size} chars")

# 2. 如果性能问题:
#    - 添加缓存机制 (相同内容不重复过滤)
#    - Lazy filtering (仅在注入前过滤)
#    - 限制 regex patterns 数量
```

---

## 已验证的集成（误报澄清）

### ContextMonitor - ✅ 已正确集成

**验证**:
- Director line 266: `context.metadata["_context_monitor"] = self._context_monitor`
- Director line 710 (resume_feature): 同样设置
- base.py line 93: `_check_and_refresh_context` 从 metadata 中获取 monitor
- Phase3 line 51, 61, 68: 调用 `_check_and_refresh_context`

**结论**: ContextMonitor 已正确集成，Phase 3 可以触发 context refresh。

---

### NexusMapIntegrator - ✅ 已正确集成

**验证**:
- understanding.py line 90: `nexus_map_knowledge = self._load_nexus_map(context)`
- understanding.py line 848-890: `_load_nexus_map` 方法完整实现
- Director line 56-57: 创建 `NexusMapIntegrator` 实例

**结论**: NexusMapIntegrator 已正确集成，Understanding 阶段自动加载 nexus-map。

---

## 总结

**真实缺陷**: 4 个
- HIGH: 1 (ErrorRecoveryManager 未集成)
- MEDIUM: 2 (CheckpointManager 测试, Middleware 调用)
- LOW: 1 (Privacy Filter 性能)

**误报澄清**: 2 个
- ContextMonitor (已正确集成)
- NexusMapIntegrator (已正确集成)

**优先级修复顺序**:
1. DEFECT-001 (HIGH): ErrorRecoveryManager 集成
2. DEFECT-002 (MEDIUM): CheckpointManager 测试
3. DEFECT-003 (MEDIUM): Middleware phase transitions
4. DEFECT-004 (LOW): Privacy Filter 性能验证