# Design Document Template (v2.2 Total-Part Structure)

> **Reference file for SDD-Workflow** - This template defines the complete design document structure.

## Document Location

```
docs/features/<feature>/design.md
```

## Complete Structure

```markdown
# <feature-name> Design Document v2.2

## Part 1: Overall Architecture (总)

### 1.1 Overview
- Feature description
- Risk level assessment (LOW/MEDIUM/HIGH)

### 1.2 Requirements
- Functional requirements (with REQ-ID)
- Non-functional requirements (performance, security, reliability)
- Constraints (platform, compatibility, standards)

### 1.3 Module List
- Module inventory and responsibility overview

---

## Part 2: Overall Data Flow & Module Interaction (总) ── PlantUML

### 2.1 Data Flow Diagram (PlantUML Component Diagram)

### 2.2 Interaction Sequence (PlantUML Sequence Diagram)

### 2.3 Module Boundary Matrix

| Source Module | Target Module | Interaction Type | Data Contract | Description |
|---------------|---------------|------------------|---------------|-------------|

### 2.4 Dependency Constraints
- Allowed Dependencies
- Forbidden Dependencies (use nexus-query to validate)

---

## Part 3: Module Decomposition & Detailed Design (分) ── PlantUML + Mermaid

### Module A: [module-name]

#### 3.1 Module Overview
- Business boundary
- Data boundary
- Behavior boundary

#### 3.2 Data Structures
**Public Data Structures:**
**Private Data Structures:**

#### 3.3 Public Interfaces (8-dimension deep definition)
**Reference**: `interface-example.md` (in sdd-workflow skill directory)

#### 3.4 Module Internal Design

##### 3.4.1 Private Data & State (Mermaid State Diagram)

##### 3.4.2 Private Interfaces (Internal)

##### 3.4.3 Interface Changes

| Interface | Change Type | Modification | Impact |
|-----------|-------------|--------------|--------|

##### 3.4.4 Implementation Logic (PlantUML Sequence + Mermaid Flowchart)

##### 3.4.5 Test Strategy

##### 3.4.6 Peripheral Module Dependencies (5-dimension deep analysis)
**Reference**: `dependency-example.md` (in sdd-workflow skill directory)

---

### Module B: [module-name]
(same structure as Module A)

---

### Module C: [module-name]
(same structure as Module A)

---

## Part 4: Integration & Verification (总)

### 4.1 Integration Points

### 4.2 Implementation Plan
- Development order
- Critical path
- Parallel opportunities

### 4.3 Verification Checklist

| REQ-ID | Verification Item | Test Method | Verification Criteria |
|--------|------------------|-------------|----------------------|

### 4.4 Change Impact Analysis
- Impact matrix
- Risk mitigation strategies
```

## Gate Requirements

**See**: `phases-reference.md` for complete gate requirements per phase.

**Part 1 Gate**:
- ✅ Overview with risk assessment
- ✅ Requirements with REQ-ID
- ✅ Module List complete

**Part 2 Gate**:
- ✅ PlantUML Data Flow Diagram
- ✅ PlantUML Interaction Sequence
- ✅ Module Boundary Matrix
- ✅ Dependency Constraints (nexus-query validated)

**Part 3 Gate** (per module):
- ✅ Module Overview (business/data/behavior)
- ✅ Data Structures (Public + Private)
- ✅ Public Interfaces (8-dimension)
- ✅ Module Internal Design
- ✅ Interface Changes
- ✅ Implementation Logic (PlantUML Sequence + Mermaid Flowchart)
- ✅ Test Strategy
- ✅ Peripheral Module Dependencies (5-dimension)

**Part 4 Gate**:
- ✅ Integration Points defined
- ✅ Implementation Plan with critical path
- ✅ Verification Checklist with REQ-ID
- ✅ Change Impact Analysis with mitigation