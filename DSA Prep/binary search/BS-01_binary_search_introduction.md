# BS-1 — Binary Search Introduction

**Type:** Coding (Python)  
**Source:** [takeUforward BS-1](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)  
**Companies:** Google · Meta · Amazon · Apple · Microsoft  
**Tier:** S (must-know template)

**Question:** Given a **sorted** array `nums` (non-decreasing) and a target `x`, return **any index** where `nums[i] == x`. If `x` is not present, return `-1`.

Implement **iterative** and **recursive** binary search. Explain overflow-safe `mid` and the `low <= high` vs `low < high` loop choice.

---

## Sub-variant coverage

| Variant | What interviewers expect |
|---|---|
| Iterative | Default production answer; O(1) extra space |
| Recursive | Same logic, O(log n) stack |
| Overflow-safe mid | `mid = low + (high - low) // 2` (not `(low + high) // 2` in languages with 32-bit ints) |
| Missing target | Return `-1`; do not crash on empty input |
| Duplicates | Any valid index is OK for this problem (first/last is BS-3) |

---

## Step 0 — Clarifying questions (say these out loud)

- **Candidate:** Is `nums` sorted non-decreasing? I'll assume yes; binary search is wrong if it is not.
- **Candidate:** Should I return any index on duplicates, or the first/last occurrence? For BS-1 I'll return any match.
- **Candidate:** Empty array or `x` not present — return `-1`?
- **Candidate:** Integers only, no floats? I'll use integer indices.
- **Candidate:** May I mutate the array? I won't; search is read-only.

## Step 1 — Approach

**Brute force:** scan left to right — O(n). Mention this, then discard it because the array is sorted.

**Optimal:** the search space `[low, high]` is ordered. Compare `nums[mid]` to `x` and throw away half the range each step.

1. Restate: “find `x` in a sorted array; return index or `-1`.”
2. Invariant: if `x` exists, it lies in `nums[low..high]` inclusive.
3. Loop while the window is non-empty (`low <= high`).
4. If `nums[mid] == x`, return `mid`.
5. If `nums[mid] < x`, the answer (if any) is to the right → `low = mid + 1`.
6. Else the answer is to the left → `high = mid - 1`.
7. If the window empties, `x` is absent.

## Step 2 — Data structures / invariants

1. `low`, `high` are **inclusive** bounds on the remaining candidate indices.
2. `mid` is always in `[low, high]` while the loop runs.
3. After `low = mid + 1` or `high = mid - 1`, `mid` is never reconsidered (it was not `x`).
4. Termination: each iteration shrinks `high - low` by at least 1, so the loop ends.
5. Recurrence: `T(n) = T(n/2) + O(1)` → `O(log n)` comparisons.

**Why not `(low + high) // 2`?** In Python ints are unbounded, so overflow is not a bug here. In C/C++/Java, `low + high` can overflow a 32-bit `int`. Always write `low + (high - low) // 2` in interviews so the interviewer knows you know.

## Step 3 — Complete solution (Python)

```python
from typing import List


def binary_search_iterative(nums: List[int], x: int) -> int:
    """Return any index i with nums[i] == x, else -1. nums must be sorted."""
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] == x:
            return mid
        if nums[mid] < x:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def binary_search_recursive(nums: List[int], x: int) -> int:
    def rec(low: int, high: int) -> int:
        if low > high:
            return -1
        mid = low + (high - low) // 2
        if nums[mid] == x:
            return mid
        if nums[mid] < x:
            return rec(mid + 1, high)
        return rec(low, mid - 1)

    return rec(0, len(nums) - 1)
```

## Step 4 — Complexity

| Version | Time | Extra space |
|---|---:|---:|
| Iterative | O(log n) | O(1) |
| Recursive | O(log n) | O(log n) call stack |
| Linear scan (brute) | O(n) | O(1) |

`n` = `len(nums)`. Each step halves the window, so at most `floor(log2 n) + 1` comparisons.

## Step 5 — Edge cases

1. Empty array `[]` → `-1`.
2. Single element: match and miss.
3. Target is first element; target is last element.
4. Target smaller than `nums[0]`; larger than `nums[-1]`.
5. All equal values (any index of `x` is correct; `-1` if `x` differs).
6. Even / odd length (makes `mid` lean left with integer division — still correct).

## Step 6 — Overflow / loop-condition notes

This is the DSA analogue of “ISR notes”: the bugs interviewers actually hunt.

- **`low <= high` (inclusive window):** use when you eliminate `mid` with `mid ± 1`. This is the BS-1 default.
- **`low < high` (converging bounds):** use when you *keep* `mid` on one side (`high = mid` or `low = mid`) to find a boundary (lower bound, first True). Do **not** mix the two templates.
- **Infinite loop trap:** if you write `low < high` but then `low = mid` when `mid == low`, the window never shrinks. Always guarantee `low` or `high` moves.
- **Python vs C:** Python `//` truncates toward `-∞`; for non-negative indices this matches C truncating division. Keep indices ≥ 0.

## Step 7 — Follow-up answers

**Q: Walk through `[1, 3, 5, 7, 9]`, target `7`.**  
**A:** `low=0, high=4`, `mid=2` (`5 < 7`) → `low=3`. `mid=3` (`7`) → return `3`.

**Q: Same array, target `6`.**  
**A:** `mid=2` (`5 < 6`) → `low=3`. `mid=3` (`7 > 6`) → `high=2`. `low > high` → `-1`.

**Q: Why is binary search O(log n) not O(n/2 + n/4 + …)?**  
**A:** The *sum* of remaining lengths is ~2n, but we only **look at one mid per step**. Work is proportional to the number of steps, which is `O(log n)`.

**Q: Can I binary-search an unsorted array after sorting?**  
**A:** Sorting is O(n log n) and **destroys original indices** unless you store pairs `(value, index)`. For a one-shot search, linear scan is simpler. Binary search pays off when the array stays sorted or you search many times.

**Q: First occurrence instead of any?**  
**A:** Don’t return on `==`. When `nums[mid] >= x`, set `high = mid - 1` and remember `mid` if equal (lower-bound template — **BS-2 / BS-3**).

**Q: Recursive vs iterative in an interview?**  
**A:** Write iterative unless they ask for recursion. Mention stack depth `O(log n)` for the recursive version.

## Step 8 — Tests

```python
def _check(fn):
    assert fn([], 1) == -1
    assert fn([7], 7) == 0
    assert fn([7], 3) == -1
    assert fn([1, 3, 5, 7, 9], 7) == 3
    assert fn([1, 3, 5, 7, 9], 1) == 0
    assert fn([1, 3, 5, 7, 9], 9) == 4
    assert fn([1, 3, 5, 7, 9], 6) == -1
    assert fn([1, 3, 5, 7, 9], 0) == -1
    assert fn([1, 3, 5, 7, 9], 10) == -1
    idx = fn([2, 2, 2, 2], 2)
    assert idx != -1 and 0 <= idx < 4
    assert fn([2, 2, 2, 2], 3) == -1
    print(fn.__name__, "ok")


if __name__ == "__main__":
    _check(binary_search_iterative)
    _check(binary_search_recursive)
    print("all passed")
```

Run the companion file:

```bash
python3 "DSA Prep/binary search/bs01_binary_search.py"
```

## Further study

- Next: **BS-2** — lower bound / upper bound / insert position (same loop, different predicate).
- Playlist: [takeUforward Binary Search](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

---

*Sample write-up for DSA Prep. Remaining BS-2–BS-27 will follow this template, Python only.*
