# Google L4 Embedded Firmware — Top 50 Mandatory Problem Set (Interview Prompts)
Use these as from-scratch coding + design problems. Each should be implemented in C/C++ with ISR-safety, SMP-awareness, and no dynamic allocation unless explicitly allowed.


## A. Memory Ownership & Allocation (6)
- Implement a fixed-size memory pool allocator with O(1) alloc/free and alignment support.
- Extend the pool with guard bytes to detect buffer overrun on free().
- Implement a variable-size free-list allocator using first-fit policy.
- Add block coalescing (prev/next/both) to the free-list allocator.
- Implement a cache-line aligned allocator (e.g., 64B) suitable for DMA descriptors.
- Design an ISR-safe object allocator with a fallback emergency pool.


## B. Queue / Ring Buffer / IPC (6)
- Implement an array-based SPSC circular buffer.
- Optimize ring indexing using power-of-2 masking.
- Design an ISR-producer / task-consumer queue API.
- Provide a DMA-friendly contiguous-read API for the ring buffer.
- Implement a lock-free SPSC queue using atomics.
- Design a multi-producer logging ring with bounded drop policy (no global lock).


## C. Synchronization & Atomics (6)
- Implement a spinlock using atomic_flag.
- Implement a minimal mutex using atomics.
- Implement a counting semaphore.
- Implement a reader-writer lock.
- Implement a bounded producer-consumer buffer.
- Implement an overflow-safe atomic shared counter.


## D. Lock-Free Pitfalls (4)
- Demonstrate the ABA problem on a lock-free stack.
- Implement a tagged-pointer based lock-free stack.
- Implement an ISR↔task flag handoff using atomics (no locks).
- Demonstrate and fix a stale-read bug in a multi-core ring buffer.


## E. Memory Ordering / ARM Barriers (7)
- Implement a producer-consumer queue using acquire/release semantics.
- Show failure of volatile vs correctness with atomics for a shared flag.
- Demonstrate SMP visibility bug without barriers.
- Place correct DMB for shared peripheral access.
- Use DSB in interrupt completion path correctly.
- Use ISB after control register write (e.g., enabling IRQ/MMU feature).
- Implement a safe MMIO polling loop with memory barriers.


## F. MMIO & Driver Safety (5)
- Design a register map abstraction layer (HAL).
- Implement safe register read-modify-write API.
- Implement atomic register access shared between ISR and task.
- Fix interrupt status clear race (read-after-write ordering).
- Implement overlap-safe memmove and optimized memcpy.


## G. DMA + Cache Coherency (5)
- Design DMA descriptor ownership handoff (CPU↔DMA).
- Implement cache clean/invalidate helpers for non-coherent DMA.
- Demonstrate CPU↔DMA shared buffer visibility bug and fix.
- Implement ping–pong DMA buffer manager.
- Design a non-coherent DMA buffer handoff API (CPU prepare → DMA consume → CPU reclaim).


## H. Timers & Scheduling (6)
- Implement a software timer queue using sorted list.
- Implement race-safe timer cancellation (ISR + task callable).
- Implement periodic timer rescheduling without drift.
- Design a driver timeout wrapper using software timers.
- Implement a timer wheel data structure.
- Implement a min-heap based timer queue.


## I. Performance Debuggability (3)
- Implement a runtime lock contention counter.
- Implement ISR execution time histogram logger.
- Implement queue depth watermark + drop telemetry.


## J. Determinism / Time Safety (2)
- Implement wraparound-safe monotonic tick compare (time_after style).
- Design driver initialization ordering with dependency-safe bring-up.

Expectation in Interview: Be able to explain ISR-safety, SMP behavior, cache/DMA interaction, and where DMB/DSB/ISB are required.
