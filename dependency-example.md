# Peripheral Module Dependencies Deep Analysis (5 Dimensions)

> **Reference file for SDD-Workflow** - Each dependency module must analyze 5 dimensions.

## Required Dimensions

| Dimension | Content | Depth Requirement |
|-----------|---------|------------------|
| **Core Implementation** | Source code snippets + key points | Extract core implementation from source |
| **Data Structure** | Complete definition + impact analysis | Full struct/enum definition |
| **Performance Constraints** | 3+ precise values + source annotation | Response time, timeout, concurrency |
| **Error Handling** | enum + handling strategy + mapping | Error types + retry/fallback policy |
| **Integration Constraints** | Business rules + impact analysis | Time limits, notification requirements |

## Complete Example: PaymentService Dependency

### 1. Core Implementation

```rust
// Read from: src/payment/service.rs (line 45-60)
struct PaymentService {
    gateway: PaymentGateway,
    transaction_repo: TransactionRepository,
}

impl PaymentService {
    fn initiate_payment(order: &Order) -> Result<PaymentId> {
        let transaction = Transaction::new(order);
        self.gateway.process(transaction)?;  // ← Key point: may GatewayTimeout
        self.transaction_repo.save(transaction)?;
        Ok(transaction.id)
    }
}
```

**Key Implementation Analysis:**
- `gateway.process(transaction)` may throw `GatewayTimeout`, needs retry strategy
- `transaction_repo.save()` may throw `DbError`, needs fallback strategy

### 2. Data Structure

```rust
struct Payment {
    id: PaymentId,
    order_id: OrderId,
    amount: Decimal,
    status: PaymentStatus,  // Pending, Completed, Failed
    created_at: DateTime,
}

struct Transaction {
    payment: Payment,
    gateway_response: GatewayResponse,  // Third-party response
}

enum PaymentStatus {
    Pending,    // Waiting for payment
    Completed,  // Payment successful
    Failed,     // Payment failed
}
```

**Data Structure Impact Analysis:**
- Payment.status has Pending state, OrderService needs to handle "waiting for payment" scenario
- Transaction contains gateway_response, PaymentService should not expose to OrderService

### 3. Performance Constraints

| Constraint | Value | Source | Impact on ModuleA |
|------------|-------|--------|-------------------|
| Response Time | < 2s | PaymentGateway docs Section 3.2 | ModuleA timeout should set > 2s |
| Concurrency | < 100 | config.yaml (max_payments) | ModuleA needs rate limiting |
| Timeout | 30s | PaymentService::TIMEOUT constant | ModuleA.timeout = 35s (buffer) |
| Retry Limit | 3 | PaymentService::MAX_RETRIES | ModuleA should not retry additionally |

**Source Annotation (Mandatory):**
- ✅ `< 2s` from PaymentGateway official docs Section 3.2
- ✅ `< 100` from config.yaml max_payments config
- ✅ `30s` from PaymentService::TIMEOUT constant definition

### 4. Error Handling

```rust
enum PaymentError {
    GatewayTimeout,        // Gateway timeout
    InsufficientFunds,     // Insufficient balance
    PaymentDeclined,       // Payment declined
    NetworkError,          // Network error
    DbError,               // Database error
}
```

| Error Type | Handling Strategy | Retry Policy | Fallback |
|------------|------------------|--------------|----------|
| GatewayTimeout | Retry | 3 times, interval 1s | Return TimeoutError |
| InsufficientFunds | No retry | 0 times | Return to user directly |
| PaymentDeclined | No retry | 0 times | Log + return to user |
| NetworkError | Retry + fallback | 3 times | Use local cache |
| DbError | Fallback | 0 times | Return DbUnavailableError |

**Error Mapping to ModuleA:**
- PaymentError.GatewayTimeout → ModuleA should catch and convert to OrderError.PaymentTimeout
- PaymentError.InsufficientFunds → ModuleA should convert to OrderError.PaymentFailed

### 5. Integration Constraints

| Constraint | Description | Source | ModuleA Handling |
|------------|-------------|--------|------------------|
| Time Limit | Must initiate payment within 5s after Order created | Business rule (risk control) | ModuleA.create_order() calls immediately |
| Status Notification | Payment status change must notify OrderService | PaymentService docs | Listen to PaymentStatusChanged event |
| Transaction ID | Transaction.id must be recorded in Order | Data consistency requirement | Order.transaction_id field |

**Integration Impact Analysis:**
- Time constraint: ModuleA needs to call PaymentService synchronously in create_order()
- Notification constraint: ModuleA needs to implement PaymentStatusChanged event listener

---

## Summary

| Dimension | Key Finding | ModuleA Design Decision |
|-----------|-------------|------------------------|
| Core Implementation | gateway.process() may timeout | Set timeout=35s |
| Data Structure | Payment.status has Pending | OrderService needs PendingPayment state |
| Performance | Timeout 30s, concurrency < 100 | Need rate limiting + timeout=35s |
| Error Handling | GatewayTimeout retries 3 times | Catch and convert errors |
| Integration | Initiate payment within 5s | Synchronous call to PaymentService |

---

## Gate Requirements (Peripheral Module Dependencies)

```
✅ Each dependency has Core Implementation (source snippet + key point annotation)
✅ Each dependency has Data Structure (complete definition + impact analysis)
✅ Each dependency has Performance Constraints (3+ precise values + source annotation)
✅ Each dependency has Error Handling (enum definition + handling strategy + mapping to this module)
✅ Each dependency has Integration Constraints (2+ constraints + impact analysis)
✅ Each dependency has Summary (key findings → design decisions)
```

---

## Example: NotificationService Dependency (Abbreviated)

### 1. Core Implementation

```rust
// Read from: src/notification/service.rs (line 20-35)
impl NotificationService {
    fn notify(event: Event) -> Result<()> {
        self.queue.publish(event)?;  // ← Key: async notification
        Ok(())
    }
}
```

### 2. Data Structure

```rust
struct Event {
    event_type: EventType,
    payload: JsonValue,
    timestamp: DateTime,
}
```

### 3. Performance Constraints

| Constraint | Value | Source | Impact |
|------------|-------|--------|--------|
| Latency | < 100ms | NotificationService docs | Async call acceptable |
| Queue Size | < 1000 | config.yaml (max_queue) | Need queue monitoring |

### 4. Error Handling

```rust
enum NotificationError {
    QueueFull,      // Queue full
    NetworkError,   // Network error
}
```

| Error | Handling | Retry | Fallback |
|-------|----------|-------|----------|
| QueueFull | Wait + retry | 3 times | Log warning |
| NetworkError | Retry | 3 times | Ignore (non-critical) |

### 5. Integration Constraints

| Constraint | Description | Source |
|------------|-------------|--------|
| Async Notification | Notification is async | NotificationService docs |
| Event Format | Must use standard Event format | API specification |

---

## Summary

| Dimension | Key Finding | ModuleA Design Decision |
|-----------|-------------|------------------------|
| Core Implementation | Async notification | Fire-and-forget pattern |
| Performance | Latency < 100ms | Non-blocking call |
| Error Handling | QueueFull retries 3 times | Non-critical, ignore if failed |