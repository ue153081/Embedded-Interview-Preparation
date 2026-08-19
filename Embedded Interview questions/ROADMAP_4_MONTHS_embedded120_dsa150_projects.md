# 4-Month Roadmap — Embedded 120 + InterviewBit 150 DSA + Projects

**Goal:** Be interview-ready for top MNC embedded/firmware roles (Google/Apple/Amazon/NVIDIA/Tesla/ARM-class).  
**Duration:** 16 weeks (~4 months)  
**Inputs:**
- Embedded: `FINAL_120_embedded_interview_questions_top_MNC.md`
- DSA: **150 InterviewBit** problems (topic plan below)
- Projects: AM64x/Pi Linux stack (driver → BSP → RT path)

**Success definition (end of month 4):**
- [x] ≥100/120 embedded marked `[x]` (code + 2 follow-ups); all Tier S solid  
- [x] 150 InterviewBit problems solved + notes; timed Mediums comfortable  
- [x] 2–3 GitHub projects demoable (driver required; BSP + RT preferred)  
- [x] 6 STAR stories + 6 design prompts practiced aloud  
- [x] ≥6 full mocks completed  

---

## Weekly time budget (adjust to your job)

| Block | Hours/week | Notes |
|-------|------------|--------|
| DSA (InterviewBit) | 7–8 | ~9–10 problems/week average |
| Embedded 120 | 6–7 | code 4–5 + verbal/design 2–3 |
| Projects | 4–5 | ship weekly milestones |
| Mocks / revision | 1–2 | from week 6 onward |
| **Total** | **~18–22** | sustainable with full-time job |

**Daily template (weekday):** 60–75 min DSA · 45–60 min embedded · 30–45 min project  
**Weekend:** 3–4 hr project deep work + 1 mock or design whiteboard  

---

## InterviewBit 150 — topic quota (exact split)

Use InterviewBit topic lists; pick **standard + a few hard** per topic. Track in a sheet: `ID | Topic | Problem | Time | Notes`.

| # | Topic | Count | Weeks (primary) |
|---|-------|------:|-----------------|
| 1 | Arrays | 20 | W1–W2 |
| 2 | Math / Number theory basics | 8 | W2 |
| 3 | Binary Search | 12 | W3 |
| 4 | Strings | 12 | W3–W4 |
| 5 | Bit Manipulation | 10 | W4 |
| 6 | Two Pointers | 10 | W5 |
| 7 | Linked Lists | 12 | W5–W6 |
| 8 | Stacks & Queues | 10 | W6 |
| 9 | Hashing | 12 | W7 |
| 10 | Heaps & Maps | 8 | W8 |
| 11 | Trees / BST | 14 | W8–W9 |
| 12 | Greedy | 6 | W10 |
| 13 | Backtracking | 6 | W10 |
| 14 | Dynamic Programming | 14 | W11–W12 |
| 15 | Graphs | 10 | W13 |
| 16 | Buffer / mixed revision set | 6 | W14–W16 |
| | **Total** | **150** | |

**DSA rules:**
- First attempt **timed** (20–30 min Medium)
- If stuck >25 min: read approach, **re-code from scratch next day**
- Maintain pattern notes (not full solutions copy-paste)
- Language: **C++** (or C++ for DSA, C for embedded)

---

## Projects — ship plan (parallel)

| Project | Repo (suggested) | Done means |
|---------|------------------|------------|
| **P1** Linux multi-channel encoder/position platform driver | `am64-linux-encoder-driver` | DT + IRQ + sysfs + userspace + README + demo |
| **P2** Buildroot/Yocto BSP packaging P1 + systemd daemon | `am64-encoder-bsp` | bootable image notes + service + recipe |
| **P3** Linux RT I/O path (SocketCAN or RPMsg) + p50/p99 | `linux-rt-can-position-gateway` | bench scripts + results checked in |

**Hardware:** Pi 4 and/or AM64x SK/EVM (whichever you have). QEMU OK for early P1 stubs.

---

## Month-by-month overview

| Month | Theme | Embedded | DSA | Project |
|-------|-------|----------|-----|---------|
| **M1** (W1–4) | Foundations | Q001–Q036 + verbal Q071–Q076 | 50 IB | P1 skeleton → IRQ working |
| **M2** (W5–8) | Drivers + concurrency | Q037–Q060 + Q077–Q085 | 50 IB | P1 complete + public GitHub |
| **M3** (W9–12) | RT + Linux + design start | Q061–Q100 + designs Q101–Q108 | 40 IB | P2 BSP + daemon |
| **M4** (W13–16) | Design polish + mocks | Q109–Q120 + weak-area redo | 10 IB + revision to 150 | P3 RT metrics + resume/LinkedIn |

---

# 16-week plan (concrete)

## WEEK 1 — Kickoff + arrays + C primitives
**DSA (IB):** 10 Arrays  
**Embedded:** Q001–Q006, Q016 (memcpy/memmove, bits start, ring start)  
**Verbal:** Q071, Q072  
**Project:** Create P1 repo; hello platform module / char stub; README architecture  
**Exit:** Ring buffer sketch compiles; 10 IB done  

## WEEK 2 — Arrays finish + memory pools
**DSA:** 10 Arrays + 5 Math (15 total week if catching pace; target **12** if heavy job week — stay on cumulative plan)  
*Target cumulative DSA end W2: ~22*  
**Embedded:** Q007–Q015, Q029–Q031  
**Verbal:** Q082, Q083  
**Project:** Device Tree overlay stub; sysfs hello  
**Exit:** Pool allocator coded once  

## WEEK 3 — Binary search + strings start + rings
**DSA:** 12 Binary Search (+ start Strings if ahead)  
**Embedded:** Q017–Q022  
**Verbal:** Q073, Q074  
**Project:** GPIO/IRQ or virtual IRQ path into ring  
**Exit:** ISR-safe ring explained aloud  

## WEEK 4 — Strings + bits + allocators
**DSA:** Strings + Bit Manipulation toward **cumulative ~50 by end M1** (spread W1–W4 to hit 50)  
**Suggested W4 DSA count:** ~12–13 to land **50 total**  
**Embedded:** Q023–Q028, Q032–Q036  
**Verbal:** Q075, Q076  
**Design lite:** Q102 outline (no full whiteboard yet)  
**Project:** Userspace `poll`/`read` demo reading positions  
**M1 checkpoint:** DSA 50 · Embedded ~Q001–Q036 solid · P1 half-done  

---

## WEEK 5 — Two pointers + LL start + concurrency code
**DSA:** Two Pointers 10 + Linked List 2–3  
**Embedded:** Q037–Q042  
**Verbal:** Q077, Q078  
**Project:** Multi-channel semantics + error counters in sysfs  
**Mock:** 45 min — ring + verbal volatile/ISR  

## WEEK 6 — Linked lists + stacks/queues + UART driver
**DSA:** Finish Linked Lists + Stacks/Queues toward cumulative ~75–80  
**Embedded:** Q043–Q050 (UART IRQ/DMA)  
**Verbal:** Q079, Q080  
**Project:** Latency script IRQ→userspace; publish v0.1 release notes  
**Mock:** UART IRQ driver timed  

## WEEK 7 — Hashing + I2C/SPI
**DSA:** Hashing 12  
**Embedded:** Q051–Q058  
**Verbal:** Q086, Q087, Q090  
**Project:** Polish P1 README + architecture diagram; record 2-min demo  
**Exit:** P1 **feature-complete** on Pi or AM64x  

## WEEK 8 — Heaps + trees start + mid-point
**DSA:** Heaps 8 + Trees start → **cumulative 100** by end W8  
**Embedded:** Q059–Q060; redo weak coding from Q001–Q050  
**Verbal:** Q088, Q089, Q091, Q092  
**Design:** Q101, Q105 (whiteboard aloud)  
**Project:** Start P2 Buildroot/Yocto package of P1  
**M2 checkpoint:** DSA 100 · Drivers Q046–Q060 done · **P1 on GitHub** · 2 mocks done  

---

## WEEK 9 — Trees + software timers
**DSA:** Trees/BST continue (aim ~8–10)  
**Embedded:** Q061–Q065  
**Verbal:** Q081, Q093–Q095 (Linux)  
**Design:** Q104, Q113  
**Project:** P2 image boots with driver loaded  

## WEEK 10 — Greedy/backtracking + FSM/reliability
**DSA:** Greedy 6 + Backtracking 6  
**Embedded:** Q066–Q070  
**Verbal:** Q096–Q098  
**Design:** Q103, Q108, Q109  
**Project:** systemd `encoderd` + health logs  
**Mock:** Tesla-style 90 min (FSM + ring + endian dump)  

## WEEK 11 — DP start + verbal finish
**DSA:** DP 7  
**Embedded:** Finish any remaining ≤Q070; **Q071–Q085** deep revision  
**Design:** Q106, Q107, Q110  
**Project:** P2 docs + flash instructions; tag `bsp-v0.1`  

## WEEK 12 — DP finish + designs
**DSA:** DP 7 → **cumulative ~140** (leave 10 for later)  
**Embedded:** Q086–Q100 verbal mastery (flashcards)  
**Design:** Q111, Q112, Q114  
**Project:** Start P3 CAN/RPMsg path skeleton  
**M3 checkpoint:** Embedded coding+verbal mostly done · P2 shipped · DSA ~140 · 4+ mocks  

---

## WEEK 13 — Graphs + gateway design + P3
**DSA:** Graphs 10  
**Embedded:** Q115, Q116 + redo Tier S coding under timer  
**Project:** P3 send/receive + SCHED_FIFO path  
**Mock:** Full loop — 1 DSA Medium + 1 embedded coding + 1 design  

## WEEK 14 — Hit 150 DSA + OTA/power designs
**DSA:** Remaining to **150** + mixed revision 3–6  
**Embedded:** Q117–Q120  
**Project:** P3 p50/p99 measurements checked into repo  
**Applications:** Soft applications / referral outreach starts  

## WEEK 15 — Weak-area bootcamp
**DSA:** Redo slowest 20 IB problems timed  
**Embedded:** Redo weakest 20 of FINAL_120  
**Design:** All Q101–Q120 one-page outlines  
**Project:** Polish all 3 READMEs; pin on GitHub profile  
**Mock:** 2 full company-specific (e.g. Google + Tesla)  

## WEEK 16 — Interview mode
**DSA:** Light — 1/day easy-medium keep warm  
**Embedded:** Day-before set from `day_before_interview_revision.md` + Tier S  
**Behavioral:** 6 STAR stories (TI bugs, HDSL scale, FPGA→PRU, customer bring-up, workshop, conflict)  
**Project:** Freeze repos; add resume bullets  
**Mocks:** 2 finals  
**Exit criteria check** (see top of file)

---

## Embedded 120 — week mapping (quick index)

| Weeks | Questions |
|-------|-----------|
| W1–W2 | Q001–Q015, Q016, Q029–Q031, Q071–Q072, Q082–Q083 |
| W3–W4 | Q017–Q028, Q032–Q036, Q073–Q076 |
| W5–W6 | Q037–Q050, Q077–Q080 |
| W7–W8 | Q051–Q060, Q086–Q092; redesign Q101/Q105 |
| W9–W10 | Q061–Q070, Q081, Q093–Q098, Q103–Q104, Q108–Q109, Q113 |
| W11–W12 | Q086–Q100 mastery, Q106–Q107, Q110–Q112, Q114 |
| W13–W14 | Q115–Q120 + Tier S redo |
| W15–W16 | Weakest 20 + full designs |

---

## Milestone calendar (copy to Notion/Google Sheet)

| Gate | When | Pass criteria |
|------|------|---------------|
| M1 gate | End W4 | 50 IB · Q001–Q036 coded once · P1 IRQ path works |
| M2 gate | End W8 | 100 IB · P1 public · UART+I2C+ring solid · 2 mocks |
| M3 gate | End W12 | ~140 IB · Q001–Q100 mostly `[x]` · P2 shipped · 4 mocks |
| M4 gate | End W16 | 150 IB · ≥100/120 embedded `[x]` · P3 metrics · 6 mocks · resume updated |

---

## Mock schedule

| Week | Mock |
|------|------|
| 5 | 45 min embedded coding |
| 6 | UART driver timed |
| 8 | Mid: DSA + embedded |
| 10 | Tesla-style 90 min |
| 13 | Full 3-part loop |
| 15 | Google-style + Tesla-style |
| 16 | 2 finals |

---

## Resume bullets to unlock by month 4 (from projects)

```text
• Linux platform driver (DT/IRQ/sysfs) for multi-channel position I/O with userspace poll/read API
• Custom Buildroot/Yocto integration packaging out-of-tree driver + systemd monitoring daemon
• Real-time Linux data path (SocketCAN/RPMsg) with p50/p99 latency characterization under load
```

---

## Risk controls (don’t derail)

| Risk | Mitigation |
|------|------------|
| DSA eats embedded time | Hard cap: DSA ≤ 8 hr/week until M3 |
| Project perfectionism | P1 must ship end W7; polish later |
| Skipping verbal | Fri = verbal-only 45 min |
| Burnout | One full rest day/week; cut project not sleep |
| Job spikes | Use “minimum viable week”: 5 IB + 3 embedded + 1 project commit |

### Minimum viable week (busy at TI)
1. 5 InterviewBit problems  
2. 3 FINAL_120 items (at least 1 coding)  
3. 1 project commit  
4. 1 STAR story polish  

---

## Tracking template

```text
Week #:
DSA done this week: __ / cumulative: __ /150
Embedded [x] this week: __ / cumulative: __ /120
Project commits: __
Mock: Y/N
Blockers:
Next week focus:
```

---

## Order of priority if you fall behind

1. **Tier S embedded (30)**  
2. **InterviewBit Arrays + BS + LL + Trees + DP + Graphs** (core ~80)  
3. **P1 driver only**  
4. Then remaining embedded verbal/design  
5. P2/P3  

---

**Bottom line:** This plan is enough **if you hit the gates**. The syllabus is FINAL_120 + 150 IB + shipped Linux proof — not passive reading. Start Week 1 with Arrays + Q001/Q016/Q071 + P1 repo today.
