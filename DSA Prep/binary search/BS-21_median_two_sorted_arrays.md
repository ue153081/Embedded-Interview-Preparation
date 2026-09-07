# BS-21 — Median of Two Sorted Arrays

**Playlist:** [takeUforward BS-21](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given two sorted arrays `a` and `b` of sizes `n1` and `n2` (each may be empty, but not both). Return the **median** of the two arrays combined, as a float.

If the combined length is odd, the median is the middle element. If even, it is the average of the two middle elements.

You must do this in O(log(min(n1, n2))) time, not by merging.

**Examples**

- `a = [1, 3]`, `b = [2]` → `2.0`
- `a = [1, 2]`, `b = [3, 4]` → `2.5`

**Constraints:** `0 <= n1, n2 <= 10^5`, `n1 + n2 >= 1`.

## Approaches

**1. Brute force**  
Merge into one sorted array, then pick the middle.  
Time: O(n1 + n2) · Space: O(n1 + n2)

**2. Better**  
Two pointers to the median position(s) without storing the merge.  
Time: O(n1 + n2) · Space: O(1)

**3. Optimized — binary search on the partition**  
Always binary-search the smaller array. Pick `i` elements from `a` and `left - i` from `b` so the left half of the combined sequence has the correct size. A valid cut satisfies `a[i-1] <= b[j]` and `b[j-1] <= a[i]`. Then the median is `max(lefts)` or the average of `max(lefts)` and `min(rights)`.  
Time: O(log min(n1, n2)) · Space: O(1)

## Pseudocode (optimized)

```
find_median(a, b):
    if len(a) > len(b): swap
    n1 ← len(a), n2 ← len(b), n ← n1 + n2
    left ← (n + 1) / 2
    low ← 0, high ← n1
    while low ≤ high:
        i ← (low + high) / 2
        j ← left - i
        aL ← a[i - 1] or -∞, aR ← a[i] or +∞
        bL ← b[j - 1] or -∞, bR ← b[j] or +∞
        if aL ≤ bR and bL ≤ aR:
            if n is odd: return max(aL, bL)
            return (max(aL, bL) + min(aR, bR)) / 2
        if aL > bR: high ← i - 1
        else: low ← i + 1
```

## Solution (optimized)

```python
from typing import List


def find_median_sorted_arrays(a: List[int], b: List[int]) -> float:
    if len(a) > len(b):
        a, b = b, a
    n1, n2 = len(a), len(b)
    n = n1 + n2
    left = (n + 1) // 2
    low, high = 0, n1
    while low <= high:
        i = (low + high) // 2
        j = left - i
        a_left = a[i - 1] if i > 0 else float("-inf")
        a_right = a[i] if i < n1 else float("inf")
        b_left = b[j - 1] if j > 0 else float("-inf")
        b_right = b[j] if j < n2 else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if n % 2 == 1:
                return float(max(a_left, b_left))
            return (max(a_left, b_left) + min(a_right, b_right)) / 2.0
        if a_left > b_right:
            high = i - 1
        else:
            low = i + 1
    raise ValueError("invalid input")
```
