# Phase Reference (Phase 1-6 Detailed Description)

> **Reference file for SDD-Workflow** - Detailed phase descriptions and gate requirements.

## Phase Overview

| Phase | Name | Skill | Input | Output | Gate |
|-------|------|-------|-------|--------|------|
| Phase 0 | Scene Analysis | scene-analysis | Feature request, domain docs | scene_analysis.md | Scene Analysis Approved |
| Phase 1 | Understanding | understanding | Feature request, codebase | findings.md Phase 0 | Anti-Superficiality Check |
| Phase 2 | Requirements & Design | brainstorming | findings.md Phase 0 | design-doc.md | Design + Decomposition Approved |
| Phase 3 | Implementation Planning | writing-plans | design-doc.md | task_plan.md | Plan Approved |
| Phase 4 | Module Development | subagent-driven-dev | task_plan.md | Code changes | Compile + Unit Tests |
| Phase 5 | Integration & Testing | verification-before-* | Code changes | Integration tests pass | Integration Tests Pass |
| Phase 6 | Code Quality Review | code-review-quality | All code | Review artifacts | All 4 Artifacts Verified |
| Phase 7 | Memory Persistence | Auto-document | All artifacts | Memory artifacts | Documentation Complete |

---

## Phase 0: Scene Analysis (Large Features Only)

**Trigger:** Feature complexity >= HIGH (tasks > 5 OR modules > 3)

**Objective:** Business scenario analysis before technical design.

**Execution Steps:**

```
Step 1: Business context collection
    Read docs/knowledge/domain/
    Read PROJECT_STATE.md
    Optional: User interview records
    
Step 2: User journey mapping
    Draw core user journeys
    Mark system response at each journey stage
    
Step 3: Use case extraction
    Extract specific use cases from journeys
    Mark frequency, complexity
    
Step 4: Priority ranking
    Use MoSCoW method: P0 (Must), P1 (Should), P2 (Could), P3 (Won't)
    
Step 5: Module mapping
    Analyze which modules each scenario needs
    Mark integration points
    
Step 6: Edge case analysis
    Analyze error scenarios, exception flows
    
Step 7: NFR annotation
    Mark non-functional requirements for each scenario
    
Step 8: Dependency analysis
    Draw scenario dependency graph
    Determine implementation order
    
Step 9: Risk assessment
    Identify high-risk scenarios
    Propose mitigation measures
    
Step 10: Write scene_analysis.md
```

**Output:** `docs/features/<feature>/scene_analysis.md`

**Gate Requirements:**
```
✅ scene_analysis.md exists with all required sections
✅ P0 scenarios >= 3 (large features have core scenarios)
✅ Scenario-to-module mapping covers all P0 scenarios
✅ User confirms scene analysis is comprehensive
```

---

## Phase 1: Understanding (Mandatory for All Features)

**Objective:** Deep research before design, avoid superficial analysis.

**Execution Steps:**

```
Step 1: Codebase analysis
    - Identify project type (language/framework/build system)
    - List at least 5 specific related files (with file names, not module names)
    - Identify key interfaces/trait definitions
    
Step 2: Technical principles
    - Identify core technology stack
    - For each concept: name, why relevant, source citation (URL/doc chapter)
    - Reference table with specific URLs or doc sections
    
Step 3: Constraints identification
    - At least 3 constraints covering: performance, security, compatibility, resources, standards
    
Step 4: Alternative comparison
    - At least 2 alternatives with 3+ specific pros/cons each
    - Comparison table with: complexity, performance, maintenance, testing
```

**Output:** `docs/features/<feature>/findings.md Phase 0`

**Gate Requirements:**
```
✅ findings.md Phase 0 exists and non-empty
✅ Codebase analysis with 5+ specific files
✅ Technical principles with 2+ external source citations
✅ Constraints >= 2
✅ Alternatives >= 2 with 3+ specific pros/cons each
✅ Anti-Superficiality check passed
✅ User confirms research is deep enough
```

**Red Flags (Research Failed):**
- 🔴 No specific file names (only module names without file names)
- 🔴 "Technical principles" section < 200 words
- 🔴 Constraints < 2 (simple features must explain "why constraints are few")
- 🔴 No external source citations (URL or doc sections)
- 🔴 Only 1 alternative
- 🔴 Each alternative has < 2 pros/cons
- 🔴 Placeholder text like "need to research X"

---

## Phase 2: Requirements Analysis & Architecture Design

**Skill:** `brainstorming`

**Execution Steps:**

```
Step 1-5: Standard Features (end here)
    Read findings.md Phase 1
    Read design doc template
    Constitution compliance check
    Update findings.md Design Summary
    
Step 6-10: Large Features (Module Decomposition Workshop)
    Define Bounded Contexts
    Draw Module Boundary Matrix
    Define Dependency Constraints
    Validate with nexus-query
    
Step 11-18: Large Features (Module Internal Architecture)
    Define Module Overview
    Define Data Structures (Public + Private)
    Define Public Interfaces (8-dimension)
    Define Module Internal Design
    
Step 19-24: Large Features (Implementation Deep Dive)
    Interface detailed design
    Implementation logic design (Mermaid)
    Module interaction design
    Change impact analysis
    Implementation order planning
```

**Output:** `docs/superpowers/specs/YYYY-MM-DD-<feature>-design.md`

**Gate Requirements:**
```
✅ Understanding phase passed
✅ Design document generated
✅ Constitution compliance check passed
✅ For large features: Module Decomposition complete
✅ For large features: Public Interfaces (8-dimension) complete
✅ For large features: Peripheral Module Dependencies (5-dimension) complete
✅ User confirms design approved
```

---

## Phase 3: Implementation Planning

**Skill:** `writing-plans`

**Execution Steps:**

```
Step 1: Read design document
Step 2: Task decomposition
    Split design into independent tasks
    Each task has: input, output, estimate (low/medium/high)
    
Step 3: Define file changes scope
    New files, Modified files (for Phase 6 incremental review)
    
Step 4: Write task_plan.md
```

**Output:** `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`, `task_plan.md`

**Gate Requirements:**
```
✅ Implementation plan exists
✅ Constitution compliance check passed
✅ Plan includes: file changes, test strategy, verification commands
✅ File Changes Scope clearly defined
✅ User approved plan
```

---

## Phase 4: Module Development

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

## Phase 5: Integration & Testing

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

## Phase 6: Code Quality Review

**Skill:** `code-review-quality`

**Output:**
- `docs/features/<feature>/reviews/architecture_review.md`
- `docs/features/<feature>/reviews/code_quality_review.md`

**Gate Requirements:**
```
✅ Architecture review complete
✅ Code quality review complete
✅ All 4 review artifacts verified:
    - Architecture compliance
    - Requirements traceability
    - Code quality metrics
    - Test coverage
```

---

## Phase 7: Memory Persistence

**Skill:** Auto-document

**Output:**
- `docs/features/<feature>/findings.md` (updated)
- `docs/features/<feature>/task_plan.md` (updated)
- `docs/features/<feature>/design-doc.md` (finalized)
- `docs/features/<feature>/.sdd/conversation_memory.json`
- `PROJECT_STATE.md` (aggregated)
- `AGENTS.md` (updated with change summary)

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
4. If ANY answer is NO → STOP, cannot proceed
```

**Human-in-Loop:**
- User must review phase output
- User must explicitly confirm "Phase approved, proceed to next phase"
- If user feedback is negative, AI must return to previous phase and redo