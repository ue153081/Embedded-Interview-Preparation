# Google Embedded Firmware — Full Master List (Q001–Q163)
This is the Google-optimized depth list covering Coding, Concurrency, DMA, MMIO, Timers, ARM Memory Model, ISR-safe APIs, Determinism, and Performance Debuggability expected for L4 Embedded FW (Pixel / Nest / Platforms).


## Topic 1 — Memory Management (18)
- Q001: Fixed-size memory pool allocator
- Q002: Pool with guard-byte corruption check
- Q003: Pool with leak counter + stats API
- Q004: Variable-size free-list allocator (first-fit)
- Q005: Free-list block split logic
- Q006: Free-list coalescing (prev/next/both)
- Q007: Buddy allocator (allocate by order)
- Q008: Buddy allocator (free + recursive merge)
- Q009: Slab allocator for fixed objects
- Q010: Slab cache with ctor/dtor hooks
- Q011: Bitmap allocator for IDs/blocks
- Q012: Bump/region allocator with reset
- Q013: Cache-aligned allocator (64B)
- Q014: Zero-copy message buffer
- Q015: Circular DMA buffer read index logic
- Q016: Double-buffer DMA manager
- Q017: ISR-safe object allocation pool
- Q018: Canary/poison corruption detector


## Topic 2 — Bit Manipulation (16)
- Q019: Reverse bits (32-bit)
- Q020: Reverse bits (64-bit)
- Q021: Count set bits (Kernighan)
- Q022: Count set bits (LUT)
- Q023: Detect power-of-2
- Q024: Next power-of-2
- Q025: Parity bit
- Q026: Swap odd/even bits
- Q027: Sensor frame bitfield pack
- Q028: Bitfield unpack + validate
- Q029: Missing number (XOR)
- Q030: Single non-duplicate (XOR)
- Q031: CRC-8
- Q032: CRC-16
- Q033: Fast divide-by-10
- Q034: Endianness helpers (16/32/64)


## Topic 3 — Circular Buffer & Queue (12)
- Q035: SPSC circular buffer
- Q036: One-slot-open full/empty
- Q037: Count-based full/empty
- Q038: Overwrite-oldest policy
- Q039: Discard-newest policy
- Q040: Power-of-2 indexing
- Q041: ISR-producer/task-consumer queue
- Q042: DMA-friendly contiguous read API
- Q043: MPSC queue (lock-protected)
- Q044: Lock-free SPSC linked queue
- Q045: Deferred interrupt work queue
- Q046: Priority event queue


## Topic 4 — Concurrency & Multithreading (14)
- Q047: Spinlock (atomic_flag)
- Q048: Ticket lock
- Q049: Minimal mutex (atomics)
- Q050: Counting semaphore
- Q051: Binary semaphore (ISR give)
- Q052: Reader-writer lock
- Q053: Overflow-safe atomic counter
- Q054: Producer-consumer bounded buffer
- Q055: Deadlock detection (wait-for)
- Q056: Priority inversion mitigation
- Q057: Starvation-free RW policy
- Q058: ABA demo (lock-free stack)
- Q059: Tagged-pointer lock-free stack
- Q060: Acquire/release correctness


## Topic 5 — Cache-Efficient Programming (8)
- Q061: False-sharing detect + padding
- Q062: Cache-line-aware struct layout
- Q063: AoS→SoA conversion
- Q064: Blocked matrix multiply
- Q065: Prefetch-friendly traversal
- Q066: Hot/cold data split
- Q067: Cache-aligned ring indices
- Q068: L1/L2 block-size tuning


## Topic 6 — Embedded Data Structures (12)
- Q069: Hash table (open addressing)
- Q070: Hash (chaining + static pool)
- Q071: Fixed-capacity map
- Q072: Binary heap PQ
- Q073: Indexed PQ
- Q074: LRU cache (hash + DLL)
- Q075: Timer wheel
- Q076: Min-heap timer queue
- Q077: Bitmap free-slot allocator
- Q078: Intrusive linked list
- Q079: container_of() usage
- Q080: Run queue (priority + FIFO)


## Topic 7 — Driver-Style Coding (18)
- Q081: UART polling
- Q082: UART IRQ RX
- Q083: UART IRQ TX
- Q084: UART DMA TX
- Q085: UART DMA circular RX
- Q086: SPI blocking
- Q087: SPI IRQ state machine
- Q088: SPI DMA full-duplex
- Q089: I2C master write
- Q090: I2C master read (repeated start)
- Q091: I2C bus recovery
- Q092: GPIO driver
- Q093: GPIO IRQ debounce
- Q094: ADC single-shot (timeout)
- Q095: ADC continuous (callback)
- Q096: PWM driver
- Q097: Watchdog (init/kick)
- Q098: RTC (set/get/alarm)


## Topic 8 — Real-Time & Reliability (10)
- Q099: Software timer queue (sorted list)
- Q100: Periodic timer w/o drift
- Q101: Race-safe timer cancel
- Q102: Rate Monotonic Scheduler
- Q103: Earliest Deadline First
- Q104: Deadline miss accounting
- Q105: Driver timeout wrapper
- Q106: Exponential backoff retry
- Q107: Driver reset/reinit
- Q108: Fault-tolerant state machine


## Topic 9 — System, MMIO, IPC (14)
- Q109: Register map HAL
- Q110: Safe register RMW
- Q111: Atomic register access (ISR+task)
- Q112: Interrupt controller abstraction
- Q113: Mailbox IPC (dual-core)
- Q114: Shared-memory IPC ring + barriers
- Q115: Logging subsystem (ring + backpressure)
- Q116: Crash-dump persistent buffer
- Q117: Event-driven FSM engine
- Q118: Telemetry pipeline
- Q119: Bootloader A/B flow
- Q120: Safe atoi
- Q121: memmove + optimized memcpy
- Q122: Framed packet parser (len+CRC)


## Topic 10 — Advanced Safety (12)
- Q123: MMIO polling helper (timeout)
- Q124: DMA descriptor ownership FSM
- Q125: Cache maintenance (clean/invalidate)
- Q126: ISR latency budget enforcement
- Q127: ISR-safe tracing buffer
- Q128: Sequence-lock shared stats
- Q129: Wraparound-safe tick compare
- Q130: Compile-time config validation
- Q131: Driver fault injection hooks
- Q132: Memory watermark tracker
- Q133: Power-state safe suspend/resume
- Q134: Fake-register HAL (host test)


## Topic 11 — HW Concurrency & ARM Ordering (26)
- Q135: Store buffering litmus (SMP)
- Q136: Dekker failure w/o barriers
- Q137: Relaxed ordering queue bug
- Q138: ISR↔task flag handoff
- Q139: Multi-core stale-read ring
- Q140: Volatile vs atomic (driver flag)
- Q141: Write-combining MMIO hazard
- Q142: SMP cache vs DMA visibility
- Q143: Correct DMB placement
- Q144: DSB in IRQ completion
- Q145: ISB after control write
- Q146: Safe MMIO polling (barriers)
- Q147: Status clear ordering race
- Q148: IRQ-safe reference counter
- Q149: IRQ-safe allocator (fallback)
- Q150: Top/bottom-half API
- Q151: Nested IRQ-safe CS
- Q152: Shared stats (ISR+task)
- Q153: Latency-bounded deferral
- Q154: CPU↔DMA ownership bug
- Q155: Cache omission failure
- Q156: Ping–pong DMA race
- Q157: Lock contention counter
- Q158: ISR time histogram
- Q159: Queue watermark telemetry
- Q160: Priority inversion trace


## Topic 12 — Determinism & SMP Logging (3)
- Q161: Wrap-safe timeout scheduler
- Q162: MPMC logging ring (bounded drop)
- Q163: Dependency-safe driver init

Target: Be able to code, reason about SMP/ISR/DMA visibility, and justify DMB/DSB/ISB placement where applicable.
