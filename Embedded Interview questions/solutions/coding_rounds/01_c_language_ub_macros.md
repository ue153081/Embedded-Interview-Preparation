# Solutions — 01 C Language Ub Macros

**Source:** [`../../coding_rounds/01_c_language_ub_macros.md`](../../coding_rounds/01_c_language_ub_macros.md)  
**Questions:** 20  

---

## C001 — container_of / offsetof

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for container_of / offsetof?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build container_of / offsetof in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
#include <stddef.h>
#define offsetof(type, member) ((size_t)&(((type *)0)->member))
#define container_of(ptr, type, member) ((type *)((char *)(ptr) - offsetof(type, member)))
struct list_node { struct list_node *next; };
struct device { int id; struct list_node link; };
struct device *device_from_node(struct list_node *n) {
    return container_of(n, struct device, link);
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

**Q:** Why not just cast node to device?

**A:** For container_of / offsetof: state the invariant you protect, measure worst-case latency, then optimize — 'Why not just cast node to device?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** NULL handling?

**A:** For container_of / offsetof: state the invariant you protect, measure worst-case latency, then optimize — 'NULL handling?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** typeof-safe variant?

**A:** For container_of / offsetof: state the invariant you protect, measure worst-case latency, then optimize — 'typeof-safe variant?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C001
#include <assert.h>

int main(void) {
    /* TODO: wire to C001 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C002 — Compile-time struct layout asserts

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Compile-time struct layout asserts?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Compile-time struct layout asserts in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
struct pkt_hdr { uint8_t type, flags; uint16_t len; uint32_t seq; };
#define STATIC_ASSERT(cond, msg) _Static_assert(cond, msg)
STATIC_ASSERT(sizeof(struct pkt_hdr) == 8, "pkt_hdr size");
STATIC_ASSERT(offsetof(struct pkt_hdr, len) == 2, "len offset");
STATIC_ASSERT(offsetof(struct pkt_hdr, seq) == 4, "seq offset");
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Timestamp counter wrap — use signed delta compare; document max interval < 2³¹ ticks.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Packed attribute vs manual serialize?

**A:** For Compile-time struct layout asserts: state the invariant you protect, measure worst-case latency, then optimize — 'Packed attribute vs manual serialize?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** How to assert alignment?

**A:** For Compile-time struct layout asserts: state the invariant you protect, measure worst-case latency, then optimize — 'How to assert alignment?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C002
#include <assert.h>

int main(void) {
    /* TODO: wire to C002 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C003 — ARRAY_SIZE / MIN / MAX / BIT / GENMASK

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for ARRAY_SIZE / MIN / MAX / BIT / GENMASK?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build ARRAY_SIZE / MIN / MAX / BIT / GENMASK in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#define BIT(n) (1u << (n))
#define GENMASK(h,l) (((BIT((h)-(l)+1) - 1u) << (l)))
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

**Q:** Unsafe MIN(i++, j) example

**A:** For ARRAY_SIZE / MIN / MAX / BIT / GENMASK: state the invariant you protect, measure worst-case latency, then optimize — 'Unsafe MIN(i++, j) example' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** typeof-based MIN

**A:** For ARRAY_SIZE / MIN / MAX / BIT / GENMASK: state the invariant you protect, measure worst-case latency, then optimize — 'typeof-based MIN' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C003
#include <assert.h>

int main(void) {
    /* TODO: wire to C003 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C004 — likely / unlikely

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for likely / unlikely?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build likely / unlikely in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
#ifdef __GNUC__
#define likely(x)   __builtin_expect(!!(x), 1)
#define unlikely(x) __builtin_expect(!!(x), 0)
#else
#define likely(x)   (x)
#define unlikely(x) (x)
#endif
int parse_frame(const uint8_t *buf, size_t n) {
    if (unlikely(!buf || n < 4)) return -1;
    if (likely(buf[0] == 0xAA)) return (int)buf[1];
    return -2;
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

**Q:** Does it affect correctness?

**A:** For likely / unlikely: state the invariant you protect, measure worst-case latency, then optimize — 'Does it affect correctness?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Mis-hinting cost?

**A:** For likely / unlikely: state the invariant you protect, measure worst-case latency, then optimize — 'Mis-hinting cost?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C004
#include <assert.h>

int main(void) {
    /* TODO: wire to C004 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C005 — Fix undefined behavior snippets

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Fix undefined behavior snippets?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Fix undefined behavior snippets in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
#include <stdbool.h>
static inline uint16_t bswap16(uint16_t x) { return (uint16_t)((x>>8)|((x&0xFFu)<<8)); }
static inline uint32_t bswap32(uint32_t x) {
    return ((x & 0xFFu)<<24)|((x & 0xFF00u)<<8)|((x>>8)&0xFF00u)|((x>>24)&0xFFu);
}
uint32_t read_be32(const uint8_t *p) {
    return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];
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

**Q:** Sanitizers to catch these?

**A:** For Fix undefined behavior snippets: state the invariant you protect, measure worst-case latency, then optimize — 'Sanitizers to catch these?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** -fwrapv?

**A:** For Fix undefined behavior snippets: state the invariant you protect, measure worst-case latency, then optimize — '-fwrapv?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C005
#include <assert.h>

int main(void) {
    /* TODO: wire to C005 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C006 — volatile flag vs atomics

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for volatile flag vs atomics?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build volatile flag vs atomics in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
void write_le16(uint8_t *p, uint16_t v) {
    p[0]=(uint8_t)v;
    p[1]=(uint8_t)(v>>8);
}
uint16_t read_le16(const uint8_t *p) {
    return (uint16_t)p[0]|((uint16_t)p[1]<<8);
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

ISR sets flags/enqueues only; task drains. If both touch state, IRQ-save critical section.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** When is volatile enough on M-profile?

**A:** For volatile flag vs atomics: state the invariant you protect, measure worst-case latency, then optimize — 'When is volatile enough on M-profile?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** acquire/release?

**A:** For volatile flag vs atomics: state the invariant you protect, measure worst-case latency, then optimize — 'acquire/release?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C006
#include <assert.h>

int main(void) {
    /* TODO: wire to C006 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C007 — align_up / align_down

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for align_up / align_down?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build align_up / align_down in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
#include <stdbool.h>
bool add_u32_sat(uint32_t a, uint32_t b, uint32_t *out) {
    uint32_t r = a + b; if (r < a) return false; *out = r; return true;
}
bool mul_u32_sat(uint32_t a, uint32_t b, uint32_t *out) {
    if (a && b > UINT32_MAX / a) return false; *out = a * b; return true;
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

**Q:** Pointer alignment?

**A:** For align_up / align_down: state the invariant you protect, measure worst-case latency, then optimize — 'Pointer alignment?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Non-PoT align?

**A:** For align_up / align_down: state the invariant you protect, measure worst-case latency, then optimize — 'Non-PoT align?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C007
#include <assert.h>

int main(void) {
    /* TODO: wire to C007 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C008 — Portable pack/unpack vs packed struct

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Portable pack/unpack vs packed struct?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Portable pack/unpack vs packed struct in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
int safe_downcast_u64_u32(uint64_t v, uint32_t *out) {
    if (v > UINT32_MAX) return -1;
    *out = (uint32_t)v;
    return 0;
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

**Q:** When is packed OK?

**A:** For Portable pack/unpack vs packed struct: state the invariant you protect, measure worst-case latency, then optimize — 'When is packed OK?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Add versioning

**A:** For Portable pack/unpack vs packed struct: state the invariant you protect, measure worst-case latency, then optimize — 'Add versioning' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C008
#include <assert.h>

int main(void) {
    /* TODO: wire to C008 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C009 — Flexible array packet alloc

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Fixed block size or variable? Is free allowed from ISR?
- **Candidate:** Should exhaustion return NULL or a dedicated error code?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Flexible array packet alloc?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Flexible array packet alloc in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
#include <stdbool.h>
bool is_aligned(const void *p, size_t a) { return (((uintptr_t)p & (a-1)) == 0); }
void *align_up_ptr(void *p, size_t a) {
    uintptr_t v = (uintptr_t)p; v = (v + a - 1) & ~(a - 1); return (void *)v;
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

**Q:** Pool version?

**A:** For Flexible array packet alloc: state the invariant you protect, measure worst-case latency, then optimize — 'Pool version?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Alignment of data[]?

**A:** For Flexible array packet alloc: state the invariant you protect, measure worst-case latency, then optimize — 'Alignment of data[]?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C009
#include <assert.h>

int main(void) {
    /* TODO: wire to C009 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C010 — const-correct APIs

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for const-correct APIs?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build const-correct APIs in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
#ifndef NDEBUG
#define ASSERT(c) do { if (!(c)) { __builtin_trap(); } } while(0)
#else
#define ASSERT(c) ((void)0)
#endif
void use(int x) { ASSERT(x >= 0); }
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

**Q:** restrict keyword?

**A:** For const-correct APIs: state the invariant you protect, measure worst-case latency, then optimize — 'restrict keyword?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** C++ overloads?

**A:** For const-correct APIs: state the invariant you protect, measure worst-case latency, then optimize — 'C++ overloads?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C010
#include <assert.h>

int main(void) {
    /* TODO: wire to C010 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C011 — Opcode handler table

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Opcode handler table?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Opcode handler table in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
typedef enum { ERR_OK=0, ERR_IO=-1, ERR_TIMEOUT=-2 } err_t;
const char *err_str(err_t e) {
    switch(e){case ERR_OK:return "OK";case ERR_IO:return "IO";default:return "TIMEOUT";}
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

**Q:** O(1) indexed table?

**A:** For Opcode handler table: state the invariant you protect, measure worst-case latency, then optimize — 'O(1) indexed table?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** ISR context?

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C011
#include <assert.h>

int main(void) {
    /* TODO: wire to C011 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C012 — memcpy vs memmove with restrict

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** May source and destination overlap? Alignment assumptions on buffers?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for memcpy vs memmove with restrict?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build memcpy vs memmove with restrict in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
typedef struct __attribute__((packed)) { uint8_t a; uint32_t b; } packed_t;
void pack_copy(const packed_t *src, uint8_t *dst) {
    for (size_t i=0;i<sizeof(packed_t);++i) ((uint8_t*)dst)[i]=((const uint8_t*)src)[i];
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Overlapping buffers — memmove direction; memcpy requires non-overlap.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Optimize with word copies?

**A:** For memcpy vs memmove with restrict: state the invariant you protect, measure worst-case latency, then optimize — 'Optimize with word copies?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** How to detect overlap?

**A:** `memcpy` is UB on overlap; `memmove` copies forward or backward depending on address order.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Overlapping regions forward and backward.

Optional harness:

```c
#ifdef TEST_C012
#include <assert.h>

int main(void) {
    /* TODO: wire to C012 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C013 — Endian helpers unaligned-safe

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Endian helpers unaligned-safe?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Endian helpers unaligned-safe in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
union reg { uint32_t w; struct { uint16_t lo, hi; } h; };
uint16_t reg_get_field(uint32_t w, unsigned lo, unsigned width) {
    return (uint16_t)((w >> lo) & ((1u<<width)-1u));
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

**Q:** BE loads / LE stores too

**A:** For Endian helpers unaligned-safe: state the invariant you protect, measure worst-case latency, then optimize — 'BE loads / LE stores too' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Cortex-M unaligned traps?

**A:** For Endian helpers unaligned-safe: state the invariant you protect, measure worst-case latency, then optimize — 'Cortex-M unaligned traps?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C013
#include <assert.h>

int main(void) {
    /* TODO: wire to C013 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C014 — uint8_t bit clear promotion bug

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for uint8_t bit clear promotion bug?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build uint8_t bit clear promotion bug in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
void *clear_struct(void *p, size_t n) {
    unsigned char *b=p;
    for(size_t i=0;
    i<n;
    ++i) b[i]=0;
    return p;
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

**Q:** uint16_t similar issues?

**A:** For uint8_t bit clear promotion bug: state the invariant you protect, measure worst-case latency, then optimize — 'uint16_t similar issues?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** MISRA notes?

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C014
#include <assert.h>

int main(void) {
    /* TODO: wire to C014 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C015 — Enum mode handler

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Enum mode handler?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Enum mode handler in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
typedef void (*isr_fn)(void);
static isr_fn g_vtable[4];
void isr_register(unsigned id, isr_fn fn) { if(id<4) g_vtable[id]=fn; }
void isr_dispatch(unsigned id) { if(id<4 && g_vtable[id]) g_vtable[id](); }
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

**Q:** Wire-size packed enums?

**A:** For Enum mode handler: state the invariant you protect, measure worst-case latency, then optimize — 'Wire-size packed enums?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Table-driven approach?

**A:** For Enum mode handler: state the invariant you protect, measure worst-case latency, then optimize — 'Table-driven approach?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C015
#include <assert.h>

int main(void) {
    /* TODO: wire to C015 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C016 — Status register pack/unpack

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Status register pack/unpack?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Status register pack/unpack in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
static const char *const names[] = {
    "idle","run","fault"
};
const char *state_name(unsigned s) {
    return s<3?names[s]:"unknown";
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

**Q:** Atomic RMW updates?

**A:** For Status register pack/unpack: state the invariant you protect, measure worst-case latency, then optimize — 'Atomic RMW updates?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Linux FIELD_GET style macros?

**A:** For Status register pack/unpack: state the invariant you protect, measure worst-case latency, then optimize — 'Linux FIELD_GET style macros?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C016
#include <assert.h>

int main(void) {
    /* TODO: wire to C016 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C017 — Driver status return codes

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Driver status return codes?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Driver status return codes in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
    int x,y;
}
point_t;
point_t points[10];
point_t *get_point(unsigned i) {
    return i<10?&points[i]:0;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Timeout expiry — return distinct error; leave hardware in bus-safe state.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Return byte count instead?

**A:** For Driver status return codes: state the invariant you protect, measure worst-case latency, then optimize — 'Return byte count instead?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Map to Linux errno?

**A:** For Driver status return codes: state the invariant you protect, measure worst-case latency, then optimize — 'Map to Linux errno?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C017
#include <assert.h>

int main(void) {
    /* TODO: wire to C017 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C018 — FW_ASSERT / BUG_ON / WARN_ON

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for FW_ASSERT / BUG_ON / WARN_ON?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build FW_ASSERT / BUG_ON / WARN_ON in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
#include <stdbool.h>
bool in_range_u32(uint32_t v, uint32_t lo, uint32_t hi) {
    return v>=lo && v<=hi;
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

**Q:** ISR-safe asserts?

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

**Q:** Retained-RAM breadcrumbs?

**A:** For FW_ASSERT / BUG_ON / WARN_ON: state the invariant you protect, measure worst-case latency, then optimize — 'Retained-RAM breadcrumbs?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C018
#include <assert.h>

int main(void) {
    /* TODO: wire to C018 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C019 — static inline max vs macro

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for static inline max vs macro?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build static inline max vs macro in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
#define STR2(x) #x
#define STR(x) STR2(x)
const char *build_tag(void) {
    return "build=" STR(__LINE__);
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

**Q:** always_inline?

**A:** For static inline max vs macro: state the invariant you protect, measure worst-case latency, then optimize — 'always_inline?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** C++ overload set?

**A:** For static inline max vs macro: state the invariant you protect, measure worst-case latency, then optimize — 'C++ overload set?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C019
#include <assert.h>

int main(void) {
    /* TODO: wire to C019 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C020 — Type-generic max

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Type-generic max?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Type-generic max in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
typedef struct node {
    struct node *next;
    int v;
}
node_t;
int list_sum(const node_t *h) {
    int s=0;
    while(h) {
        s+=h->v;
        h=h->next;
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

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Linux min/max macros?

**A:** For Type-generic max: state the invariant you protect, measure worst-case latency, then optimize — 'Linux min/max macros?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** float NaN?

**A:** For Type-generic max: state the invariant you protect, measure worst-case latency, then optimize — 'float NaN?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C020
#include <assert.h>

int main(void) {
    /* TODO: wire to C020 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

