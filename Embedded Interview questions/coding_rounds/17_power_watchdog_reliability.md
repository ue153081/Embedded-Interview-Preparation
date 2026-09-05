# Power, Watchdog & Reliability

**IDs:** C241–C250 (10 questions)  
**Focus:** WDT, heartbeats, brownout, backoff, circuit breaker, safe state.

[← Back to category index](./README.md)

---

### C241 — Watchdog kick window

**Interview prompt:**  
Start watchdog; kick within open window; early/late kick is bad if windowed.

**Implement:**
```c
int wdt_init(uint32_t timeout_ms);
int wdt_kick(void);
```

**Constraints / expectations:**
- Document windowed vs simple
- Error if kicked wrong

**Follow-ups:**
- Task-based kicking
- External WDT pin

---

### C242 — Task heartbeat supervisor

**Interview prompt:**  
Tasks register and kick heartbeats; supervisor resets if one stalls.

**Implement:**
```c
int hb_register(unsigned id, uint32_t max_ms);
void hb_kick(unsigned id);
void hb_supervise(uint32_t now_ms);
```

**Constraints / expectations:**
- Detect stuck id
- Action: log+reset

**Follow-ups:**
- Suspend when task paused
- Priority of supervisor

---

### C243 — Stuck detection via progress counter

**Interview prompt:**  
Monitored code increments progress; checker ensures it changes.

**Implement:**
```c
void progress_tick(void);
int progress_check(uint32_t now);
```

**Constraints / expectations:**
- Timeout
- Sticky fault

**Follow-ups:**
- vs heartbeat API
- False positive when idle intentionally

---

### C244 — Brownout latch → safe mode

**Interview prompt:**  
On brownout IRQ, latch flag and enter safe outputs.

**Implement:**
```c
void brownout_isr(void);
void main_check_brownout(void);
```

**Constraints / expectations:**
- ISR minimal
- Safe GPIO state

**Follow-ups:**
- Hysteresis re-enable
- Capacitor time budget

---

### C245 — Exponential backoff retry

**Interview prompt:**  
Retry an operation with exponential backoff + optional jitter.

**Implement:**
```c
int retry_call(int (*fn)(void), unsigned max_tries);
```

**Constraints / expectations:**
- Cap max delay
- Jitter function stub

**Follow-ups:**
- Distinguish retryable errors
- Circuit breaker

---

### C246 — Circuit breaker

**Interview prompt:**  
After N consecutive failures, open circuit for cooldown; then half-open trial.

**Implement:**
```c
typedef enum { CB_CLOSED, CB_OPEN, CB_HALF } cb_st;
int cb_call(cb_t *cb, int (*fn)(void));
```

**Constraints / expectations:**
- State machine correct
- Configurable thresholds

**Follow-ups:**
- Metrics
- Per-endpoint breakers

---

### C247 — Suspend/resume peripheral context

**Interview prompt:**  
Save/restore device registers around suspend.

**Implement:**
```c
int dev_suspend(dev_t *d);
int dev_resume(dev_t *d);
```

**Constraints / expectations:**
- Idempotent
- Order of restore

**Follow-ups:**
- Runtime PM counts
- Wake IRQ

---

### C248 — Idempotent reinit after reset

**Interview prompt:**  
Device may be hard-reset; reinit must work whether first time or after crash.

**Implement:**
```c
int dev_reinit(dev_t *d);
```

**Constraints / expectations:**
- No leak of resources
- Detect already-inited

**Follow-ups:**
- Partial failure
- Soft vs hard reset

---

### C249 — Config CRC + default repair

**Interview prompt:**  
Stored config has CRC; on mismatch load defaults and flag error.

**Implement:**
```c
int config_load(cfg_t *c);
int config_save(const cfg_t *c);
```

**Constraints / expectations:**
- CRC function reuse
- Atomic save strategy simple

**Follow-ups:**
- A/B config slots
- Migration

---

### C250 — Safe-state outputs

**Interview prompt:**  
Central function forces outputs into safe mode (motors off, valves closed).

**Implement:**
```c
void enter_safe_state(void);
```

**Constraints / expectations:**
- Can call from fault path
- No alloc
- Document each pin

**Follow-ups:**
- Exit conditions
- Latched vs temporary

---


---

[← Back to category index](./README.md)
