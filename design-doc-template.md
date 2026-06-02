# Design Document Template

Save as:

```text
docs/features/<feature>/design.md
```

Plugin compatibility: if `sdd_memory_details` or injected memory context needs `design-doc.md`, keep `docs/features/<feature>/design-doc.md` as a copy or pointer to this file.

## Complete Structure

```markdown
# <feature-name> Design Document

## Part 1: Overall Architecture

### 1.1 Overview
- Feature description
- Current behavior
- Target behavior
- Risk level: LOW / MEDIUM / HIGH

### 1.2 Requirements
- Functional requirements with REQ-IDs
- Non-functional requirements: performance, security, reliability, compatibility
- Constraints: platform, migration, standards, operational limits

### 1.3 Module List
| Module | Responsibility | Owner/Area | Change Type |
|--------|----------------|------------|-------------|
|  |  |  | new / modified / unchanged |

---

## Part 2: Overall Data Flow and Module Interaction

### 2.1 Data Flow Diagram
Use PlantUML component diagram.

### 2.2 Interaction Sequence
Use PlantUML sequence diagram.

### 2.3 Module Boundary Matrix
| Source Module | Target Module | Interaction Type | Data Contract | Description |
|---------------|---------------|------------------|---------------|-------------|
|  |  |  |  |  |

### 2.4 Dependency Constraints
- Allowed dependencies
- Forbidden dependencies
- Validation method: code search, architecture map, tests, or documented review

---

## Part 3: Module Decomposition and Detailed Design

### Module: <module-name>

#### 3.1 Module Overview
- Business boundary
- Data boundary
- Behavior boundary

#### 3.2 Data Structures
- Public data structures
- Private data structures
- Schema or migration impact

#### 3.3 Public Interfaces
Use `interface-example.md` when public interfaces or contracts change.

#### 3.4 Module Internal Design

##### 3.4.1 Private Data and State
Use Mermaid state diagram when state transitions matter.

##### 3.4.2 Private Interfaces

##### 3.4.3 Interface Changes
| Interface | Change Type | Modification | Impact |
|-----------|-------------|--------------|--------|
|  |  |  |  |

##### 3.4.4 Implementation Logic
Use PlantUML sequence diagrams for interactions and Mermaid flowcharts for non-interaction decision logic.

##### 3.4.5 Test Strategy
| REQ-ID | Test Type | Test File/Command | Expected Evidence |
|--------|-----------|-------------------|-------------------|
|  |  |  |  |

##### 3.4.6 Peripheral Module Dependencies
Use `dependency-example.md` when this module depends on services, shared modules, or external systems.

---

## Part 4: Integration and Verification

### 4.1 Integration Points

### 4.2 Implementation Plan
- Development order
- Critical path
- Parallel opportunities

### 4.3 Verification Checklist
| REQ-ID | Verification Item | Test Method | Verification Criteria |
|--------|-------------------|-------------|----------------------|
|  |  |  |  |

### 4.4 Change Impact Analysis
- Impact matrix
- Risk mitigation strategies
- Rollback considerations
```

## Gate Requirements

### Part 1

- [ ] Overview includes risk assessment.
- [ ] Requirements include REQ-IDs.
- [ ] Module list is complete for the planned scope.

### Part 2

- [ ] Data flow is shown with PlantUML.
- [ ] Interaction sequence is shown with PlantUML.
- [ ] Module boundary matrix is complete.
- [ ] Dependency constraints are validated or review method is documented.

### Part 3

- [ ] Each changed module has business, data, and behavior boundaries.
- [ ] Public interfaces are defined with 8 dimensions when applicable.
- [ ] Internal state and implementation logic are documented where risk warrants it.
- [ ] Peripheral dependencies are analyzed with 5 dimensions when applicable.
- [ ] Test strategy maps to requirements.

### Part 4

- [ ] Integration points are defined.
- [ ] Implementation order and parallel opportunities are clear.
- [ ] Verification checklist maps to REQ-IDs.
- [ ] Change impact and rollback considerations are documented.
