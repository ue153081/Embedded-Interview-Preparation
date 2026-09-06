# Final 120 Embedded Interview Questions — Top MNC Crack List

**Purpose:** One concrete list to prepare for Google • Apple • Meta • Amazon (Lab126/Devices) • NVIDIA • Tesla • ARM • Microsoft • Qualcomm • ASML-style industrial roles.  
**Sources consolidated:** this repo’s master lists, solved Embedded handbooks, system-design sheets, top-MNC depth guide, and company interview archive PDF.  
**Rule:** If you can **code + explain + handle 2 follow-ups** on each item, you cover the vast majority of embedded loops at top MNCs.

**Legend:** `C` = code it · `V` = verbal/explain · `D` = design (whiteboard 30–45 min)  
**Company tags:** G Google · A Apple · M Meta · Z Amazon · N NVIDIA · T Tesla · R ARM · Q Qualcomm · I Industrial/ASML

---

## How to use (practical)

1. Weeks 1–4: **Q001–Q050** (must-code core)  
2. Weeks 5–8: **Q051–Q085** (concurrency/DMA/drivers) + **Q086–Q105** (verbal)  
3. Weeks 9–12: **Q106–Q120** (design) + timed mocks from Tier S  
4. Track: `[ ]` / `[~]` / `[x]`

---

# PART A — Coding (Q001–Q070) · implement in C

## A1. C / Bits / Memory primitives (Q001–Q015)

| # | Type | Question | Companies |
|---|------|----------|-----------|
| Q001 | C | Implement overlap-safe `memmove` and optimized `memcpy` (null/alignment follow-ups) | G A N T |
| Q002 | C | Implement `memset` and explain when compiler may not elide it (e.g. security wipe) | G A |
| Q003 | C | Safe `atoi` with overflow / invalid input detection | G A |
| Q004 | C | Endian conversion helpers for 16/32/64-bit values | G A N T |
| Q005 | C | Count set bits (`uint8`/`uint32`) — Kernighan + LUT; discuss speed | G T N |
| Q006 | C | Reverse bits in a byte/32-bit word; optimize with LUT (lazy init) | G T |
| Q007 | C | Flip MSB and LSB of a byte in place | T |
| Q008 | C | Detect power-of-two; compute next power-of-two | G N |
| Q009 | C | Integer `floor(log2(n))` without `math.h` (edge: 0, overflow) | G |
| Q010 | C | Pack/unpack sensor bitfields from a wire frame | G A T I |
| Q011 | C | Implement CRC-8 | G T I |
| Q012 | C | Implement CRC-16 | G T I |
| Q013 | C | Expand 5-bit RGB channel to 8-bit using shifts (`0→0`, max→255) | G |
| Q014 | C | Parse little-endian struct from a raw memory dump (padding/alignment aware) | T A N |
| Q015 | C | Write `container_of`-style macro and use it on an intrusive list node | G Q R |

## A2. Buffers / Queues / IPC coding (Q016–Q028)

| # | Type | Question | Companies |
|---|------|----------|-----------|
| Q016 | C | SPSC circular buffer (byte) — init/push/pop; define full/empty | G A Z T N |
| Q017 | C | Ring buffer using power-of-2 size and mask indexing | G N |
| Q018 | C | Ring buffer overwrite-oldest policy (Tesla-style stream cache) | T Z |
| Q019 | C | ISR-producer / task-consumer queue with correct critical sections | G A T N |
| Q020 | C | Lock-free SPSC queue + state memory ordering assumptions | G A N |
| Q021 | C | DMA-friendly contiguous-read API from a circular RX buffer | G A N |
| Q022 | C | Multi-producer logging ring with bounded drop + counters | G A T |
| Q023 | C | Priority event queue (ISR posts events; task dispatches) | G A T |
| Q024 | C | Dual-core mailbox: shared-memory message + doorbell IRQ | A N R |
| Q025 | C | Zero-copy message buffer handoff (ownership transfer) | G N |
| Q026 | C | Sequence-lock for shared statistics (ISR writer / task reader) | G N |
| Q027 | C | Lock-free ISR↔task flag/event handoff | G A N |
| Q028 | C | Bounded producer–consumer buffer (mutex + condvar or RTOS primitives) | G A Z |

## A3. Memory allocators (Q029–Q036)

| # | Type | Question | Companies |
|---|------|----------|-----------|
| Q029 | C | Fixed-size memory pool allocator (O(1) alloc/free) | G A T N |
| Q030 | C | ISR-safe object pool (no blocking) | G T N |
| Q031 | C | Pool with guard bytes / poison / leak + watermark stats | G A |
| Q032 | C | Variable-size free-list allocator (first-fit) | G A |
| Q033 | C | Free-list split + coalesce (fragmentation discussion) | G A |
| Q034 | C | Buddy allocator alloc/free sketch | G |
| Q035 | C | Cache-aligned / DMA-safe allocator | G A N |
| Q036 | C | Bump/region allocator with reset for boot/init phases | G A R |

## A4. Concurrency primitives (Q037–Q045)

| # | Type | Question | Companies |
|---|------|----------|-----------|
| Q037 | C | Spinlock with `atomic_flag` | G A N Q |
| Q038 | C | Ticket lock | G N |
| Q039 | C | Minimal mutex | G A Z |
| Q040 | C | Counting semaphore + binary semaphore with ISR give | G A T |
| Q041 | C | Reader–writer lock (starvation discussion) | G A |
| Q042 | C | Atomic overflow-safe counters | G N |
| Q043 | C | Demonstrate ABA problem; sketch tagged-pointer mitigation | G N |
| Q044 | C | Acquire/release ordering: fix a broken shared flag protocol | G A N R |
| Q045 | C | False-sharing: detect and fix hot counters with cache-line padding | G A N |

## A5. Drivers / peripherals coding (Q046–Q060)

| # | Type | Question | Companies |
|---|------|----------|-----------|
| Q046 | C | Register HAL: `read32/write32/rmw` with `volatile` MMIO | G A N T R |
| Q047 | C | Safe MMIO poll-with-timeout helper | G A T |
| Q048 | C | UART polling driver (TX/RX) | G A |
| Q049 | C | Interrupt-driven UART RX/TX with rings + backpressure | G A Z T N |
| Q050 | C | UART DMA TX and/or circular DMA RX | G A N |
| Q051 | C | SPI blocking transfer | A N |
| Q052 | C | SPI interrupt or DMA full-duplex state machine | A N |
| Q053 | C | I2C master write + read (repeated start) | A Z T |
| Q054 | C | I2C bus recovery / stuck-bus handling | A Z |
| Q055 | C | GPIO driver + interrupt debounce algorithm | A T |
| Q056 | C | PWM driver (period/duty, enable/disable) | A T |
| Q057 | C | ADC single-shot with timeout; explain `volatile` ADC pitfalls | T A |
| Q058 | C | Thermal/sensor driver built on given I2C API | A |
| Q059 | C | Watchdog init/kick API and “who kicks” policy code sketch | A T Z |
| Q060 | C | Packet parser FSM: length + CRC + resynchronization on stream | G T I |

## A6. Timers / RT / reliability coding (Q061–Q070)

| # | Type | Question | Companies |
|---|------|----------|-----------|
| Q061 | C | Software timer queue on **one** HW timer (`set_timer` + ISR) | G T |
| Q062 | C | Software timers: cancel + periodic reschedule, wrap-safe ticks | G A T |
| Q063 | C | Timer wheel **or** min-heap timer queue (implement one; justify other) | G A |
| Q064 | C | Non-blocking scheduler: `regCall` / `callNext` style tick dispatcher | G |
| Q065 | C | Deadline-miss counter for a periodic task | T N I |
| Q066 | C | Exponential backoff retry wrapper for a driver call | G A Z |
| Q067 | C | Fault-tolerant peripheral state machine (idle/active/error/recover) | A T I |
| Q068 | C | Traffic-light **or** vending-machine FSM (ignore invalid inputs) | A T |
| Q069 | C | Exponential weighted moving average / low-pass filter (init on first sample) | T |
| Q070 | C | Unit tests that cover all branches of a pointer/data validator | T G |

---

# PART B — Verbal / Conceptual (Q071–Q100) · explain like a senior

| # | Type | Question | Companies |
|---|------|----------|-----------|
| Q071 | V | `volatile` vs atomics vs memory barriers — when each is wrong | G A N T R Q |
| Q072 | V | What is illegal inside an ISR and why? | G A T N |
| Q073 | V | Top-half vs bottom-half / deferred interrupt processing | G A Q N |
| Q074 | V | Mutex vs spinlock vs semaphore — choose for task vs IRQ context | G A N Q |
| Q075 | V | Priority inversion: cause, detection, inheritance/ceiling fixes | T N G |
| Q076 | V | Deadlock conditions and how drivers avoid them | G A Z |
| Q077 | V | Cache coherency with DMA: clean/invalidate ownership rules | G A N R |
| Q078 | V | MMIO posting, readback, write-combine hazards | G A R |
| Q079 | V | DMB vs DSB vs ISB — one concrete driver example each | G A R N |
| Q080 | V | Bare-metal vs RTOS vs Linux PREEMPT_RT — tradeoffs | G A T N I |
| Q081 | V | Boot flow: reset → vectors → `.data/.bss` → `main` (and Linux handoff) | A R G |
| Q082 | V | Stack vs heap vs static — fragmentation and why FW limits heap | G A T N |
| Q083 | V | Undefined behavior in C — 5 examples beyond null deref | A G |
| Q084 | V | Pointer arithmetic with typed pointers (`&x + n` scaling) | A |
| Q085 | V | How paging/MMU/TLB provide protection (driver-relevant level) | Q G R |
| Q086 | V | How you’d measure and budget ISR latency / jitter | T N I G |
| Q087 | V | How you’d debug intermittent protocol/CRC/timing failures on the bench | T I G A |
| Q088 | V | Heisenbug: bug disappears after adding `printf` — likely causes | T G |
| Q089 | V | Debug priority inversion / lost data on a high-rate timer task | T N |
| Q090 | V | I2C timing fundamentals (start/stop, ACK, clock stretch) at EE depth | Z A |
| Q091 | V | CAN/CAN-FD basics: arbitration, bus-off recovery mindset | T N I |
| Q092 | V | Endianness bugs you’ve seen; how to prevent in protocols | T A N |
| Q093 | V | How app talks efficiently to a Linux driver (`ioctl`/`mmap`/`poll`/netlink) | A G Q Z |
| Q094 | V | Platform driver `probe`/`remove` + Device Tree matching | G Z M Q |
| Q095 | V | Hard IRQ vs threaded IRQ — choose for GPIO encoder edges | G Z N |
| Q096 | V | Runtime PM suspend/resume for a peripheral | A G Z |
| Q097 | V | Secure boot / anti-rollback concepts (high level) | A T Z R |
| Q098 | V | ASIL/IEC safety concepts: diagnostics, watchdog hierarchy, degrade modes | T N I |
| Q099 | V | Exception levels / MPU vs MMU / TrustZone overview (portable language) | R A |
| Q100 | V | How you’d validate a hard real-time multi-channel protocol stack | I T N G |

---

# PART C — System Design (Q101–Q120) · whiteboard

| # | Type | Question | Companies |
|---|------|----------|-----------|
| Q101 | D | Design UART stack: polling / IRQ / DMA behind one API | G A N |
| Q102 | D | Design ISR→task event pipeline with latency budget + backpressure | G A T N |
| Q103 | D | Design firmware logging: levels, ring, crash persistence, RT safety | G A T Z |
| Q104 | D | Design software timer service; justify list vs heap vs wheel | G A T |
| Q105 | D | Design DMA framework: descriptor ownership, completion, error recovery | G A N T |
| Q106 | D | Design I2C transaction engine with retry/timeout/recovery | A Z |
| Q107 | D | Design SPI multi-device framework (CS, modes, DMA path) | A N |
| Q108 | D | Design watchdog architecture with task heartbeats + safe reset | A T Z |
| Q109 | D | Design fault manager: detect → classify → retry/degrade/reset | T N I |
| Q110 | D | Design OTA with A/B slots, auth, anti-brick rollback | A G Z T |
| Q111 | D | Design complete boot + health checks to application handoff | A R G |
| Q112 | D | Design dual-core RT + app IPC (shared mem + IRQs + protocols) | A N R |
| Q113 | D | Design Linux platform driver + userspace ABI for a sensor/encoder device | G Z M |
| Q114 | D | Design multi-channel position/encoder interface (hard RT + host API) | I T N G |
| Q115 | D | Design Ethernet↔CAN (or UART) gateway with QoS/backpressure | T N I |
| Q116 | D | Design DMA sensor pipeline → filter → alerts (bounded memory) | G A N |
| Q117 | D | Design device↔controller path: IRQ → SHM → DMA → power/sleep options | G Z |
| Q118 | D | Design power suspend/resume for a peripheral stack | A G Z |
| Q119 | D | Design secure firmware load + factory vs field modes | A T Z |
| Q120 | D | Design bring-up/test strategy: fake registers, fault injection, timing tests | G A T N |

---

## Tier S — first 30 if time-boxed (subset of the 120)

Q001, Q005, Q006, Q014, Q016, Q019, Q020, Q029, Q046, Q049,  
Q053, Q055, Q060, Q061, Q068, Q071, Q072, Q074, Q075, Q077,  
Q086, Q087, Q093, Q102, Q105, Q110, Q113, Q114, Q115, Q117

---

## Coverage map (why this list cracks top MNCs)

| Company | Lean hardest on |
|---------|-----------------|
| **Google** | Q016–Q027, Q029–Q033, Q049–Q050, Q061–Q064, Q071–Q079, Q101–Q105, Q113, Q116–Q117 |
| **Apple** | Q001, Q046–Q058, Q068, Q071–Q084, Q093–Q097, Q101–Q111, Q118–Q119 |
| **Amazon Devices** | Q016–Q019, Q053–Q054, Q090, Q108, Q110, Q113, Q117–Q119 |
| **NVIDIA** | Q020–Q027, Q049–Q052, Q071–Q080, Q091, Q105, Q112, Q114–Q116 |
| **Tesla** | Q014, Q018–Q019, Q057, Q061, Q065–Q070, Q075, Q086–Q089, Q091, Q098, Q108–Q110, Q114–Q115 |
| **ARM** | Q015, Q024, Q036, Q071, Q079–Q081, Q085, Q099, Q111–Q112 |
| **Qualcomm / Linux FW** | Q071–Q074, Q085, Q093–Q095 |
| **ASML / industrial** | Q010–Q012, Q060, Q086–Q087, Q091, Q098, Q100, Q114–Q115 |

---

## Checklist (copy/paste progress)

### Coding Q001–Q070
- [ ] Q001 [ ] Q002 [ ] Q003 [ ] Q004 [ ] Q005 [ ] Q006 [ ] Q007 [ ] Q008 [ ] Q009 [ ] Q010
- [ ] Q011 [ ] Q012 [ ] Q013 [ ] Q014 [ ] Q015 [ ] Q016 [ ] Q017 [ ] Q018 [ ] Q019 [ ] Q020
- [ ] Q021 [ ] Q022 [ ] Q023 [ ] Q024 [ ] Q025 [ ] Q026 [ ] Q027 [ ] Q028 [ ] Q029 [ ] Q030
- [ ] Q031 [ ] Q032 [ ] Q033 [ ] Q034 [ ] Q035 [ ] Q036 [ ] Q037 [ ] Q038 [ ] Q039 [ ] Q040
- [ ] Q041 [ ] Q042 [ ] Q043 [ ] Q044 [ ] Q045 [ ] Q046 [ ] Q047 [ ] Q048 [ ] Q049 [ ] Q050
- [ ] Q051 [ ] Q052 [ ] Q053 [ ] Q054 [ ] Q055 [ ] Q056 [ ] Q057 [ ] Q058 [ ] Q059 [ ] Q060
- [ ] Q061 [ ] Q062 [ ] Q063 [ ] Q064 [ ] Q065 [ ] Q066 [ ] Q067 [ ] Q068 [ ] Q069 [ ] Q070

### Verbal Q071–Q100
- [ ] Q071 [ ] Q072 [ ] Q073 [ ] Q074 [ ] Q075 [ ] Q076 [ ] Q077 [ ] Q078 [ ] Q079 [ ] Q080
- [ ] Q081 [ ] Q082 [ ] Q083 [ ] Q084 [ ] Q085 [ ] Q086 [ ] Q087 [ ] Q088 [ ] Q089 [ ] Q090
- [ ] Q091 [ ] Q092 [ ] Q093 [ ] Q094 [ ] Q095 [ ] Q096 [ ] Q097 [ ] Q098 [ ] Q099 [ ] Q100

### Design Q101–Q120
- [ ] Q101 [ ] Q102 [ ] Q103 [ ] Q104 [ ] Q105 [ ] Q106 [ ] Q107 [ ] Q108 [ ] Q109 [ ] Q110
- [ ] Q111 [ ] Q112 [ ] Q113 [ ] Q114 [ ] Q115 [ ] Q116 [ ] Q117 [ ] Q118 [ ] Q119 [ ] Q120

---

## Cross-links inside this repo

| Need solutions for… | Open |
|---------------------|------|
| Memory / bits / rings / concurrency / drivers | `Embedded/01` … `12_*_solutions.md` |
| Google deep solved set | `google_l4_top50_full_solved_handbook.md` |
| Design prompts expanded | `Embedded/system_design_questions_only.md` |
| Company archive originals | `interview_questions_archive_by_company.md` |
| Strategy / depth rules | `top_mnc_embedded_interview_questions_indepth.md` |
| **FINAL 120 solutions (Steps 0–8)** | `solutions/FINAL_120/README.md` (sample: Q016) |
| **Merged 40-topic list** | `FINAL_120_MERGED_TOPICS.md` |
| Day-before drill | `day_before_interview_revision.md` |

---

**Count verification:** Q001–Q120 = **120 questions** (70 coding + 30 verbal + 20 design).
