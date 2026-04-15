# Change Summary

> ⚠️ **重要**: 每次代码变更后必须填写此文档。

## 变更信息

| 字段 | 内容 |
|------|------|
| 日期 | YYYY-MM-DD |
| 开发者 | @username |
| 分支 | feature/xxx |
| 关联 Feature | feature-name |

---

## 变更的文件

### 新增文件
```list
- src/new-file-1.ts
- src/new-file-2.ts
```

### 修改文件
```list
- src/modified-file-1.ts
- src/modified-file-2.ts
```

### 删除文件
```list
- src/deleted-file.ts (不再使用)
```

---

## 变更内容

### 主要变更 (What)

> 简要描述这次变更做了什么

-

### 变更原因 (Why)

> 为什么需要这个变更？解决什么问题？

-

### 影响范围

> 这个变更会影响哪些模块/功能？

-

---

## 未变更的部分 (Intentional)

> ⚠️ **重要**: 明确说明哪些相关部分**有意没有修改**，避免后续误以为遗漏

```list
- src/related-file.ts: 有类似的验证逻辑，但本次 scope 不包含
- src/old-module.ts: 计划在下一个 feature 中重构
```

---

## 潜在风险

> ⚠️ **重要**: 识别可能的风险点

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| | | |

### 向后兼容性

- [ ] 此变更是否影响现有 API？
- [ ] 此变更是否需要数据库迁移？
- [ ] 此变更是否需要更新配置？

### 性能影响

- [ ] 此变更是否影响性能？
- [ ] 是否需要基准测试？

---

## 测试验证

### 已执行的测试

- [ ] 单元测试: `npm test` ✅
- [ ] 集成测试: `npm run test:integration` ✅
- [ ] E2E 测试: `npm run test:e2e` ✅

### 测试覆盖

| 文件 | 测试文件 | 覆盖率 |
|------|---------|--------|
| src/modified-1.ts | tests/modified-1.test.ts | 85% |

---

## 部署信息

### 环境

- [ ] 开发环境 (dev) - 已测试
- [ ] 预发布环境 (staging) - 待部署
- [ ] 生产环境 (production) - 待审批

### 依赖变更

| 依赖 | 版本变更 | 影响 |
|------|---------|------|
| zod | 3.0.0 → 3.1.0 | 需要重新安装 |

---

## Rollback 计划

> 如何回滚这个变更？

```bash
git revert <commit-hash>
```

回滚步骤:
1.
2.

---

## 相关链接

- Feature: [link]
- Issue: [link]
- Design Doc: [link]
- 测试报告: [link]

---

**填写人**: @username
**填写时间**: YYYY-MM-DD HH:mm
**审查人**: @reviewer
**审查时间**: YYYY-MM-DD HH:mm