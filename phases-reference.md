# Phase Reference (Phase 0-6 Detailed Description)

> **Reference file for SDD-Workflow** - Detailed phase descriptions and gate requirements.

## Phase Overview

**See SKILL.md for Phase table summary (Phase 0-6, Skill, Gate).**

This document provides:
- Execution steps per phase
- Input/Output artifacts per phase
- Detailed gate requirements
- Red flags per phase

---

## Phase 0: Research & Understanding (Mandatory for All Features)

**Objective:** Deep research before design, avoid superficial analysis.

**Skill:** `comprehensive-research-agent` (MUST call at start)

**Execution Steps:**

```
Step 0: Call comprehensive-research-agent skill
    skill("comprehensive-research-agent")
    → Provides: error recovery, cross-validation, source tracking
    → AI MUST use this skill patterns throughout Phase 0
    
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
    
Step 5: Cross-validation (from comprehensive-research-agent)
    - Verify key claims across 2+ sources
    - Document confidence level for each claim
    
Step 6: Error recovery (from comprehensive-research-agent)
    - Document tool failures and fallback strategies
    - Maintain source tracking table
    
Step 7: Document gaps
    - Explicitly list unverified claims
    - Document what was attempted but failed
```

**Output:** `docs/features/<feature>/findings.md` (Phase 0 section)

**Gate Requirements:**
```
✅ findings.md exists with Phase 0 section
✅ Phase 0 section has Codebase analysis (5+ files)
✅ Phase 0 section has Technical principles (2+ citations)
✅ Phase 0 section has Constraints (2+)
✅ Phase 0 section has Alternatives (2+ with 3+ pros/cons)
✅ Source tracking table present (from comprehensive-research-agent)
✅ Cross-validation documented (key claims verified)
✅ Limitations & Gaps section (unverified claims listed)
✅ User confirms research is deep enough
```

**Red Flags (Research Failed):**
- 🔴 No specific file names (only module names)
- 🔴 "Technical principles" section < 200 words
- 🔴 Constraints < 2
- 🔴 No external citations
- 🔴 Only 1 alternative
- 🔴 Placeholder text like "need to research X"
- 🔴 **No source tracking table** (comprehensive-research-agent not used)
- 🔴 **No cross-validation** (single source claims)
- 🔴 **No error recovery documented** (tool failures ignored)

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

**Skill:** `verification-before-completion` (MUST call before claiming work is complete)

**Execution Steps:**

```
Step 0: Call verification-before-completion skill
    skill("verification-before-completion")
    → AI MUST run verification commands before any success claims
    
Step 1: Run integration tests
Step 2: Run end-to-end tests
Step 3: Verify REQ-ID coverage
Step 4: Performance benchmark (if needed)
Step 5: Document verification results with command output
```

**Output:** Test results (with actual command output evidence)

**Gate Requirements:**
```
✅ Integration tests pass (command output shown)
✅ E2E tests pass (command output shown)
✅ REQ-ID coverage >= 80%
✅ Performance meets requirements
✅ verification-before-completion skill called
```

---

## Phase 5: Code Quality Review

**Skill:** `requesting-code-review` (MUST call before merge/PR)

**Execution Steps:**

```
Step 0: Call requesting-code-review skill
    skill("requesting-code-review")
    → AI MUST request code review before merging
    
Step 1: Generate architecture review
Step 2: Generate code quality review
Step 3: Verify requirements traceability
Step 4: Verify test coverage
```

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
✅ requesting-code-review skill called
```

---

## Phase 6: Memory Persistence

**Skill:** `memory-systems` (for designing persistence architecture)

**Execution Steps:**

```
Step 0: Call memory-systems skill (if needed)
    skill("memory-systems")
    → For designing persistent memory architecture
    
Step 1: Update findings.md (finalize)
Step 2: Update task_plan.md (finalize)
Step 3: Update design.md (finalize)
Step 4: Generate conversation_memory.json
Step 5: Update PROJECT_STATE.md
Step 6: Update AGENTS.md
```

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