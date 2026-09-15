# BS-22 — Kth Element of Two Sorted Arrays

**Playlist:** [takeUforward BS-22](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given two sorted arrays `a` and `b` of sizes `n1` and `n2`, and an integer `k` (1-indexed).

Return the `k`th element in the merged sorted sequence of `a` and `b` (do not actually merge if you can avoid it).

**Examples**

- `a = [2, 3, 6, 7, 9]`, `b = [1, 4, 8, 10]`, `k = 5` → `6`  
  Merged: `[1, 2, 3, 4, 6, 7, 8, 9, 10]`
- `a = [1, 4, 8, 10]`, `b = [2, 3, 6, 7, 9]`, `k = 4` → `4`

**Constraints:** `1 <= k <= n1 + n2`.

## Approaches

**1. Brute force**  
Merge, then return index `k - 1`.  
Time: O(n1 + n2) · Space: O(n1 + n2)

**2. Better**  
Two pointers until you have advanced `k` steps.  
Time: O(k) · Space: O(1)

**3. Optimized — partition like the median problem**  
Take `i` elements from `a` and `k - i` from `b`. Bound `i` to `[max(0, k - n2), min(k, n1)]`. Same cut condition as BS-21; the kth element is `max(a_left, b_left)`.  
Time: O(log min(n1, n2)) · Space: O(1)

## Pseudocode (optimized)

```
kth_element(a, b, k):
    if len(a) > len(b): swap
    n1 ← len(a), n2 ← len(b)
    low ← max(0, k - n2), high ← min(k, n1)
    while low ≤ high:
        i ← (low + high) / 2
        j ← k - i
        aL, aR, bL, bR ← neighbors of the cut (use ±∞ at ends)
        if aL ≤ bR and bL ≤ aR:
            return max(aL, bL)
        if aL > bR: high ← i - 1
        else: low ← i + 1
```

## Solution (optimized)

```python
from typing import List


def kth_element_two_sorted(a: List[int], b: List[int], k: int) -> int:
    n1, n2 = len(a), len(b)
    if n1 > n2:
        return kth_element_two_sorted(b, a, k)
    low = max(0, k - n2)
    high = min(k, n1)
    while low <= high:
        i = (low + high) // 2
        j = k - i
        a_left = a[i - 1] if i > 0 else float("-inf")
        a_right = a[i] if i < n1 else float("inf")
        b_left = b[j - 1] if j > 0 else float("-inf")
        b_right = b[j] if j < n2 else float("inf")
        if a_left <= b_right and b_left <= a_right:
            return int(max(a_left, b_left))
        if a_left > b_right:
            high = i - 1
        else:
            low = i + 1
    raise ValueError("invalid k")
```
