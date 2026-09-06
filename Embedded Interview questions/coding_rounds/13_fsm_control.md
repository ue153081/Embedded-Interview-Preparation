# FSM & Control Coding

**IDs:** C201–C212 (12 questions)  
**Focus:** Traffic/vending/connection FSMs, table-driven and hierarchical.

[← Back to category index](./README.md)

---

### C201 — Traffic light FSM

**Interview prompt:**  
Implement a traffic light state machine; ignore invalid inputs; support FAULT from any state.

**Implement:**
```c
typedef enum { IDLE, READY, GO, FAULT } st_t;
typedef enum { TIMER, BUTTON, FAULT_EVT } ev_t;
st_t traffic_step(st_t s, ev_t e);
```

**Constraints / expectations:**
- No transition on invalid
- Pure function or with side effects—document

**Follow-ups:**
- Timing table
- Pedestrian phase

---

### C202 — Vending machine FSM (Tesla-style)

**Interview prompt:**  
States IDLE/READY/VENDING/FAULT; inputs COIN, COIN_RETURN, BUTTON, VEND_COMPLETE, GENERIC_FAULT. Invalid inputs do nothing. GENERIC_FAULT→FAULT from any state.

**Implement:**
```c
typedef enum { IDLE, READY, VENDING, FAULT } state_E;
typedef enum { COIN, COIN_RETURN, BUTTON, VEND_COMPLETE, GENERIC_FAULT } input_E;
state_E stateMachine(input_E input);
```

**Constraints / expectations:**
- Initial IDLE
- Return current state
- No crash on unexpected

**Follow-ups:**
- Add refund path
- Unit tests all edges

---

### C203 — Connection FSM

**Interview prompt:**  
DISCONNECTED→CONNECTING→AUTH→READY→ERROR with timeouts.

**Implement:**
```c
st_t conn_step(st_t s, ev_t e, uint32_t now);
```

**Constraints / expectations:**
- Timeout events
- Retry limits

**Follow-ups:**
- Backoff
- TLS analogy

---

### C204 — Driver power FSM

**Interview prompt:**  
OFF/INIT/RUN/SUSPEND/ERROR with legal transitions only.

**Implement:**
```c
int drv_event(drv_t *d, ev_t e);
```

**Constraints / expectations:**
- Illegal transition errors
- Entry/exit actions stubs

**Follow-ups:**
- Runtime PM mapping
- Wake sources

---

### C205 — Hierarchical FSM

**Interview prompt:**  
Parent mode ACTIVE has child states RUNNING/PAUSED. Implement hierarchy.

**Implement:**
```c
/* parent/child state handlers */
```

**Constraints / expectations:**
- Events bubble or consume—document
- Exit child before parent

**Follow-ups:**
- UML statechart features
- Concurrency regions skip

---

### C206 — Table-driven FSM

**Interview prompt:**  
Encode transitions in a table[state][event] = next/action.

**Implement:**
```c
typedef void (*action_t)(void);
typedef struct { int next; action_t act; } cell_t;
int fsm_step(int state, int event);
```

**Constraints / expectations:**
- Sparse table OK
- Bounds check

**Follow-ups:**
- Code gen from table
- Flash size

---

### C207 — Entry/exit actions + guards

**Interview prompt:**  
On transition, run exit(old), action, enter(new). Guards can cancel.

**Implement:**
```c
int fsm_try(fsm_t *f, int event);
```

**Constraints / expectations:**
- Order of actions
- Guard predicates

**Follow-ups:**
- Re-entrant events
- Logging transitions

---

### C208 — Quadrature direction FSM

**Interview prompt:**  
From two sampler bits in a cyclic Gray sequence, decide forward/backward (Google-style).

**Implement:**
```c
typedef enum { FWD, BACK, NONE, ERROR } dir_t;
dir_t direction(uint8_t prev, uint8_t now);
```

**Constraints / expectations:**
- Illegal jumps → ERROR not crash
- Document encoding of two bits

**Follow-ups:**
- Missing sample recovery
- Debounce

---

### C209 — Button UI FSM

**Interview prompt:**  
IDLE→DOWN→HOLD→REPEAT with timings.

**Implement:**
```c
ui_ev_t button_fsm(uint32_t now, int level);
```

**Constraints / expectations:**
- Configurable ms
- Clean edges

**Follow-ups:**
- Multi-button
- Gesture

---

### C210 — Session FSM with timeouts

**Interview prompt:**  
Protocol session with keepalive timeout and retransmit timer integration.

**Implement:**
```c
void session_on_rx(void);
void session_on_tick(uint32_t now);
```

**Constraints / expectations:**
- Armed timers
- State-specific timeout

**Follow-ups:**
- Backoff
- Max lifetime

---

### C211 — Retry then fault FSM

**Interview prompt:**  
On error retry up to N with delay; then FAULT; allow RESET event.

**Implement:**
```c
st_t recover_step(st_t s, ev_t e);
```

**Constraints / expectations:**
- Count retries
- Reset clears

**Follow-ups:**
- Jittered delay
- Circuit breaker link

---

### C212 — Exclusive mode manager

**Interview prompt:**  
Clients request modes; only one active; queue or reject second request.

**Implement:**
```c
int mode_request(mode_t m);
void mode_release(mode_t m);
```

**Constraints / expectations:**
- Priority optional
- Define conflict policy

**Follow-ups:**
- Preempt low mode
- Reference count shared mode

---


---

[← Back to category index](./README.md)
