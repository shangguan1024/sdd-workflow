# Design Document Template (v2.2 Total-Part Structure)

> **Reference file for SDD-Workflow** - This template defines the complete design document structure.

## Document Location

```
docs/superpowers/specs/YYYY-MM-DD-<feature>-design.md
```

## Complete Structure

```markdown
# <feature-name> Design Document v2.2

## Part 1: Overall Architecture (总)

### 1. Overview
- Feature description
- Risk level assessment (LOW/MEDIUM/HIGH)

### 2. Requirements
- Functional requirements (with REQ-ID)
- Non-functional requirements (performance, security, reliability)
- Constraints (platform, compatibility, standards)

### 3. Module List
- Module inventory and responsibility overview

---

## Part 2: Overall Data Flow & Module Interaction (总) ── PlantUML

### 4. Data Flow Diagram (PlantUML Component Diagram)

### 5. Interaction Sequence (PlantUML Sequence Diagram)

### 6. Module Boundary Matrix

| Source Module | Target Module | Interaction Type | Data Contract | Description |
|---------------|---------------|------------------|---------------|-------------|

### 7. Dependency Constraints
- Allowed Dependencies
- Forbidden Dependencies (use nexus-query to validate)

---

## Part 3: Module Decomposition & Detailed Design (分) ── Mermaid

### Module A: [module-name]

#### 8. Module Overview
- Business boundary
- Data boundary
- Behavior boundary

#### 9. Data Structures
**Public Data Structures:**
**Private Data Structures:**

#### 10. Public Interfaces (8-dimension deep definition)
See: interface-example.md for complete structure

#### 11. Module Internal Design

##### 11.1 Private Data & State (Mermaid State Diagram)

##### 11.2 Private Interfaces (Internal)

##### 11.3 Interface Changes

| Interface | Change Type | Modification | Impact |
|-----------|-------------|--------------|--------|

##### 11.4 Implementation Logic (Mermaid Flowchart + Sequence)

##### 11.5 Test Strategy

##### 11.6 Peripheral Module Dependencies (5-dimension deep analysis)
See: dependency-example.md for complete structure

---

### Module B: [module-name]
(same structure as Module A)

---

### Module C: [module-name]
(same structure as Module A)

---

## Part 4: Integration & Verification (总)

### 12. Integration Points

### 13. Implementation Plan
- Development order
- Critical path
- Parallel opportunities

### 14. Verification Checklist

| REQ-ID | Verification Item | Test Method | Verification Criteria |
|--------|------------------|-------------|----------------------|

### 15. Change Impact Analysis
- Impact matrix
- Risk mitigation strategies
```

## Gate Requirements (Per Part)

**Part 1: Overall Architecture**
- ✅ Overview with risk assessment
- ✅ Requirements with REQ-ID
- ✅ Module List complete

**Part 2: Data Flow & Interaction**
- ✅ PlantUML Data Flow Diagram
- ✅ PlantUML Interaction Sequence
- ✅ Module Boundary Matrix
- ✅ Dependency Constraints (nexus-query validated)

**Part 3: Module Decomposition**
- ✅ Each module has Module Overview
- ✅ Each module has Data Structures (Public + Private)
- ✅ Each module has Public Interfaces (8-dimension)
- ✅ Each module has Module Internal Design
- ✅ Each module has Interface Changes
- ✅ Each module has Implementation Logic (Mermaid)
- ✅ Each module has Test Strategy
- ✅ Each module has Peripheral Module Dependencies (5-dimension)

**Part 4: Integration & Verification**
- ✅ Integration Points defined
- ✅ Implementation Plan with critical path
- ✅ Verification Checklist with REQ-ID
- ✅ Change Impact Analysis with mitigation