# Phase Reference (Phase 0-6 Detailed Description)

> **Reference file for SDD-Workflow** - Detailed phase descriptions and gate requirements.

## Plugin + Skill Cooperation

Each phase execution follows this pattern:

```
1. Plugin injects Phase Prompt into system message
2. Plugin enforces tool restrictions (phase gate middleware)
3. AI reads Skill documentation for detailed guidance
4. AI executes phase tasks
5. AI calls sdd_gate tool for approval
6. Plugin transitions to next phase (after human confirmation)
```

---

## Phase 0: Research & Understanding (Mandatory for All Features)

**Objective:** Deep research before design, avoid superficial analysis.

**Gate Name:** Anti-Superficiality Check

**Skill:** Primary skill determined by `workflow_config.json` (default: `comprehensive-research-agent`, overridden by `skills` field if configured). MUST call at start.

**Skill Override Rule:**
- If `workflow_config.json` phase has `skills` field with non-empty array → use those as primary skills (replace defaults)
- If `skills` field is absent or empty → use `default_primary_skills` for that phase
- Always call `sdd_dispatch_skill` first to determine actual primary skill

**Plugin Behavior:**

| Behavior | Description |
|----------|-------------|
| Creates files | `docs/features/<feature>/findings.md`, `task_plan.md` |
| Blocks tools | `edit`, `write`, `bash` |
| Allows tools | `read`, `glob`, `grep` |
| Injects prompt | Phase 0 Prompt into system message |

**Execution Steps:**

```
Step 0: Check workflow_config.json and call primary skill
    sdd_dispatch_skill mode=primary
    → Returns actual primary skill name (may differ from default)
    → Call the returned primary skill:
      skill("<returned-skill-name>")
    → If default: comprehensive-research-agent → error recovery, cross-validation, source tracking
    → If overridden (e.g. requirement-web-kernel-clarifier) → follow that skill's guidance
    
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
    
Step 5: Cross-validation
    - Verify key claims across 2+ sources
    - Document confidence level for each claim
    
Step 6: Document gaps
    - Explicitly list unverified claims
    - Document what was attempted but failed
    
Step 7: Write findings.md
    Write to docs/features/<feature>/findings.md:
    ## Phase 0: Research
    ### Codebase Analysis
    ### Technical Principles
    ### Constraints
    ### Alternatives
```

**Tool Commands:**

```
# Start feature (enter Phase 0)
sdd_start feature="user-auth"

# Check Phase 1 gate requirements
sdd_gate phase=1 action=check

# Output:
✅ findings.md exists with Phase 0 section
✅ Phase 0 section has Codebase analysis (5+ files)
✅ Phase 0 section has Technical principles (2+ citations)
✅ Phase 0 section has Constraints (2+)
✅ Phase 0 section has Alternatives (2+ with 3+ pros/cons)

# Request approval (requires human confirmation)
sdd_gate phase=1 action=approve

# Plugin returns:
⚠️ HUMAN CONFIRMATION REQUIRED for Phase 1
DO NOT proceed without explicit human approval.
Ask the user: 'Phase gate requirements met. Should I proceed to Phase 1?'

# After user confirms "Yes":
sdd_gate phase=1 action=approve confirmed=true
```

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
- 🔴 "I already manually tested it" (claiming manual testing without verifiable evidence)
- 🔴 "Phase gate is just ritual" (dismissing gates as ceremonial, leads to skipping quality checks)

---

## Phase 1: Requirements & Design

**Gate Name:** Design + Decomposition Approved

**Skill:** Primary skill determined by `workflow_config.json` (default: `brainstorming`, overridden by `skills` field if configured).

**Skill Override Rule:** Same as Phase 0 — if `skills` field configured → replaces default; otherwise → use default_primary_skills. Always call `sdd_dispatch_skill mode=primary` first.

**Complexity Threshold:**
- Standard features: Steps 1-5 only (design document + constitution check)
- High complexity features (Complexity >= HIGH): Steps 1-24 (full module decomposition)
- Indicators of HIGH complexity: 3+ modules, cross-team dependencies, external API integration, performance-critical paths

**Plugin Behavior:**

| Behavior | Description |
|----------|-------------|
| Blocks tools | `bash` |
| Allows tools | `read`, `glob`, `grep`, `edit`, `write` |
| Injects prompt | Phase 1 Prompt into system message |

**Execution Steps:**

```
Step 1-5: Standard Features
    Read findings.md (Phase 0 section)
    Read Skill documents:
      - design-doc-template.md
      - interface-example.md
      - dependency-example.md
    
    ⚠️ Knowledge Base First Principle (代码理解优先级):
    When understanding code/architecture during design, follow this priority:
      1. FIRST: Use additional skills to query knowledge base
         - Dispatch skills configured in workflow_config.json
      2. THEN: Only if knowledge base has NO answer → use code search
         - Use grep/glob/read to search source code
      3. NEVER: Skip knowledge base and go straight to code search
    
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

**Tool Commands:**

```
# Check Phase 2 gate requirements
sdd_gate phase=2 action=check

# Output:
✅ Phase 0 passed
✅ Design document generated
✅ Constitution compliance check passed
✅ For large features: Module Decomposition complete
✅ For large features: Public Interfaces (8-dimension)
✅ For large features: Peripheral Module Dependencies (5-dimension)

# Request approval
sdd_gate phase=2 action=approve
# Wait for user confirmation
sdd_gate phase=2 action=approve confirmed=true
```

**Output:** `docs/features/<feature>/design.md`

**Gate Requirements:**
```
✅ Phase 0 passed
✅ Design document generated
✅ Constitution compliance check passed
✅ Knowledge base checked before code search (Knowledge Base First Principle)
✅ For large features: Module Decomposition complete
✅ For large features: Public Interfaces (8-dimension)
✅ For large features: Peripheral Module Dependencies (5-dimension)
✅ User confirms design approved
```

---

## Phase 2: Implementation Planning

**Gate Name:** Plan Approved

**Skill:** Primary skill determined by `workflow_config.json` (default: `writing-plans`, overridden by `skills` field if configured).

**Skill Override Rule:** Same as Phase 0 — if `skills` field configured → replaces default; otherwise → use default_primary_skills. Always call `sdd_dispatch_skill mode=primary` first.

**Plugin Behavior:**

| Behavior | Description |
|----------|-------------|
| Allows tools | All tools allowed |
| Injects prompt | Phase 2 Prompt into system message |

**Execution Steps:**

```
Step 1: Read design document
Step 2: Task decomposition
    Split into independent tasks
    Each task: input, output, estimate
    
Step 3: Define file changes scope
    New files, Modified files
    
Step 4: Write task_plan.md
    Each task with:
    - Input requirements
    - Output artifacts
    - Verification commands
    - Estimated time
```

**Tool Commands:**

```
# Check Phase 3 gate requirements
sdd_gate phase=3 action=check

# Output:
✅ Implementation plan exists
✅ Constitution compliance check passed
✅ Plan includes: file changes, test strategy, verification commands

# Request approval
sdd_gate phase=3 action=approve
# Wait for user confirmation
sdd_gate phase=3 action=approve confirmed=true
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

**Gate Name:** Compile + Unit Tests

**Skill:** Primary skill determined by `workflow_config.json` (default: `subagent-driven-development`, overridden by `skills` field if configured).

**Skill Override Rule:** Same as Phase 0 — if `skills` field configured → replaces default; otherwise → use default_primary_skills. Always call `sdd_dispatch_skill mode=primary` first.

**Plugin Behavior:**

| Behavior | Description |
|----------|-------------|
| Allows tools | All tools allowed |
| Monitors edits | Context Monitor tracks edit counts |
| Loop detection | Blocks single file 20+ edits |
| Injects prompt | Phase 3 Prompt into system message |

**Execution Steps:**

```
For each task:
    Step 1: Create worktree (if needed)
    Step 2: Implement task
    Step 3: Run unit tests
    Step 4: Run lint/typecheck
    Step 5: Update task_plan.md
    
Context Monitor:
    Every 50 edits → inject context refresh
    Hot files warning (5+ edits per file)
```

**Tool Commands:**

```
# Check Phase 4 gate requirements
sdd_gate phase=4 action=check

# Output:
✅ All tasks completed
✅ Unit tests pass
✅ Compile successful
✅ Lint/typecheck pass

# Request approval
sdd_gate phase=4 action=approve
# Wait for user confirmation
sdd_gate phase=4 action=approve confirmed=true

# Context refresh (if needed)
sdd_refresh reason="AI deviating from design"
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

**Gate Name:** Integration Tests Pass

**Skill:** Primary skill determined by `workflow_config.json` (default: `verification-before-completion`, overridden by `skills` field if configured). MUST call before claiming work is complete.

**Skill Override Rule:** Same as Phase 0 — if `skills` field configured → replaces default; otherwise → use default_primary_skills. Always call `sdd_dispatch_skill mode=primary` first.

**Plugin Behavior:**

| Behavior | Description |
|----------|-------------|
| Allows tools | All tools allowed |
| Injects prompt | Phase 4 Prompt into system message |

**Execution Steps:**

```
Step 0: Call primary skill (determined by workflow_config.json)
    sdd_dispatch_skill mode=primary
    → Call the returned primary skill
    → If default (verification-before-completion): AI MUST run verification commands before any success claims
    
Step 1: Run integration tests
    npm run test:integration
    cargo test --all
    
Step 2: Run end-to-end tests
    npm run test:e2e
    
Step 3: Verify REQ-ID coverage
    Check design.md REQ-ID mapping
    
Step 4: Test coverage gap analysis (MANDATORY)
    For each REQ-ID, build a Scenario Matrix:
    
    | REQ-ID | Direct Test | Context Tests | Edge Cases | Gap? |
    |--------|-------------|---------------|------------|------|
    | REQ-001 | test on its own | test in Pipeline context | default impl in Pipeline | ? |
    | REQ-002 | ... | ... | ... | ? |
    
    Rules:
    - Every REQ-ID must be tested NOT ONLY in isolation but also in its integration context
    - If a REQ has a default behavior (e.g., default trait impl), it must be tested in the consuming context too
    - If any cell shows "Gap?", write additional unit tests to cover it
    - Ask user: "Coverage gap analysis found X missing scenarios. Should I write tests for them?"
    
Step 5: Write incremental unit tests (if gaps found)
    Add tests to cover identified gaps
    Run tests to verify they pass
    
Step 6: Performance benchmark (if needed)
    
Step 7: Document verification results with command output
    Write to findings.md Phase 4 section
```

**Tool Commands:**

```
# Check Phase 5 gate requirements
sdd_gate phase=5 action=check

# Output:
✅ Integration tests pass (command output shown)
✅ E2E tests pass (command output shown)
✅ REQ-ID coverage >= 80%
✅ Test coverage gap analysis completed (Scenario Matrix)
✅ Incremental unit tests written for gaps (if any)
✅ Performance meets requirements
✅ verification-before-completion skill called

# Request approval
sdd_gate phase=5 action=approve
# Wait for user confirmation
sdd_gate phase=5 action=approve confirmed=true
```

**Output:** Test results (with actual command output evidence)

**Gate Requirements:**
```
✅ Integration tests pass (command output shown)
✅ E2E tests pass (command output shown)
✅ REQ-ID coverage >= 80%
✅ Test coverage gap analysis completed (Scenario Matrix documented)
✅ Incremental unit tests written for identified gaps (if any)
✅ Performance meets requirements
✅ verification-before-completion skill called
```

---

## Phase 5: Code Quality Review

**Gate Name:** All 4 Artifacts Verified

**Skill:** `requesting-code-review` (MUST call before merge/PR)

**Plugin Behavior:**

| Behavior | Description |
|----------|-------------|
| Allows tools | All tools allowed |
| Injects prompt | Phase 5 Prompt into system message |

**Execution Steps:**

```
Step 0: Call requesting-code-review skill
    skill("requesting-code-review")
    → AI MUST request code review before merging
    
Step 1: Generate architecture review
    docs/features/<feature>/reviews/architecture_review.md
    
Step 2: Generate code quality review
    docs/features/<feature>/reviews/code_quality_review.md
    
Step 3: Verify requirements traceability
    REQ-ID → Implementation mapping
    
Step 4: Verify test coverage
    Unit test coverage report
```

**Tool Commands:**

```
# Check Phase 6 gate requirements
sdd_gate phase=6 action=check

# Output:
✅ Architecture review complete
✅ Code quality review complete
✅ All 4 artifacts verified:
    - Architecture compliance
    - Requirements traceability
    - Code quality metrics
    - Test coverage
✅ requesting-code-review skill called

# Request approval
sdd_gate phase=6 action=approve
# Wait for user confirmation
sdd_gate phase=6 action=approve confirmed=true
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

**Gate Name:** Documentation Complete

**Skill:** `memory-systems` (for designing persistence architecture)

**Plugin Behavior:**

| Behavior | Description |
|----------|-------------|
| Allows tools | All tools allowed |
| Injects prompt | Phase 6 Prompt into system message |

**Execution Steps:**

```
Step 0: Call memory-systems skill (if needed)
    skill("memory-systems")
    → For designing persistent memory architecture
    
Step 1: Update findings.md (finalize)
    Complete all Phase sections
    
Step 2: Update task_plan.md (finalize)
    Mark all tasks as completed
    
Step 3: Update design.md (finalize)
    Final design document
    
Step 4: Update PROJECT_STATE.md
    Aggregate feature status
    
Step 5: Update AGENTS.md
    AI context recovery instructions
    
Step 6: Mark feature as completed
    Write COMPLETED file
```

**Tool Commands:**

```
# Check COMPLETED gate requirements
sdd_gate phase=7 action=check

# Output:
✅ All memory artifacts exist
✅ PROJECT_STATE.md updated
✅ AGENTS.md updated

# Complete workflow
sdd_complete feature="user-auth"

# Output:
✅ Workflow for 'user-auth' completed. Ready for merge.
```

**Output:**
- `docs/features/<feature>/findings.md` (updated)
- `docs/features/<feature>/task_plan.md` (finalized)
- `docs/features/<feature>/design.md` (finalized)
- `docs/features/<feature>/COMPLETED`
- `PROJECT_STATE.md` (aggregated)
- `AGENTS.md` (updated)

**Gate Requirements:**
```
✅ All memory artifacts exist
✅ PROJECT_STATE.md updated
✅ AGENTS.md updated
```

---

## Phase Gate System (Plugin Enforced)

**Every phase transition requires Developer Confirmation Gate:**

```
Gate Checklist:
1. Current phase output exists? (Plugin checks)
2. Next phase input requirements met? (Plugin checks)
3. Developer explicit confirmation received? (sdd_gate approve)
4. If ANY answer is NO → STOP (Plugin blocks tools)
```

**Human-in-Loop:**
- User must review phase output
- User must explicitly confirm via `sdd_gate approve`
- Plugin enforces transition rules
- If user feedback is negative, AI must return to previous phase

**Tool Blocking Rules:**

| Phase | Blocked Tools | Allowed Tools |
|-------|---------------|---------------|
| 0 (Understanding) | edit, write, bash | read, glob, grep |
| 1 (Requirements) | bash | read, glob, grep, edit, write |
| 2-6 | none | all |

---

## Resume Workflow

If workflow interrupted (session crash):

```
# 1. Check status
sdd_status verbose=true

# Output:
Active features:
  - user-auth (Phase 3: Module Development)

# 2. Resume feature
sdd_resume feature="user-auth"

# Plugin behavior:
✅ Loads .sdd/state.json
✅ Restores Phase 3 state
✅ Injects Phase 3 Prompt
✅ Loads checkpoint.json

# 3. Continue work
AI reads:
  - findings.md
  - design.md
  - task_plan.md
AI continues execution
```

---

## Context Refresh

If AI context drift:

```
# Manual refresh
sdd_refresh reason="AI deviating from design document"

# Plugin behavior:
✅ Injects key requirements
✅ Injects design decisions
✅ Injects hot file warnings
✅ Resets edit counter

# Auto refresh (Plugin)
Every 50 edits → Plugin auto-injects context refresh
```