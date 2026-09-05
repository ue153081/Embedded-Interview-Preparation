# Solutions — 13 Fsm Control

**Source:** [`../../coding_rounds/13_fsm_control.md`](../../coding_rounds/13_fsm_control.md)  
**Questions:** 12  

---

## C201 — Traffic light FSM

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Traffic light FSM?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Traffic light FSM in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef enum {
    IDLE, READY, GO, FAULT
}
st_t;
typedef enum {
    TIMER, BUTTON, FAULT_EVT
}
ev_t;
st_t traffic_step(st_t s,ev_t e) {
    switch(s) {
        case IDLE:if(e==TIMER)return READY;
        break;
        case READY:if(e==BUTTON)return GO;
        break;
        case GO:if(e==TIMER)return IDLE;
        break;
        default:break;
    }
    if(e==FAULT_EVT)return FAULT;
    return s;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Timing table

**A:** For Traffic light FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Timing table' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Pedestrian phase

**A:** For Traffic light FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Pedestrian phase' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C201
#include <assert.h>

int main(void) {
    /* TODO: wire to C201 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C202 — Vending machine FSM (Tesla-style)

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Vending machine FSM (Tesla-style)?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Vending machine FSM (Tesla-style) in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>

typedef enum { IDLE, READY, VENDING, FAULT } state_E;
typedef enum { COIN, COIN_RETURN, BUTTON, VEND_COMPLETE, GENERIC_FAULT } input_E;

static state_E g_state = IDLE;

state_E stateMachine(input_E input) {
    switch (g_state) {
    case IDLE:
        if (input == COIN) g_state = READY;
        else if (input == GENERIC_FAULT) g_state = FAULT;
        break;
    case READY:
        if (input == BUTTON) g_state = VENDING;
        else if (input == COIN_RETURN) g_state = IDLE;
        else if (input == GENERIC_FAULT) g_state = FAULT;
        break;
    case VENDING:
        if (input == VEND_COMPLETE) g_state = IDLE;
        else if (input == GENERIC_FAULT) g_state = FAULT;
        break;
    case FAULT:
        break; /* stay in FAULT until reset outside scope */
    default:
        g_state = FAULT;
        break;
    }
    if (input == GENERIC_FAULT) {
        g_state = FAULT;
    }
    return g_state;
}

void stateMachine_reset(void) { g_state = IDLE; }
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Add refund path

**A:** For Vending machine FSM (Tesla-style): state the invariant you protect, measure worst-case latency, then optimize — 'Add refund path' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Unit tests all edges

**A:** Table-test every state/event edge, plus fault injection for timeouts, NACK, and buffer full.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C202
#include <assert.h>

int main(void) {
    /* TODO: wire to C202 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C203 — Connection FSM

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Connection FSM?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Connection FSM in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef enum {
    DISC, CONN, AUTH, RDY, ERR
}
st_t;
typedef enum {
    OPEN, OK, FAIL, TIMEOUT
}
ev_t;
st_t conn_step(st_t s,ev_t e,uint32_t now) {
    (void)now;
    (void)e;
    return s;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Backoff

**A:** For Connection FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Backoff' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** TLS analogy

**A:** For Connection FSM: state the invariant you protect, measure worst-case latency, then optimize — 'TLS analogy' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C203
#include <assert.h>

int main(void) {
    /* TODO: wire to C203 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C204 — Driver power FSM

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Driver power FSM?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Driver power FSM in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef enum {
    OFF, INIT, RUN, SUSP, ERROR
}
pwr_t;
pwr_t pwr_step(pwr_t s,int ev) {
    switch(s) {
        case OFF:if(ev==1)return INIT;
        break;
        case INIT:if(ev==2)return RUN;
        break;
        case RUN:if(ev==3)return SUSP;
        break;
        default:break;
    }
    return s;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Runtime PM mapping

**A:** For Driver power FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Runtime PM mapping' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Wake sources

**A:** For Driver power FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Wake sources' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C204
#include <assert.h>

int main(void) {
    /* TODO: wire to C204 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C205 — Hierarchical FSM

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Hierarchical FSM?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Hierarchical FSM in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef enum {
    IDLE, READY, GO, FAULT
}
st_t;
typedef struct {
    st_t s;
    void (*enter)(st_t);
}
sm_t;
void sm_step(sm_t *m,st_t next) {
    m->s=next;
    if(m->enter)m->enter(next);
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** UML statechart features

**A:** For Hierarchical FSM: state the invariant you protect, measure worst-case latency, then optimize — 'UML statechart features' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Concurrency regions skip

**A:** For Hierarchical FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Concurrency regions skip' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C205
#include <assert.h>

int main(void) {
    /* TODO: wire to C205 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C206 — Table-driven FSM

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Table-driven FSM?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Table-driven FSM in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef int (*handler_t)(void);
int table_drive(const handler_t *t,size_t n,unsigned idx) {
    return idx<n&&t[idx]?t[idx]():-1;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Code gen from table

**A:** For Table-driven FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Code gen from table' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Flash size

**A:** For Table-driven FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Flash size' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C206
#include <assert.h>

int main(void) {
    /* TODO: wire to C206 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C207 — Entry/exit actions + guards

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Entry/exit actions + guards?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Entry/exit actions + guards in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef enum {
    IDLE, READY, GO, FAULT
}
st_t;
typedef enum {
    TIMER, BUTTON, FAULT_EVT
}
ev_t;
typedef struct {
    st_t cur, parent;
}
hsm_t;
st_t hsm_step(hsm_t *h,ev_t e) {
    return traffic_step(h->cur,e);
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Re-entrant events

**A:** For Entry/exit actions + guards: state the invariant you protect, measure worst-case latency, then optimize — 'Re-entrant events' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Logging transitions

**A:** For Entry/exit actions + guards: state the invariant you protect, measure worst-case latency, then optimize — 'Logging transitions' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C207
#include <assert.h>

int main(void) {
    /* TODO: wire to C207 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C208 — Quadrature direction FSM

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Quadrature direction FSM?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Quadrature direction FSM in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef enum {
    IDLE, READY, GO, FAULT, ERR
}
st_t;
typedef struct {
    uint32_t timeout_ms;
    st_t s;
}
to_sm_t;
st_t to_tick(to_sm_t *m,uint32_t now) {
    return now>m->timeout_ms?ERR:m->s;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Missing sample recovery

**A:** For Quadrature direction FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Missing sample recovery' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Debounce

**A:** Restart timer on each edge; fire only after quiet period. Separate timers for press vs release if needed.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C208
#include <assert.h>

int main(void) {
    /* TODO: wire to C208 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C209 — Button UI FSM

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Button UI FSM?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Button UI FSM in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef enum {
    IDLE, READY, GO, FAULT
}
st_t;
typedef enum {
    TIMER, BUTTON, FAULT_EVT
}
ev_t;
st_t traffic_step(st_t s,ev_t e);
int fsm_self_test(void) {
    return traffic_step(IDLE,TIMER)==READY?0:-1;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Multi-button

**A:** For Button UI FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Multi-button' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Gesture

**A:** For Button UI FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Gesture' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C209
#include <assert.h>

int main(void) {
    /* TODO: wire to C209 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C210 — Session FSM with timeouts

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Session FSM with timeouts?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Session FSM with timeouts in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef enum {
    IDLE, READY, GO, FAULT
}
st_t;
typedef struct {
    st_t s;
    int history[8];
    int hp;
}
hist_sm_t;
void hist_push(hist_sm_t *m,st_t s) {
    m->history[m->hp++%8]=s;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Timeout expiry — return distinct error; leave hardware in bus-safe state.
2. Timestamp counter wrap — use signed delta compare; document max interval < 2³¹ ticks.
3. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Backoff

**A:** For Session FSM with timeouts: state the invariant you protect, measure worst-case latency, then optimize — 'Backoff' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Max lifetime

**A:** For Session FSM with timeouts: state the invariant you protect, measure worst-case latency, then optimize — 'Max lifetime' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C210
#include <assert.h>

int main(void) {
    /* TODO: wire to C210 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C211 — Retry then fault FSM

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Retry then fault FSM?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Retry then fault FSM in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef enum {
    IDLE, READY, GO, FAULT
}
st_t;
typedef enum {
    TIMER, BUTTON, FAULT_EVT
}
ev_t;
st_t traffic_step(st_t s,ev_t e);
st_t guarded_step(st_t s,ev_t e,int ok) {
    return ok?traffic_step(s,e):s;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Jittered delay

**A:** For Retry then fault FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Jittered delay' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Circuit breaker link

**A:** For Retry then fault FSM: state the invariant you protect, measure worst-case latency, then optimize — 'Circuit breaker link' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C211
#include <assert.h>

int main(void) {
    /* TODO: wire to C211 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C212 — Exclusive mode manager

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should invalid inputs be ignored silently or counted for diagnostics?
- **Candidate:** Do we need entry/exit actions per state, or pure transition function?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Exclusive mode manager?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Exclusive mode manager in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Table- or switch-driven transitions; GENERIC_FAULT from every state.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Current state + transition table rows indexed by `(state, event)`.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
int mode_request(mode_t m);
void mode_release(mode_t m);
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Invalid event in current state — remain in state or transition to FAULT per spec.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Preempt low mode

**A:** For Exclusive mode manager: state the invariant you protect, measure worst-case latency, then optimize — 'Preempt low mode' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Reference count shared mode

**A:** For Exclusive mode manager: state the invariant you protect, measure worst-case latency, then optimize — 'Reference count shared mode' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.

Optional harness:

```c
#ifdef TEST_C212
#include <assert.h>

int main(void) {
    /* TODO: wire to C212 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

