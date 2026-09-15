# 3-Month DSA Plan (Google-style rounds, embedded role)

**Goal:** Be able to pick a pattern, write a correct solution, and explain complexity in 35–45 minutes.

**Sources**

- Playlist index: [A2Z_playlist_topic_list.md](./A2Z_playlist_topic_list.md)
- Binary search notes + [CHEATSHEET.md](./binary%20search/CHEATSHEET.md)
- Sheet for extra topics not in the playlist: [Strivers A2Z sheet](https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/)

**Assumption:** ~12–15 focused hours/week (weekdays 1.5–2 h, weekend 4–5 h). If you have more time, add problems — do not add more videos.

**Language:** Keep notes/solutions in **Python**. Once a week, recode 2 problems in **C++** (Google embedded often uses C++).

Do **not** try to finish all 314 videos. Watch 1.5–2×, skip dry C++/Java duplicates, then **solve**.

---

## Weekly rhythm

| Day | What |
|---|---|
| Mon–Thu | 1 pattern video + 2 problems (brute → optimal on paper, then code) |
| Fri | Weak-topic drill: 3 problems from this week, no video |
| Sat | 4–5 problems mixed (include 1 from 2 weeks ago) |
| Sun | 1 timed set: **2 problems in 90 minutes**, then review mistakes |

After every problem write one line: **pattern + invariant** (example: “BS on answer, `can(mid)` = hours ≤ h”).

---

## What “done” means for a topic

- You can solve a **new** problem of that pattern without opening notes.
- You can state time/space and why the loop/recurrence is correct.
- You have 8–12 **marked** problems (the ones you failed first time) for revision.

---

## Month 1 — Arrays, search, window (Weeks 1–4)

Foundation Google screens live here. Binary search is already written in this repo — use notes, do not rewatch all 28 videos.

### Week 1 — Setup, hashing, sorting, array easy

**Watch:** complexity, STL *or* Python collections, hashing, sorting (selection/merge/quick at high level), array intro videos (second largest → max consecutive 1s).

**Solve (10–12):** second largest, remove duplicates, rotate array, move zeros, missing number, appear-once (XOR), max consecutive 1s, union/intersection of sorted arrays, two sum (hash), valid anagram / frequency map.

**Exit:** O(n) vs O(n log n) vs O(n²) is automatic; hash map vs sort tradeoff.

### Week 2 — Array medium

**Watch:** 2 sum variants, sort 0/1/2, majority (Moore), Kadane, stock I, rearrange by sign, next permutation, leaders, longest consecutive, matrix zero / rotate / spiral.

**Solve (12–14):** all of the above + Pascal nCr, majority II, merge intervals, merge two sorted arrays in-place.

**Exit:** Kadane, Dutch national flag, and “hash set for consecutive sequence” without notes.

### Week 3 — Array hard + start binary search

**Watch:** 3 sum, 4 sum, subarray XOR K, missing+repeating, inversions, reverse pairs, max product subarray. Then BS cheatsheet only.

**Solve (10):** 3 sum, subarray sum K, XOR K, reverse pairs *or* inversions (one merge-sort count is enough), max product. Then BS-1 to BS-9 from [binary search](./binary%20search/README.md) — code each from the cheatsheet, not from the solution file.

**Exit:** two pointers on a sorted array; lower/upper bound; rotated array search.

### Week 4 — Binary search on answer + 2D

**Watch:** skip BS-1–9 if Week 3 is solid. Skim BS-10–27 using the cheatsheet.

**Solve (12):** sqrt, koko, bouquets, ship packages, kth missing, aggressive cows, book allocation / split array, search 2D I & II, median of two sorted arrays, peak I.

**Must recode in C++:** koko + rotated search + 2D matrix.

**Exit:** you can invent `can(x)` for a “minimize the maximum” prompt.

**Month 1 checkpoint (end of Week 4):** 8 random array/BS problems in 3 hours, ≥5 fully correct.

---

## Month 2 — Linear DS, bits, trees (Weeks 5–8)

### Week 5 — Sliding window, two pointers, strings

**Watch:** SW L1 templates + L3, L4, L8, L12 (skip if time: L2, L7). Strings from the **A2Z sheet** (not this playlist): reverse, palindrome, atoi-style parse, longest palindrome, KMP only if extra time.

**Solve (12):** longest substring no repeat, max consecutive 1s III, fruit baskets, character replacement, min window substring, binary subarrays with sum, 3-sum (again), container-with-most-water or trapping rainwater (preview of stack), group anagrams, longest common prefix.

**Exit:** variable window “grow/shrink” template.

### Week 6 — Linked list + bit manipulation

**Watch:** LL L1–L17 (basics, reverse, middle, cycle, intersection, palindrome). Bits from sheet: set/unset/toggle, count bits, XOR of all, single number, subsets via bits *or* one power-of-two video.

**Solve (12):** reverse LL, reverse k-group (at least understand), detect/start of cycle, intersection, palindrome LL, add two numbers, copy random pointer (stretch), bits: single number, missing number XOR, count bits, power of two, subset generation.

**Exit:** Floyd cycle + reverse LL in sleep.

### Week 7 — Stack, queue, heaps

**Watch:** stack L1–L8, L12, L16, LRU. Heaps from sheet: heapify, kth largest, top-K frequent, merge K lists, median of stream (stretch).

**Solve (12):** valid parentheses, min stack, NGE, trapping rain water, largest rectangle in histogram, sliding window maximum, LRU, kth largest, top K frequent, k closest, merge K sorted lists.

**Exit:** monotonic stack “next greater”; heap for kth.

### Week 8 — Recursion / backtracking + binary trees start

**Watch:** Re 1–5. Sheet backtracking: subsequences, combination sum I/II, subset sum, palindrome partition, N-Queens (1–2 problems). Trees L1–L13 (traversals).

**Solve (12):** print subsequences, combination sum, subsets, N-Queens or sudoku (one is enough), recursive + iterative inorder/preorder/postorder, level order, height, balanced tree, diameter.

**Exit:** recursion tree + base case; BFS vs DFS on trees.

**Month 2 checkpoint:** 1 linked-list + 1 window + 1 tree + 1 stack in 2 hours.

---

## Month 3 — Trees, graphs, DP, mocks (Weeks 9–12)

### Week 9 — Trees medium/hard + BST

**Watch:** trees L14–L27, L34–L36 (construct, serialize). BST L39–L47, L51.

**Solve (12):** max path sum, LCA, views (right + vertical or zig-zag), symmetric, burn tree *or* nodes at distance K (one), construct from in+pre, validate BST, kth in BST, LCA in BST, BST iterator or two-sum BST.

**Exit:** “DFS returning extra info” (height/diameter/path sum).

### Week 10 — Graphs I (must for Google)

**Watch:** G-1 to G-26 (skip duplicate C++/Java). Focus BFS/DFS, islands, cycle, bipartite, topo, course schedule, alien dictionary.

**Solve (12):** number of islands/provinces, rotten oranges, flood fill, cycle undirected + directed, bipartite, topo sort, course schedule, word ladder I, clone graph if you know it.

**Exit:** adjacency list, BFS queue, DFS stack/recursion, indegree.

### Week 11 — Graphs II + greedy

**Watch:** Dijkstra G-32–G-38, DSU G-46–G-50 (skip G-54–56 unless extra). Greedy: jump I/II, meetings / non-overlap, fractional knapsack, platforms.

**Solve (10):** Dijkstra on a grid (binary maze or min effort), cheapest flights K stops (stretch), network connected / accounts merge (DSU), jump game, N meetings, min platforms.

**Skip unless extra:** Kosaraju, Tarjan bridges, articulation, Floyd–Warshall deep dive.

**Exit:** “when BFS vs Dijkstra vs Union-Find.”

### Week 12 — DP core + full revision

**Do not** finish DP 1–56. Cover patterns:

| Pattern | Problems |
|---|---|
| 1D | climb stairs, frog jump, house robber I/II |
| Grid | unique paths, min path sum, triangle |
| Knapsack / subset | subset sum, partition equal, 0/1 knapsack, coin change |
| Strings | LCS, edit distance (LIS via DP or binary search) |
| Stock | stock I (already) + II |

**Solve (10 DP + mixed mocks):** those patterns, then **3 mock interviews** (2 problems, 45 min each, no notes). Redo all marked fails from months 1–2.

**Skip for now:** MCM, burst balloons, boolean parenthesization, DP on rectangles — unless mocks are already green.

**Month 3 checkpoint:** 2 unseen mediums in 45 minutes, talk through invariants.

---

## Revision (do this the whole 12 weeks)

- **Anki/list of fails only** — not every solved problem.
- Every Saturday: 2 problems from **≥14 days ago**.
- After Week 4: 15 min cheatsheet recap (binary search families A/B/C).
- After Week 10: one graph + one DP every weekend forever until the interview.

---

## If time explodes (cut in this order)

1. Graph G-41–G-56 (Bellman, Floyd, MST extras, SCC)  
2. DP partition + rectangles (DP 48–56)  
3. Tree L29–L32, L37 Morris  
4. Maths sieve playlist  
5. LFU, word ladder II  

**Never cut:** arrays, hashing, BS-on-answer, sliding window, LL cycle/reverse, stack NGE, tree DFS, graph BFS/DFS/topo, house robber / knapsack / LCS.

---

## Parallel: embedded vs DSA

This plan is **DSA only**. Keep embedded (drivers, rings, memory, concurrency) on a **separate** 4–6 h/week track so DSA does not eat the firmware round. If a week is overloaded, drop greedy/maths, not C coding.

---

## Numbers to hit in 12 weeks

| | Target |
|---|---|
| New problems coded | ~130–150 |
| Marked for revision | ~40 |
| Timed 90-min sessions | ≥12 (one per Sunday) |
| C++ recodes | ≥20 |
| Full mocks (2 Q, 45 min) | ≥6 in weeks 11–12 |

That is enough **technique** for Google DSA if you are solving, not collecting videos. The playlist list is the map; this file is the calendar.
