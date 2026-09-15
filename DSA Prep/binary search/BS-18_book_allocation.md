# BS-18 — Book Allocation

**Playlist:** [takeUforward BS-18](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

There are `n` books in a row; `pages[i]` is the number of pages in the `i`th book. You must allocate the books to `m` students such that:

- each student gets a **contiguous** sequence of books
- every book is given to exactly one student
- you **minimize the maximum** total pages assigned to any student

Return that minimized maximum. If `m > n`, allocation is impossible — return `-1`.

**Examples**

- `pages = [12, 34, 67, 90]`, `m = 2` → `113`  
  Split after the third book: `(12+34+67, 90) = (113, 90)`
- `pages = [15, 17, 20]`, `m = 2` → `32` (`15+17` and `20`)

**Constraints:** `1 <= n <= 10^5`. Same pattern as “painter’s partition” / split-array largest sum (BS-19).

## Approaches

**1. Brute force**  
Try every way to place `m - 1` cuts among the `n - 1` gaps.  
Time: exponential · Space: O(m)

**2. Optimized — binary search on the max load**  
The answer lies in `[max(pages), sum(pages)]`. For a candidate limit `L`, greedily count how many students you need if no student exceeds `L`. If that count is `<= m`, try a smaller limit.  
Time: O(n log sum) · Space: O(1)

## Pseudocode (optimized)

```
allocate_books(pages, m):
    if m > n: return -1
    low ← max(pages), high ← sum(pages), ans ← high

    students_needed(limit):
        parts ← 1, acc ← 0
        for x in pages:
            if acc + x > limit:
                parts ← parts + 1
                acc ← 0
            acc ← acc + x
        return parts

    while low ≤ high:
        mid ← low + (high - low) / 2
        if students_needed(mid) ≤ m:
            ans ← mid
            high ← mid - 1
        else:
            low ← mid + 1
    return ans
```

## Solution (optimized)

```python
from typing import List


def allocate_books(pages: List[int], students: int) -> int:
    if students > len(pages):
        return -1
    low, high = max(pages), sum(pages)
    ans = high

    def students_needed(limit: int) -> int:
        parts, acc = 1, 0
        for x in pages:
            if acc + x > limit:
                parts += 1
                acc = 0
            acc += x
        return parts

    while low <= high:
        mid = low + (high - low) // 2
        if students_needed(mid) <= students:
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans
```
