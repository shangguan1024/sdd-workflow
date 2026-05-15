# Visualization Guide (PlantUML + Mermaid)

> **Reference file for SDD-Workflow** - Dual engine visualization strategy.

## Dual Engine Strategy

| Layer | Visualization Content | Tool | Reason |
|-------|----------------------|------|--------|
| **Architecture Layer** | Module dependencies, interaction sequences | **PlantUML** | Supports complex package structures, activation bars, color definitions |
| **Module Internal Layer** | Function flow, call sequences, state transitions | **Mermaid** | Markdown native, simple syntax, easy to maintain |

---

## PlantUML Usage

### Use Cases

| Diagram Type | Purpose | Section |
|--------------|---------|---------|
| Component Diagram | Module dependency relationships | Part 2: Data Flow Diagram |
| Sequence Diagram | Module interaction sequences | Part 2: Interaction Sequence |

### Component Diagram Example

```plantuml
@startuml
!define MODULE_COLOR #E3F2FD
!define DATA_COLOR #FFF9C4

package "Overall Architecture" {
    [ModuleA] as A MODULE_COLOR
    [ModuleB] as B MODULE_COLOR
    [ModuleC] as C MODULE_COLOR
    database "DB" as DB DATA_COLOR
}

A -> B : API call\nPass: RequestData
B -> C : Event notification\nPass: EventData
C --> A : Callback response\nReturn: ResponseData
B -> DB : Data persistence\nStore: PersistentData
@enduml
```

### Sequence Diagram Example

```plantuml
@startuml
actor User
participant "ModuleA" as A
participant "ModuleB" as B
participant "ModuleC" as C

User -> A : Send request
activate A
A -> B : processData(RequestData)
activate B
B -> C : notifyEvent(EventData)
activate C
C --> B : confirmResult(ResultData)
deactivate C
B --> A : returnResponse(ResponseData)
deactivate B
A --> User : Return result
deactivate A
@enduml
```

---

## Mermaid Usage

### Use Cases

| Diagram Type | Purpose | Section |
|--------------|---------|---------|
| Flowchart | Function implementation flow | Part 3: Implementation Logic |
| Sequence Diagram | Function call sequences | Part 3: Implementation Logic |
| State Diagram | State transitions | Part 3: Private Data & State |

### Flowchart Example

```mermaid
flowchart TD
    Start[Receive RequestData] --> Validate{Validate data format?}
    Validate -->|yes| Transform[Convert to internal format]
    Validate -->|no| Error1[Return ValidationError]
    
    Transform --> Process[Execute business logic]
    Process --> Fork1{Parallel processing}
    
    Fork1 --> CallB[Call ModuleB]
    Fork1 --> UpdateState[Update state machine]
    
    CallB --> Merge[Merge results]
    UpdateState --> Merge
    
    Merge --> Assemble[Assemble return result]
    Assemble --> End1[Return ResponseData]
    Error1 --> End2[End]
    End1 --> End2
```

### Sequence Diagram Example

```mermaid
sequenceDiagram
    participant Client
    participant ModuleA
    participant Validator
    participant ModuleB
    
    Client->>ModuleA: process_request(data)
    ModuleA->>Validator: validate(data)
    Validator-->>ModuleA: ValidationResult
    
    alt Validation successful
        ModuleA->>ModuleB: process(InternalData)
        ModuleB-->>ModuleA: ResultData
        ModuleA-->>Client: ResponseData
    else Validation failed
        ModuleA-->>Client: ValidationError
    end
```

### State Diagram Example

```mermaid
stateDiagram-v2
    [*] --> Idle: Initialize
    Idle --> Processing: Receive request
    Processing --> Waiting: Call dependency module
    Waiting --> Completed: Receive response
    Waiting --> Failed: Timeout/Error
    Completed --> [*]: Return result
    Failed --> [*]: Return error
```

---

## When to Use Flowcharts

**Use flowcharts ONLY for:**
- Non-obvious decision points
- Process loops where you might stop too early
- "When to use A vs B" decisions

**Never use flowcharts for:**
- Reference material → Tables, lists
- Code examples → Markdown blocks
- Linear instructions → Numbered lists
- Labels without semantic meaning (step1, helper2)

---

## Quick Reference

| Need | Use |
|------|-----|
| Module architecture | PlantUML Component Diagram |
| Module interaction | PlantUML Sequence Diagram |
| Function flow | Mermaid Flowchart |
| Function call sequence | Mermaid Sequence Diagram |
| State machine | Mermaid State Diagram |
| Reference data | Markdown Table |
| Linear steps | Numbered List |