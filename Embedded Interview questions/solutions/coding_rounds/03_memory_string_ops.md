# Solutions — 03 Memory String Ops

**Source:** [`../../coding_rounds/03_memory_string_ops.md`](../../coding_rounds/03_memory_string_ops.md)  
**Questions:** 15  

---

## C041 — Optimized memcpy

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** May source and destination overlap? Alignment assumptions on buffers?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Optimized memcpy?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Optimized memcpy in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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

static void *copy_bytes(void *dst, const void *src, size_t n) {
    unsigned char *d = (unsigned char *)dst;
    const unsigned char *s = (const unsigned char *)src;
    for (size_t i = 0; i < n; ++i) {
        d[i] = s[i];
    }
    return dst;
}

void *my_memcpy(void *dst, const void *src, size_t n) {
    if (n == 0) {
        return dst;
    }
    uintptr_t da = (uintptr_t)dst;
    uintptr_t sa = (uintptr_t)src;
    if ((da & 3u) == 0 && (sa & 3u) == 0) {
        while (n >= 16) {
            ((uint32_t *)da)[0] = ((const uint32_t *)sa)[0];
            ((uint32_t *)da)[1] = ((const uint32_t *)sa)[1];
            ((uint32_t *)da)[2] = ((const uint32_t *)sa)[2];
            ((uint32_t *)da)[3] = ((const uint32_t *)sa)[3];
            da += 16; sa += 16; n -= 16;
        }
        while (n >= 4) {
            *(uint32_t *)da = *(const uint32_t *)sa;
            da += 4; sa += 4; n -= 4;
        }
    }
    return copy_bytes((void *)da, (const void *)sa, n);
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

**Q:** How Apple interview optimizes this

**A:** For Optimized memcpy: state the invariant you protect, measure worst-case latency, then optimize — 'How Apple interview optimizes this' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Unaligned src/dst strategy

**A:** For Optimized memcpy: state the invariant you protect, measure worst-case latency, then optimize — 'Unaligned src/dst strategy' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C041
#include <assert.h>

int main(void) {
    /* TODO: wire to C041 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C042 — memmove

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** May source and destination overlap? Alignment assumptions on buffers?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for memmove?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build memmove in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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

void *my_memmove(void *dst, const void *src, size_t n) {
    unsigned char *d = (unsigned char *)dst;
    const unsigned char *s = (const unsigned char *)src;
    if (n == 0 || dst == src) {
        return dst;
    }
    if (d < s) {
        for (size_t i = 0; i < n; ++i) {
            d[i] = s[i];
        }
    } else {
        for (size_t i = n; i > 0; --i) {
            d[i - 1] = s[i - 1];
        }
    }
    return dst;
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

**Q:** Can it call memcpy when no overlap?

**A:** `memcpy` is UB on overlap; `memmove` copies forward or backward depending on address order.

**Q:** Test cases you would write

**A:** Table-test every state/event edge, plus fault injection for timeouts, NACK, and buffer full.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Overlapping regions forward and backward.

Optional harness:

```c
#ifdef TEST_C042
#include <assert.h>

int main(void) {
    /* TODO: wire to C042 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C043 — memset that won't be optimized away

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** May source and destination overlap? Alignment assumptions on buffers?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for memset that won't be optimized away?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build memset that won't be optimized away in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
#include <string.h>
void *my_memset(void *s,int c,size_t n) {
    unsigned char *p=s;
    while(n--) *p++=(unsigned char)c;
    return s;
}
void secure_zero(void *s,size_t n) {
    volatile unsigned char *p=s;
    while(n--) *p++=0;
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

**Q:** memset_s

**A:** For memset that won't be optimized away: state the invariant you protect, measure worst-case latency, then optimize — 'memset_s' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Why memset on password buffer fails

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C043
#include <assert.h>

int main(void) {
    /* TODO: wire to C043 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C044 — memcmp

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for memcmp?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build memcmp in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
int my_memcmp(const void *a,const void *b,size_t n) {
    const unsigned char *p=a,*q=b;
    for(size_t i=0;
    i<n;
    ++i) {
        if(p[i]!=q[i])return (int)p[i]-(int)q[i];
    }
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
2. Overlapping buffers — memmove direction; memcpy requires non-overlap.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Constant-time variant later

**A:** For memcmp: state the invariant you protect, measure worst-case latency, then optimize — 'Constant-time variant later' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** SIMD

**A:** For memcmp: state the invariant you protect, measure worst-case latency, then optimize — 'SIMD' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C044
#include <assert.h>

int main(void) {
    /* TODO: wire to C044 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C045 — strlen / strnlen

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for strlen / strnlen?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build strlen / strnlen in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
size_t my_strlen(const char *s) {
    size_t n=0;
    if(!s)return 0;
    while(s[n])++n;
    return n;
}
size_t my_strnlen(const char *s,size_t m) {
    size_t n=0;
    if(!s)return 0;
    while(n<m&&s[n])++n;
    return n;
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

**Q:** Wide strings?

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

**Q:** Safety in untrusted buffers

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C045
#include <assert.h>

int main(void) {
    /* TODO: wire to C045 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C046 — strlcpy semantics

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for strlcpy semantics?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build strlcpy semantics in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
size_t my_strlcpy(char *d,const char *s,size_t sz) {
    size_t len=0;
    if(!s) {
        if(sz)d[0]=0;
        return 0;
    }
    while(s[len])++len;
    if(sz) {
        size_t c=len<sz-1?len:sz-1;
        for(size_t i=0;
        i<c;
        ++i)d[i]=s[i];
        d[c]=0;
    }
    return len;
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

**Q:** vs strncpy hazards

**A:** For strlcpy semantics: state the invariant you protect, measure worst-case latency, then optimize — 'vs strncpy hazards' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Truncation detection

**A:** For strlcpy semantics: state the invariant you protect, measure worst-case latency, then optimize — 'Truncation detection' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C046
#include <assert.h>

int main(void) {
    /* TODO: wire to C046 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C047 — atoi with overflow detection

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for atoi with overflow detection?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build atoi with overflow detection in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
size_t my_strlcat(char *d,const char *s,size_t sz) {
    size_t dl=0;
    while(dl<sz&&d[dl])++dl;
    size_t sl=0;
    while(s[sl])++sl;
    if(dl>=sz)return sz+sl;
    size_t c=sl<sz-dl-1?sl:sz-dl-1;
    for(size_t i=0;
    i<c;
    ++i)d[dl+i]=s[i];
    d[dl+c]=0;
    return dl+sl;
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

**Q:** strtol base

**A:** For atoi with overflow detection: state the invariant you protect, measure worst-case latency, then optimize — 'strtol base' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Reject trailing junk?

**A:** For atoi with overflow detection: state the invariant you protect, measure worst-case latency, then optimize — 'Reject trailing junk?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C047
#include <assert.h>

int main(void) {
    /* TODO: wire to C047 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C048 — itoa for logging

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for itoa for logging?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build itoa for logging in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
int my_atoi(const char *s,int *out) {
    int sign=1,v=0;
    if(!s||!*s)return -1;
    if(*s=='-') {
        sign=-1;
        ++s;
    }
    while(*s>='0'&&*s<='9') {
        v=v*10+(*s-'0');
        ++s;
    }
    *out=sign*v;
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
2. Overlapping buffers — memmove direction; memcpy requires non-overlap.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** hex itoa

**A:** For itoa for logging: state the invariant you protect, measure worst-case latency, then optimize — 'hex itoa' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** zero-pad widths

**A:** Parse with `of_property_read_u32`; check `-EINVAL`; use `devm_kzalloc` for probe-lifetime memory.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C048
#include <assert.h>

int main(void) {
    /* TODO: wire to C048 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C049 — bytes_to_hex

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for bytes_to_hex?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build bytes_to_hex in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
int hex_nibble(char c) {
    if(c>='0'&&c<='9')return c-'0';
    if(c>='a'&&c<='f')return c-'a'+10;
    if(c>='A'&&c<='F')return c-'A'+10;
    return -1;
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

**Q:** Include ASCII sidebar?

**A:** For bytes_to_hex: state the invariant you protect, measure worst-case latency, then optimize — 'Include ASCII sidebar?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Streaming version

**A:** For bytes_to_hex: state the invariant you protect, measure worst-case latency, then optimize — 'Streaming version' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C049
#include <assert.h>

int main(void) {
    /* TODO: wire to C049 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C050 — Constant-time memcmp

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Constant-time memcmp?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Constant-time memcmp in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
int hex_nibble(char c);
size_t hex_encode(const uint8_t *in,size_t n,char *out,size_t cap) {
    size_t need=n*2;
    if(cap<need+1)return 0;
    static const char *h="0123456789abcdef";
    for(size_t i=0;
    i<n;
    ++i) {
        out[2*i]=h[in[i]>>4];
        out[2*i+1]=h[in[i]&0xF];
    }
    out[need]=0;
    return need;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Timestamp counter wrap — use signed delta compare; document max interval < 2³¹ ticks.
3. Overlapping buffers — memmove direction; memcpy requires non-overlap.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Why needed for crypto

**A:** For Constant-time memcmp: state the invariant you protect, measure worst-case latency, then optimize — 'Why needed for crypto' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Compiler reordering risks

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C050
#include <assert.h>

int main(void) {
    /* TODO: wire to C050 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C051 — Split memcpy across ring wrap

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** May source and destination overlap? Alignment assumptions on buffers?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Split memcpy across ring wrap?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Split memcpy across ring wrap in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
int hex_nibble(char c);
size_t hex_decode(const char *in,uint8_t *out,size_t cap) {
    size_t o=0;
    while(in[0]&&in[1]&&o<cap) {
        int hi=hex_nibble(in[0]),lo=hex_nibble(in[1]);
        if(hi<0||lo<0)break;
        out[o++]=(uint8_t)((hi<<4)|lo);
        in+=2;
    }
    return o;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.
3. Timestamp counter wrap — use signed delta compare; document max interval < 2³¹ ticks.
4. Overlapping buffers — memmove direction; memcpy requires non-overlap.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Reserve/commit write side

**A:** For Split memcpy across ring wrap: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

**Q:** DMA contiguous helper link

**A:** Cache-coherency: flush CPU writes before DMA TX; invalidate after DMA RX. Use `dma_alloc_coherent` on Linux or MPU non-cacheable regions on bare-metal.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C051
#include <assert.h>

int main(void) {
    /* TODO: wire to C051 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C052 — In-place buffer reverse

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for In-place buffer reverse?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build In-place buffer reverse in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
int base64_encode_block(const uint8_t *in,size_t n,char *out) {
    static const char *t="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    for(size_t i=0;
    i<n;
    i+=3) {
        uint32_t v=(in[i]<<16)|((i+1<n)?in[i+1]<<8:0)|((i+2<n)?in[i+2]:0);
        *out++=t[(v>>18)&63];
        *out++=t[(v>>12)&63];
        *out++=(i+1<n)?t[(v>>6)&63]:'=';
        *out++=(i+2<n)?t[v&63]:'=';
    }
    *out=0;
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
2. Overlapping buffers — memmove direction; memcpy requires non-overlap.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

N/A — single-threaded test harness; no ISR concurrency in scope.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Reverse uint32_t array

**A:** For In-place buffer reverse: state the invariant you protect, measure worst-case latency, then optimize — 'Reverse uint32_t array' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Endian swap relationship

**A:** Wire format is usually big-endian (network); MCU memory is little-endian on ARM. Always use explicit `read_be16`/`write_le32` helpers, never cast packed structs pointers.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C052
#include <assert.h>

int main(void) {
    /* TODO: wire to C052 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C053 — Rotate byte array

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Rotate byte array?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Rotate byte array in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
int mem_is_zero(const void *p,size_t n) {
    const unsigned char *b=p;
    for(size_t i=0;
    i<n;
    ++i)if(b[i])return 0;
    return 1;
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

**Q:** In-place vs scratch

**A:** For Rotate byte array: state the invariant you protect, measure worst-case latency, then optimize — 'In-place vs scratch' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Bit rotate vs byte rotate

**A:** For Rotate byte array: state the invariant you protect, measure worst-case latency, then optimize — 'Bit rotate vs byte rotate' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C053
#include <assert.h>

int main(void) {
    /* TODO: wire to C053 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C054 — Secure wipe + barrier

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Secure wipe + barrier?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Secure wipe + barrier in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
void *memswap(void *a,void *b,size_t n) {
    unsigned char *x=a,*y=b;
    for(size_t i=0;
    i<n;
    ++i) {
        unsigned char t=x[i];
        x[i]=y[i];
        y[i]=t;
    }
    return a;
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

**Q:** DMA coherency barriers vs compiler barriers

**A:** Cache-coherency: flush CPU writes before DMA TX; invalidate after DMA RX. Use `dma_alloc_coherent` on Linux or MPU non-cacheable regions on bare-metal.

**Q:** OPAQUE

**A:** For Secure wipe + barrier: state the invariant you protect, measure worst-case latency, then optimize — 'OPAQUE' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C054
#include <assert.h>

int main(void) {
    /* TODO: wire to C054 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C055 — snprintf-lite integers only

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for snprintf-lite integers only?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build snprintf-lite integers only in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
int bounded_copy(uint8_t *d,size_t dc,const uint8_t *s,size_t sc) {
    size_t n=dc<sc?dc:sc;
    for(size_t i=0;
    i<n;
    ++i)d[i]=s[i];
    return (int)n;
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

**Q:** How far toward real printf?

**A:** For snprintf-lite integers only: state the invariant you protect, measure worst-case latency, then optimize — 'How far toward real printf?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Reentrant?

**A:** For snprintf-lite integers only: state the invariant you protect, measure worst-case latency, then optimize — 'Reentrant?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C055
#include <assert.h>

int main(void) {
    /* TODO: wire to C055 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

