# Public Interfaces Deep Definition (8 Dimensions)

> **Reference file for SDD-Workflow** - Each public interface must define 8 dimensions.

## Required Dimensions

| Dimension | Content | Depth Requirement |
|-----------|---------|------------------|
| **Function Description** | Detailed description + business logic steps | "Receive → Validate → Process → Return" |
| **Use Cases** | Scenario list + usage frequency | At least 3 scenarios |
| **Business Logic** | Core processing flow + performance complexity | Step sequence + O(n) |
| **Constraints** | Performance/security/concurrency + source annotation | At least 3 constraint values |
| **Parameters** | Table form + boundary values | Name, type, required, constraint, default |
| **Return Values** | Table form + field descriptions | Field, type, description, constraint |
| **Exceptions** | enum + trigger conditions + handling | Table form + HTTP Status |
| **Examples** | Complete code snippets | Normal call, error handling, async call |

## Complete Example: process() Interface

### 1. Function Description

**Detailed Description:**
- Receives user request and executes complete business processing flow
- Includes validation, transformation, business logic execution, result assembly
- Supports async processing and callback notification
- Coordinates multiple dependency modules

### 2. Use Cases

| Scenario | Description | Frequency |
|----------|-------------|-----------|
| User submits order | User initiates order creation request | High (100/min) |
| Batch data processing | System batch processes data tasks | Medium (10/hour) |
| API request handling | External system calls API | Low (5/hour) |

### 3. Business Logic

```
Step 1: Validate request
        - Check data format completeness
        - Validate user permissions (AuthService)
        - Check business rule constraints
        
Step 2: Transform data format
        - RequestData → InternalData
        - Initialize state machine (Idle → Processing)
        
Step 3: Execute core business
        - Apply business rules
        - Update internal state
        
Step 4: Call dependency modules
        - ModuleB.process(InternalData)
        - Handle response and errors
        
Step 5: Assemble return result
        - InternalResult → ResponseData
        - Notify observers (Observer.notify)
        
Step 6: State transition
        - Processing → Completed/Failed

Performance: O(n) where n = payload.len()
```

### 4. Constraints

| Constraint | Value | Source | Impact |
|------------|-------|--------|--------|
| Response Time | < 500ms | NFR-001 | Timeout returns TimeoutError |
| Permission Check | Required | Security Rule | user_id must be verified |
| Concurrency Limit | Max 5 per user | Business Rule | Returns ConcurrentLimitError |
| Payload Size | Max 1MB | System Config | Returns PayloadTooLargeError |
| Retry Limit | Max 3 retries | Error Handling Policy | Fallback after failure |

**Source Annotation (Mandatory):**
- ✅ `< 500ms` from Requirements NFR-001
- ✅ `Permission Check` from Security Rules Section 2.3
- ✅ `Max 5` from Business Rules concurrent_limit config

### 5. Parameters

| Parameter | Type | Required | Description | Constraint | Default |
|-----------|------|----------|-------------|------------|---------|
| user_id | UserId | ✅ | User identifier | UUID v4 format, must verify permission | - |
| payload | Vec<u8> | ✅ | Business data | Max 1MB, binary format | - |
| metadata | Metadata | ❌ | Metadata info | Key-value format, max 10 items | {} |
| timeout | Duration | ❌ | Timeout duration | Range: 1s-60s | 30s |
| priority | Priority | ❌ | Processing priority | Low/Medium/High | Medium |

**Boundary Values:**

| Parameter | Boundary Condition | Handling |
|-----------|--------------------|-----------|
| payload.len() | > 1MB | Return PayloadTooLargeError |
| metadata.len() | > 10 | Ignore extra items |
| timeout | < 1s or > 60s | Use default 30s |
| user_id | Not UUID v4 format | Return InvalidUserIdError |

### 6. Return Values

```rust
struct ResponseData {
    result: ResultCode,        // Processing result status code
    data: Option<Data>,        // Returned business data
    error: Option<ErrorInfo>,  // Error detailed info
    metadata: ResponseMetadata, // Response metadata
}

enum ResultCode {
    Success,       // Processing successful
    PartialSuccess, // Partially successful
    Failure,       // Processing failed
    Timeout,       // Processing timeout
}
```

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| result | ResultCode | Processing result status | Required, enum value |
| data | Option<Data> | Returned business data | Required when Success |
| error | Option<ErrorInfo> | Error detailed info | Required when Failure |
| metadata | ResponseMetadata | Response metadata | Contains trace_id, timestamp |

### 7. Exceptions

```rust
enum ProcessError {
    ValidationError(ValidationError),  // Validation error
    TimeoutError(Duration),             // Processing timeout
    ConcurrentLimitError(u32),          // Concurrency limit error
    PayloadTooLargeError(u64),          // Payload too large
    PermissionDeniedError(UserId),      // Permission denied
    DependencyError(String),            // Dependency module error
}
```

| Exception Type | Trigger Condition | Handling | HTTP Status |
|----------------|-------------------|----------|-------------|
| ValidationError | Data format error | Return to user directly | 400 Bad Request |
| TimeoutError | Processing exceeds timeout | Log + return | 504 Gateway Timeout |
| ConcurrentLimitError | Concurrency exceeds 5 | Reject new request | 429 Too Many Requests |
| PayloadTooLargeError | payload > 1MB | Reject request | 413 Payload Too Large |
| PermissionDeniedError | user_id lacks permission | Reject request | 403 Forbidden |
| DependencyError | ModuleB call fails | Retry + fallback | 500 Internal Error |

**Exception Mapping to Caller:**
- ProcessError.ValidationError → Client should fix data format
- ProcessError.TimeoutError → Client should increase timeout or retry
- ProcessError.DependencyError → Client should fallback

### 8. Usage Examples

```rust
// Example 1: Normal call
let request = RequestData {
    user_id: UserId::new("550e8400-e29b-41d4-a716-446655440000"),
    payload: vec![1, 2, 3, 4, 5],
    metadata: Metadata::new(),
    timeout: Duration::from_secs(30),
    priority: Priority::High,
};

let result = module_a.process(request)?;
match result.result {
    ResultCode::Success => {
        println!("Success: {:?}", result.data);
    }
    ResultCode::Failure => {
        println!("Failure: {:?}", result.error);
    }
    _ => {}
}

// Example 2: Error handling
let request = RequestData {
    user_id: UserId::new("invalid-uuid"),  // ← Wrong UUID format
    payload: vec![],
    metadata: Metadata::new(),
    timeout: Duration::from_secs(30),
    priority: Priority::Low,
};

match module_a.process(request) {
    Ok(result) => println!("Success: {:?}", result),
    Err(ProcessError::ValidationError(e)) => {
        println!("Validation error: {}", e.message);
    }
    Err(e) => println!("Other error: {}", e),
}

// Example 3: Async call (if supported)
let async_result = module_a.process_async(request).await?;
```

---

## Summary Table

| Interface | Core Responsibility | Performance Constraint | Main Exceptions |
|-----------|---------------------|----------------------|-----------------|
| process() | Complete business processing | < 500ms | ValidationError, TimeoutError |
| validate() | Fast data validation | < 10ms | ValidationError |
| query() | Status query | < 50ms | NotFoundError |

---

## Gate Requirements (Public Interfaces)

```
✅ Each interface has Function Description (detailed + business logic steps)
✅ Each interface has Use Cases (at least 3 scenarios)
✅ Each interface has Business Logic (step sequence + performance complexity)
✅ Each interface has Constraints (at least 3 values + source annotation)
✅ Each interface has Parameters (table form + boundary values)
✅ Each interface has Return Values (table form + field descriptions)
✅ Each interface has Exceptions (enum + trigger + handling + HTTP Status)
✅ Each interface has Examples (complete code snippets)
✅ Each interface has Summary (core + constraints + exceptions)
```