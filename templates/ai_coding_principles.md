# AI Coding Principles

> 基于 Andrej Karpathy 的观察和 SDD-Workflow 的工程实践

---

## 核心原则

### 1. Think Before Coding (思考优先)

**Don't assume. Don't hide confusion. Surface tradeoffs.**

LLMs often pick an interpretation silently and run with it. This principle forces explicit reasoning:

| 要求 | 说明 |
|------|------|
| **State assumptions explicitly** | 如果不确定，主动提问而非猜测 |
| **Present multiple interpretations** | 存在歧义时不要沉默选择 |
| **Push back when warranted** | 当存在更简单的方案时，主动提出 |
| **Stop when confused** | 命名不明确的地方，主动提问 |

**实践检查清单:**

```
Before coding, ask:
- [ ] 我理解用户真正想要的是什么吗？
- [ ] 我是否声明了所有关键假设？
- [ ] 我是否需要向用户提问以澄清问题？
- [ ] 我是否识别了所有潜在问题？
```

### 2. Simplicity First (简洁优先)

**Minimum code that solves the problem. Nothing speculative.**

| 禁止 | 说明 |
|------|------|
| ❌ | 实现超出需求的功能 |
| ❌ | 为单次使用创建抽象 |
| ❌ | 添加未被要求的"灵活性" |
| ❌ | 为不可能的场景添加错误处理 |
| ❌ | 200 行能解决却写成 1000 行 |

**检验:** 如果一个 senior engineer 说这个设计过度复杂，就简化。

### 3. Surgical Changes (精确改动)

**Touch only what you must. Clean up only your own mess.**

| 行为 | 规则 |
|------|------|
| **不要改进** | 相邻代码、注释、格式 |
| **不要重构** | 没有问题的代码 |
| **匹配现有风格** | 即使你会有不同做法 |
| **提到但不删除** | 发现无关的 dead code → 提到而非删除 |

| 变更产生的 orphans | 规则 |
|------------------|------|
| YOUR 变更产生的 unused imports | ✅ 删除 |
| 变更产生的 unused variables | ✅ 删除 |
| 变更产生的 unused functions | ✅ 删除 |
| 之前存在的 dead code | ❌ 除非被要求，否则不删除 |

**检验:** 每个改动的代码行都应该能追溯到用户的请求。

### 4. Goal-Driven Execution (目标驱动)

**Define success criteria. Loop until verified.**

| Instead of... | Transform to... |
|---------------|-----------------|
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test that reproduces it, then make it pass" |
| "Refactor X" | "Ensure tests pass before and after" |

**多步骤任务格式:**

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

---

## SDD-Workflow 特定规则

### Phase 执行规则

| Phase | 规则 |
|-------|------|
| **Understanding** | 必须先完成才能开始 Design |
| **Design** | 必须先完成才能开始 Plan |
| **Plan** | 必须先完成才能开始 Code |
| **Phase Gate** | 必须用户确认才能继续 |

### Constitution 规则

| 规则 | 要求 |
|------|------|
| DESIGN-001 | 单一职责 |
| DESIGN-002 | 接口分离 (≤10 方法) |
| DESIGN-003 | 依赖抽象而非具体 |
| DESIGN-004 | 无循环依赖 |
| IMPL-001 | 错误处理 (Result/Option) |
| IMPL-002 | 无裸 await |
| IMPL-003 | 必须有测试 |

### Git Workflow 规则

| 规则 | 说明 |
|------|------|
| **Commit 格式** | `<type>: <description>` |
| **分支命名** | `feature/xxx`, `fix/xxx` |
| **Atomic Commits** | 每个 commit 做一件事 |
| **Change Summary** | 每次变更必须填写 |

---

## Common Rationalizations (常见借口)

| AI 借口 | 现实 |
|---------|------|
| "这很简单，不需要设计" | 即使简单，也需要理解现有代码 |
| "看了一遍代码，大概理解了" | 列出具体文件和模块 |
| "官方文档说这样做就行" | 引用具体章节 |
| "应该没问题" | 不要假设，要验证 |
| "功能完成后再测试" | 测试先行 |
| "这是最后再优化" | 简洁性是设计出来的，不是优化出来的 |

---

## Red Flags (红旗)

出现以下情况，说明可能违反了原则：

- [ ] 开始写代码前没有明确的目标
- [ ] 直接实现而不先理解现有代码
- [ ] 实现的功能超出用户请求
- [ ] 改动范围超出请求的范围
- [ ] 没有先写测试
- [ ] 用户要求澄清时选择猜测
- [ ] 代码过于复杂难以理解

---

## 适用性

对于简单任务（如 typo 修复、明显的一行代码），使用判断力而非教条主义。

目标是减少**非平凡工作**上的代价高昂的错误，而非减慢简单任务的速度。