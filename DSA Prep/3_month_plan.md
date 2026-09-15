# 12-Week Plan — DSA + Embedded (Google L4 firmware)

Two tracks, every week. Do not blend them into one sitting.

| Track | Source | Hours/week |
|---|---|---|
| **DSA** | [binary search](./binary%20search/README.md) + [A2Z list](./A2Z_playlist_topic_list.md) | 10–12 |
| **Embedded** | [FINAL 120 merged](https://github.com/ue153081/Embedded-Interview-Preparation/tree/f8840c93ac30681a67de512e3f1ff3f6323a2bc9/Embedded%20Interview%20questions/solutions/FINAL_120_MERGED) (M001–M044) | 6–8 |

**DSA order:** Binary search → recursion/backtracking → trees → graphs → DP.  
**Embedded order:** C bytes/bits → rings/concurrency → drivers → timers/reliability → verbal → design.

**Language:** DSA notes in Python; **all timed work and all embedded coding in C/C++**.

**Embedded “done”:** close the solution file and **re-implement from memory** (compile on host). Reading M006 is not prep. Variants listed in each M-file are follow-ups — be able to speak them.

---

## Weekly rhythm

| | DSA | Embedded |
|---|---|---|
| Mon–Tue | Pattern + 2 problems | 1 coding topic: read 20 min, **code 90 min** |
| Wed–Thu | Pattern + 2 problems | Finish that topic + 1 sub-variant |
| Fri | 2 DSA from this week + **1 array/hash screen** | Recode yesterday’s API from blank file (30–45 min) |
| Sat | 3 mixed DSA (1 old) + **1 bit/array screen** | Verbal **or** design: 45 min out-loud (from Week 6) |
| Sun | **90 min timed, C++** (2 DSA) *or* **60 min timed C** (1 embedded API) — alternate | Review fail list |

If the week is too full: cut a graph/DP video, **not** the embedded recode and **not** the 2 DSA screen problems.

---

## At a glance

| Week | DSA | Embedded (FINAL 120 merged) |
|---:|---|---|
| 1 | BS index search (A) | M001 memcpy/memmove · M004 bits |
| 2 | BS on answer + 2D (B, C) | M003 endian/wire · M002 atoi · M023 macros |
| 3 | Recursion + backtracking | **M006 ring/SPSC** (start) · M005 CRC |
| 4 | Trees medium | **M006** finish · M011 MMIO/poll |
| 5 | Trees hard + BST | M010 atomics/order · M007 IPC/mailbox |
| 6 | Graphs BFS/DFS | M008 allocators · M009 locks/sem |
| 7 | Graphs topo + shortest | M012 UART stack · M013 SPI |
| 8 | Graphs DSU | M014 I2C · M015 GPIO/PWM/ADC |
| 9 | DP 1D + grid | M018 software timers · M016 watchdog |
| 10 | DP knapsack | M017 parser · M020 FSM · M019 reliability |
| 11 | DP strings/LIS | M021 filter · M022 tests · verbal M026–M029 |
| 12 | Linear DSA + mocks | Verbal M030–M036 · design M039–M044 · **M045 mock** |

---

## Month 1

### Week 1

**DSA:** BS-1 to BS-9 from the [cheatsheet](./binary%20search/CHEATSHEET.md) (exact, bounds, rotated, peak, single). ~12 problems. C++ recode: rotated search.

**Embedded**

- **M001** — `memcpy` / `memmove` / `memset` / secure wipe. Code overlap-safe memmove; explain compiler-elided memset.
- **M004** — popcount, reverse bits, pow2, floor_log2. This *is* your bit screen for the week (skip a duplicate DSA bit problem).

**Exit:** memmove direction; `n & (n-1)` for pow2.

### Week 2

**DSA:** Koko, ship, cows, books/split array, kth missing, 2D matrix I, median of two arrays. Invent `can(x)`.

**Embedded**

- **M003** — LE/BE helpers, packed wire struct, padding.
- **M002** — safe atoi (overflow, sign, junk).
- **M023** — container_of / intrusive list macros (read + small example).

**Exit:** you can unpack a little-endian frame without `#pragma pack` as the only trick.

### Week 3

**DSA:** Recursion Re 1–5; subsequences, combination sum, subsets, N-Queens or sudoku, generate parentheses.

**Embedded — highest-value coding week**

- **M006** start — spare-slot ring, pow2 mask, ISR producer / task consumer. Compile `push`/`pop`/`count`.
- **M005** — CRC-8 (bitwise); mention table-driven.

**Exit:** empty vs full; why one spare slot **or** an explicit count, never mixed.

### Week 4

**DSA:** Tree traversals, height, balanced, diameter, max path sum, right view, LCA.

**Embedded**

- **M006** finish — overwrite policy, lock-free SPSC acquire/release, `push_n`/`pop_n` / contiguous DMA view.
- **M011** — `read32`/`write32`/`rmw`, poll-with-timeout, `volatile` limits.

**Month 1 checkpoint**

- DSA: 1 BS-on-answer + 1 backtracking + 1 tree in 90 min (C++).
- Embedded: blank-file SPSC ring + MMIO poll in 60 min (C).

---

## Month 2

### Week 5

**DSA:** Construct tree, serialize, BST validate/kth/LCA/two-sum.

**Embedded**

- **M010** — atomic counters, ABA sketch, acquire/release flag, false sharing pad.
- **M007** — mailbox / doorbell / seqlock *or* ISR→task flag (pick one full implementation + talk the rest).

**Sat verbal (start):** **M027** ISR rules (no malloc, no printf, defer work) — 20 min out loud.

**Exit:** you can say which fields an ISR may touch.

### Week 6

**DSA:** Graph BFS/DFS, islands, rotten oranges, cycle undirected, bipartite.

**Embedded**

- **M008** — O(1) pool + ISR-safe variant; *sketch* first-fit free list (do not boil the ocean on buddy).
- **M009** — spinlock + counting semaphore give-from-ISR.

**Sat verbal:** **M026** volatile vs atomic vs barrier.

**Exit:** pool vs heap; why malloc in ISR is wrong.

### Week 7

**DSA:** Directed cycle, topo, course schedule, Dijkstra, grid shortest path.

**Embedded**

- **M012** — UART poll → IRQ + rings. DMA as follow-up verbally if short on time.
- **M013** — SPI blocking transfer + CS; IRQ/DMA as follow-up.

**Sat verbal:** **M033** I2C vs SPI vs UART (addressing, CS, start/stop).

**Exit:** one coherent UART RX path: ISR → ring → task.

### Week 8

**DSA:** DSU, network connected, jump game.

**Embedded**

- **M014** — I2C write/read/repeated start + stuck-bus recovery story.
- **M015** — debounce **or** PWM/ADC wrapper (one coded, others verbal).

**Sat verbal:** **M028** mutex vs spinlock vs semaphore vs lock-free.

**Month 2 checkpoint**

- DSA: islands + course schedule + Dijkstra grid.
- Embedded: UART IRQ + pool alloc + “what can run in ISR?”

---

## Month 3

### Week 9

**DSA:** Climb stairs, frog, house robber, unique paths, min path sum.

**Embedded**

- **M018** — tick + software timers (list or wheel at a high level; code a simple sorted list wheel).
- **M016** — watchdog pet + deadline monitor.

**Sat verbal:** **M029** DMA + cache maintenance (clean/invalidate, when).

**Exit:** who pets the watchdog; timer in ISR vs task.

### Week 10

**DSA:** Subset sum, knapsack, coin change, unbounded vs 0/1.

**Embedded**

- **M017** — frame + length + CRC parser (state machine).
- **M020** — classic FSM table.
- **M019** — backoff + fault FSM (can be the same code as M020 with extra states).

**Sat verbal:** **M032** how you would debug a heisenbug / ISR-only fail.

**Exit:** parser that does not block in ISR.

### Week 11

**DSA:** LCS, edit distance, LIS, stock I/II.

**Embedded**

- **M021** — EWMA (tiny).
- **M022** — host test fakes for ring or parser.
- **Verbal block:** M026–M029 recap; add **M030** (linker: .text/.data/.bss/stack/heap), **M031** (boot, MPU vs MMU, TrustZone at “what problem it solves” depth).

**Sat design (45 min whiteboard):** **M040** ISR → ring → task → DMA pipeline. Numbers: ISR budget, ring size, backlog.

**Exit:** one end-to-end data-path story with numbers.

### Week 12 — Mocks (both tracks)

**DSA linear catch-up (2–3 days, not the whole week):** two sum, Kadane, 3 sum, merge intervals, longest substring, reverse LL, cycle, NGE or rain water.

**Embedded**

- **M034** Linux platform driver / probe (verbal; enough for Android-adjacent L4, not a kernel maintainer interview).
- **M035** security/safety (TOCTOU, stack canary, MPU regions) — verbal.
- **M036** RT validation (rate monotonic intuition, priority inversion / inversion dodge).
- **Design:** M039 driver stack, M041 timers/logging/watchdog platform, M042 boot/OTA/power, M043 dual-core or gateway (pick the one closest to your resume), M044 bring-up/test.
- **M045** — full mock day: 45 min C coding (ring **or** UART **or** parser) + 45 min design (M040 or M043) + 30 min verbal (ISR + memory order).

**DSA mocks:** ≥4 sets of 2 problems / 45 min in C++.

---

## Combined checkpoints

| When | You should be able to |
|---|---|
| End week 4 | SPSC ring + MMIO poll from blank file; BS `can(x)` + tree DFS |
| End week 8 | UART IRQ path + allocator story; graph BFS + Dijkstra |
| End week 11 | Timer/watchdog + parser FSM; DP knapsack + LCS |
| End week 12 | Two mixed DSA in 45 min; one embedded C API in 45 min; one design with numbers |

---

## Are the two lists enough for Google L4?

**They are a strong, hire-shaped syllabus. They are not a guarantee of L4, and they are not complete by themselves.**

### What is enough

| Loop piece | These two lists |
|---|---|
| Firmware **coding** (C, rings, bits, MMIO, UART, pools, FSM) | **Yes** — M001–M023 is as complete as most candidates ever get |
| Firmware **verbal** (ISR, atomics, DMA/cache, layout) | **Yes** — M026–M036 if you can teach them, not recite them |
| Firmware **design** (data path, boot/OTA, dual-core) | **Good baseline** — M039–M044 |
| **DSA coding** for Google | **Yes for patterns** if you *solve* the 12-week set (BS, trees, graphs, DP) — not if you only read notes |

Google L4 embedded is usually: **2× DSA-style coding** + **embedded/systems** + **Googley / resume**. Your DSA plan + FINAL 120 merged maps onto the first two.

### What is *not* in either list (L4 still asks this)

1. **Depth under pressure** — L4 is “I’ve shipped this and I know the failure mode,” not “I memorized M006.” Interviewers twist the ring (overwrite vs drop, DMA wrap, 64-bit indexes).
2. **Resume project** — 10 min architecture of *your* firmware with numbers (CPU, latency, RAM, what broke in production). Neither list replaces that.
3. **Linux/Android kernel** — if the req is kernel/driver (GKI, device tree, kthread, sleep vs atomic context), M034 is only a trailer. Add one real driver read-through.
4. **OS theory they still use** — scheduling / priority inversion / priority inheritance, page tables vs MPU, cache associativity. M029–M031 are sketches.
5. **C++ for DSA onsites** — list is Python-first; L4 coding is C++. Timed C++ is mandatory.
6. **Behavioral / leadership** — L4 is not L3+. Expect “disagreement, impact, debugging a cross-team failure.”
7. **Unseen DSA** — A2Z subset + BS-1–27 covers patterns; Google will still give a problem you have not seen. Transfer (templates) matters more than covering DP 48–56.
8. **The 300 firmware coding-round bank** on the other branch — optional extra reps, not required if M001–M023 are *coded* cold.

### L4 bar vs L3

| | L3 | L4 (your target) |
|---|---|---|
| Ring buffer | Works | ISR-safe, policy, memory order, test, DMA wrap |
| Design | Block diagram | Numbers, failure, backpressure, what you cut |
| DSA | Medium, hints OK | Medium-hard, little hints, clean C++ |

The **lists** get you to the door. **Cold recodes + mocks + your project story** are what L4 scores.

### Practical verdict

- **Do both lists on this 12-week calendar** → you are **competitive for Google L4 embedded coding + firmware** if execution is honest (compile, timed, out-loud).
- **Lists alone, read-only** → not enough for L4.
- **Add three non-list items:** (1) one resume deep-dive, (2) C++ DSA mocks, (3) if the role is Android/kernel, one real Linux driver.

You do **not** need to finish all 314 A2Z videos or all 300 extra firmware questions first.
