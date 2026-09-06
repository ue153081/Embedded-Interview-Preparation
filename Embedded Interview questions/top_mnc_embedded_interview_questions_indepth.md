# Top MNC Embedded Interview Questions (In-Depth Prep)

**Audience:** Google • Apple • Meta • Amazon (Lab126/Devices) • NVIDIA • Tesla • ARM • Microsoft • ASML-style industrial  
**Source repo reviewed:** `ue153081/Embedded-Interview-Preparation`  
**How this file differs from existing material:** company-tagged priorities, verbal/design depth prompts, Linux/platform gaps, and a “must go deep” shortlist mapped to your TI real-time / protocol background.

---

## 0. What you already have in this repo (use it)

| Existing file | Use for |
|---------------|---------|
| `google_embedded_full_master_list_q001_q163.md` | Google L4 coding breadth |
| `google_l4_top50_full_solved_handbook.md` | Solved deep dives |
| `Embedded/01`–`12_*_solutions.md` | C implementations + follow-ups |
| `universal_embedded_interview_master_list_all_companies_2026.md` | Cross-company coding checklist |
| `Embedded/system_design_questions_only.md` | Design prompts |
| `top 20/top_25_embedded_system_design_questions.md` | Classic design set |
| `day_before_interview_revision.md` | Final 24h drill |

**Do not re-solve everything.** Use **Section 1** below as the depth filter, then company sections for targeting.

---

## 1. Must prepare IN DEPTH (top 40 across all big tech)

If you can code + explain + handle 3 follow-ups on each of these, you cover most embedded loops.

### A. Coding (implement from blank file)

| ID | Question | Why big tech asks it |
|----|----------|----------------------|
| D01 | ISR-safe SPSC ring buffer (full/empty, power-of-2 index) | UART/DMA/logging everywhere |
| D02 | Lock-free SPSC queue + memory ordering notes | Google/Apple/NVIDIA concurrency |
| D03 | Interrupt-driven UART RX/TX with ring + backpressure | Classic driver screen |
| D04 | DMA double-buffer / ping-pong ownership FSM | NVIDIA/Tesla/Apple sensors |
| D05 | Fixed-size memory pool (ISR-safe alloc/free + stats) | No-heap firmware culture |
| D06 | Free-list allocator: split + coalesce + fragmentation story | Google/Apple systems depth |
| D07 | Register HAL: read/write/RMW, bitfields, `volatile` limits | Every FW loop |
| D08 | Software timer queue (cancel + periodic, wrap-safe ticks) | RTOS / event systems |
| D09 | I2C master state machine (NACK, timeout, bus recovery) | Devices / bring-up |
| D10 | Packet parser FSM (len + CRC + resync) | Protocol firmware (your strength) |
| D11 | CRC-8/CRC-16 + bitfield pack/unpack | Industrial / auto protocols |
| D12 | Shared-memory mailbox IPC + barriers (dual-core) | AMP SoCs (AM64x / Apple / ARM) |
| D13 | Watchdog architecture (kick policy, task heartbeats) | Reliability rounds |
| D14 | Logging ring with bounded drop + crash buffer | Debuggability obsession |
| D15 | LRU cache (hash + DLL) | Often mixed into “embedded DSA” |

### B. Conceptual / verbal (explain like a senior)

| ID | Question | Depth bar |
|----|----------|-----------|
| V01 | `volatile` vs atomics vs memory barriers — when each fails | Must be flawless |
| V02 | ISR vs thread: what is illegal in ISR and why | Must be flawless |
| V03 | Priority inversion + inheritance / ceiling | Tesla/NVIDIA/RTOS |
| V04 | Cache coherency with DMA (clean/invalidate ownership) | Apple/NVIDIA/Google |
| V05 | Bare-metal vs RTOS vs Linux PREEMPT_RT tradeoffs | Role fit |
| V06 | How you measure and budget ISR/jitter latency | Your TI edge |
| V07 | Boot flow: reset → vectors → `.data/.bss` → main / Linux | ARM/Apple |
| V08 | MMIO posting, readback, write-combine hazards | Low-level FW |
| V09 | Deadlock conditions in driver locks | All |
| V10 | How you’d validate a timing-sensitive protocol on the bench | Your TI edge |

### C. System design (45-min whiteboard)

| ID | Design prompt | Primary companies |
|----|---------------|-------------------|
| S01 | Multi-channel sensor/encoder interface (hard RT + host API) | NVIDIA, Tesla, ASML, TI→FAANG |
| S02 | Ethernet↔CAN (or UART) gateway with latency/backpressure | Tesla, NVIDIA, industrial |
| S03 | OTA with A/B slots, auth, anti-brick rollback | Apple, Google, Amazon, Tesla |
| S04 | DMA sensor pipeline → filter → alert (bounded memory) | Google, Apple, NVIDIA |
| S05 | Dual-core: real-time core + app core IPC | ARM, Apple, AM64x story |
| S06 | Linux platform driver + userspace ABI for a device | Google, Amazon, Meta |
| S07 | Fault manager: detect → classify → degrade/reset | Tesla, ASML, auto |
| S08 | Power: suspend/resume for a peripheral stack | Apple, Google Pixel/Nest |

**Your differentiator stories to attach:** HDSL multi-channel + IMEM, FPGA→PRU, EnDat3, Ethernet↔CAN, customer bring-up, APEC paper.

---

## 2. Google (Pixel / Nest / Platforms / Waymo HW) — embedded focus

### Coding / low-level (prep deep)
1. SPSC ring + ISR producer / task consumer  
2. UART IRQ + DMA RX circular buffer  
3. Memory pool + leak/watermark stats  
4. Free-list allocator coalesce edge cases  
5. Timer wheel vs min-heap — implement one, justify other  
6. Lock-free flag handoff ISR↔task (acquire/release)  
7. Sequence lock for shared stats  
8. Packet framing parser with resync  
9. `memcpy`/`memmove` correctness  
10. False sharing fix in hot counters  

### OS / concurrency verbal
11. Explain page cache vs device `mmap` (high level)  
12. Mutex vs spinlock in driver softirq/tasklet-equivalent  
13. Priority inheritance example from a real bug  
14. How you’d avoid priority inversion in a sensor pipeline  
15. DMB/DSB/ISB: one concrete driver example each  

### Linux / platform (gap vs your MCU work — prep)
16. Platform driver probe/remove + Device Tree matching  
17. Threaded IRQ vs hard IRQ bottom half  
18. `poll`/`read`/`mmap` userspace ABI design  
19. sysfs knobs for diagnostics (error counts, enable)  
20. Power management: runtime PM suspend/resume sketch  

### Design
21. Design Nest/Pixel-style sensor hub firmware  
22. Design reliable logging under real-time constraints  
23. Design factory test hooks without hurting production latency  
24. Design OTA for a constrained MCU companion chip  

### Behavioral hybrids Google likes
25. Walk through hardest timing/CRC bug — root cause method  
26. Time you improved latency/memory under a hard constraint  
27. Disagreement with hardware/protocol assumptions — data used  

**Google depth rule:** correctness, invariants, tests, and clear communication > clever micro-opts.

**Repo map:** grind `google_l4_top50_full_solved_handbook.md` + Topics 7–12 in Q001–Q163.

---

## 3. Apple (Firmware / Embedded / Silicon-adjacent)

### Expect deeper “why” chains
1. Object layout, padding, alignment traps on ARM  
2. Exact meaning of `volatile` on MMIO (and why atomics differ)  
3. Interrupt nesting, critical sections, baspri-style masking  
4. Cache line size effects on driver shared structs  
5. DMA coherency bugs you’ve seen / would hunt  
6. BootROM → loader → firmware trust boundaries (high level)  
7. Secure boot / anti-rollback concepts (no need for Apple secrets)  
8. Power domains / clock gating / wake sources design  
9. Zero-copy I/O path from IRQ to consumer  
10. Deterministic logging that cannot deadlock RT path  

### Design prompts
11. Design a high-rate sensor pipeline with backpressure  
12. Design driver API that is hard to misuse  
13. Design bring-up sequence for a new board spin  
14. Design crash dump + postmortem without large RAM  

### Coding
15. Ring buffer + UART or SPI DMA  
16. State machine protocol parser  
17. Pool allocator with poisoning/canaries  
18. Lock-free SPSC  
19. Timer service with cancel races fixed  

**Apple depth rule:** elegant APIs, performance awareness, relentless follow-ups. Practice answering “what breaks if…” five times.

---

## 4. Meta (Reality Labs / embedded devices)

1. Camera/IMU/sensor time sync across streams  
2. High-bandwidth DMA path + userspace delivery  
3. Thermal/power throttling interaction with FW  
4. Concurrent producers to one logging/telemetry sink  
5. Design XR device sensor fusion timing (conceptual)  
6. Buffer management under bursty IRQ rates  
7. Fault isolation between subsystems  
8. Classic: ring, pool, UART/SPI, parser, OTA  

**Meta depth rule:** DSA still matters; embed domain as design flavor.

---

## 5. Amazon (Lab126 / Devices / custom silicon FW)

1. OTA A/B + rollback + field metrics  
2. Device provisioning / factory vs field modes  
3. Flash wear, littlefs-style constraints (conceptual)  
4. Watchdog + safe mode + customer-force update story  
5. Low-power wake + brownout handling  
6. Metrics: what counters would you ship?  
7. Driver timeout/retry that doesn’t brick UX  
8. Leadership Principles mapped to FW ownership stories  

**Amazon depth rule:** customer impact + operational excellence in every design answer.

---

## 6. NVIDIA (Drive / Jetson / embedded platforms)

### Prep deep
1. Hard real-time path vs Linux best-effort split  
2. Sensor → DMA → processing deadline budget  
3. Cache/DMA ownership on heterogeneous SoCs  
4. Multi-core / AMP IPC (RPMsg-style thinking)  
5. Safety: diagnostics, watchdogs, degraded mode  
6. Ethernet / CAN / camera timing sync concepts  
7. Profiling: how you find jitter sources  
8. CUDA is optional; **determinism + drivers + C++** are not  

### Design
9. Design Drive-style sensor interface with redundancy hooks  
10. Design logging that survives fault injection  
11. Design gateway between high-speed link and MCU CAN  

**NVIDIA depth rule:** performance numbers, failure modes, scalable architecture.

---

## 7. Tesla (Firmware / Autopilot / controls-adjacent)

1. Control-loop deadline miss detection + response  
2. CAN/CAN-FD frame handling, bus-off recovery  
3. Freedom-from-interference between ASIL and QM software (concepts)  
4. Watchdog hierarchies (task / system / external)  
5. Boot integrity + secure update mindset  
6. Fault injection testing strategy  
7. Rate monotonic vs EDF — when you’d use which  
8. Noise/CRC/timing debug on the bench (your TI stories)  
9. Design multi-channel encoder/position input into a vehicle controller  
10. Ownership: shipped under ambiguity / hardware late  

**Tesla depth rule:** intensity, ownership, first-principles debugging.

---

## 8. ARM (Firmware / platform / architecture-aware SW)

1. Exception levels (EL0–EL3) high-level map  
2. Vector table / exception entry-exit  
3. MMU vs MPU — when each  
4. Cache hierarchy + maintenance ops  
5. GIC: SPI/PPI/SGI concepts  
6. Memory types: Device vs Normal, why MMIO is Device  
7. Barriers: DMB/DSB/ISB concrete placements  
8. TrustZone / secure vs non-secure world (overview)  
9. Boot: TF-A style conceptual flow (no internals needed)  
10. Bring-up on Cortex-R (use your R5F experience in portable language)  

**ARM depth rule:** architecture vocabulary + bare-metal correctness.

---

## 9. Microsoft / Qualcomm / Intel-class (if applied)

- Same core as Google coding set  
- Add: Windows-on-devices or SoC BSP vocabulary only if JD says so  
- Qualcomm: high-speed interconnects, power/clock, modem-adjacent IPC themes  
- Focus still: drivers, DMA, concurrency, bring-up  

---

## 10. ASML / industrial motion (prestige + your best fit)

1. Deterministic multi-axis sync / distributed clocks  
2. Jitter budget from sensor to actuator command  
3. Protocol stack under memory constraints (your HDSL scaling)  
4. Redundancy and graceful degradation  
5. Host (Linux) vs real-time engine split  
6. Long-cable / noise / delay compensation validation  
7. Safety CRC / sign-of-life monitoring design  
8. Design position-sense multi-protocol abstraction (EnDat/BiSS-like — speak generically)  

**ASML depth rule:** control + timing + reliability > LeetCode Hard volume.

---

## 11. Linux driver questions (your stated gap — new vs old repo lists)

Prep these even while building GitHub projects:

1. Explain platform driver lifecycle (`probe`/`remove`)  
2. Device Tree: compatible, resources, interrupts  
3. `devm_*` managed resources — why  
4. Hard IRQ vs threaded IRQ — choose for encoder edges  
5. `copy_to_user` / `copy_from_user` pitfalls  
6. Design `poll` + wait queue for “new sample”  
7. `mmap` of kernel buffer / IO memory — risks  
8. sysfs vs ioctl vs netlink — when each  
9. Concurrent openers: one reader vs many  
10. How you’d unit-test a driver with fake registers  

---

## 12. Company → priority matrix (study order)

| If interviewing at… | Primary depth set | Secondary |
|---------------------|-------------------|-----------|
| Google | §1 A+B + §2 + Linux §11 | Design S03/S04/S06 |
| Apple | §1 + §3 | Power/boot/security concepts |
| Meta | §1 A + DSA + §4 | Sensor sync design |
| Amazon | §1 + §5 + LP stories | OTA/watchdog |
| NVIDIA | §1 + §6 + DMA/IPC | Safety lite |
| Tesla | §1 + §7 + your protocol stories | CAN + deadlines |
| ARM | §1 B/C + §8 | Cortex-R bring-up narrative |
| ASML | §1 C + §10 + jitter/sync | Linux host split |

---

## 13. 4-week depth plan (embedded-only track)

### Week 1 — Foundations
- Code: D01, D03, D05, D07  
- Verbal: V01, V02, V06  
- Re-read: `day_before_interview_revision.md` Section A  

### Week 2 — Concurrency / DMA
- Code: D02, D04, D12, D14  
- Verbal: V03, V04, V08  
- Design aloud: S04, S05  

### Week 3 — Protocols / reliability / Linux
- Code: D09, D10, D11, D13  
- Verbal: V05, V09, V10  
- Linux: §11 questions 1–6  
- Design: S01, S02 (use TI metrics, generic protocol names)  

### Week 4 — Company polish + mocks
- Design: S03, S06, S07, S08  
- 4 mocks: 1 coding driver + 1 design + 1 verbal barrage  
- Company section matching next onsite  

---

## 14. Answer framework (use every time)

### Coding
1. Clarify constraints (ISR? SMP? no alloc? latency?)  
2. State invariants (full/empty, ownership, wrap)  
3. Code cleanly  
4. Complexity + failure modes  
5. Tests: unit + fault injection + timing  

### Design
1. Goals / non-goals  
2. Block diagram  
3. Data path + control path  
4. Timing budget  
5. Memory budget  
6. Failure & recovery  
7. Observability  
8. Tradeoffs / v2  

### Debug story (STAR + technical)
**Situation → symptom → hypothesis tree → measurement (scope/LA/logs) → root cause → fix → prevention metric.**

---

## 15. Cross-links inside this repo

- Solved coding depth: `Embedded/01_memory_management_solutions.md` … `12_determinism_and_smp_logging_solutions.md`  
- Google handbook: `google_l4_top50_full_solved_handbook.md`  
- Design-only sheet: `Embedded/system_design_questions_only.md`  
- Universal checklist: `universal_embedded_interview_master_list_all_companies_2026.md`  
- Top-25 design: `../top 20/top_25_embedded_system_design_questions.md`  

---

## 16. Suggested next files (optional)

1. `top_mnc_embedded_answer_outlines.md` — bullet answers for §1 V-questions + S-designs  
2. `linux_driver_interview_drill.md` — §11 with sketch solutions  
3. Update `day_before_interview_revision.md` to include Linux 5-question mini-set  

---

**Bottom line:** Your repo already covers Google-style **coding breadth**. This file is the **depth + company targeting** layer—especially Linux/platform, architecture (ARM/Apple), and industrial/auto design that match your TI profile for NVIDIA/Tesla/ASML while keeping Google/Apple loops honest about OS/driver fundamentals.
