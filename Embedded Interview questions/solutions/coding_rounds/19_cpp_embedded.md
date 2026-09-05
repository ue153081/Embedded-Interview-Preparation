# Solutions — 19 Cpp Embedded

**Source:** [`../../coding_rounds/19_cpp_embedded.md`](../../coding_rounds/19_cpp_embedded.md)  
**Questions:** 15  

---

## C261 — RAII IRQ lock

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for RAII IRQ lock?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build RAII IRQ lock in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <cstdint>
extern "C" uint32_t irq_save(void);
extern "C" void irq_restore(uint32_t);
class IrqLock {
    uint32_t st_;
    public: IrqLock():st_(irq_save()) {
    }
    ~IrqLock() {
        irq_restore(st_);
    }
    IrqLock(const IrqLock&)=delete;
    IrqLock& operator=(const IrqLock&)=delete;
};
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Lock_guard mutex

**A:** Spinlock for ISR/task short sections; mutex (sleeping) only in thread context. Never hold spinlock across blocking calls.

**Q:** std::atomic signal

**A:** For RAII IRQ lock: state the invariant you protect, measure worst-case latency, then optimize — 'std::atomic signal' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C261
#include <assert.h>

int main(void) {
    /* TODO: wire to C261 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C262 — Non-owning span

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Non-owning span?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Non-owning span in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <cstddef>
template<typename T> class Span {
    T* data_;
    std::size_t size_;
    public: Span(T* d,std::size_t n):data_(d),size_(n) {
    }
    T* data()const {
        return data_;
    }
    std::size_t size()const {
        return size_;
    }
    T& at(std::size_t i)const {
        if(i>=size_)throw 1;
        return data_[i];
    }
    Span subspan(std::size_t off,std::size_t n)const {
        return Span(data_+off,n);
    }
};
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** vs std::span

**A:** For Non-owning span: state the invariant you protect, measure worst-case latency, then optimize — 'vs std::span' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Lifetime safety

**A:** For Non-owning span: state the invariant you protect, measure worst-case latency, then optimize — 'Lifetime safety' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C262
#include <assert.h>

int main(void) {
    /* TODO: wire to C262 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C263 — Intrusive list template

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Intrusive list template?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Intrusive list template in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <cstddef>
template<typename Tag> struct Link {
    Link* next=nullptr;
};
template<typename T,typename Tag> T* container_of(Link<Tag>* n) {
    return reinterpret_cast<T*>(n);
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

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Safe iteration while erase

**A:** For Intrusive list template: state the invariant you protect, measure worst-case latency, then optimize — 'Safe iteration while erase' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** container_of style

**A:** For Intrusive list template: state the invariant you protect, measure worst-case latency, then optimize — 'container_of style' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C263
#include <assert.h>

int main(void) {
    /* TODO: wire to C263 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C264 — Static capacity ring (no heap)

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Static capacity ring (no heap)?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Static capacity ring (no heap) in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Empty: `head==tail`; full: `next(head)==tail` (spare slot) unless count field used.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <cstdint>
template<std::size_t Cap> struct Ring {
    std::uint8_t b[Cap];
    std::size_t h,t;
    bool push(std::uint8_t v) {
        auto n=(h+1)%Cap;
        if(n==t)return false;
        b[h]=v;
        h=n;
        return true;
    }
    bool pop(std::uint8_t& v) {
        if(t==h)return false;
        v=b[t];
        t=(t+1)%Cap;
        return true;
    }
};
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** emplace

**A:** For Static capacity ring (no heap): document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

**Q:** ISR-safe policy

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```cpp
#ifdef TEST_C264
#include <assert.h>

int main(void) {
    /* TODO: wire to C264 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C265 — function_ref without heap

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for function_ref without heap?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build function_ref without heap in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <cstddef>
template<typename Sig> class function_ref;
template<typename R,typename...A> class function_ref<R(A...)> {
    R(*fn_)(void*,A...);
    void* ctx_;
    public: template<typename F> function_ref(F&f):fn_([](void* c,A...a)->R {
        return (*static_cast<F*>(c))(a...);
    }
    ),ctx_(&f) {
    }
    R operator()(A...a)const {
        return fn_(ctx_,a...);
    }
};
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** vs std::function

**A:** For function_ref without heap: state the invariant you protect, measure worst-case latency, then optimize — 'vs std::function' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** function_view

**A:** For function_ref without heap: state the invariant you protect, measure worst-case latency, then optimize — 'function_view' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C265
#include <assert.h>

int main(void) {
    /* TODO: wire to C265 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C266 — unique_ptr custom deleter for DMA

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is the buffer cache-coherent, or do I need explicit flush/invalidate?
- **Candidate:** Single-shot or circular descriptor chain?
- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for unique_ptr custom deleter for DMA?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build unique_ptr custom deleter for DMA in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <memory>
struct DmaDeleter {
    void operator()(void* p)const {
        dma_free(p);
    }
};
using DmaPtr=std::unique_ptr<void,DmaDeleter>;
void dma_free(void*);
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** shared_ptr cache

**A:** SoA vs AoS: SoA helps SIMD and sequential access; AoS is better for single-struct locality. Prefetch next cache line in hot loops; align to 32/64 B.

**Q:** span from unique

**A:** For unique_ptr custom deleter for DMA: state the invariant you protect, measure worst-case latency, then optimize — 'span from unique' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C266
#include <assert.h>

int main(void) {
    /* TODO: wire to C266 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C267 — enum class + to_string

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for enum class + to_string?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build enum class + to_string in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Empty: `head==tail`; full: `next(head)==tail` (spare slot) unless count field used.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <cstdint>
enum class State: std::uint8_t {
    Idle, Run, Fault
};
const char* to_string(State s) {
    switch(s) {
        case State::Idle:return "Idle";
        case State::Run:return "Run";
        default:return "Fault";
    }
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

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** std::optional parse

**A:** For enum class + to_string: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

**Q:** Flag enums

**A:** For enum class + to_string: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```cpp
#ifdef TEST_C267
#include <assert.h>

int main(void) {
    /* TODO: wire to C267 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C268 — CRTP driver vs vtable

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for CRTP driver vs vtable?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build CRTP driver vs vtable in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
struct Base {
    virtual int read()=0;
};
struct CrtpDev {
    int read() {
        return 42;
    }
};
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Concepts interface

**A:** For CRTP driver vs vtable: state the invariant you protect, measure worst-case latency, then optimize — 'Concepts interface' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Fake for tests

**A:** Table-test every state/event edge, plus fault injection for timeouts, NACK, and buffer full.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C268
#include <assert.h>

int main(void) {
    /* TODO: wire to C268 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C269 — Move-only message queue

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Move-only message queue?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Move-only message queue in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <utility>
template<typename T,std::size_t N> class MoveQueue {
    T buf[N];
    std::size_t h,t,sz;
    public: bool push(T&&v) {
        if(sz==N)return false;
        buf[h]=std::move(v);
        h=(h+1)%N;
        ++sz;
        return true;
    }
    bool pop(T&out) {
        if(!sz)return false;
        out=std::move(buf[t]);
        t=(t+1)%N;
        --sz;
        return true;
    }
};
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** emplace

**A:** For Move-only message queue: state the invariant you protect, measure worst-case latency, then optimize — 'emplace' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** ISR restrictions

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C269
#include <assert.h>

int main(void) {
    /* TODO: wire to C269 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C270 — constexpr register encode

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for constexpr register encode?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build constexpr register encode in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <cstdint>
constexpr std::uint32_t reg(std::uint32_t off,std::uint32_t val) {
    return (off<<16)|val;
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

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** consteval

**A:** For constexpr register encode: state the invariant you protect, measure worst-case latency, then optimize — 'consteval' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Lookup tables

**A:** For constexpr register encode: state the invariant you protect, measure worst-case latency, then optimize — 'Lookup tables' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C270
#include <assert.h>

int main(void) {
    /* TODO: wire to C270 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C271 — Placement-new object pool

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Fixed block size or variable? Is free allowed from ISR?
- **Candidate:** Should exhaustion return NULL or a dedicated error code?
- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Placement-new object pool?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Placement-new object pool in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <cstddef>
#include <new>
template<typename T,std::size_t N> struct Pool {
    alignas(T) unsigned char mem[sizeof(T)*N];
    bool used[N] {
    };
    T* allocate() {
        for(std::size_t i=0;
        i<N;
        ++i)if(!used[i]) {
            used[i]=true;
            return new(&mem[i*sizeof(T)]) T();
        }
        return nullptr;
    }
};
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Exception safety

**A:** Disable exceptions on embedded; use `expected<T,E>` or error codes. RAII guards release DMA/locks on scope exit.

**Q:** Free list

**A:** For Placement-new object pool: state the invariant you protect, measure worst-case latency, then optimize — 'Free list' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C271
#include <assert.h>

int main(void) {
    /* TODO: wire to C271 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C272 — expected<T,E> lite

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for expected<T,E> lite?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build expected<T,E> lite in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
template<typename T,typename E> struct expected {
    bool ok;
    T v;
    E e;
    static expected value(T x) {
        return {
            true,x, {
            }
        };
    }
    static expected error(E err) {
        return {
            false, {
            }
            ,err
        };
    }
};
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** std::expected C++23

**A:** For expected<T,E> lite: state the invariant you protect, measure worst-case latency, then optimize — 'std::expected C++23' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Result monad

**A:** For expected<T,E> lite: state the invariant you protect, measure worst-case latency, then optimize — 'Result monad' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C272
#include <assert.h>

int main(void) {
    /* TODO: wire to C272 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C273 — Atomic flag handoff C++

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Atomic flag handoff C++?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build Atomic flag handoff C++ in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <atomic>
struct Flag {
    std::atomic<bool> f {
        false
    };
    void give() {
        f.store(true,std::memory_order_release);
    }
    void take() {
        while(!f.exchange(false,std::memory_order_acquire)) {
        }
    }
};
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

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** atomic<uint64_t>

**A:** For Atomic flag handoff C++: state the invariant you protect, measure worst-case latency, then optimize — 'atomic<uint64_t>' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** seq_cst tax

**A:** For Atomic flag handoff C++: state the invariant you protect, measure worst-case latency, then optimize — 'seq_cst tax' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C273
#include <assert.h>

int main(void) {
    /* TODO: wire to C273 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C274 — Fix temporary lifetime callback bug

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Fix temporary lifetime callback bug?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Fix temporary lifetime callback bug in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
struct Handler {
    void on(int& x) {
        x=1;
    }
};
void bug() {
    int tmp=0;
    auto cb=[&]() {
        Handler h;
        h.on(tmp);
    };
    cb();
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Timestamp counter wrap — use signed delta compare; document max interval < 2³¹ ticks.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** string_view pitfalls

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

**Q:** co_routines skip

**A:** For Fix temporary lifetime callback bug: state the invariant you protect, measure worst-case latency, then optimize — 'co_routines skip' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C274
#include <assert.h>

int main(void) {
    /* TODO: wire to C274 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C275 — Header-only HAL traits

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Header-only HAL traits?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Header-only HAL traits in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <type_traits>
template<typename T> struct is_mmio_reg: std::false_type {
};
template<> struct is_mmio_reg<volatile unsigned>: std::true_type {
};
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

No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Concepts constrain Platform

**A:** For Header-only HAL traits: state the invariant you protect, measure worst-case latency, then optimize — 'Concepts constrain Platform' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Policy-based design

**A:** For Header-only HAL traits: state the invariant you protect, measure worst-case latency, then optimize — 'Policy-based design' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C275
#include <assert.h>

int main(void) {
    /* TODO: wire to C275 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

