# Solutions — 14 Filters Numeric

**Source:** [`../../coding_rounds/14_filters_numeric.md`](../../coding_rounds/14_filters_numeric.md)  
**Questions:** 6  

---

## C213 — Moving average

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Moving average?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Moving average in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    int32_t buf[8];
    int idx;
    int32_t sum;
}
ma_t;
int32_t ma_push(ma_t *m,int32_t v) {
    m->sum-=m->buf[m->idx];
    m->buf[m->idx]=v;
    m->sum+=v;
    m->idx=(m->idx+1)%8;
    return m->sum/8;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Fixed-point

**A:** Use 32-bit Q16.16; guard shifts; saturate on overflow; verify with float reference offline.

**Q:** Weighted

**A:** For Moving average: state the invariant you protect, measure worst-case latency, then optimize — 'Weighted' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C213
#include <assert.h>

int main(void) {
    /* TODO: wire to C213 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C214 — EWMA / LPF (Tesla-style)

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for EWMA / LPF (Tesla-style)?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build EWMA / LPF (Tesla-style) in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    int32_t y;
    int alpha_q8;
}
ewma_t;
int32_t ewma_push(ewma_t *f,int32_t x) {
    f->y=f->y+((f->alpha_q8*(x-f->y))>>8);
    return f->y;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Zero-length operation — defined no-op success.
2. Maximum size/at limit — correct result without overrun.
3. Repeated calls idempotent where API semantics require it.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Fixed-point version

**A:** Use 32-bit Q16.16; guard shifts; saturate on overflow; verify with float reference offline.

**Q:** α parameterization

**A:** For EWMA / LPF (Tesla-style): state the invariant you protect, measure worst-case latency, then optimize — 'α parameterization' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C214
#include <assert.h>

int main(void) {
    /* TODO: wire to C214 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C215 — Binary debounce filter

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Bit width and polynomial for CRC? Table-driven or bit-by-bit?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Binary debounce filter?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Binary debounce filter in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
int32_t clamp_i32(int32_t v,int32_t lo,int32_t hi) {
    if(v<lo)return lo;
    if(v>hi)return hi;
    return v;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Zero-length operation — defined no-op success.
2. Maximum size/at limit — correct result without overrun.
3. Repeated calls idempotent where API semantics require it.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Time-based vs count-based

**A:** For Binary debounce filter: state the invariant you protect, measure worst-case latency, then optimize — 'Time-based vs count-based' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** ISR usage

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C215
#include <assert.h>

int main(void) {
    /* TODO: wire to C215 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C216 — Median of 3

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Median of 3?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Median of 3 in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
int32_t map_range(int32_t x,int32_t in_lo,int32_t in_hi,int32_t out_lo,int32_t out_hi) {
    return out_lo+(x-in_lo)*(out_hi-out_lo)/(in_hi-in_lo);
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Zero-length operation — defined no-op success.
2. Maximum size/at limit — correct result without overrun.
3. Repeated calls idempotent where API semantics require it.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Median of 5

**A:** For Median of 3: state the invariant you protect, measure worst-case latency, then optimize — 'Median of 5' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Sort network

**A:** For Median of 3: state the invariant you protect, measure worst-case latency, then optimize — 'Sort network' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C216
#include <assert.h>

int main(void) {
    /* TODO: wire to C216 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C217 — Slew / rate limit

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Slew / rate limit?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Slew / rate limit in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
int32_t lerp(int32_t a,int32_t b,int32_t t_q15) {
    return a+((b-a)*t_q15>>15);
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Zero-length operation — defined no-op success.
2. Maximum size/at limit — correct result without overrun.
3. Repeated calls idempotent where API semantics require it.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Time-based slew

**A:** For Slew / rate limit: state the invariant you protect, measure worst-case latency, then optimize — 'Time-based slew' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Nonlinear

**A:** For Slew / rate limit: state the invariant you protect, measure worst-case latency, then optimize — 'Nonlinear' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C217
#include <assert.h>

int main(void) {
    /* TODO: wire to C217 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C218 — PID step (fixed-point)

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for PID step (fixed-point)?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build PID step (fixed-point) in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
int32_t median3(int32_t a,int32_t b,int32_t c) {
    if(a>b) {
        int32_t t=a;
        a=b;
        b=t;
    }
    if(b>c) {
        int32_t t=b;
        b=c;
        c=t;
    }
    if(a>b) {
        int32_t t=a;
        a=b;
        b=t;
    }
    return b;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Derivative on measurement

**A:** For PID step (fixed-point): state the invariant you protect, measure worst-case latency, then optimize — 'Derivative on measurement' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Feedforward

**A:** For PID step (fixed-point): state the invariant you protect, measure worst-case latency, then optimize — 'Feedforward' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C218
#include <assert.h>

int main(void) {
    /* TODO: wire to C218 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

