# Phase Reference (Phase 0-6 Detailed Description)

> **Reference file for SDD-Workflow** - Detailed phase descriptions and gate requirements.

## Phase Overview

| Phase | Name | Skill | Input | Output | Gate |
|-------|------|-------|-------|--------|------|
| Phase 0 | Research & Understanding | understanding | Feature request, codebase | findings.md (Phase 0 section) | Anti-Superficiality Check |
| Phase 1 | Requirements & Design | brainstorming | findings.md (Phase 0 section) | design.md | Design + Decomposition Approved |
| Phase 2 | Implementation Planning | writing-plans | design.md | task_plan.md | Plan Approved |
| Phase 3 | Module Development | subagent-driven-dev | task_plan.md | Code changes | Compile + Unit Tests |
| Phase 4 | Integration & Testing | verification-before-* | Code changes | Test results | Integration Tests Pass |
| Phase 5 | Code Quality Review | code-review-quality | All code | Review artifacts | All 4 Artifacts Verified |
| Phase 6 | Memory Persistence | Auto-document | All artifacts | Memory artifacts | Documentation Complete |

---

## Phase 0: Research & Understanding (Mandatory for All Features)

**Objective:** Deep research before design, avoid superficial analysis.

**Execution Steps:**

```
Step 1: Codebase analysis
    - Identify project type (language/framework/build system)
    - List at least 5 specific related files (with file names)
    - Identify key interfaces/trait definitions
    
Step 2: Technical principles
    - Identify core technology stack
    - For each concept: name, why relevant, source citation
    - Reference table with URLs or doc sections
    
Step 3: Constraints identification
    - At least 3 constraints: performance, security, compatibility
    
Step 4: Alternative comparison
    - At least 2 alternatives with 3+ pros/cons each
    - Comparison table: complexity, performance, maintenance
```

**Output:** `docs/features/<feature>/findings.md` (Phase 0 section)

**Gate Requirements:**
```
✅ findings.md exists with Phase 0 section
✅ Phase 0 section has Codebase analysis (5+ files)
✅ Phase 0 section has Technical principles (2+ citations)
✅ Phase 0 section has Constraints (2+)
✅ Phase 0 section has Alternatives (2+ with 3+ pros/cons)
✅ User confirms research is deep enough
```

**Red Flags (Research Failed):**
- 🔴 No specific file names (only module names)
- 🔴 "Technical principles" section < 200 words
- 🔴 Constraints < 2
- 🔴 No external citations
- 🔴 Only 1 alternative
- 🔴 Placeholder text like "need to research X"

---

## Phase 1: Requirements & Design

**Skill:** `brainstorming`

**Execution Steps:**

```
Step 1-5: Standard Features (end here)
    Read findings.md (Phase 0 section)
    Read design doc template
    Constitution compliance check
    Update findings.md (Phase 1 section)
    
Step 6-10: Large Features (Module Decomposition)
    Define Bounded Contexts
    Draw Module Boundary Matrix
    Define Dependency Constraints
    Validate with nexus-query
    
Step 11-18: Large Features (Module Internal Architecture)
    Define Module Overview
    Define Data Structures
    Define Public Interfaces (8-dimension)
    Define Module Internal Design
    
Step 19-24: Large Features (Implementation Deep Dive)
    Interface detailed design
    Implementation logic (Mermaid)
    Module interaction design
    Change impact analysis
    Implementation order
```

**Output:** `docs/features/<feature>/design.md`

**Gate Requirements:**
```
✅ Phase 0 passed
✅ Design document generated
✅ Constitution compliance check passed
✅ For large features: Module Decomposition complete
✅ For large features: Public Interfaces (8-dimension)
✅ For large features: Peripheral Module Dependencies (5-dimension)
✅ User confirms design approved
```

---

## Phase 2: Implementation Planning

**Skill:** `writing-plans`

**Execution Steps:**

```
Step 1: Read design document
Step 2: Task decomposition
    Split into independent tasks
    Each task: input, output, estimate
    
Step 3: Define file changes scope
    New files, Modified files
    
Step 4: Write task_plan.md
```

**Output:** `docs/features/<feature>/task_plan.md`

**Gate Requirements:**
```
✅ Implementation plan exists
✅ Constitution compliance check passed
✅ Plan includes: file changes, test strategy, verification commands
✅ User approved plan
```

---

## Phase 3: Module Development

**Skill:** `subagent-driven-development`

**Execution Steps:**

```
For each task:
    Step 1: Create worktree (if needed)
    Step 2: Implement task
    Step 3: Run unit tests
    Step 4: Run lint/typecheck
    Step 5: Update task_plan.md
```

**Output:** Code changes

**Gate Requirements:**
```
✅ All tasks completed
✅ Unit tests pass
✅ Compile successful
✅ Lint/typecheck pass
```

---

## Phase 4: Integration & Testing

**Skill:** `verification-before-completion`

**Execution Steps:**

```
Step 1: Run integration tests
Step 2: Run end-to-end tests
Step 3: Verify REQ-ID coverage
Step 4: Performance benchmark (if needed)
```

**Output:** Test results

**Gate Requirements:**
```
✅ Integration tests pass
✅ E2E tests pass
✅ REQ-ID coverage >= 80%
✅ Performance meets requirements
```

---

## Phase 5: Code Quality Review

**Skill:** `code-review-quality`

**Output:**
- `docs/features/<feature>/reviews/architecture_review.md`
- `docs/features/<feature>/reviews/code_quality_review.md`

**Gate Requirements:**
```
✅ Architecture review complete
✅ Code quality review complete
✅ All 4 artifacts verified:
    - Architecture compliance
    - Requirements traceability
    - Code quality metrics
    - Test coverage
```

---

## Phase 6: Memory Persistence

**Skill:** Auto-document

**Output:**
- `docs/features/<feature>/findings.md` (updated)
- `docs/features/<feature>/task_plan.md` (finalized)
- `docs/features/<feature>/design.md` (finalized)
- `docs/features/<feature>/.sdd/conversation_memory.json`
- `PROJECT_STATE.md` (aggregated)
- `AGENTS.md` (updated)

**Gate Requirements:**
```
✅ All memory artifacts exist
✅ PROJECT_STATE.md updated
✅ AGENTS.md updated
```

---

## Phase Gate System

**Every phase transition requires Developer Confirmation Gate:**

```
Gate Checklist:
1. Current phase output exists?
2. Next phase input requirements met?
3. Developer explicit confirmation received?
4. If ANY answer is NO → STOP
```

**Human-in-Loop:**
- User must review phase output
- User must explicitly confirm "Phase approved, proceed to next phase"
- If user feedback is negative, AI must return to previous phase