# Embedded / Firmware Coding Rounds — Complete Question Bank

**Scope:** Coding rounds only for Embedded / Firmware / Device Driver roles  
**Excluded:** Pure DSA (arrays/trees/graphs/DP), system design / architecture whiteboards  
**Included:** C/C++ implementation problems interviewers ask you to **write, debug, or complete** under time

**Target coverage:** Google Embedded FW · Apple FW · Amazon Lab126 · NVIDIA · Tesla · Qualcomm · Meta Devices · industrial / auto FW

**How to use**
- Mark `[ ]` → `[~]` → `[x]` only when you can code from blank + handle 2 follow-ups
- Language default: **C11**; mark `(C++)` where C++ is commonly expected
- Tier **S** first (bottom checklist)

---

## Coverage map (what this bank is built to hit)

| Coding theme | Q range |
|--------------|---------|
| C language / UB / types / macros | C001–C020 |
| Bits, endian, wire formats | C021–C040 |
| Memory ops & strings (embedded style) | C041–C055 |
| Allocators & memory mgmt | C056–C070 |
| Rings, queues, buffers | C071–C090 |
| Synchronization & lock-free coding | C091–C110 |
| Interrupts / deferred work (code) | C111–C120 |
| MMIO / register HAL | C121–C135 |
| UART / SPI / I2C / GPIO drivers (code) | C136–C160 |
| DMA coding patterns | C161–C172 |
| Timers / schedulers (code) | C173–C185 |
| Protocol parsers / CRC / framing | C186–C200 |
| FSM / control coding | C201–C212 |
| Filters / signal-lite coding | C213–C218 |
| IPC / dual-core / shared memory (code) | C219–C230 |
| Logging / crash / diagnostics (code) | C231–C240 |
| Power / watchdog / reliability (code) | C241–C250 |
| Testing / fakes / harness (code) | C251–C260 |
| C++ embedded coding | C261–C275 |
| Performance / cache coding | C276–C285 |
| Linux driver coding snippets | C286–C300 |

**Total: 300 coding prompts** (breadth). For a time-boxed path use **Tier S (80)** then **Tier A (120 more)** below.

---

# A. C language, UB, types, macros (C001–C020)

| ID | Implement / fix |
|----|-----------------|
| C001 | `container_of` / `offsetof` macros; use on intrusive list node |
| C002 | Safe `STATIC_ASSERT` / `_Static_assert` for struct size/align |
| C003 | `ARRAY_SIZE`, `MIN/MAX`, `BIT(n)`, `GENMASK` macros without double-eval bugs |
| C004 | Write `likely`/`unlikely` wrappers; show when they matter |
| C005 | Fix UB: signed overflow, shift ≥ width, strict aliasing violation examples |
| C006 | Explain+fix: `volatile` misuses vs atomics (code samples) |
| C007 | Implement `ALIGN_UP`/`ALIGN_DOWN`; handle overflow |
| C008 | Packed vs aligned structs; serialize without relying on packing alone |
| C009 | Flexible array member pattern (header + payload) |
| C010 | `const` correctness for buffer APIs (`const uint8_t*`, `uint8_t* const`) |
| C011 | Function-pointer table dispatch (command handler registry) |
| C012 | `restrict`-correct `memcpy`-style API (document aliasing contract) |
| C013 | Endian-agnostic load/store helpers (`read_le16`, `write_be32`) |
| C014 | Integer promotion pitfalls in bitwise ops on `uint8_t` (fix with tests) |
| C015 | `enum` packing / switch exhaustiveness pattern |
| C016 | Bitfield struct vs shift/mask — implement both; show portability issues |
| C017 | `errno`-style vs return-code API for driver functions |
| C018 | Implement `assert` policy for FW (`BUG_ON`, `WARN_ON` stubs) |
| C019 | Inline vs macro vs `static inline` tradeoffs (write examples) |
| C020 | `typeof`/`_Generic` (or C++ overload) for type-generic `max` |

---

# B. Bits, endian, wire formats (C021–C040)

| ID | Implement / fix |
|----|-----------------|
| C021 | Count set bits (`uint32_t`) — Kernighan + SWAR + LUT |
| C022 | Reverse bits in byte / 32-bit word (+ LUT optimize) |
| C023 | Flip MSB and LSB of a byte |
| C024 | Extract/insert bitfield (`get_bits`/`set_bits` with mask+shift) |
| C025 | Detect power-of-2; round up to next power-of-2 (overflow-safe) |
| C026 | Floor `log2` for `uint32_t` without libm |
| C027 | Parity, swap nibble, swap odd/even bits |
| C028 | Gray code encode/decode |
| C029 | Saturating add/sub for `uint8`/`uint16` |
| C030 | Fixed-point Q15 multiply helper |
| C031 | Unpack LE struct from byte dump (padding-aware) |
| C032 | Pack struct to BE wire format (explicit serialization) |
| C033 | Expand 5-bit channel to 8-bit (`(v<<3)|(v>>2)` style) |
| C034 | RGB565 ↔ RGB888 convert |
| C035 | Checksum: additive, XOR, Fletcher-16 |
| C036 | CRC-8 (poly configurable) |
| C037 | CRC-16-CCITT |
| C038 | CRC-32 (table + optional slice-by-4 mention) |
| C039 | Bitstream reader (read `n` bits MSB-first from byte stream) |
| C040 | Hamming ECC encode/decode for small block (interview classic) |

---

# C. Memory / string ops — embedded style (C041–C055)

| ID | Implement / fix |
|----|-----------------|
| C041 | `memcpy` (aligned word copy + byte tail) |
| C042 | `memmove` (overlap-safe) |
| C043 | `memset` / `memset_s`-style that compiler won’t strip |
| C044 | `memcmp` |
| C045 | `strlen` / `strnlen` |
| C046 | `strcpy`/`strncpy` safe replacement (`strlcpy` semantics) |
| C047 | `atoi`/`strtol` with overflow detection |
| C048 | `itoa` / `utoa` for bare-metal logging |
| C049 | Hex dump formatter (`bytes_to_hex`) |
| C050 | Constant-time `memcmp` (crypto-lite interview) |
| C051 | Ring-friendly `memcpy` split across wrap (two-part copy API) |
| C052 | In-place reverse buffer |
| C053 | Circular right/left rotate of byte array |
| C054 | Secure wipe + compiler barrier |
| C055 | Bounded `snprintf`-lite for integer formatting only |

---

# D. Allocators & memory management (C056–C070)

| ID | Implement / fix |
|----|-----------------|
| C056 | Fixed-size block pool (`alloc`/`free` O(1)) |
| C057 | ISR-safe pool (disable IRQ or lock-free freelist) |
| C058 | Pool with watermark / high-water / leak counters |
| C059 | Pool with guard magic + double-free detect |
| C060 | Bitmap allocator for N slots |
| C061 | Free-list variable allocator (first-fit) |
| C062 | Free-list split |
| C063 | Free-list coalesce |
| C064 | Bump/arena allocator with reset |
| C065 | Aligned alloc (`align_as` power-of-2) on top of pool |
| C066 | DMA-capable allocator (align + non-cacheable note / flag) |
| C067 | Reference-counted buffer object (`get`/`put`) |
| C068 | Slab-like cache for one object type (ctor/dtor hooks) |
| C069 | Buddy allocator (small order range) |
| C070 | Lifetime bug fix: use-after-free in callback queue (write correct ownership) |

---

# E. Rings, queues, buffers (C071–C090)

| ID | Implement / fix |
|----|-----------------|
| C071 | SPSC byte ring — size/push/pop; define full/empty |
| C072 | Power-of-2 ring with mask indexing |
| C073 | Ring using count field vs spare-slot scheme |
| C074 | Overwrite-oldest ring (telemetry) |
| C075 | Discard-newest on full (policy switch) |
| C076 | Peek / skip APIs |
| C077 | Contiguous-read API for DMA (returns pointer+len to linear slice) |
| C078 | Contiguous-write reserve/commit API |
| C079 | Element ring of fixed struct `T` (typed ring) |
| C080 | MPSC queue with IRQ lock or ticket approach |
| C081 | Priority queue (bitmap + FIFOs per priority) |
| C082 | Double buffer (ping-pong) handoff |
| C083 | Triple buffer for tear-free producer/consumer |
| C084 | Message queue: length-prefixed messages in byte ring |
| C085 | Zero-copy slot ring (allocate slot → fill → submit) |
| C086 | Watermark callbacks (high/low) |
| C087 | Lock-free SPSC index protocol with memory_order notes |
| C088 | Blocking queue on RTOS (`put`/`get` with timeout) — code against fake RTOS API |
| C089 | Batch drain (`pop_n`) |
| C090 | Mirror buffer / history buffer for debug |

---

# F. Synchronization & lock-free coding (C091–C110)

| ID | Implement / fix |
|----|-----------------|
| C091 | Spinlock with `atomic_flag` |
| C092 | Ticket lock |
| C093 | IRQ-safe critical section macros (`enter`/`exit` save PRIMASK) |
| C094 | Mutex (task context) against fake scheduler hooks |
| C095 | Binary semaphore (ISR give / task take) |
| C096 | Counting semaphore |
| C097 | Recursion-safe lock detection (debug owner) |
| C098 | RW lock (writer preference or reader preference — pick & code) |
| C099 | Seqlock for counters/stats |
| C100 | Atomic refcount with free-on-zero |
| C101 | Lock-free SPSC queue (indexes + payload) |
| C102 | Lock-free MPSC using CAS list (or document limits if only SPSC allowed) |
| C103 | Treiber stack (and discuss ABA) |
| C104 | ABA-safe stack with tagged pointer / generation counter |
| C105 | Acquire/release flag handoff ISR→task |
| C106 | Sense-reversing barrier (N threads) `(C++)` |
| C107 | Producer–consumer with condition variables `(C++)` |
| C108 | Deadlock demo + fix (lock ordering) — write broken then fixed |
| C109 | Priority inheritance mutex sketch (owner boost hooks) |
| C110 | Wait-free single-word mailbox status protocol |

---

# G. Interrupts / deferred work — coding (C111–C120)

| ID | Implement / fix |
|----|-----------------|
| C111 | ISR that only clears HW + pushes event to queue |
| C112 | Top-half / bottom-half: softirq-like worker drain |
| C113 | Threaded IRQ pattern (wake worker thread) |
| C114 | Nested interrupt-safe refcount |
| C115 | Debounced GPIO ISR (time-based suppress) |
| C116 | Coalesced IRQ counter (count in ISR, process in task) |
| C117 | Spurious IRQ guard / rate limit |
| C118 | Workqueue item: one-shot deferred function |
| C119 | ISR latency histogram buckets (code) |
| C120 | Race: flag vs queue — write correct wakeup pattern |

---

# H. MMIO / register HAL (C121–C135)

| ID | Implement / fix |
|----|-----------------|
| C121 | `reg_read32` / `reg_write32` with `volatile` |
| C122 | `reg_rmw32` (read-modify-write) mask/value |
| C123 | Bit set/clear/toggle helpers |
| C124 | Poll bit with timeout (`wait_for_bit`) |
| C125 | Poll with backoff / deadline using tick API |
| C126 | Register map struct + `static_assert` offsets |
| C127 | Write-posting: readback barrier helper |
| C128 | Shadow register cache for write-only regs |
| C129 | Fake MMIO backend for host unit tests |
| C130 | Atomic RMW when ISR and thread share a reg |
| C131 | Multi-register atomic update (lock or hw latch sequence) |
| C132 | Endian MMIO access for BE peripheral on LE CPU |
| C133 | Field macros: `REG_FIELD_GET`/`PREP` |
| C134 | Soft reset sequence with timeout + retry |
| C135 | Dump all registers to log buffer (debugfs-style) |

---

# I. UART / SPI / I2C / GPIO drivers — coding (C136–C160)

| ID | Implement / fix |
|----|-----------------|
| C136 | UART polling TX/RX |
| C137 | UART IRQ RX into ring |
| C138 | UART IRQ TX from ring (start TX on first byte) |
| C139 | UART TX complete / drain API |
| C140 | UART flow control (RTS/CTS software model) |
| C141 | UART framing error / overrun counters + recovery |
| C142 | SPI full-duplex polling transfer |
| C143 | SPI IRQ state machine (byte/word) |
| C144 | SPI CS framing + multi-device select |
| C145 | I2C start/addr/data/stop state machine |
| C146 | I2C write then repeated-start read |
| C147 | I2C NACK / timeout / arbitration-loss handling |
| C148 | I2C bus recovery (clock toggles + STOP) |
| C149 | GPIO read/write/dir + irq edge config stubs |
| C150 | GPIO debounce state machine (stable N samples) |
| C151 | PWM set period/duty (fixed-point percent) |
| C152 | ADC read with settling + timeout + averaging |
| C153 | Soft-UART bit-bang TX (timer-based) — interview favorite |
| C154 | Button long-press / double-click detector |
| C155 | Rotary encoder quadrature decode (state table) |
| C156 | Shift register 74HC595-style bit-bang |
| C157 | One-wire reset/presence + read byte (timing stubs OK) |
| C158 | Multi-instance driver: `struct device` context (no globals) |
| C159 | Driver init/deinit idempotency |
| C160 | Non-blocking `read`/`write` with `EAGAIN` semantics |

---

# J. DMA coding patterns (C161–C172)

| ID | Implement / fix |
|----|-----------------|
| C161 | DMA descriptor struct + fill for MEM↔PERIPH |
| C162 | Start/stop/abort DMA channel API |
| C163 | Completion ISR → callback / semaphore |
| C164 | Ping-pong DMA buffer swap |
| C165 | Circular DMA RX index math from remaining-count register |
| C166 | Cache clean before DMA TX / invalidate after RX (API stubs) |
| C167 | Ownership FSM: CPU ↔ DMA buffer states |
| C168 | Scatter-gather list walk |
| C169 | DMA timeout watchdog |
| C170 | Half-transfer + full-transfer handling |
| C171 | Align buffer constraints checker |
| C172 | Zero-copy RX: hand DMA buffer to upper layer (refcount) |

---

# K. Timers / schedulers — coding (C173–C185)

| ID | Implement / fix |
|----|-----------------|
| C173 | Software timers on **one** HW timer (sorted list by abs deadline) |
| C174 | `set` / `cancel` / `periodic` with race-safe cancel |
| C175 | Wrap-safe tick compare (`time_after`) |
| C176 | Timer wheel (hierarchical optional) |
| C177 | Min-heap timer queue |
| C178 | Drift-free periodic schedule (`next += period`) |
| C179 | Coop scheduler: round-robin tasks with `yield` |
| C180 | Priority ready-queue scheduler (bitmap) |
| C181 | `regCall`/`callNext` tick dispatcher (Google-style) |
| C182 | Deadline miss counter for periodic task |
| C183 | Time-wheel for hash-distributed timeouts |
| C184 | Debounce using software timer (not busy wait) |
| C185 | One-shot vs auto-reload HW timer abstraction |

---

# L. Protocol parsers / framing (C186–C200)

| ID | Implement / fix |
|----|-----------------|
| C186 | Length + payload + CRC frame parser FSM |
| C187 | Resync on CRC fail / lost framing |
| C188 | COBS encode/decode |
| C189 | SLIP encode/decode |
| C190 | HDLC-like bit stuffing (simplified) |
| C191 | TLV parser with bounds checks |
| C192 | Ring-buffer stream parser (consume incrementally) |
| C193 | Escape-delimited binary protocol |
| C194 | Command dispatcher from parsed opcodes |
| C195 | Fragment reassembly (offset/len/total) |
| C196 | Sequence number + duplicate drop + gap detect |
| C197 | Retransmit queue with timeout ACK |
| C198 | Sliding window (small N) ACK protocol |
| C199 | Byte-stuffed ASCII telemetry parser |
| C200 | Defensive parser fuzz hooks (reject oversize/len mismatch) |

---

# M. FSM / control coding (C201–C212)

| ID | Implement / fix |
|----|-----------------|
| C201 | Traffic light FSM (invalid inputs ignored) |
| C202 | Vending machine FSM + fault state |
| C203 | Connection state machine (disc/connecting/auth/ready/error) |
| C204 | Driver power FSM (off/init/run/suspend/error) |
| C205 | Hierarchical FSM (parent/child modes) |
| C206 | Table-driven FSM (state × event → action/next) |
| C207 | Guard conditions + entry/exit actions |
| C208 | Quadrature direction FSM (Google wheel sampler) |
| C209 | Button UI FSM (idle/down/hold/repeat) |
| C210 | Protocol session FSM with timeouts |
| C211 | Recoverable error FSM (retry N then fault) |
| C212 | Mode manager: exclusive modes with request/release |

---

# N. Filters / numeric lite (C213–C218)

| ID | Implement / fix |
|----|-----------------|
| C213 | Moving average (ring of N) |
| C214 | EWMA / low-pass (`y = αx + (1-α)y`) with first-sample init |
| C215 | Debounce filter for binary signal |
| C216 | Median-of-3 filter |
| C217 | Clamp / rate-limit (slew) helper |
| C218 | PID step function (fixed-point) — common auto FW coding |

---

# O. IPC / dual-core / shared memory — coding (C219–C230)

| ID | Implement / fix |
|----|-----------------|
| C219 | Shared-memory SPSC with head/tail + barriers |
| C220 | Mailbox: write message + generate IPI/IRQ |
| C221 | ACK protocol between cores |
| C222 | Spinlock shared across cores (test-and-set) |
| C223 | Seqlock stats published by RT core, read by app core |
| C224 | RPMsg-lite style channel stubs (send/recv endpoints) |
| C225 | Shared circular log with multi-core producers (lock or drop policy) |
| C226 | Zero-copy buffer handoff across cores (ownership enum) |
| C227 | Versioned shared config struct (seq begin/end) |
| C228 | Heartbeat / life-counter monitor between cores |
| C229 | Command queue + completion queue pair |
| C230 | Cache maintenance points marked in IPC path (comments + API calls) |

---

# P. Logging / crash / diagnostics — coding (C231–C240)

| ID | Implement / fix |
|----|-----------------|
| C231 | ISR-safe log push (string ID + args, not full printf in ISR) |
| C232 | Task-side log formatter drain |
| C233 | Log levels + compile-time strip |
| C234 | Drop counters on full log ring |
| C235 | Crash breadcrumb area in `.noinit` / retained RAM |
| C236 | Stack canary / paint pattern checker |
| C237 | Hex register dump on fault |
| C238 | Ring backtrace capture stubs |
| C239 | Health counters export (JSON-lite or key=value) |
| C240 | Rate-limited assert log |

---

# Q. Power / watchdog / reliability — coding (C241–C250)

| ID | Implement / fix |
|----|-----------------|
| C241 | Watchdog init/kick/windowed kick |
| C242 | Task heartbeat registry + supervisor |
| C243 | Stuck-task detector |
| C244 | Brownout flag latch + safe mode entry |
| C245 | Retry with exponential backoff (+ jitter) |
| C246 | Circuit breaker (open after N faults) |
| C247 | Suspend/resume context save for a peripheral |
| C248 | Idempotent re-init after reset |
| C249 | CRC of critical config + repair/default |
| C250 | Safe state outputs on fault (GPIO flatten) |

---

# R. Testing / fakes / harness — coding (C251–C260)

| ID | Implement / fix |
|----|-----------------|
| C251 | Fake timer that advances virtual time |
| C252 | Fake UART byte injector for parser tests |
| C253 | Fake MMIO register block |
| C254 | Unit tests for ring buffer (wrap/full/empty/overwrite) |
| C255 | Unit tests covering all branches of a validator (Tesla-style) |
| C256 | Fault injection: force NACK / DMA error |
| C257 | Deterministic PRNG for test vectors |
| C258 | Golden-reference CRC tests |
| C259 | Concurrency test: ISR simulation via callbacks |
| C260 | CI `main` that runs all self-tests bare-metal style |

---

# S. C++ embedded coding (C261–C275)

| ID | Implement / fix |
|----|-----------------|
| C261 | RAII IRQ lock / mutex guard `(C++)` |
| C262 | `span`-like non-owning buffer view `(C++)` |
| C263 | Intrusive list in C++ templates `(C++)` |
| C264 | Static-capacity `vector`/`ring` (no heap) `(C++)` |
| C265 | Type-erased callback (`function_ref`) without heap `(C++)` |
| C266 | Unique ownership for DMA buffer (`unique_ptr` custom deleter) `(C++)` |
| C267 | Enum class + exhaustiveness helpers `(C++)` |
| C268 | CRTP driver interface vs vtable — implement both `(C++)` |
| C269 | Move-only queue of messages `(C++)` |
| C270 | Constexpr register encode/decode `(C++)` |
| C271 | Placement-new object pool `(C++)` |
| C272 | Avoid exceptions: `expected<T,E>` lite `(C++)` |
| C273 | Atomic shared flag with `memory_order` `(C++)` |
| C274 | Fix lifetime bug with temporaries/callbacks `(C++)` |
| C275 | Header-only HAL with concepts/traits lite `(C++)` |

---

# T. Performance / cache coding (C276–C285)

| ID | Implement / fix |
|----|-----------------|
| C276 | SoA vs AoS transform for sensor samples |
| C277 | Prefetch-friendly loop for buffer process |
| C278 | False-sharing fix: pad hot atomics to cache line |
| C279 | Branchless clamp/select examples |
| C280 | Unroll + word-wise checksum |
| C281 | Alignment-aware SIMD-ready copy stub (or NEON intrinsics optional) |
| C282 | Hot/cold field split in driver struct |
| C283 | Measure + reduce copies in TX path (API redesign code) |
| C284 | Lookup table vs compute tradeoff (bit reverse) |
| C285 | Cache-line aware ring indices placement |

---

# U. Linux driver coding snippets (C286–C300)

*(Still coding-round style: write functions / small modules — not full system design.)*

| ID | Implement / fix |
|----|-----------------|
| C286 | Platform driver `probe`/`remove` skeleton with `devm_*` |
| C287 | Character device `file_operations` open/read/write/release |
| C288 | `copy_to_user` / `copy_from_user` bounded read path |
| C289 | `ioctl` with versioned struct + `_IOC` macros |
| C290 | `poll`/`wait_queue` for data-ready |
| C291 | sysfs attribute show/store for error counters |
| C292 | Threaded IRQ handler registration |
| C293 | `dma_alloc_coherent` + map error paths |
| C294 | DT parse: read u32 property + gpio optional |
| C295 | Runtime PM `suspend`/`resume` stubs with refcount |
| C296 | `mmap` of kernel buffer (VM ops simplified) |
| C297 | Netlink or simple miscdevice event notify (pick one) |
| C298 | Debugfs file for register dump |
| C299 | Module param + spinlock-protected global state |
| C300 | Fix TOCTOU in userspace-controlled length path |

---

## Tier S — do these first (80)

If you only had time for one list before embedded coding rounds:

C006 C013 C021 C022 C031 C036 C041 C042 C056 C057  
C071 C072 C074 C077 C087 C091 C093 C095 C101 C105  
C111 C115 C121 C122 C124 C137 C138 C145 C146 C148  
C150 C155 C164 C165 C166 C167 C173 C174 C175 C181  
C186 C187 C202 C208 C214 C219 C220 C231 C241 C245  
C251 C254 C255 C261 C264 C273 C278 C286 C288 C289  
C290 C292 C010 C014 C067 C082 C118 C134 C141 C160  
C196 C211 C226 C242 C249 C270 C283 C294  

*(80 IDs — master these cold.)*

---

## Tier A — next 120 (after Tier S)

All remaining items in: **B bits, E rings, F sync, I buses, J DMA, K timers, L parsers, O IPC, R tests, U Linux** not already in Tier S.

---

## What this bank deliberately excludes

| Excluded | Covered elsewhere |
|----------|-------------------|
| LeetCode DSA (trees/graphs/DP) | InterviewBit 150 / DSA folder |
| System design whiteboards | FINAL_120 Part C / design sheets |
| Pure behavioral | STAR prep |

---

## Mapping to classic MNC coding prompts

| Famous prompt | IDs |
|---------------|-----|
| Google software timer on 1 HW timer | C173–C175, C181 |
| Google flip bitmap / reverse bits | C022 + buffer reverse |
| Google touch IRQ ring | C071, C111, C137 |
| Apple memcpy + optimize | C041–C042, C276–C284 |
| Apple I2C sensor + debounce | C145–C150, C158 |
| Apple PWM / FSM | C151, C201–C202 |
| Tesla timed FW test | C007, C023, C031, C202, C214, C071–C074, C255, C091–C093 |
| Amazon no-heap ring | C071–C072, C264 |
| NVIDIA volatile / endian / memmove | C006, C031, C042, C091 |

---

## Suggested 8-week coding-only grind

| Week | Focus IDs |
|------|-----------|
| 1 | C001–C055 core C/bits/mem |
| 2 | C056–C090 alloc + rings |
| 3 | C091–C120 sync + IRQ |
| 4 | C121–C160 HAL + buses |
| 5 | C161–C185 DMA + timers |
| 6 | C186–C218 parsers + FSM + filters |
| 7 | C219–C260 IPC + log + WD + tests |
| 8 | C261–C300 C++ / perf / Linux snippets + Tier S redo timed |

---

## Progress tracker

- Tier S completed: ___ / 80  
- Total coded from blank: ___ / 300  
- Timed mocks (45–60 min) conducted: ___  

---

**Note on “100%”:** No finite list guarantees every question, but this bank is designed to cover **all common embedded/firmware coding-round patterns** used at top MNCs (C/C++ implementation under constraints). Pair with DSA + system design lists separately as planned.
