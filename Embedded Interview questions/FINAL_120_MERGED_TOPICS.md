# FINAL 120 → Merged Topic List (45 prep units)

**Purpose:** One question per **topic** — related FINAL 120 items merged so you prepare each idea once, with variants as follow-ups inside a single solution.  
**Source:** [`FINAL_120_embedded_interview_questions_top_MNC.md`](./FINAL_120_embedded_interview_questions_top_MNC.md) (120 → **40** merged topics + 1 mock checkpoint)  
**Solutions:** [`solutions/FINAL_120_MERGED/README.md`](./solutions/FINAL_120_MERGED/README.md) — **all 40 topics complete** (Steps 0–8 + Further study links)

**Legend:** `C` coding · `V` verbal · `D` design · `M` merged (may span C+V+D)

---

## Why merge?

| Pattern | Example originals | One merged topic |
|---------|-------------------|------------------|
| Same API, tiny twist | Q016 spare-slot ring, Q017 pow2 mask, Q018 overwrite | **M006** Ring buffers |
| Same bus, different mode | Q048 UART poll, Q049 IRQ, Q050 DMA | **M016** UART stack |
| Same concept, width change | Q011 CRC-8, Q012 CRC-16 | **M005** CRC |
| Code + verbal + design | Q016 ring + Q102 pipeline + Q103 logging | Split by layer: code in M006/M007, design in M038/M039 |

**Rule:** Mark `[x]` when you can **code OR explain OR whiteboard** the merged topic **plus all listed sub-variants** without notes.

---

## Summary

| Part | Merged IDs | Original Q count | Topics |
|------|------------|------------------|-------:|
| A — Coding | M001–M023 | 70 | 23 |
| B — Verbal | M026–M036 | 30 | 11 |
| C — Design | M039–M044 | 20 | 6 |
| Mock checkpoint | M045 | — | 1 |
| **Total** | **M001–M045** | **120** | **40** (+ mock) |

---

# PART A — Coding merged (M001–M023)

## M001 — Memory byte operations (`memcpy` / `memmove` / `memset` / secure wipe)

**Type:** C · **Tier:** S  
**Merged from:** Q001, Q002  
**Companies:** G A N T

**Single prep question:** Implement overlap-safe `memmove`, optimized `memcpy` (alignment paths), and `memset`; explain when the compiler elides memset and how to force secure zeroization.

**Sub-variants to handle in one solution:**
- NULL / zero-length semantics
- Overlapping regions (memmove direction)
- Word-aligned fast path vs byte tail
- `volatile`/`memset_s`/`explicit_bzero` for secrets

---

## M002 — Safe string / integer parsing

**Type:** C  
**Merged from:** Q003  
**Companies:** G A

**Single prep question:** Implement safe `atoi` with overflow detection, invalid input handling, and clear return codes.

**Sub-variants:** leading whitespace, sign, partial parse, `INT_MAX` boundary.

---

## M003 — Endianness, wire layout & struct unpacking

**Type:** C  
**Merged from:** Q004, Q010, Q014  
**Companies:** G A N T I

**Single prep question:** Implement endian helpers (`read_le16`, `write_be32`, 64-bit); pack/unpack sensor bitfields from a wire frame; parse a little-endian struct from a raw dump with padding/alignment awareness.

**Sub-variants:** `#pragma pack` vs shift/mask, unaligned access, portable serialization.

---

## M004 — Bit manipulation toolkit

**Type:** C · **Tier:** S  
**Merged from:** Q005, Q006, Q007, Q008, Q009, Q013  
**Companies:** G A T N

**Single prep question:** One module: popcount (Kernighan + optional LUT), reverse bits (byte/32), flip MSB/LSB, `is_pow2` / `next_pow2`, `floor_log2` without `math.h`, 5-bit→8-bit RGB expand.

**Sub-variants:** SWAR popcount, lazy LUT init, edge cases (`n=0`, overflow).

---

## M005 — CRC & checksums

**Type:** C  
**Merged from:** Q011, Q012  
**Companies:** G T I

**Single prep question:** Implement CRC-8 and CRC-16 (bitwise + optional table); same API shape for both widths.

**Sub-variants:** init/xorout/refin/refout, table-driven speedup, use in parser (→ M024).

---

## M006 — Ring buffers & SPSC queues (complete)

**Type:** C · **Tier:** S  
**Merged from:** Q016, Q017, Q018, Q019, Q020, Q021  
**Companies:** G A Z T N

**Single prep question:** Implement a byte ring with `init`/`push`/`pop`; cover spare-slot full/empty, power-of-2 mask indexing, overwrite-oldest policy, ISR-producer/task-consumer critical sections, lock-free SPSC with acquire/release, and DMA-friendly contiguous read API.

**Sub-variants:** drop-newest vs overwrite-oldest, `push_n`/`pop_n`, peek, drop counters, SMP memory orders.

**Solution ready:** [`solutions/FINAL_120/Q016_SPSC_circular_buffer.md`](./solutions/FINAL_120/Q016_SPSC_circular_buffer.md) — expand to full **M006** solution.

---

## M007 — IPC, mailboxes & lock-free handoff

**Type:** C  
**Merged from:** Q022, Q023, Q024, Q025, Q026, Q027, Q028  
**Companies:** G A Z T N R

**Single prep question:** One prep doc covering: multi-producer logging ring with bounded drop; priority event queue (ISR post / task dispatch); dual-core mailbox (shared memory + doorbell IRQ); zero-copy buffer ownership transfer; sequence-lock for stats; lock-free ISR↔task flag; and bounded blocking producer–consumer (mutex + condvar / RTOS).

**Sub-variants:** backpressure, generation counters, cache-line alignment, `irq_save` vs atomics.

---

## M008 — Memory allocators (pools → heap → special)

**Type:** C · **Tier:** S (pool part)  
**Merged from:** Q029, Q030, Q031, Q032, Q033, Q034, Q035, Q036  
**Companies:** G A T N R

**Single prep question:** Implement fixed-size pool (O(1) alloc/free), ISR-safe pool variant, guard/poison/watermark stats; then variable free-list (first-fit, split/coalesce), buddy sketch; plus DMA-aligned and bump/region allocators.

**Sub-variants:** fragmentation story, TLSF mention, handle indirection, double-free detection.

---

## M009 — Locks, semaphores & reader–writer

**Type:** C  
**Merged from:** Q037, Q038, Q039, Q040, Q041  
**Companies:** G A N Q Z T

**Single prep question:** Implement spinlock (`atomic_flag`), ticket lock, minimal mutex, counting/binary semaphore (ISR-safe give), and reader–writer lock; discuss starvation and when each is legal in ISR vs task.

---

## M010 — Atomics, memory order & cache effects

**Type:** C · **Tier:** S (ordering part)  
**Merged from:** Q042, Q043, Q044, Q045  
**Companies:** G A N R

**Single prep question:** Overflow-safe atomic counters; demonstrate ABA on a naive lock-free stack and tagged-pointer fix; repair a broken acquire/release flag protocol; fix false sharing with cache-line padding.

---

## M011 — MMIO register HAL & timed polling

**Type:** C · **Tier:** S  
**Merged from:** Q046, Q047  
**Companies:** G A N T R

**Single prep question:** `read32`/`write32`/`rmw` with correct MMIO semantics; bitfield helpers; poll-with-timeout for status bits; document `volatile` limits.

---

## M012 — UART driver (poll → IRQ → DMA)

**Type:** C · **Tier:** S  
**Merged from:** Q048, Q049, Q050  
**Companies:** G A Z T N

**Single prep question:** One UART module: polling TX/RX, IRQ-driven RX/TX with rings and backpressure, optional circular DMA RX / DMA TX; unified internal state machine.

**Sub-variants:** flush, error flags, RTS/CTS hooks, drop policy on full ring.

---

## M013 — SPI driver (blocking → IRQ/DMA)

**Type:** C  
**Merged from:** Q051, Q052  
**Companies:** A N

**Single prep question:** Blocking full-duplex transfer; extend to IRQ or DMA state machine with CS management.

---

## M014 — I2C master (transfer + recovery)

**Type:** C · **Tier:** S  
**Merged from:** Q053, Q054  
**Companies:** A Z T

**Single prep question:** Write, read, repeated-start write+read; NACK/timeout handling; stuck-bus recovery (clock pulse + STOP).

---

## M015 — GPIO, debounce, PWM, ADC & sensor wrapper

**Type:** C  
**Merged from:** Q055, Q056, Q057, Q058  
**Companies:** A T

**Single prep question:** GPIO read/write/toggle + interrupt debounce; PWM period/duty; ADC single-shot with timeout; thin sensor driver on top of I2C API.

**Sub-variants:** `volatile` ADC pitfalls, thermal read retry.

---

## M016 — Watchdog & deadline monitoring

**Type:** C  
**Merged from:** Q059, Q065  
**Companies:** A T Z N I

**Single prep question:** Watchdog init/kick policy (who kicks, windowed WDT sketch); deadline-miss counter for periodic tasks; tie to schedulability (`sum(WCET) ≤ period`).

---

## M017 — Protocol stream parser (framing + CRC + resync)

**Type:** C · **Tier:** S  
**Merged from:** Q060  
**Companies:** G T I

**Single prep question:** Byte-stream parser FSM: length field, CRC validate, resync on corruption; return NEED_MORE / OK / RESYNC.

*(Stays one original Q — foundation for encoder/protocol roles.)*

---

## M018 — Software timers & tick dispatch

**Type:** C · **Tier:** S  
**Merged from:** Q061, Q062, Q063, Q064  
**Companies:** G A T

**Single prep question:** Software timers on one HW timer (set/cancel/ISR); periodic + wrap-safe time comparisons; implement **either** sorted list, min-heap, or timer wheel and justify the others; `regCall`/`callNext` deadline dispatcher.

---

## M019 — Reliability patterns (backoff, fault FSM)

**Type:** C  
**Merged from:** Q066, Q067  
**Companies:** G A Z T I

**Single prep question:** Exponential backoff wrapper for driver retries; fault-tolerant peripheral FSM (idle/active/error/recover) with explicit transitions.

---

## M020 — Classic FSM coding

**Type:** C  
**Merged from:** Q068  
**Companies:** A T

**Single prep question:** Traffic-light or vending-machine FSM; ignore or count invalid inputs; table-driven vs switch.

---

## M021 — Filters & signal-lite numeric

**Type:** C  
**Merged from:** Q069  
**Companies:** T

**Single prep question:** EWMA / first-order low-pass; init on first sample; fixed-point variant mention.

---

## M022 — Embedded unit-test harness

**Type:** C  
**Merged from:** Q070  
**Companies:** T G

**Single prep question:** Branch-complete tests for a pointer/range validator; fake HAL; fault injection hooks.

---

## M023 — C macros & intrusive structures

**Type:** C  
**Merged from:** Q015  
**Companies:** G Q R

**Single prep question:** `container_of`, `offsetof`, intrusive doubly-linked list node usage.

*Tip: M017 (parser) + M005 (CRC) are often tested together — prepare one integrated example.*

---

# PART B — Verbal merged (M026–M036)

## M026 — Memory model: `volatile`, atomics, barriers, MMIO, UB

**Type:** V · **Tier:** S  
**Merged from:** Q071, Q078, Q083, Q084  
**Companies:** G A N T R Q

**Single prep question:** When is `volatile` required vs wrong? When do atomics and barriers replace it? MMIO posting/readback hazards; five UB examples beyond null deref; typed pointer arithmetic rules.

**60-sec script + 3 follow-ups required.**

---

## M027 — Interrupt architecture (ISR rules, deferral, threaded IRQ)

**Type:** V · **Tier:** S  
**Merged from:** Q072, Q073, Q095  
**Companies:** G A T N Q Z

**Single prep question:** What is illegal in ISR and why? Top-half vs bottom-half / workqueue / threaded IRQ; when to pick hard vs threaded IRQ for GPIO encoder edges.

---

## M028 — Synchronization choice & failure modes

**Type:** V · **Tier:** S  
**Merged from:** Q074, Q075, Q076, Q089  
**Companies:** G A N Q Z T

**Single prep question:** Mutex vs spinlock vs semaphore in task vs IRQ; priority inversion (cause, inheritance, ceiling); deadlock four conditions + driver avoidance; debug lost data on high-rate timer task.

---

## M029 — DMA, cache & ARM ordering instructions

**Type:** V · **Tier:** S  
**Merged from:** Q077, Q079  
**Companies:** G A N R

**Single prep question:** DMA cache coherency (clean/invalidate, ownership); DMB vs DSB vs ISB with one driver example each.

---

## M030 — Runtime environments & memory layout

**Type:** V  
**Merged from:** Q080, Q082  
**Companies:** G A T N I

**Single prep question:** Bare-metal vs RTOS vs Linux PREEMPT_RT; stack vs heap vs static; why FW limits heap and fragmentation risk.

---

## M031 — Boot, MMU, MPU & TrustZone

**Type:** V  
**Merged from:** Q081, Q085, Q099  
**Companies:** A R G Q

**Single prep question:** Reset → vectors → `.data/.bss` → `main` (and Linux handoff); paging/MMU/TLB at driver-relevant depth; MPU vs MMU vs exception levels / TrustZone overview.

---

## M032 — Measurement, debug & heisenbugs

**Type:** V · **Tier:** S  
**Merged from:** Q086, Q087, Q088  
**Companies:** T N I G A

**Single prep question:** How to measure/budget ISR latency and jitter; debug intermittent protocol/CRC/timing on bench; why `printf` hides bugs.

**Your TI stories:** EnDAT timing, customer bring-up, APEC measurement methodology.

---

## M033 — Buses & protocols (I2C, CAN, endian)

**Type:** V  
**Merged from:** Q090, Q091, Q092  
**Companies:** Z A T N I

**Single prep question:** I2C timing (start/stop, ACK, clock stretch); CAN/CAN-FD arbitration and bus-off mindset; endianness bugs and prevention in protocols.

---

## M034 — Linux driver interface & platform model

**Type:** V · **Tier:** S  
**Merged from:** Q093, Q094, Q096  
**Companies:** A G Q Z M

**Single prep question:** `ioctl` / `mmap` / `poll` / netlink tradeoffs; platform driver probe/remove + Device Tree; runtime PM suspend/resume.

---

## M035 — Security & safety concepts

**Type:** V  
**Merged from:** Q097, Q098  
**Companies:** A T Z R N I

**Single prep question:** Secure boot and anti-rollback (high level); ASIL/IEC diagnostics, watchdog hierarchy, degrade modes.

---

## M036 — RT validation & system-level verbal

**Type:** V  
**Merged from:** Q100  
**Companies:** I T N G

**Single prep question:** How to validate a hard real-time multi-channel protocol stack end-to-end.

---

# PART C — Design merged (M039–M044)

## M039 — Driver stacks & bus frameworks

**Type:** D · **Tier:** S  
**Merged from:** Q101, Q106, Q107  
**Companies:** G A N Z

**Single prep question:** Design unified APIs for UART (poll/IRQ/DMA), I2C transaction engine (retry/timeout/recovery), and SPI multi-device (CS, modes, DMA).

---

## M040 — Data path: ISR → task → DMA → pipeline

**Type:** D · **Tier:** S  
**Merged from:** Q102, Q105, Q116, Q117  
**Companies:** G A T N Z

**Single prep question:** Design ISR→task event pipeline (latency budget, backpressure); DMA framework (descriptor ownership, completion, errors); sensor pipeline DMA→filter→alerts; device path IRQ→SHM→DMA→power/sleep.

---

## M041 — Platform services: timers, logging, watchdog, fault

**Type:** D  
**Merged from:** Q103, Q104, Q108, Q109  
**Companies:** G A T Z N I

**Single prep question:** Firmware logging (levels, ring, crash persistence, RT-safe); software timer service (list vs heap vs wheel); watchdog + task heartbeats; fault manager (detect→classify→retry/degrade/reset).

---

## M042 — Boot, OTA, security & power

**Type:** D · **Tier:** S (OTA)  
**Merged from:** Q110, Q111, Q118, Q119  
**Companies:** A G Z T R

**Single prep question:** OTA A/B + auth + anti-brick rollback; boot + health checks to app handoff; peripheral suspend/resume stack; secure firmware load factory vs field.

---

## M043 — Multi-core, encoder & gateway systems

**Type:** D · **Tier:** S  
**Merged from:** Q112, Q113, Q114, Q115  
**Companies:** A N R G Z M I T N

**Single prep question:** Dual-core RT + app IPC; Linux platform driver + userspace ABI for sensor/encoder; **multi-channel position/encoder interface (hard RT + host API)**; Ethernet↔CAN/UART gateway with QoS/backpressure.

**Your signature topic:** map HDSL / EnDAT3 / PRU / FPGA paths to M043.

---

## M044 — Test, bring-up & validation architecture

**Type:** D  
**Merged from:** Q120  
**Companies:** G A T N

**Single prep question:** Fake registers, fault injection, timing tests, CI for FW.

---

## M045 — Mock checkpoint (not a new topic)

Run **3 full design mocks** from M039, M040, M043. Review any `[ ]` items on the 40-topic checklist below.

---

# Master mapping: original Q → merged M

| Original | → M | Original | → M | Original | → M |
|----------|-----|----------|-----|----------|-----|
| Q001 | M001 | Q041 | M009 | Q081 | M031 |
| Q002 | M001 | Q042 | M010 | Q082 | M030 |
| Q003 | M002 | Q043 | M010 | Q083 | M026 |
| Q004 | M003 | Q044 | M010 | Q084 | M026 |
| Q005 | M004 | Q045 | M010 | Q085 | M031 |
| Q006 | M004 | Q046 | M011 | Q086 | M032 |
| Q007 | M004 | Q047 | M011 | Q087 | M032 |
| Q008 | M004 | Q048 | M012 | Q088 | M032 |
| Q009 | M004 | Q049 | M012 | Q089 | M028 |
| Q010 | M003 | Q050 | M012 | Q090 | M033 |
| Q011 | M005 | Q051 | M013 | Q091 | M033 |
| Q012 | M005 | Q052 | M013 | Q092 | M033 |
| Q013 | M004 | Q053 | M014 | Q093 | M034 |
| Q014 | M003 | Q054 | M014 | Q094 | M034 |
| Q015 | M023 | Q055 | M015 | Q095 | M027 |
| Q016 | M006 | Q056 | M015 | Q096 | M034 |
| Q017 | M006 | Q057 | M015 | Q097 | M035 |
| Q018 | M006 | Q058 | M015 | Q098 | M035 |
| Q019 | M006 | Q059 | M016 | Q099 | M031 |
| Q020 | M006 | Q060 | M017 | Q100 | M036 |
| Q021 | M006 | Q061 | M018 | Q101 | M039 |
| Q022 | M007 | Q062 | M018 | Q102 | M040 |
| Q023 | M007 | Q063 | M018 | Q103 | M041 |
| Q024 | M007 | Q064 | M018 | Q104 | M041 |
| Q025 | M007 | Q065 | M016 | Q105 | M040 |
| Q026 | M007 | Q066 | M019 | Q106 | M039 |
| Q027 | M007 | Q067 | M019 | Q107 | M039 |
| Q028 | M007 | Q068 | M020 | Q108 | M041 |
| Q029 | M008 | Q069 | M021 | Q109 | M041 |
| Q030 | M008 | Q070 | M022 | Q110 | M042 |
| Q031 | M008 | | | Q111 | M042 |
| Q032 | M008 | | | Q112 | M043 |
| Q033 | M008 | | | Q113 | M043 |
| Q034 | M008 | | | Q114 | M043 |
| Q035 | M008 | | | Q115 | M043 |
| Q036 | M008 | | | Q116 | M040 |
| Q037 | M009 | | | Q117 | M040 |
| Q038 | M009 | | | Q118 | M042 |
| Q039 | M009 | | | Q119 | M042 |
| Q040 | M009 | | | Q120 | M044 |

---

# Tier S remapped (prepare these merged topics first)

| Merged | Was (original Tier S) |
|--------|------------------------|
| **M001** | Q001 |
| **M004** | Q005, Q006 |
| **M003** | Q014 |
| **M006** | Q016, Q019, Q020 |
| **M008** | Q029 |
| **M011** | Q046 |
| **M012** | Q049 |
| **M014** | Q053 |
| **M015** | Q055 |
| **M017** | Q060 |
| **M018** | Q061 |
| **M020** | Q068 |
| **M026** | Q071 |
| **M027** | Q072 |
| **M028** | Q074, Q075 |
| **M029** | Q077 |
| **M032** | Q086, Q087 |
| **M034** | Q093 |
| **M040** | Q102, Q105 |
| **M042** | Q110 |
| **M043** | Q113, Q114, Q115 |
| **M040** | Q117 |

**22 merged Tier-S topics** (down from 30 original IDs — some Tier S items folded into same M).

---

# 8-week study plan (merged list only)

| Week | Merged topics | Focus |
|------|---------------|--------|
| 1 | M001, M004, M003, M005, M006 | Memory, bits, rings |
| 2 | M008, M009, M010, M011 | Allocators, sync, MMIO |
| 3 | M012, M013, M014, M015, M017 | Drivers |
| 4 | M018, M019, M020, M021, M022, M026, M027 | Timers, FSM, verbal core |
| 5 | M007, M028, M029, M030, M031 | IPC + deep verbal |
| 6 | M032, M033, M034, M035, M036 | Debug, Linux, safety |
| 7 | M039, M040, M041 | Design platforms |
| 8 | M042, M043, M044, M045 | OTA, encoder/gateway, test arch, mocks |

---

# Checklist (40 merged topics)

### Coding M001–M023
- [ ] M001 [ ] M002 [ ] M003 [ ] M004 [ ] M005 [ ] M006 [ ] M007 [ ] M008 [ ] M009 [ ] M010
- [ ] M011 [ ] M012 [ ] M013 [ ] M014 [ ] M015 [ ] M016 [ ] M017 [ ] M018 [ ] M019 [ ] M020
- [ ] M021 [ ] M022 [ ] M023

### Verbal M026–M036
- [ ] M026 [ ] M027 [ ] M028 [ ] M029 [ ] M030 [ ] M031 [ ] M032 [ ] M033 [ ] M034 [ ] M035 [ ] M036

### Design M039–M044
- [ ] M039 [ ] M040 [ ] M041 [ ] M042 [ ] M043 [ ] M044

### Mock
- [ ] M045 (3 mocks done)

---

## Cross-links

| Resource | Path |
|----------|------|
| Original 120 questions | `FINAL_120_embedded_interview_questions_top_MNC.md` |
| Merged solutions (WIP) | `solutions/FINAL_120_MERGED/README.md` |
| Sample ring solution (→ expand to M006) | `solutions/FINAL_120/Q016_SPSC_circular_buffer.md` |
| 300 coding drill bank | `solutions/coding_rounds/README.md` |

**Count:** 120 original → **40 merged topics** (+ M045 mock checkpoint). Same coverage, less repetition.
