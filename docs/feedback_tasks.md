# Feedback Implementation Plan

## High Priority Fixes
- [ ] **State Management**:
    - [ ] Implement `atomic_write` in `StateManager`.
    - [ ] Add `order_history` and `open_orders` to state structure.
- [ ] **Idempotency**:
    - [ ] Update `SignalEngine` to generate deterministic `signal_id`.
    - [ ] Update `Broker` to check `order_history` before execution (using `signal_id` or `order_id`).
- [ ] **Risk Manager Refinement**:
    - [ ] Refactor `check_risk` to `evaluate(signal, state)` returning `{allow: bool, size_pct: float, reason: str}`.
- [ ] **Logging**:
    - [ ] Enforce strict JSON schema in `logger.py`.
    - [ ] Add `log_id`, `pid`, `host` fields.
- [ ] **Testing**:
    - [ ] Add idempotency test (crash simulation).
    - [ ] Add atomic write test.
    - [ ] Add risk rejection test.

## Documentation
- [ ] Update `ACCEPTANCE.md`.
- [ ] Create `SECURITY.md`.
- [ ] Create `OPERATIONS.md`.
- [ ] Create `CHANGELOG.md`.
