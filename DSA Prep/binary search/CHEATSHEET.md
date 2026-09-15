# Binary Search Cheatsheet (BS-1 to BS-27)

Use this in interviews. Do **not** memorize 27 solutions — pick a template, name the search space, write a monotonic check.

Source notes: [README](./README.md)

---

## 60-second decision

1. Is **something sorted** (array, row, column, timestamps)? → search **indices**.
2. Is the array **rotated / paired / mountain**? → still indices, but the **invariant** changes (sorted half, pair parity, slope).
3. Are you asked to **minimize/maximize a number** (speed, days, capacity, distance, load)? → search the **answer**, not an index.
4. Two sorted arrays / “kth / median”? → **partition** both arrays.
5. 2D?
   - rows concatenated into one increasing sequence → flatten to 1D (BS-24)
   - rows **and** columns sorted, no global order → staircase (BS-25)
   - each row sorted, need a **value** median → BS on value + count (BS-27)
   - peak in a grid → BS on column + max in that column (BS-26)

If you cannot state: “if `mid` works, then all larger (or all smaller) work,” it is not binary search on the answer yet.

---

## Loop rules (never mix)

| Template | Loop | When `mid` matches | Use |
|---|---|---|---|
| **Eliminate mid** | `while low <= high` | `low = mid + 1` **or** `high = mid - 1` | Find exact value, lower/upper bound with stored `ans` |
| **Keep mid** | `while low < high` | `low = mid` **or** `high = mid` (one side must move) | Converge to a boundary / single leftover index |

Always:

```text
mid ← low + (high - low) / 2     # not (low + high) / 2 in C/Java
```

Python ints do not overflow; still write the safe form in interviews.

**Infinite loop:** `while low < high` and `low = mid` when `mid == low`. Force progress (`mid = (low + high + 1) // 2` if you set `low = mid`).

---

## The three families

```
A. Index search     nums is (almost) sorted
B. Answer search    predicate can(x) is monotonic
C. Partition / 2D   cut two arrays or a matrix
```

---

## Family A — search on indices

### A1. Exact match (BS-1)

Inclusive window. Throw away `mid`.

```
low, high = 0, n - 1
while low <= high:
    mid = low + (high - low) // 2
    if nums[mid] == target: return mid
    if nums[mid] < target:  low = mid + 1
    else:                   high = mid - 1
return -1
```

### A2. First True / bounds (BS-2, BS-3)

Predicate `P(i)` is `False False … False True True … True`.

- **Lower bound:** first `i` with `nums[i] >= x` (or `n`)
- **Upper bound:** first `i` with `nums[i] > x` (or `n`)
- **Search insert:** lower bound (distinct values)
- **Floor:** value at `lb - 1` if `lb > 0` (or `x` if equal)
- **Ceil:** value at `lb` if `lb < n`
- **First occurrence:** lower bound, then check equality
- **Last occurrence:** upper bound − 1
- **Count:** `last - first + 1`

```
ans = n
while low <= high:
    mid = low + (high - low) // 2
    if P(mid):      # e.g. nums[mid] >= x
        ans = mid
        high = mid - 1
    else:
        low = mid + 1
return ans
```

### A3. Sorted half in a rotation (BS-4, BS-5, BS-6, BS-7)

In a rotated **unique** array, **at least one** of `[low, mid]` and `[mid, high]` is sorted.

- `nums[low] <= nums[mid]` → left half sorted. If target is inside that half’s value range, go left; else right.
- Else right half is sorted. Same test on `[nums[mid], nums[high]]`.

**Duplicates (BS-5):** if `nums[low] == nums[mid] == nums[high]`, you cannot tell. `low += 1; high -= 1`. Worst case O(n).

**Minimum / rotation count (BS-6, BS-7):** if `nums[low] <= nums[high]`, window is sorted → `nums[low]` is min. Else drop the sorted half (min cannot sit strictly inside a sorted increasing run). Rotation count = **index of min**.

### A4. Pair parity — unique element (BS-8)

Every value twice except one. Before the single, pairs are `(even, odd)`; after, `(odd, even)`.

Force `mid` even. If `nums[mid] == nums[mid+1]`, single is to the **right** (`low = mid + 2`); else at `mid` or left (`high = mid`).

### A5. Climb the slope — 1D peak (BS-9)

`nums[i] != nums[i+1]`. Treat ends as peaks vs one neighbor.

If `nums[mid] < nums[mid+1]`, a peak exists on the **right** (still rising). Else peak at `mid` or left.

---

## Family B — binary search on the answer

Search **x** in `[lo_ans, hi_ans]`, not an index in `nums`.

```
can(x)  →  True if x is “enough”
monotonic:  can(x) True  ⇒  can(x+1) True     (or the reverse)

minimize x:  if can(mid): ans = mid; high = mid - 1
             else:        low = mid + 1

maximize x:  if can(mid): ans = mid; low = mid + 1
             else:        high = mid - 1
```

| Problem | Search space | `can(x)` | Min or max |
|---|---|---|---|
| BS-10 sqrt | `1 .. n/2` | `mid*mid <= n` | max |
| BS-11 nth root | `1 .. m` | `mid^n ? m` | exact (else −1) |
| BS-12 Koko | `1 .. max(piles)` | hours `sum(ceil(p/k)) <= h` | min k |
| BS-13 bouquets | `min_day .. max_day` | ≥ m groups of k adjacent bloomed | min day |
| BS-14 divisor | `1 .. max(nums)` | `sum(ceil(a/d)) <= threshold` | min d |
| BS-15 ship | `max(w) .. sum(w)` | days needed ≤ D (greedy load) | min cap |
| BS-16 kth missing | index in `arr` | missing before `i` is `arr[i]-(i+1)` | find split, answer `low + k` |
| BS-17 cows | `1 .. max-min` | place `cows` with min dist ≥ d | **max** d |
| BS-18 / BS-19 books, split | `max(a) .. sum(a)` | #contiguous groups with sum ≤ L is ≤ k | min L |
| BS-20 gas stations | real `0 .. max_gap` | extras `sum(ceil(gap/d)-1) <= k` | min d (float) |

**Greedy check patterns you reuse:**

- **Ceil divide:** `(x + d - 1) // d`
- **Pack contiguous until limit** (ship, books, split): start a new group when `acc + x > limit`
- **Place leftmost then next at ≥ dist** (cows)
- **Adjacent run length** (bouquets): reset streak on a 0 / not-yet-bloomed

**Float search (BS-20):** 60–80 iterations of `(low+high)/2`; shrink `high` on feasible.

**Missing count (BS-16):** do not search the integer 1..∞. Search the array index; closed form `answer = low + k` after the loop.

---

## Family C — partition and 2D

### C1. Two sorted arrays (BS-21, BS-22)

Always binary-search the **shorter** array.

Take `i` elements from `a`, `need - i` from `b`. Valid cut:

```
a[i-1] <= b[j]  and  b[j-1] <= a[i]
```

Use `±∞` at ends.

- **Median:** `need = (n1+n2+1)//2`. Odd → `max(lefts)`. Even → average of `max(lefts)` and `min(rights)`.
- **Kth (1-indexed):** `need = k`. Bound `i` to `[max(0, k-n2), min(k, n1)]`. Answer `max(lefts)`.

If `a[i-1] > b[j]`, take fewer from `a` (`high = i-1`); else `low = i+1`.

### C2. Row with max 1s (BS-23)

Each row is `000..0111..1`. Ones in a row = `m - lower_bound(row, 1)`. Track best row. O(n log m).

### C3. Matrix I — globally increasing (BS-24)

Row `i` starts after row `i-1` ends. Flatten:

```
val = matrix[mid // m][mid % m]
```

Standard A1 on `[0, n*m - 1]`.

### C4. Matrix II — row *and* column sorted (BS-25)

**Not** flattenable. Start **top-right** `(0, m-1)`:

- equal → found
- too big → left (drop a column)
- too small → down (drop a row)

O(n + m).

### C5. Peak II (BS-26)

Binary search **columns**. In `mid` column, take the **max** cell. Compare left/right neighbors:

- both ≤ current → peak
- left larger → peak exists on the left (climb)
- else go right

O(n log m).

### C6. Median of row-wise sorted matrix (BS-27)

`n`, `m` odd. Median = smallest `x` with **more than** `(n*m)//2` entries `<= x`.

Search **value** in `[min first-col, max last-col]`. Count `<= mid` with **upper_bound** per row. O(n log m · log(value range)).

---

## Technique → questions

| Technique | IDs |
|---|---|
| Inclusive exact search | BS-1 |
| Lower / upper bound, floor, ceil, insert | BS-2 |
| First / last / count via bounds | BS-3 |
| Identify sorted half | BS-4 |
| Shrink ends on duplicates | BS-5 |
| Min in rotation / drop sorted half | BS-6, BS-7 |
| Even-index pair alignment | BS-8 |
| Slope / unimodal peak | BS-9, BS-26 |
| BS on integer answer + `can(x)` | BS-10 … BS-15, BS-17 … BS-19 |
| Missing = `value - expected_index` | BS-16 |
| Maximize min / minimize max | BS-17 vs BS-18/19 |
| BS on real answer | BS-20 |
| Partition two sorted arrays | BS-21, BS-22 |
| Bound per row in a 2D sorted row | BS-23, BS-27 |
| Flatten 2D to 1D | BS-24 |
| Staircase elimination | BS-25 |
| Count how many ≤ x (value BS) | BS-27 |

---

## Interview bugs

1. Using index-search on an **unsorted** array (unless you search the **answer**).
2. Mixing `low <= high` with `high = mid`.
3. Off-by-one on last occurrence (`upper_bound - 1` without checking the value exists).
4. Rotated search without the `nums[low] <= nums[mid]` (or `<` with duplicates) test.
5. Koko/ship: capacity/speed **0** or empty divide — `low` must be ≥ 1, ship `low = max(weights)`.
6. Books/split: `k > n` is impossible for non-empty groups.
7. Median of two arrays: always BS the smaller array; `±∞` sentinels.
8. Matrix II treated as Matrix I.

---

## What to say out loud

> Search space is ____ from ____ to ____.  
> `can(mid)` is ____ and it is monotonic because ____.  
> I throw away the left/right because ____.

If that sentence is clean, the code is the template above.
