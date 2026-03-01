# Universal Embedded Systems Interview Master List (All Companies)
A consolidated from-scratch coding + design problem set covering expectations across: Google • Apple • Meta • Microsoft • Amazon Lab126 • Qualcomm • Nvidia • Broadcom • Intel • NXP • TI • ARM


## 1. C Language & Low-Level Fundamentals (12)
- Implement custom memset/memcpy/memmove (overlap-safe)
- Implement safe atoi with overflow detection
- Bitfield packing/unpacking for sensor frame
- Endianness conversion helpers (16/32/64)
- Detect power-of-2 and next power-of-2
- Count set bits (Kernighan / LUT)
- Reverse bits in 32/64-bit integer
- Swap odd/even bits
- Fast divide-by-10 without ‘/’
- CRC-8 implementation
- CRC-16 implementation
- container_of() macro usage


## 2. Memory Management (12)
- Fixed-size memory pool allocator
- Pool with guard-byte corruption detection
- Variable-size free-list allocator
- Free-list block split
- Free-list coalescing
- Buddy allocator (alloc/free)
- Slab allocator for fixed objects
- Bitmap allocator
- Region/Bump allocator
- Cache-aligned allocator (DMA-safe)
- Zero-copy message buffer
- ISR-safe object allocator


## 3. Queues / Buffers / IPC (10)
- SPSC circular buffer
- Ring full/empty via one-slot-open
- Ring full/empty via count
- Power-of-2 indexing optimization
- ISR-producer/task-consumer queue
- Lock-free SPSC queue
- DMA-friendly contiguous-read API
- Multi-producer logging ring (bounded drop)
- Priority event queue
- Mailbox IPC (dual-core)


## 4. Concurrency & Atomics (12)
- Spinlock using atomic_flag
- Ticket lock
- Minimal mutex
- Counting semaphore
- Binary semaphore (ISR give)
- Reader-writer lock
- Producer-consumer bounded buffer
- Atomic overflow-safe counter
- ABA issue demo
- Tagged-pointer lock-free stack
- Acquire/Release ordering correctness
- Lock-free ISR↔task flag handoff


## 5. Interrupts & ISR Design (8)
- Top-half / bottom-half deferral
- IRQ-safe reference counter
- Nested interrupt-safe critical section
- Race-safe interrupt status clear
- Deferred interrupt work queue
- Latency-bounded ISR logging
- Interrupt controller abstraction
- ISR-safe tracing buffer


## 6. MMIO & Driver Safety (8)
- Register map HAL
- Safe register RMW API
- Atomic register access (ISR+task)
- Safe MMIO polling with timeout
- Volatile vs atomic register flag demo
- Write-combining MMIO hazard
- Control register update + ISB
- Shared peripheral access with DMB


## 7. DMA & Cache Coherency (8)
- DMA descriptor ownership handoff
- Ping–pong DMA manager
- Circular DMA RX buffer logic
- CPU↔DMA shared buffer visibility bug
- Cache clean/invalidate API
- Non-coherent DMA buffer API
- DMA timeout wrapper
- DMA error recovery state machine


## 8. Timers & Scheduling (10)
- Software timer queue (sorted list)
- Race-safe timer cancellation
- Periodic timer without drift
- Timer wheel DS
- Min-heap timer queue
- Driver timeout wrapper
- Rate Monotonic Scheduler
- Earliest Deadline First
- Deadline miss detection
- Wraparound-safe tick compare


## 9. Peripheral Drivers (12)
- UART polling driver
- UART interrupt RX
- UART interrupt TX
- UART DMA TX
- SPI blocking transfer
- SPI interrupt transfer
- SPI DMA full-duplex
- I2C master write
- I2C master read (repeated start)
- GPIO driver (dir/read/write)
- ADC single-shot
- PWM driver


## 10. System Reliability (8)
- Retry with exponential backoff
- Driver reset/reinit flow
- Fault-tolerant state machine
- Watchdog init/kick policy
- Bootloader A/B update flow
- Crash-dump ring buffer
- Logging with backpressure
- Deterministic driver init ordering


## 11. Performance & Cache Awareness (6)
- False sharing detection
- Cache-line struct layout
- AoS→SoA conversion
- Blocked matrix multiply
- Lock contention counter
- Queue watermark telemetry


## 12. IPC / Multi-Core (4)
- Shared-memory ring with barriers
- Sequence-lock shared stats
- Multi-core stale-read demo
- SMP producer-consumer fix


## 13. Power & Lifecycle (4)
- Driver suspend/resume
- Power-state safe reinit
- Peripheral clock gating API
- Low-power wake interrupt flow


## 14. Protocol / Framing (4)
- Framed packet parser (len+CRC)
- Stream resynchronization logic
- CAN-style ID filtering bitmap
- UART SLIP/COBS framing


## 15. Testability & Host Simulation (4)
- Fake-register HAL backend
- Driver fault injection hooks
- DMA mock backend
- Timer virtualization layer

Use: Implement with ISR-safety, SMP awareness, DMA coherency, and correct memory barriers where applicable.
