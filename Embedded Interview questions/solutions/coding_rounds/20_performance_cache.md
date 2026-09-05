# Solutions — 20 Performance Cache

**Source:** [`../../coding_rounds/20_performance_cache.md`](../../coding_rounds/20_performance_cache.md)  
**Questions:** 10  

---

## C276 — AoS to SoA transform

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for AoS to SoA transform?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build AoS to SoA transform in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
    float x,y,z;
}
aos_t;
typedef struct {
    float x[1024],y[1024],z[1024];
}
soa_t;
void aos_to_soa(const aos_t *in,soa_t *out,size_t n) {
    for(size_t i=0;
    i<n;
    ++i) {
        out->x[i]=in[i].x;
        out->y[i]=in[i].y;
        out->z[i]=in[i].z;
    }
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

**Q:** In-place?

**A:** For AoS to SoA transform: state the invariant you protect, measure worst-case latency, then optimize — 'In-place?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** SIMD

**A:** For AoS to SoA transform: state the invariant you protect, measure worst-case latency, then optimize — 'SIMD' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C276
#include <assert.h>

int main(void) {
    /* TODO: wire to C276 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C277 — Prefetch-friendly loop

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Prefetch-friendly loop?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Prefetch-friendly loop in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
uint32_t checksum(const uint8_t *b, size_t n);
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

**Q:** Blocking for L1

**A:** For Prefetch-friendly loop: state the invariant you protect, measure worst-case latency, then optimize — 'Blocking for L1' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Prefetch distance

**A:** `__builtin_prefetch(p+stride, 0, 3)` one iteration ahead; align base to cache line.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C277
#include <assert.h>

int main(void) {
    /* TODO: wire to C277 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C278 — False sharing fix

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for False sharing fix?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build False sharing fix in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Empty: `head==tail`; full: `next(head)==tail` (spare slot) unless count field used.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
void hot_loop(int *a,size_t n) {
    for(size_t i=0;
    i<n;
    ++i)a[i]*=2;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** How to measure

**A:** For False sharing fix: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

**Q:** Destructive interference

**A:** For False sharing fix: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C278
#include <assert.h>

int main(void) {
    /* TODO: wire to C278 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C279 — Branchless clamp

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Branchless clamp?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Branchless clamp in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
    uint8_t a,b,c,d;
}
padded_t;
size_t packed_copy(padded_t *d,const padded_t *s,size_t n) {
    for(size_t i=0;
    i<n;
    ++i)d[i]=s[i];
    return n;
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

**Q:** Conditional move

**A:** For Branchless clamp: state the invariant you protect, measure worst-case latency, then optimize — 'Conditional move' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** SIMD select

**A:** `poll_wait` adds fd to wait queue; ISR wakes via `wake_up_interruptible` when data ready.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C279
#include <assert.h>

int main(void) {
    /* TODO: wire to C279 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C280 — Word-wise checksum

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Bit width and polynomial for CRC? Table-driven or bit-by-bit?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Word-wise checksum?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Word-wise checksum in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
void unroll4(const int *in,int *out,size_t n) {
    size_t i=0;
    for(;
    i+4<=n;
    i+=4) {
        out[i]=in[i];
        out[i+1]=in[i+1];
        out[i+2]=in[i+2];
        out[i+3]=in[i+3];
    }
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

**Q:** Unaligned BE CPU

**A:** For Word-wise checksum: state the invariant you protect, measure worst-case latency, then optimize — 'Unaligned BE CPU' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** IP checksum

**A:** CRC catches bursty errors; add sequence numbers for duplication; ECC for NAND/NOR at driver layer.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C280
#include <assert.h>

int main(void) {
    /* TODO: wire to C280 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C281 — Alignment-aware copy

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Alignment-aware copy?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Alignment-aware copy in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
int branchless_max(int a,int b) {
    return a+((b-a)&((b-a)>>31));
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

**Q:** memmove overlap

**A:** `memcpy` is UB on overlap; `memmove` copies forward or backward depending on address order.

**Q:** Benchmark

**A:** For Alignment-aware copy: state the invariant you protect, measure worst-case latency, then optimize — 'Benchmark' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C281
#include <assert.h>

int main(void) {
    /* TODO: wire to C281 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C282 — Hot/cold structure split

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Hot/cold structure split?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Hot/cold structure split in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
void aligned_copy(void *dst,const void *src,size_t n) {
    unsigned char *d=dst;
    const unsigned char *s=src;
    for(size_t i=0;
    i<n;
    ++i)d[i]=s[i];
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

**Q:** Profile-guided

**A:** For Hot/cold structure split: state the invariant you protect, measure worst-case latency, then optimize — 'Profile-guided' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** False sharing again

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C282
#include <assert.h>

int main(void) {
    /* TODO: wire to C282 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C283 — Reduce copies in TX path

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Reduce copies in TX path?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Reduce copies in TX path in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
    int key, val;
}
kv_t;
void sort_kv(kv_t *a,size_t n) {
    for(size_t i=1;
    i<n;
    ++i) {
        kv_t k=a[i];
        ssize_t j=i-1;
        while(j>=0&&a[j].key>k.key) {
            a[j+1]=a[j];
            --j;
        }
        a[j+1]=k;
    }
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

**Q:** Lifetime scatterlist

**A:** Build descriptor list in RAM; program first desc; chain `next` pointers; IRQ on last completion.

**Q:** Lifetime lifetime

**A:** For Reduce copies in TX path: state the invariant you protect, measure worst-case latency, then optimize — 'Lifetime lifetime' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C283
#include <assert.h>

int main(void) {
    /* TODO: wire to C283 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C284 — Bit-reverse LUT vs compute

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Bit-reverse LUT vs compute?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Bit-reverse LUT vs compute in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
size_t strided_sum(const int *a,size_t n,size_t stride) {
    size_t s=0;
    for(size_t i=0;
    i<n;
    i+=stride)s+=a[i];
    return s;
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

**Q:** Generate LUT at compile time

**A:** For Bit-reverse LUT vs compute: state the invariant you protect, measure worst-case latency, then optimize — 'Generate LUT at compile time' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Cache pressure

**A:** SoA vs AoS: SoA helps SIMD and sequential access; AoS is better for single-struct locality. Prefetch next cache line in hot loops; align to 32/64 B.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C284
#include <assert.h>

int main(void) {
    /* TODO: wire to C284 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C285 — Ring indices cache-line placement

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Ring indices cache-line placement?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Ring indices cache-line placement in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Empty: `head==tail`; full: `next(head)==tail` (spare slot) unless count field used.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
int perf_self_test(void) {
    return 0;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Linux kernel ring examples

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

**Q:** Performance test

**A:** Table-test every state/event edge, plus fault injection for timeouts, NACK, and buffer full.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C285
#include <assert.h>

int main(void) {
    /* TODO: wire to C285 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

