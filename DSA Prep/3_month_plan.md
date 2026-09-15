# 3-Month DSA Plan — Hard topics first

**Order you asked for:** Binary search → Recursion / backtracking → Trees → Graphs → DP.

Arrays, sliding window, linked list, and stack are **not** month 1. They are a **short catch-up in Week 12** plus whatever you already know from work. Google still asks them; they just come *after* the topics that take longest to learn.

**Goal:** In 35–45 minutes: name the pattern, code it, explain complexity.

**Sources**

- Binary search: [notes](./binary%20search/README.md) + [CHEATSHEET.md](./binary%20search/CHEATSHEET.md) — do **not** rewatch all 28 videos
- Playlist: [A2Z_playlist_topic_list.md](./A2Z_playlist_topic_list.md)
- Backtracking / heaps / bits / strings: [A2Z sheet](https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/) (those videos are mostly *not* in the A2Z playlist)

**Time (DSA):** ~10–12 h/week. Watch 1.5–2×, skip duplicate C++/Java, **then solve**.

**Language:** Learn in Python if faster. **Sunday timed sets and mocks in C++** — Google embedded coding is usually C++.

---

## Is this plan right for Google embedded?

**Yes, as the DSA half** — if firmware prep stays on a **separate** track. Google embedded loops are typically:

- **2 coding interviews** that look like SWE DSA (trees, graphs, DP, binary search on answer, sometimes arrays/LL)
- **1+ embedded / systems** (memory, concurrency, interrupts, drivers, bits, C)

Your hard-topic order matches the **coding** bar. It is a weak plan if it is your *only* prep, or if you delay **arrays + bits** until week 12 and then get a phone screen in month 1.

**Keep this plan, with three Google-embedded rules:**

1. **Embedded questions stay outside these 12 weeks’ DSA hours.** Target ~6–8 h/week on your existing embedded set (rings, MMIO, ISR, memory, C). Do not steal that time to finish extra DP videos.
2. **Every week, 2 “screen” problems** (30–40 min total): one **array/hash/two-pointer**, one **bit / simple C array**. Phone screens love these even when onsites are graphs.
3. **Timed practice in C++**, not only Python.

With that, the order BS → recursion → trees → graphs → DP is the right 3-month DSA spine for Google. Week 12 is polish, not the first time you see two-sum.

**Do not add** more graph theory (SCC, Tarjan) or partition DP until mocks are already passing. Embedded depth beats those.

---

## At a glance

| Weeks | Focus |
|---|---|
| 1–2 | Binary search (all 3 families) |
| 3 | Recursion + backtracking |
| 4–5 | Binary trees + BST |
| 6–8 | Graphs |
| 9–11 | DP |
| 12 | Linear catch-up (arrays / window / LL / stack) + mocks |

---

## Weekly rhythm

| Day | What |
|---|---|
| Mon–Thu | 1 pattern + 2 problems (brute → optimal, then code) |
| Fri | 2 problems from **this** week + **1 screen problem** (array/hash **or** bits) |
| Sat | 3 mixed (include 1 from ≥2 weeks ago) + **1 bit/array screen** |
| Sun | **2 problems in 90 minutes, in C++**, then review |

After each problem, one line: **pattern + invariant**.

**Screen pool (rotate, 2/week, all 12 weeks):** two sum, Kadane, move zeros, merge intervals, 3-sum, longest substring no repeat, reverse linked list, detect cycle, valid parentheses, XOR single-number, count set bits, power of two, reverse bits, subarrays with given XOR. You already have several of these in `Embedded Interview questions/DSA/`.

---

## Month 1 — Binary search, recursion, trees (Weeks 1–4)

### Week 1 — Binary search on indices (families A)

You already have full notes. Code from the **cheatsheet**, not by copying solutions.

**Learn:** exact search, lower/upper bound, first/last, rotated I/II, min/rotation count, single element, 1D peak.

**Solve (12):** BS-1 to BS-9 + search insert + floor/ceil + count occurrences. One C++ recode: rotated search.

**Exit:** `low <= high` vs bound-search; identify the sorted half in a rotation.

### Week 2 — Binary search on the answer + 2D (families B, C)

**Learn:** sqrt, nth root, Koko, bouquets, ship, kth missing, cows, books/split array, 2D search I/II, median of two arrays, peak II (stretch).

**Solve (12):** at least Koko, ship, cows, books, kth missing, 2D I, median of two arrays. Cheatsheet families B and C until `can(x)` is automatic.

**Exit:** given “minimize the maximum”, you write `can(mid)` without a similar problem open.

### Week 3 — Recursion + backtracking

This is the DFS engine for trees, graphs, and DP.

**Watch:** Re 1–5 (playlist). Sheet: print all subsequences, combination sum I/II, subsets, subset sum, palindrome partition, N-Queens **or** sudoku (pick one hard).

**Solve (12):** factorial/print 1..n style, reverse array via recursion, subsequences, combination sum, subsets, N-Queens, word search (grid DFS), generate parentheses.

**Exit:** base case, choose/not-choose, undo on backtrack. You never lose track of “what is in the path.”

### Week 4 — Binary trees (traversals → medium)

**Watch:** L1–L8, L14–L18, L24, L26–L27 (skip L2/L3 language clones).

**Solve (12):** pre/in/post recursive + iterative inorder, level order, height, balanced, diameter, max path sum, identical, right view, root-to-node path, LCA.

**Exit:** DFS that **returns extra state** (height, max path).

**Month 1 checkpoint:** 1 BS-on-answer + 1 backtracking + 1 tree DFS in 90 minutes.

---

## Month 2 — Trees finish, then graphs (Weeks 5–8)

### Week 5 — Trees hard + BST

**Watch:** L19–L21, L34–L36, L38. BST L39–L47, L51.

**Solve (12):** zig-zag, vertical or top/bottom view, construct from in+pre, serialize/deserialize, flatten (stretch), search/insert BST, ceil/floor, validate BST, kth in BST, LCA in BST, two-sum BST.

**Exit:** inorder of a BST is sorted; construct tree from two traversals.

### Week 6 — Graphs I — BFS / DFS / matrix

**Watch:** G-1 to G-18 (skip G-2/G-3 language clone).

**Solve (12):** graph representation, BFS, DFS, provinces, islands, flood fill, rotten oranges, 0/1 nearest, surrounded regions, cycle undirected (BFS or DFS), bipartite, distinct islands (stretch).

**Exit:** visited[], queue vs recursion, “multi-source BFS.”

### Week 7 — Graphs II — directed, topo, shortest

**Watch:** G-19 to G-38 (skip Word Ladder II if behind).

**Solve (12):** cycle directed, topo DFS, Kahn, course schedule, alien dictionary, DAG shortest path, unit-weight shortest, word ladder I, Dijkstra (array or grid), binary maze / min effort.

**Exit:** indegree + queue; Dijkstra vs BFS (when weights are 1).

### Week 8 — Graphs III — DSU + light greedy

**Watch:** G-44–G-50. Optional G-54. Greedy only if time: jump I/II, N meetings.

**Solve (10):** MST idea (Prim or Kruskal — one is enough), DSU template, number of provinces (DSU), network connected, accounts merge, islands II **or** stones. Jump game I.

**Skip:** Bellman, Floyd, Tarjan, articulation, Word Ladder II.

**Exit:** “BFS vs Dijkstra vs Union-Find” in one sentence each.

**Month 2 checkpoint:** islands + course schedule + Dijkstra on a grid, no notes.

---

## Month 3 — DP, then linear catch-up + mocks (Weeks 9–12)

### Week 9 — DP 1D and grids

**Watch:** DP 1–13 (stock I can wait).

**Solve (12):** climb stairs, frog jump ± K, house robber I/II, ninja training, unique paths I/II, min path sum, triangle, falling path sum. Cherry pickup II only if ahead.

**Exit:** memo → tabulation → rolling array for 1D.

### Week 10 — DP knapsack / subset / coins

**Watch:** DP 14–24.

**Solve (12):** subset sum, partition equal, min subset difference, count subsets, 0/1 knapsack, unbounded knapsack, coin change (min coins + combinations), target sum, rod cutting.

**Exit:** 0/1 vs unbounded (loop order).

### Week 11 — DP strings, LIS, stocks

**Watch:** DP 25–34, 36–40, 41–43. Skip DP 48–56 unless extra.

**Solve (12):** LCS, longest common substring, palindromic subsequence, edit distance, wildcard (stretch), LIS (DP + n log n idea), stock I/II, stock with cooldown **or** fee (one).

**Exit:** string DP `dp[i][j]`; LIS as “patience / tails” or classic DP.

### Week 12 — Linear catch-up + mocks

Google still asks these. One week, high yield only.

**Arrays / hash (1–2 days):** two sum, Kadane, stock I (already), 3 sum, merge intervals, set matrix zero.

**Window (1 day):** longest substring no repeat, min window, max consecutive 1s III.

**Linked list (1 day):** reverse, cycle start, intersection, middle, palindrome.

**Stack (1 day):** valid parentheses, NGE, trapping rain water **or** histogram.

**Then:** 4–6 timed mocks (2 questions, 45 min, no notes). Redo the fail list from weeks 1–11.

**Month 3 checkpoint:** 2 unseen mediums in 45 minutes, including at least one of {graph, DP, tree, BS-on-answer}.

---

## Revision (all 12 weeks)

- Fail list only (~40 problems).
- Saturday: 2 problems from ≥14 days ago (always mix **this month’s hard topic**).
- After Week 2: 15 min BS cheatsheet (families A/B/C).
- After Week 8: 1 graph every weekend until the interview.
- After Week 11: 1 DP every weekend until the interview.

---

## If a week slips (cut in this order)

1. DP 48–56 (MCM, balloons, rectangles)  
2. Graph G-41–G-56 extras (Floyd, SCC, bridges)  
3. Tree Morris / burn / complete-tree count  
4. Greedy playlist  
5. Word ladder II, LFU, cherry pickup II  

**Never cut:** BS-on-answer, backtracking template, tree LCA/path-sum, graph BFS/DFS/topo/Dijkstra, house robber, knapsack, LCS.

**Do not skip Week 12 linear catch-up** unless your mocks already include two-sum, window, and reverse-LL — those still show up in Google screens.

---

## Parallel: embedded (do not merge into DSA days)

| Track | Hours/week | Content |
|---|---|---|
| DSA (this file) | 10–12 | BS, recursion, trees, graphs, DP + 2 screen problems |
| Embedded | 6–8 | Your planned firmware set: C, bits in registers, rings, ISR vs task, memory, concurrency, one driver story |

If the week is too full, **cut a DP/graph video**, not the embedded block and not the 2 screen problems.

Total ~16–20 h/week for 12 weeks is enough for a Google embedded loop if both tracks stay honest. More hours should go to **mocks + C++**, not more playlists.

---

## 12-week numbers

| | Target |
|---|---|
| New problems | ~130 |
| Fail-list | ~40 |
| Sunday 90-min sets | 12 |
| C++ recodes | ≥20 |
| Full mocks | ≥6 in Week 12 (start two in Week 11 if possible) |

Binary search, recursion, trees, graphs, and DP get **11 of 12 weeks**. Linear DSA gets a compressed Week 12 so the important topics are not delayed.
